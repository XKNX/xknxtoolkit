import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import imgui_bundle._patch_runners_add_save_screenshot_param as _screenshot_patch

_screenshot_patch._get_caller_filename = lambda depth: ""  # type: ignore[assignment]

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import portable_file_dialogs as pfd
from sqlalchemy.exc import SQLAlchemyError
from xknxproject.exceptions import InvalidPasswordException, XknxProjectException

from knx_gui.plugins.base import API_VERSION, Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.cat import CatPlugin
from knx_gui.plugins.catalog import CatalogPlugin, CatalogService
from knx_gui.plugins.connection import ConnectionPlugin
from knx_gui.plugins.connection.service import ConnectionService
from knx_gui.plugins.keyring import KeyringPlugin
from knx_gui.plugins.logger import LoggerPlugin, LogService
from knx_gui.plugins.monitor import MonitorPlugin
from knx_gui.plugins.network import NetworkPlugin
from knx_gui.plugins.node_editor import NodeEditorPlugin
from knx_gui.plugins.project import ProjectPlugin, ProjectService
from knx_gui.plugins.project.knxproj_manufacturer import collect_manufacturer_bundle
from knx_gui.plugins.proxy import ProxyPlugin
from knx_gui.plugins.virtual import VirtualPlugin
from knx_gui.strings import S, set_locale
from xknxmono.product.errors import ArchiveError
from xknxmono.project import export_knxproj


