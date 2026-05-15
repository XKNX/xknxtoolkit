from pathlib import Path
from typing import Any

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import portable_file_dialogs as pfd
from xknxmono.product.errors import ArchiveError

from knx_gui.knxprod import DeviceApplication
from knx_gui.plugins.base import API_VERSION, PanelDefinition, PluginAPI
from knx_gui.plugins.cat import CatPlugin
from knx_gui.plugins.catalog import CatalogDatabase, CatalogPlugin, CatalogService
from knx_gui.plugins.connection import ConnectionPlugin
from knx_gui.plugins.connection.service import ConnectionService
from knx_gui.plugins.network import NetworkPlugin
from knx_gui.plugins.node_editor import NodeEditorPlugin
from knx_gui.plugins.project import ProjectPlugin, ProjectService
from knx_gui.strings import S, set_locale


class KnxGuiApp:
    def __init__(self, catalog_path: Path) -> None:
        self._catalog_db = CatalogDatabase(catalog_path)
        if catalog_path.exists():
            self._catalog_db.open()
        else:
            self._catalog_db.create()
        self._catalog_service = CatalogService(self._catalog_db)

        self._open_file_dialog: pfd.open_file | None = None
        self._save_file_dialog: pfd.save_file | None = None
        self._open_project_dialog: pfd.open_file | None = None
        self._save_project_dialog: pfd.save_file | None = None

        self._project_service = ProjectService(self._catalog_service)
        self._connection_service = ConnectionService()

        self._plugin_api = PluginAPI(
            api_version=API_VERSION,
            project=self._project_service,
            catalog=self._catalog_service,
            connection=self._connection_service,
        )

        self._catalog_plugin = CatalogPlugin(self._plugin_api)
        self._connection_plugin = ConnectionPlugin(self._plugin_api)
        self._network_plugin = NetworkPlugin(self._plugin_api)
        self._node_editor_plugin = NodeEditorPlugin(self._plugin_api)
        self._project_plugin = ProjectPlugin(
            self._plugin_api,
            get_selected_node_ids=self._node_editor_plugin.get_selected_node_ids,
        )

        self._cat_plugin = CatPlugin(self._plugin_api)

        self._plugins: list[Any] = [
            self._catalog_plugin,
            self._connection_plugin,
            self._network_plugin,
            self._node_editor_plugin,
            self._project_plugin,
        ]

    def setup(self) -> None:
        self._node_editor_plugin.setup()
        self._cat_plugin.on_load()

    def shutdown(self) -> None:
        self._connection_plugin.shutdown()
        self._node_editor_plugin.shutdown()
        if self._project_service.is_open:
            self._project_service.close()
        self._catalog_db.close()

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
        print(f"[knxprod] loading {path} into catalog")
        try:
            added = self._catalog_service.import_knxprod(Path(path))
            if added:
                print(f"[knxprod] added {len(added)} application(s) to catalog")
                for app_id in added:
                    print(f"[knxprod]   - {app_id}")
            else:
                print("[knxprod] no new applications (already in catalog)")
        except ArchiveError as e:
            print(f"[knxprod] archive error: {e}")
        except (OSError, ValueError) as e:
            print(f"[knxprod] error: {type(e).__name__}: {e}")

    def _add_candidate_as_device(
        self, app: DeviceApplication, template_id: str | None = None
    ) -> None:
        print(
            f"[knxprod] adding {app.name} ({len(app.com_objects)} total, {len(app.visible_com_objects())} visible)"
        )
        if template_id is None:
            template_id = f"{app.manufacturer_id}_{app.application_id}"

        device_id = self._project_service.add_device(
            template_id=template_id,
            name=app.name,
            app=app,
        )
        if device_id:
            self._project_service.add_device_to_state_with_id(
                app=app, node_id=device_id, address=""
            )
        else:
            self._project_service.add_device_to_state(app=app, address="")

        print(
            f"[knxprod] device added; total devices: {len(self._project_service.devices)}"
        )

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

        self._poll_dialogs()
        self._handle_shortcuts()

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
    runner_params.callbacks.post_render_dockable_windows = app._cat_plugin.render

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
