from pathlib import Path
from typing import Any

import imgui_bundle._patch_runners_add_save_screenshot_param as _screenshot_patch

_screenshot_patch._get_caller_filename = lambda depth: ""  # type: ignore[assignment]

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import portable_file_dialogs as pfd

from knx_gui.plugins.base import API_VERSION, Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.cat import CatPlugin
from knx_gui.plugins.catalog import CatalogPlugin, CatalogService
from knx_gui.plugins.connection import ConnectionPlugin
from knx_gui.plugins.connection.service import ConnectionService
from knx_gui.plugins.logger import LoggerPlugin, LogService
from knx_gui.plugins.network import NetworkPlugin
from knx_gui.plugins.node_editor import NodeEditorPlugin
from knx_gui.plugins.project import ProjectPlugin, ProjectService
from knx_gui.plugins.proxy import ProxyPlugin
from knx_gui.plugins.virtual import VirtualPlugin
from knx_gui.strings import S, set_locale
from xknxmono.product.errors import ArchiveError


class KnxGuiApp:
    def __init__(self, catalog_path: Path) -> None:
        self._catalog_service = CatalogService(catalog_path)

        self._open_file_dialog: pfd.open_file | None = None
        self._save_file_dialog: pfd.save_file | None = None
        self._open_project_dialog: pfd.open_file | None = None
        self._save_project_dialog: pfd.save_file | None = None

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
            self._virtual_plugin,
            self._node_editor_plugin,
            self._project_plugin,
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
        self._open_project_dialog = pfd.open_file(
            S.FILE_DIALOG_PROJECT_TITLE,
            "",
            [S.FILE_DIALOG_PROJECT_FILTER, "*.xknx", S.FILE_DIALOG_ALL_FILES, "*"],
        )

    def _do_new_project(self, path: str) -> None:
        self._project_service.new(Path(path))

    def _do_open_project(self, path: str) -> None:
        self._project_service.open(Path(path))

    def _undo(self) -> None:
        self._project_service.undo()

    def _redo(self) -> None:
        self._project_service.redo()

    def _can_undo(self) -> bool:
        return self._project_service.is_open and self._project_service.can_undo()

    def _can_redo(self) -> bool:
        return self._project_service.is_open and self._project_service.can_redo()

    def _poll_dialogs(self) -> None:
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
        self._log.info("loading knxprod", path=path)
        try:
            added = self._catalog_service.import_knxprod(Path(path))
            if added:
                self._log.info("added applications to catalog", count=len(added))
            else:
                self._log.info("no new applications", path=path)
        except ArchiveError as e:
            self._log.error("archive error", path=path, error=str(e))
        except (OSError, ValueError) as e:
            self._log.error("import error", path=path, error=f"{type(e).__name__}: {e}")

    def gui_status_bar(self) -> None:
        self._connection_plugin.render_status_indicator()

    def gui_menu(self) -> None:
        if imgui.begin_menu(S.MENU_FILE):
            if imgui.menu_item(S.MENU_NEW_PROJECT, "", False)[0]:
                self._new_project()
            if imgui.menu_item(S.MENU_OPEN_PROJECT, "", False)[0]:
                self._open_project()
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