class KnxGuiApp:
    def __init__(self, catalog_path: Path) -> None:
        self._catalog_service = CatalogService(catalog_path)

        self._open_file_dialog: pfd.open_file | None = None
        self._save_file_dialog: pfd.save_file | None = None
        self._open_project_dialog: pfd.open_file | None = None
        self._save_project_dialog: pfd.save_file | None = None
        self._import_knxproj_save_dialog: pfd.save_file | None = None
        self._export_knxproj_dialog: pfd.save_file | None = None
        self._import_knxproj_source: str | None = None
        self._import_knxproj_dest: str | None = None
        self._password_prompt_requested = False
        self._import_password = ""
        self._import_password_error: str | None = None
        # Background import (keeps the UI responsive during the slow parse/catalog/device build).
        self._import_thread: threading.Thread | None = None
        self._import_pw: str | None = None
        self._import_needs_password = False
        # Generic background worker (catalog load, project open) sharing the progress modal.
        self._bg_thread: threading.Thread | None = None
        # Shared progress-modal state, driven by both the importer and generic background ops.
        self._progress_running = False
        self._progress_requested = False
        self._progress_started_at = 0.0
        self._progress_text = ""

        self._project_service = ProjectService(self._catalog_service)
        self._connection_service = ConnectionService()
        self._log_service = LogService()

        self._plugin_api = PluginAPI(
            api_version=API_VERSION,
            project=self._project_service,
            catalog=self._catalog_service,
            connection=self._connection_service,
            log=self._log_service,
        )

        self._catalog_plugin = CatalogPlugin(self._plugin_api)
        self._connection_plugin = ConnectionPlugin(self._plugin_api)
        self._proxy_plugin = ProxyPlugin(self._plugin_api)
        self._network_plugin = NetworkPlugin(self._plugin_api)
        self._monitor_plugin = MonitorPlugin(self._plugin_api)
        self._keyring_plugin = KeyringPlugin(self._plugin_api)
        self._virtual_plugin = VirtualPlugin(self._plugin_api)
        self._node_editor_plugin = NodeEditorPlugin(self._plugin_api)
        self._project_plugin = ProjectPlugin(
            self._plugin_api,
            get_selected_node_ids=self._node_editor_plugin.get_selected_node_ids,
        )

        self._log = Logger(self._log_service, "app")
        self._cat_plugin = CatPlugin(self._plugin_api)
        self._logger_plugin = LoggerPlugin(self._log_service)

        self._plugins: list[Any] = [
            self._catalog_plugin,
            self._connection_plugin,
            self._proxy_plugin,
            self._network_plugin,
            self._monitor_plugin,
            self._keyring_plugin,
            self._virtual_plugin,
            # project before node_editor so the ETS-like Editor is the default MainDockSpace tab and
            # the node graph sits behind it (still available as a tab).
            self._project_plugin,
            self._node_editor_plugin,
            self._logger_plugin,
        ]

    def setup(self) -> None:
        self._node_editor_plugin.setup()
        self._cat_plugin.on_load()

    def shutdown(self) -> None:
        self._connection_plugin.shutdown()
        self._proxy_plugin.shutdown()
        self._virtual_plugin.shutdown()
        self._node_editor_plugin.shutdown()
        if self._project_service.is_open:
            self._project_service.close()

    def _new_project(self) -> None:
        self._save_project_dialog = pfd.save_file(
            S.FILE_DIALOG_PROJECT_SAVE_TITLE,
            "",
            [S.FILE_DIALOG_PROJECT_FILTER, "*.xknx", S.FILE_DIALOG_ALL_FILES, "*"],
        )

    def _open_project(self) -> None:
        # Accept .knxproj here too: _do_open_project routes ETS archives through the importer.
        self._open_project_dialog = pfd.open_file(
            S.FILE_DIALOG_PROJECT_TITLE,
            "",
            [
                S.FILE_DIALOG_OPEN_FILTER,
                "*.xknx *.knxproj",
                S.FILE_DIALOG_PROJECT_FILTER,
                "*.xknx",
                S.FILE_DIALOG_KNXPROJ_FILTER,
                "*.knxproj",
                S.FILE_DIALOG_ALL_FILES,
                "*",
            ],
        )

    def _export_knxproj(self) -> None:
        if not self._project_service.is_open:
            return
        default = "project.knxproj"
        if self._project_service.path is not None:
            default = self._project_service.path.with_suffix(".knxproj").name
        self._export_knxproj_dialog = pfd.save_file(
            S.FILE_DIALOG_KNXPROJ_SAVE_TITLE,
            default,
            [S.FILE_DIALOG_KNXPROJ_FILTER, "*.knxproj", S.FILE_DIALOG_ALL_FILES, "*"],
        )

    def _do_export_knxproj(self, dest: str) -> None:
        source = self._project_service.path
        if source is None:
            return
        extra_files: dict[str, bytes] = {}
        master_xml: bytes | None = None
        try:
            bundle = collect_manufacturer_bundle(
                self._project_service.program_refs(), self._catalog_service
            )
            extra_files, master_xml = bundle.extra_files, bundle.master_xml
            self._log.info(
                "manufacturer bundle collected",
                manufacturers=len(bundle.resolved_manufacturers),
                files=len(extra_files),
                skipped=len(bundle.skipped_refs),
            )
        except (
            Exception
        ) as e:  # best effort: export the structure even if bundling fails
            self._log.warning(
                "manufacturer bundle failed", error=f"{type(e).__name__}: {e}"
            )
        try:
            export_knxproj(
                source, Path(dest), extra_files=extra_files, master_xml=master_xml
            )
            self._log.info("project exported", path=dest)
        except (OSError, ValueError) as e:
            self._log.error(
                "export failed", path=dest, error=f"{type(e).__name__}: {e}"
            )

    def _do_import_knxproj(self, source: str, dest: str) -> None:
        self._import_knxproj_source = source
        self._import_knxproj_dest = dest
        self._start_import(None)

    def _start_import(self, password: str | None) -> None:
        """Run the import on a worker thread so the UI stays responsive (the facade holds the shared
        lock, so per-frame reads bail to empty placeholders while it runs)."""
        source, dest = self._import_knxproj_source, self._import_knxproj_dest
        if source is None or dest is None or self._import_thread is not None:
            return
        self._log.info("importing knxproj", source=source, dest=dest)
        self._import_pw = password
        self._import_needs_password = False
        self._begin_progress(S.IMPORT_PROGRESS_TEXT)
        self._import_thread = threading.Thread(
            target=self._run_import, args=(source, dest, password), daemon=True
        )
        self._import_thread.start()

    def _run_import(self, source: str, dest: str, password: str | None) -> None:
        # Worker thread: only touches services + logging (never imgui). Outcome is read in
        # _poll_import on the UI thread once the thread has finished.
        self._import_needs_password = self._try_import_knxproj(source, dest, password)

    def _poll_import(self) -> None:
        thread = self._import_thread
        if thread is None or thread.is_alive():
            return
        self._import_thread = None
        self._progress_running = False
        if self._import_needs_password:
            # Wrong password on retry (a password was supplied); otherwise the first prompt.
            self._import_password_error = (
                S.IMPORT_PASSWORD_WRONG if self._import_pw is not None else None
            )
            self._import_password = ""
            self._password_prompt_requested = True
        else:
            self._clear_import_prompt()

    def _begin_progress(self, text: str) -> None:
        self._progress_text = text
        self._progress_running = True
        self._progress_requested = True
        self._progress_started_at = time.time()

    def _run_bg(self, text: str, fn: "Callable[[], None]") -> None:
        """Run ``fn`` on a worker thread behind the progress modal. ``fn`` must hold the shared IO
        lock while it writes so per-frame UI reads bail (see ProjectService/CatalogService)."""
        if self._bg_thread is not None or self._import_thread is not None:
            return
        self._begin_progress(text)

        def worker() -> None:
            try:
                fn()
            except Exception as e:
                self._log.error(
                    "background task failed", error=f"{type(e).__name__}: {e}"
                )

        self._bg_thread = threading.Thread(target=worker, daemon=True)
        self._bg_thread.start()

    def _poll_bg(self) -> None:
        if self._bg_thread is not None and not self._bg_thread.is_alive():
            self._bg_thread = None
            self._progress_running = False

    def _render_progress_modal(self) -> None:
        if self._progress_requested:
            imgui.open_popup(S.PROGRESS_TITLE)
            self._progress_requested = False
        imgui.set_next_window_size(imgui.ImVec2(360.0, 0.0), imgui.Cond_.appearing)
        if not imgui.begin_popup_modal(
            S.PROGRESS_TITLE, None, imgui.WindowFlags_.always_auto_resize
        )[0]:
            return
        imgui.text_wrapped(self._progress_text)
        elapsed = time.time() - self._progress_started_at
        dots = "." * (int(elapsed * 2) % 4)
        imgui.text_disabled(f"{elapsed:0.0f}s {dots}")
        if not self._progress_running:
            imgui.close_current_popup()
        imgui.end_popup()

    def _try_import_knxproj(self, source: str, dest: str, password: str | None) -> bool:
        """Attempt the import. Returns ``True`` if a password is required (or wrong) and the caller
        should prompt; ``False`` on success or on any other failure (which is logged)."""
        try:
            self._project_service.import_knxproj(
                Path(source), Path(dest), password=password
            )
        except InvalidPasswordException:
            return True
        except XknxProjectException as e:
            self._log.error("knxproj import failed", source=source, error=str(e))
        except Exception as e:
            # Runs on a worker thread: never let an unexpected error kill the thread silently, or
            # the UI would wait on a spinner that never clears. Log and report as a plain failure.
            self._log.error(
                "knxproj import error", source=source, error=f"{type(e).__name__}: {e}"
            )
        return False

    def _render_import_password_modal(self) -> None:
        if self._password_prompt_requested:
            imgui.open_popup(S.IMPORT_PASSWORD_TITLE)
            self._password_prompt_requested = False
        imgui.set_next_window_size(imgui.ImVec2(420, 0), imgui.Cond_.appearing)
        if not imgui.begin_popup_modal(
            S.IMPORT_PASSWORD_TITLE, None, imgui.WindowFlags_.always_auto_resize
        )[0]:
            return
        imgui.text_wrapped(S.IMPORT_PASSWORD_PROMPT)
        imgui.set_next_item_width(-1)
        submitted, self._import_password = imgui.input_text(
            "##import-password",
            self._import_password,
            imgui.InputTextFlags_.password | imgui.InputTextFlags_.enter_returns_true,
        )
        if self._import_password_error:
            imgui.text_colored(
                imgui.ImVec4(0.9, 0.4, 0.4, 1.0), self._import_password_error
            )
        imgui.spacing()
        btn_w = imgui.ImVec2(120, 0)
        confirm = imgui.button(S.BTN_OK, btn_w) or submitted
        imgui.same_line()
        cancel = imgui.button(S.BTN_CANCEL, btn_w)
        source, dest = self._import_knxproj_source, self._import_knxproj_dest
        if confirm and source is not None and dest is not None:
            # Retry on a worker thread; _poll_import re-opens this modal if the password was wrong.
            imgui.close_current_popup()
            self._start_import(self._import_password)
        elif cancel:
            self._clear_import_prompt()
            imgui.close_current_popup()
        imgui.end_popup()

    def _clear_import_prompt(self) -> None:
        self._import_knxproj_source = None
        self._import_knxproj_dest = None
        self._import_password = ""
        self._import_password_error = None

    def _do_new_project(self, path: str) -> None:
        self._project_service.new(Path(path))

    def _do_open_project(self, path: str) -> None:
        # A .knxproj is an ETS archive, not an .xknx SQLite document. If one is picked here (a common
        # mix-up), route it through the importer instead of trying to open it as a database.
        if path.lower().endswith(".knxproj"):
            self._prompt_import_dest(path)
            return

        def worker() -> None:
            try:
                self._project_service.open(Path(path))
            except (ValueError, SQLAlchemyError) as e:
                # A missing/stale/corrupt file must not take down the app (e.g. the demo project
                # opened at startup, or a bad file picked via "Open Project").
                self._log.error("could not open project", path=path, error=str(e))

        # Open on a worker thread behind the spinner: building a large project's device view is slow.
        self._run_bg(S.PROGRESS_OPEN_PROJECT, worker)

    def _prompt_import_dest(self, source: str) -> None:
        """Remember the .knxproj source and ask where to save the imported .xknx project."""
        self._import_knxproj_source = source
        # Pass only the default file name, not a full path: on macOS a path with "/" in the save
        # dialog's name field gets mangled into ":"-separated segments.
        self._import_knxproj_save_dialog = pfd.save_file(
            S.FILE_DIALOG_PROJECT_SAVE_TITLE,
            Path(source).with_suffix(".xknx").name,
            [S.FILE_DIALOG_PROJECT_FILTER, "*.xknx", S.FILE_DIALOG_ALL_FILES, "*"],
        )

    def _undo(self) -> None:
        self._project_service.undo()

    def _redo(self) -> None:
        self._project_service.redo()

    def _can_undo(self) -> bool:
        return self._project_service.is_open and self._project_service.can_undo()

    def _can_redo(self) -> bool:
        return self._project_service.is_open and self._project_service.can_redo()

    def _poll_dialogs(self) -> None:
        self._poll_import()
        self._poll_bg()

        if self._open_file_dialog is not None and self._open_file_dialog.ready():
            result = self._open_file_dialog.result()
            self._open_file_dialog = None
            if result:
                self._load_knxprod(result[0])

        if self._save_project_dialog is not None and self._save_project_dialog.ready():
            result = self._save_project_dialog.result()
            self._save_project_dialog = None
            if result:
                self._do_new_project(result)

        if self._open_project_dialog is not None and self._open_project_dialog.ready():
            result = self._open_project_dialog.result()
            self._open_project_dialog = None
            if result:
                self._do_open_project(result[0])

        if (
            self._export_knxproj_dialog is not None
            and self._export_knxproj_dialog.ready()
        ):
            result = self._export_knxproj_dialog.result()
            self._export_knxproj_dialog = None
            if result:
                self._do_export_knxproj(result)

        if (
            self._import_knxproj_save_dialog is not None
            and self._import_knxproj_save_dialog.ready()
        ):
            result = self._import_knxproj_save_dialog.result()
            self._import_knxproj_save_dialog = None
            source = self._import_knxproj_source
            self._import_knxproj_source = None
            if result and source is not None:
                self._do_import_knxproj(source, result)

    def _handle_shortcuts(self) -> None:
        io = imgui.get_io()
        if (io.key_ctrl or io.key_super) and imgui.is_key_pressed(imgui.Key.z):
            if io.key_shift:
                self._redo()
            else:
                self._undo()
        elif (io.key_ctrl or io.key_super) and imgui.is_key_pressed(imgui.Key.y):
            self._redo()

    def _load_knxprod(self, path: str) -> None:
        def worker() -> None:
            # Hold the catalog lock so per-frame catalog reads bail while it writes (see io_guarded).
            with self._catalog_service.io_lock:
                self._log.info("loading knxprod", path=path)
                try:
                    added = self._catalog_service.import_knxprod(Path(path))
                    if added:
                        self._log.info(
                            "added applications to catalog", count=len(added)
                        )
                    else:
                        self._log.info("no new applications", path=path)
                except ArchiveError as e:
                    self._log.error("archive error", path=path, error=str(e))
                except (OSError, ValueError) as e:
                    self._log.error(
                        "import error", path=path, error=f"{type(e).__name__}: {e}"
                    )

        self._run_bg(S.PROGRESS_LOAD_KNXPROD, worker)

    def gui_status_bar(self) -> None:
        self._connection_plugin.render_status_indicator()

        # ETS-like indicator: a bus operation (programming/testing) in progress.
        busy = self._connection_service.busy_operation
        if busy is not None:
            kind, address = busy
            if kind == "program":
                text = S.STATUS_PROGRAMMING.format(address=address)
                prog = self._connection_service.busy_progress
                if prog is not None:
                    text += f" ({prog[0]}/{prog[1]})"
            else:
                text = S.STATUS_TESTING.format(address=address)
            imgui.same_line()
            imgui.text_disabled(" | ")
            imgui.same_line()
            imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.95, 0.75, 0.2, 1.0))
            imgui.text(text)
            imgui.pop_style_color()
        elif self._connection_service.not_connected_notice():
            # A connection-requiring feature (program/test/send) was just refused:
            # flash the reason so the user sees *why* nothing happened.
            imgui.same_line()
            imgui.text_disabled(" | ")
            imgui.same_line()
            imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.9, 0.35, 0.35, 1.0))
            imgui.text(S.STATUS_NO_CONNECTION)
            imgui.pop_style_color()
        else:
            # Briefly show the last programming outcome after the busy indicator clears.
            notice = self._connection_service.program_notice()
            if notice is not None:
                ok = notice
                color = (
                    imgui.ImVec4(0.4, 0.85, 0.45, 1.0)
                    if ok
                    else imgui.ImVec4(0.9, 0.35, 0.35, 1.0)
                )
                imgui.same_line()
                imgui.text_disabled(" | ")
                imgui.same_line()
                imgui.push_style_color(imgui.Col_.text, color)
                imgui.text(S.STATUS_PROGRAM_DONE if ok else S.STATUS_PROGRAM_FAILED)
                imgui.pop_style_color()

        # Current project summary.
        imgui.same_line()
        imgui.text_disabled(" | ")
        imgui.same_line()
        if self._project_service.is_open:
            meta = self._project_service.get_project_metadata()
            name = meta.name if meta and meta.name else None
            if not name and self._project_service.path is not None:
                name = self._project_service.path.name
            imgui.text_disabled(
                S.STATUS_PROJECT.format(
                    name=name or "?",
                    devices=len(self._project_service.devices),
                    gas=len(self._project_service.group_addresses),
                )
            )
        else:
            imgui.text_disabled(S.STATUS_NO_PROJECT)

    def gui_menu(self) -> None:
        if imgui.begin_menu(S.MENU_FILE):
            if imgui.menu_item(S.MENU_NEW_PROJECT, "", False)[0]:
                self._new_project()
            if imgui.menu_item(S.MENU_OPEN_PROJECT, "", False)[0]:
                self._open_project()
            if imgui.menu_item(
                S.MENU_EXPORT_KNXPROJ, "", False, self._project_service.is_open
            )[0]:
                self._export_knxproj()
            imgui.separator()
            if imgui.menu_item(S.MENU_LOAD_KNXPROD, "", False)[0]:
                self._open_file_dialog = pfd.open_file(
                    S.FILE_DIALOG_KNXPROD_TITLE,
                    "",
                    [
                        S.FILE_DIALOG_KNXPROD_FILTER,
                        "*.knxprod",
                        S.FILE_DIALOG_ALL_FILES,
                        "*",
                    ],
                )
            imgui.separator()
            if imgui.menu_item(S.MENU_EXIT, "", False)[0]:
                hello_imgui.get_runner_params().app_shall_exit = True
            imgui.end_menu()

        if imgui.begin_menu(S.MENU_EDIT):
            if imgui.menu_item(S.MENU_UNDO, S.SHORTCUT_UNDO, False, self._can_undo())[
                0
            ]:
                self._undo()
            if imgui.menu_item(S.MENU_REDO, S.SHORTCUT_REDO, False, self._can_redo())[
                0
            ]:
                self._redo()
            imgui.end_menu()

        hello_imgui.show_view_menu(hello_imgui.get_runner_params())

        self._connection_plugin.render_menu()
        self._proxy_plugin.render_menu()

        self._poll_dialogs()
        self._handle_shortcuts()

    def render_overlays(self) -> None:
        self._cat_plugin.render()
        self._project_plugin.render_overlays()
        self._render_progress_modal()
        self._render_import_password_modal()

    def get_all_panels(self) -> list[PanelDefinition]:
        panels: list[PanelDefinition] = []
        for plugin in self._plugins:
            panels.extend(plugin.panels)
        return panels


