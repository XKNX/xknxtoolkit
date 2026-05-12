from pathlib import Path

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import portable_file_dialogs as pfd
from xknxmono.product.errors import ArchiveError

from knx_gui.dialogs import LinkWarningDialog
from knx_gui.dpt import lookup_or_make_dpt
from knx_gui.knxprod import DeviceApplication, parse_application_xml
from knx_gui.plugins.base import API_VERSION, EventBus, PluginAPI
from knx_gui.plugins.catalog import CatalogDatabase, CatalogPlugin, CatalogService
from knx_gui.plugins.catalog.db import ApplicationModel
from knx_gui.plugins.connection import ConnectionPlugin
from knx_gui.plugins.node_editor import NodeEditorPlugin
from knx_gui.plugins.project import ProjectPlugin, ProjectService
from knx_gui.plugins.telegrams import TelegramsPlugin
from knx_gui.state import AppState, create_empty_state
from knx_gui.strings import S
from knx_gui.types import Device


class KnxGuiApp:
    def __init__(self, state: AppState, catalog_path: Path) -> None:
        self._state = state
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

        self._link_warning_dialog = LinkWarningDialog(
            on_confirm=self._on_link_warning_confirm
        )

        self._event_bus = EventBus()
        self._project_service = ProjectService(self._event_bus)

        self._plugin_api = PluginAPI(
            api_version=API_VERSION,
            state=self._state,
            project=self._project_service,
            catalog=self._catalog_service,
            events=self._event_bus,
        )

        self._catalog_plugin = CatalogPlugin(self._plugin_api)
        self._connection_plugin = ConnectionPlugin(self._plugin_api)
        self._telegrams_plugin = TelegramsPlugin(self._plugin_api)
        self._node_editor_plugin = NodeEditorPlugin(
            api=self._plugin_api,
            on_param_change=self._on_param_change,
        )
        self._project_plugin = ProjectPlugin(
            api=self._plugin_api,
            on_param_change=self._on_param_change,
        )

        self._state.subscribe("reload_requested", self._on_reload_requested)

    def _on_reload_requested(self) -> None:
        self._load_devices_from_db()
        self._load_links_from_db()

    def _remove_device(self, device_id: str) -> None:
        raise NotImplementedError("Device removal not yet implemented")

    def _on_param_change(self, device: Device, param_id: str, value: str) -> None:
        old_value = device._param_values.get(param_id, "")
        if old_value == value:
            return

        hidden_cos = self._state.check_param_change_hides_com_objects(
            device, param_id, value
        )
        if hidden_cos:
            affected_links = self._node_editor_plugin.panel.find_links_for_com_objects(
                device, hidden_cos
            )
            if affected_links:
                self._link_warning_dialog.request_confirmation(
                    device, param_id, value, hidden_cos, affected_links
                )
                return

        self._state.set_param(device, param_id, value)

    def _on_link_warning_confirm(
        self,
        device: Device,
        param_id: str,
        value: str,
        affected_links: list[tuple[int, int, int]],
    ) -> None:
        for link in affected_links:
            self._state.remove_link(link[0])
        self._state.set_param(device, param_id, value)

    def _add_device_from_catalog(self, application_id: str) -> None:
        xml_data = self._catalog_service.get_application_xml(application_id)
        if not xml_data:
            print(f"[catalog] application not found: {application_id}")
            return

        app_model = (
            self._catalog_service.session.query(ApplicationModel)
            .filter_by(application_id=application_id)
            .first()
        )
        if not app_model:
            return

        apps = parse_application_xml(xml_data, app_model.manufacturer_id)
        if not apps:
            print(f"[catalog] no applications parsed from {application_id}")
            return

        app = apps[0]
        print(f"[catalog] adding {app.name} ({len(app.com_objects)} com objects)")
        self._add_candidate_as_device(app, template_id=application_id)

    def setup(self) -> None:
        self._node_editor_plugin.setup()

    def shutdown(self) -> None:
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
        self._state.devices.clear()
        self._state.links.clear()

    def _do_open_project(self, path: str) -> None:
        self._project_service.open(Path(path))
        self._load_devices_from_db()
        self._load_links_from_db()

    def _load_links_from_db(self) -> None:
        if not self._project_service.is_open:
            return
        from knx_gui.plugins.project.db import LinkModel

        self._state.links.clear()
        for link_model in self._project_service.session.query(LinkModel).all():
            self._state.links.append(
                (link_model.id, link_model.start_pin, link_model.end_pin)
            )
        max_link_id = max((link[0] for link in self._state.links), default=999)
        self._state._next_link_id = max_link_id + 1

    def _load_devices_from_db(self) -> None:
        if not self._project_service.is_open:
            return
        from knx_gui.plugins.project.db import (
            ComObjectModel,
            DeviceModel,
            ParameterModel,
        )

        selected_node_id = (
            self._state.selected_device.node_id if self._state.selected_device else None
        )
        self._state.devices.clear()
        for device_model in self._project_service.session.query(DeviceModel).all():
            app = self._get_app_for_device(device_model.template_id)
            if not app:
                print(
                    f"[project] skipping device {device_model.id}: template '{device_model.template_id}' not found"
                )
                continue
            device = self._state.add_device_with_id(
                app=app,
                node_id=device_model.id,
                address=device_model.address or "",
            )
            for param_model in (
                self._project_service.session.query(ParameterModel)
                .filter_by(device_id=device_model.id)
                .all()
            ):
                device.set_param_value(param_model.param_id, param_model.value)
            for co_model in (
                self._project_service.session.query(ComObjectModel)
                .filter_by(device_id=device_model.id)
                .all()
            ):
                co = device.find_com_object(co_model.co_id)
                if co:
                    co.dpt = lookup_or_make_dpt(
                        f"{co_model.dpt_major}.{co_model.dpt_minor}"
                    )
                    co.flags.communication = co_model.flag_communication
                    co.flags.read = co_model.flag_read
                    co.flags.write = co_model.flag_write
                    co.flags.transmit = co_model.flag_transmit
                    co.flags.update = co_model.flag_update
        if selected_node_id is not None:
            self._state.selected_device = self._state.find_device_by_node_id(
                selected_node_id
            )

    def _get_app_for_device(self, template_id: str) -> DeviceApplication | None:
        xml_data = self._catalog_service.get_application_xml(template_id)
        if not xml_data:
            return None
        app_model = (
            self._catalog_service.session.query(ApplicationModel)
            .filter_by(application_id=template_id)
            .first()
        )
        if not app_model:
            return None
        apps = parse_application_xml(xml_data, app_model.manufacturer_id)
        if not apps:
            return None
        return apps[0]

    def _undo(self) -> None:
        if self._project_service and self._project_service.can_undo():
            self._project_service.undo()
            self._project_service.session.expire_all()
            self._load_devices_from_db()
            self._load_links_from_db()

    def _redo(self) -> None:
        if self._project_service and self._project_service.can_redo():
            self._project_service.redo()
            self._project_service.session.expire_all()
            self._load_devices_from_db()
            self._load_links_from_db()

    def _can_undo(self) -> bool:
        return self._project_service.is_open and self._project_service.can_undo()

    def _can_redo(self) -> bool:
        return self._project_service.is_open and self._project_service.can_redo()

    def _sync_selected_device_from_editor(self) -> None:
        selected_ids = self._node_editor_plugin.panel.get_selected_node_ids()
        if len(selected_ids) != 1:
            return
        node_id = selected_ids[0]
        if (
            self._state.selected_device
            and self._state.selected_device.node_id == node_id
        ):
            return
        device = self._state.find_device_by_node_id(node_id)
        if device:
            self._state.selected_device = device

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
            self._state.add_device_with_id(app=app, node_id=device_id, address="")
        else:
            self._state.add_device(app=app, address="")

        print(f"[knxprod] device added; total devices: {len(self._state.devices)}")

    def gui_status_bar(self) -> None:
        self._connection_plugin.render_status_indicator()
        imgui.same_line()
        imgui.text(
            S.STATUS_DEVICES_LINKS.format(
                devices=len(self._state.devices), links=len(self._state.links)
            )
        )

    def gui_menu(self) -> None:
        if imgui.begin_menu(S.MENU_FILE):
            if imgui.menu_item(S.MENU_NEW_PROJECT, "", False)[0]:
                self._new_project()
            if imgui.menu_item(S.MENU_OPEN_PROJECT, "", False)[0]:
                self._open_project()
            imgui.begin_disabled(not self._project_service.is_open)
            if imgui.menu_item(S.MENU_SAVE_PROJECT, "", False)[0]:
                pass
            imgui.end_disabled()
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

        self._connection_plugin.render_menu()

        self._poll_dialogs()
        self._handle_shortcuts()

    def gui_devices(self) -> None:
        self._project_plugin.devices_panel.render()

    def gui_catalog(self) -> None:
        self._catalog_plugin.panel.render()

    def gui_node_editor(self) -> None:
        self._node_editor_plugin.panel.render()
        self._link_warning_dialog.render()

    def gui_telegrams(self) -> None:
        self._telegrams_plugin.panel.render()

    def gui_configure(self) -> None:
        self._sync_selected_device_from_editor()
        self._project_plugin.configure_panel.render()

    def gui_history(self) -> None:
        self._project_plugin.history_panel.render()


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
    devices_window = hello_imgui.DockableWindow()
    devices_window.label = S.PANEL_DEVICES
    devices_window.dock_space_name = "LeftSpace"
    devices_window.gui_function = app.gui_devices

    catalog_window = hello_imgui.DockableWindow()
    catalog_window.label = S.PANEL_CATALOG
    catalog_window.dock_space_name = "LeftSpace"
    catalog_window.gui_function = app.gui_catalog

    editor_window = hello_imgui.DockableWindow()
    editor_window.label = S.PANEL_NODE_EDITOR
    editor_window.dock_space_name = "MainDockSpace"
    editor_window.gui_function = app.gui_node_editor

    telegrams_window = hello_imgui.DockableWindow()
    telegrams_window.label = S.PANEL_TELEGRAMS
    telegrams_window.dock_space_name = "BottomSpace"
    telegrams_window.gui_function = app.gui_telegrams

    configure_window = hello_imgui.DockableWindow()
    configure_window.label = S.PANEL_CONFIGURE
    configure_window.dock_space_name = "RightSpace"
    configure_window.gui_function = app.gui_configure

    history_window = hello_imgui.DockableWindow()
    history_window.label = S.PANEL_HISTORY
    history_window.dock_space_name = "RightSpace"
    history_window.gui_function = app.gui_history

    return [
        devices_window,
        catalog_window,
        editor_window,
        telegrams_window,
        configure_window,
        history_window,
    ]


def main() -> None:
    state = create_empty_state()
    catalog_path = Path(__file__).parent.parent.parent / "demo.xknxcatalog"
    app = KnxGuiApp(state, catalog_path)

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
    runner_params.imgui_window_params.show_menu_view = True
    runner_params.callbacks.show_menus = app.gui_menu

    runner_params.imgui_window_params.show_status_bar = True
    runner_params.imgui_window_params.remember_status_bar_settings = False
    runner_params.callbacks.show_status = app.gui_status_bar

    runner_params.docking_params.docking_splits = create_docking_splits()
    runner_params.docking_params.dockable_windows = create_dockable_windows(app)

    runner_params.callbacks.post_init = app.setup
    runner_params.callbacks.before_exit = app.shutdown

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