def create_docking_splits() -> list[hello_imgui.DockingSplit]:
    split_left = hello_imgui.DockingSplit()
    split_left.initial_dock = "MainDockSpace"
    split_left.new_dock = "LeftSpace"
    split_left.direction = imgui.Dir.left
    split_left.ratio = 0.2

    split_bottom = hello_imgui.DockingSplit()
    split_bottom.initial_dock = "MainDockSpace"
    split_bottom.new_dock = "BottomSpace"
    split_bottom.direction = imgui.Dir.down
    split_bottom.ratio = 0.25

    split_right = hello_imgui.DockingSplit()
    split_right.initial_dock = "MainDockSpace"
    split_right.new_dock = "RightSpace"
    split_right.direction = imgui.Dir.right
    split_right.ratio = 0.25

    return [split_left, split_bottom, split_right]


def create_dockable_windows(app: KnxGuiApp) -> list[hello_imgui.DockableWindow]:
    windows: list[hello_imgui.DockableWindow] = []
    for panel in app.get_all_panels():
        window = hello_imgui.DockableWindow()
        window.label = panel.label
        window.dock_space_name = panel.dock
        window.gui_function = panel.render
        windows.append(window)
    return windows


def _detect_locale() -> str:
    import locale

    try:
        locale.setlocale(locale.LC_ALL, "")
        lang, _ = locale.getlocale()
        if lang:
            return lang.split("_")[0]
    except (ValueError, locale.Error):
        pass

    return "en"


def main() -> None:
    import sys

    if "--profile" in sys.argv:
        import cProfile
        import io
        import pstats

        pr = cProfile.Profile()
        pr.enable()
        try:
            _main()
        finally:
            pr.disable()
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
            ps.print_stats(80)
            print(s.getvalue())
        return
    _main()


def _main() -> None:
    set_locale(_detect_locale())

    catalog_path = Path(__file__).parent.parent.parent / "demo.xknxcatalog"
    app = KnxGuiApp(catalog_path)

    demo_path = Path(__file__).parent.parent.parent / "demo.xknx"
    if demo_path.exists():
        app._do_open_project(str(demo_path))

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = S.APP_TITLE
    runner_params.app_window_params.window_geometry.size = (1280, 720)
    runner_params.app_window_params.restore_previous_geometry = True
    runner_params.fps_idling.enable_idling = False

    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    runner_params.imgui_window_params.enable_viewports = True

    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.imgui_window_params.show_menu_app = False
    runner_params.imgui_window_params.show_menu_view = False
    runner_params.callbacks.show_menus = app.gui_menu

    runner_params.imgui_window_params.show_status_bar = True
    runner_params.imgui_window_params.remember_status_bar_settings = False
    runner_params.callbacks.show_status = app.gui_status_bar

    runner_params.docking_params.docking_splits = create_docking_splits()
    runner_params.docking_params.dockable_windows = create_dockable_windows(app)

    runner_params.callbacks.post_init = app.setup
    runner_params.callbacks.before_exit = app.shutdown
    runner_params.callbacks.post_render_dockable_windows = app.render_overlays

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
