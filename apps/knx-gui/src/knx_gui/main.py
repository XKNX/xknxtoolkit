import math
from pathlib import Path

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import portable_file_dialogs as pfd

from knx_gui.catalog import (
    CatalogDatabase,
    get_application_xml,
    load_knxprod_to_catalog,
)
from knx_gui.catalog.models import ApplicationModel
from knx_gui.dpt import DPT, DPT_UNKNOWN, lookup_or_make_dpt
from knx_gui.knxprod import DeviceApplication, parse_application_xml
from knx_gui.panels import (
    CatalogEntry,
    CatalogPanel,
    ConfigurePanel,
    DevicesPanel,
    HistoryPanel,
    NodeEditorPanel,
    TelegramsPanel,
)
from knx_gui.project.database import ProjectDatabase
from knx_gui.project.events import (
    ComObjectFlagChanged,
    DeviceAdded,
    LinkCreated,
    LinkRemoved,
)
from knx_gui.state import AppState, create_empty_state
from knx_gui.strings import S
from knx_gui.types import (
    ComObject,
    ComObjectFlags,
    Device,
    DeviceConfig,
    DeviceTemplate,
    Parameter,
    color_u32,
)
from xknx.product.errors import ArchiveError

NAVIGATE_TO_NODE_DURATION = 0.3


class KnxGuiApp:
    def __init__(self, state: AppState, catalog_path: Path) -> None:
        self._state = state
        self._project: ProjectDatabase | None = None
        self._project_path: Path | None = None
        self._catalog = CatalogDatabase(catalog_path)
        if catalog_path.exists():
            self._catalog.open()
        else:
            self._catalog.create()

        self._open_file_dialog: pfd.open_file | None = None
        self._save_file_dialog: pfd.save_file | None = None
        self._open_project_dialog: pfd.open_file | None = None
        self._save_project_dialog: pfd.save_file | None = None

        self._node_editor_panel = NodeEditorPanel(
            get_devices=lambda: self._state.devices,
            get_links=lambda: self._state.links,
            add_link=self._add_link,
            remove_link=self._remove_link,
            on_param_change=self._state.check_param_change_hides_com_objects,
            on_flag_change=self._on_flag_change,
        )
        self._devices_panel = DevicesPanel(
            get_devices=lambda: self._state.devices,
            on_select_device=self._select_and_navigate_to_device,
        )
        self._catalog_panel = CatalogPanel(
            get_catalog_entries=self._get_catalog_entries,
            on_add_from_catalog=self._add_device_from_catalog,
        )
        self._telegrams_panel = TelegramsPanel(
            get_telegrams=lambda: self._state.telegrams,
            on_focus_source=self._focus_device_by_address,
        )
        self._configure_panel = ConfigurePanel(
            get_devices=lambda: self._state.devices,
            get_selected_device=lambda: self._state.selected_device,
            set_selected_device=self._set_selected_device,
            on_param_change=self._on_config_param_change,
            on_flag_change=self._on_flag_change,
        )
        self._history_panel = HistoryPanel(
            get_entries=self._get_history_entries,
            get_cursor=self._get_cursor,
            on_jump_to=self._on_jump_to,
        )

    def _get_history_entries(self) -> list:
        if not self._project:
            return []
        from knx_gui.panels.history import HistoryEntry
        from knx_gui.project.events import deserialize_event
        from knx_gui.project.models import EventModel

        entries = []
        for e in self._project.session.query(EventModel).order_by(EventModel.id.desc()).all():
            event = deserialize_event(e.type, e.data)
            entries.append(HistoryEntry(id=e.id, display_text=event.display_text(), reverted=e.reverted))
        return entries

    def _get_cursor(self) -> int:
        if not self._project:
            return 0
        return self._project.event_store.cursor

    def _on_jump_to(self, event_id: int) -> None:
        if not self._project:
            return
        self._project.event_store.jump_to(event_id)
        self._project.session.expire_all()
        self._load_devices_from_db()
        self._load_links_from_db()

    def _select_and_navigate_to_device(self, device: Device) -> None:
        self._state.selected_device = device
        self._node_editor_panel.select_node(device.node_id, False)
        self._node_editor_panel.navigate_to_selection(False, NAVIGATE_TO_NODE_DURATION)

    def _set_selected_device(self, device: Device) -> None:
        self._state.selected_device = device
        self._node_editor_panel.select_node(device.node_id, False)

    def _on_config_param_change(
        self, device: Device, param_id: str, value: str
    ) -> None:
        device.set_param_value(param_id, value)

    def _on_flag_change(
        self, device: Device, co_id: str, flag_name: str, new_value: bool
    ) -> None:
        com_object = device.find_com_object(co_id)
        if not com_object:
            return
        old_value = getattr(com_object.flags, flag_name)
        setattr(com_object.flags, flag_name, new_value)
        if self._project:
            event = ComObjectFlagChanged(
                device_id=device.node_id,
                co_id=co_id,
                flag_name=flag_name,
                old_value=old_value,
                new_value=new_value,
            )
            self._project.event_store.append(event)

    def _focus_device_by_address(self, address: str) -> None:
        device = self._state.find_device_by_address(address)
        if device:
            self._state.selected_device = device
            self._node_editor_panel.select_node(device.node_id, False)
            self._node_editor_panel.navigate_to_selection(
                False, NAVIGATE_TO_NODE_DURATION
            )

    def _get_catalog_entries(self) -> list[CatalogEntry]:
        entries: list[CatalogEntry] = []
        for app in self._catalog.session.query(ApplicationModel).all():
            entries.append(
                CatalogEntry(
                    application_id=app.application_id,
                    manufacturer_id=app.manufacturer_id,
                    name=app.name,
                )
            )
        return entries

    def _add_device_from_catalog(self, application_id: str) -> None:
        xml_data = get_application_xml(self._catalog, application_id)
        if not xml_data:
            print(f"[catalog] application not found: {application_id}")
            return

        app_model = (
            self._catalog.session.query(ApplicationModel)
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
        self._add_candidate_as_device(app)

    def setup(self) -> None:
        self._node_editor_panel.setup()

    def shutdown(self) -> None:
        self._node_editor_panel.shutdown()
        if self._project:
            self._project.close()
        self._catalog.close()

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
        if self._project:
            self._project.close()
        self._project_path = Path(path)
        if not self._project_path.suffix:
            self._project_path = self._project_path.with_suffix(".xknx")
        self._project = ProjectDatabase(self._project_path)
        self._project.create()
        self._state.devices.clear()
        self._state.links.clear()

    def _do_open_project(self, path: str) -> None:
        if self._project:
            self._project.close()
        self._project_path = Path(path)
        self._project = ProjectDatabase(self._project_path)
        self._project.open()
        self._load_devices_from_db()
        self._load_links_from_db()

    def _load_links_from_db(self) -> None:
        if not self._project:
            return
        from knx_gui.project.models import LinkModel

        self._state.links.clear()
        for link_model in self._project.session.query(LinkModel).all():
            self._state.links.append(
                (link_model.id, link_model.start_pin, link_model.end_pin)
            )
        max_link_id = max((link[0] for link in self._state.links), default=999)
        self._state._next_link_id = max_link_id + 1

    def _load_devices_from_db(self) -> None:
        if not self._project:
            return
        from knx_gui.project.models import ComObjectModel, DeviceModel

        selected_node_id = self._state.selected_device.node_id if self._state.selected_device else None
        self._state.devices.clear()
        for device_model in self._project.session.query(DeviceModel).all():
            template = self._get_template_for_device(device_model.template_id)
            if not template:
                print(f"[project] skipping device {device_model.id}: template '{device_model.template_id}' not found")
                continue
            device = Device(
                node_id=device_model.id,
                name=device_model.name,
                template=template,
                address=device_model.address or "",
            )
            for co_model in self._project.session.query(ComObjectModel).filter_by(device_id=device_model.id).all():
                co = device.find_com_object(co_model.co_id)
                if co:
                    co.flags.communication = co_model.flag_communication
                    co.flags.read = co_model.flag_read
                    co.flags.write = co_model.flag_write
                    co.flags.transmit = co_model.flag_transmit
                    co.flags.update = co_model.flag_update
            self._state.devices.append(device)
        if selected_node_id is not None:
            self._state.selected_device = self._state.find_device_by_node_id(selected_node_id)

    def _get_template_for_device(self, template_id: str) -> DeviceTemplate | None:
        xml_data = get_application_xml(self._catalog, template_id)
        if not xml_data:
            return None
        app_model = (
            self._catalog.session.query(ApplicationModel)
            .filter_by(application_id=template_id)
            .first()
        )
        if not app_model:
            return None
        apps = parse_application_xml(xml_data, app_model.manufacturer_id)
        if not apps:
            return None
        return self._app_to_template(apps[0])

    def _undo(self) -> None:
        if self._project and self._project.event_store.can_undo():
            self._project.event_store.undo()
            self._project.session.expire_all()
            self._load_devices_from_db()
            self._load_links_from_db()

    def _redo(self) -> None:
        if self._project and self._project.event_store.can_redo():
            self._project.event_store.redo()
            self._project.session.expire_all()
            self._load_devices_from_db()
            self._load_links_from_db()

    def _can_undo(self) -> bool:
        return self._project is not None and self._project.event_store.can_undo()

    def _can_redo(self) -> bool:
        return self._project is not None and self._project.event_store.can_redo()

    def _add_link(self, start_pin: int, end_pin: int) -> int:
        link_id = self._state.add_link(start_pin, end_pin)
        if self._project:
            event = LinkCreated(link_id=link_id, start_pin=start_pin, end_pin=end_pin)
            self._project.event_store.append(event)
        return link_id

    def _remove_link(self, link_id: int) -> None:
        link_data = next(
            (link for link in self._state.links if link[0] == link_id), None
        )
        self._state.remove_link(link_id)
        if self._project and link_data:
            event = LinkRemoved(
                link_id=link_data[0], start_pin=link_data[1], end_pin=link_data[2]
            )
            self._project.event_store.append(event)

    def _sync_selected_device_from_editor(self) -> None:
        selected_ids = self._node_editor_panel.get_selected_node_ids()
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
            added = load_knxprod_to_catalog(self._catalog, Path(path))
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

    def _add_candidate_as_device(self, app: DeviceApplication) -> None:
        print(f"[knxprod] adding {app.name} ({len(app.com_objects)} com objects)")
        template = self._app_to_template(app)
        template_id = f"knxprod:{app.manufacturer_id}:{app.application_id}"
        params = [(p.id, p.value) for p in template.parameters]
        com_objs = [
            {
                "co_id": co.id,
                "dpt_major": co.dpt.major,
                "dpt_minor": co.dpt.minor,
                "flag_communication": co.flags.communication,
                "flag_read": co.flags.read,
                "flag_write": co.flags.write,
                "flag_transmit": co.flags.transmit,
                "flag_update": co.flags.update,
            }
            for co in template.com_objects
        ]

        if self._project:
            event = DeviceAdded(
                device_id=0,
                address="",
                template_id=template_id,
                name=app.name,
                parameters=params,
                com_objects=com_objs,
            )
            self._project.event_store.append(event)
            device = Device(
                node_id=event.device_id,
                name=app.name,
                template=template,
                address="",
                app=app,
            )
            self._state.devices.append(device)
        else:
            device = Device(
                node_id=self._state._next_device_id,
                name=app.name,
                template=template,
                address="",
                app=app,
            )
            self._state._next_device_id += 1
            self._state.devices.append(device)

        print(f"[knxprod] device added; total devices: {len(self._state.devices)}")

    def _app_to_template(self, app: DeviceApplication) -> DeviceTemplate:
        com_objects: list[ComObject] = []
        for co in app.com_objects:
            flags = ComObjectFlags(
                communication=co.flags.communication,
                read=co.flags.read,
                write=co.flags.write,
                transmit=co.flags.transmit,
                update=co.flags.update,
                read_on_init=co.flags.read_on_init,
                read_locked=co.flags.read_locked,
                write_locked=co.flags.write_locked,
                transmit_locked=co.flags.transmit_locked,
                update_locked=co.flags.update_locked,
                read_on_init_locked=co.flags.read_on_init_locked,
            )
            supported = [lookup_or_make_dpt(code) for code in co.dpt_codes]
            seen: set[tuple[int, int]] = set()
            unique_supported: list[DPT] = []
            for dpt in supported:
                key = (dpt.major, dpt.minor)
                if key in seen:
                    continue
                seen.add(key)
                unique_supported.append(dpt)
            primary = unique_supported[0] if unique_supported else DPT_UNKNOWN
            com_objects.append(
                ComObject(
                    id=co.id,
                    name=co.name,
                    dpt=primary,
                    flags=flags,
                    supported_dpts=unique_supported,
                )
            )
        visible_params = app.visible_parameters()
        parameters = [
            Parameter(
                id=p.id,
                name=p.name,
                text=p.text,
                value=p.value,
                param_type=p.param_type,
            )
            for p in visible_params
        ]
        return DeviceTemplate(
            name=app.name,
            com_objects=com_objects,
            config=DeviceConfig(
                manufacturer=app.manufacturer_id,
                application=app.application_id,
                hardware="",
                firmware="",
            ),
            parameters=parameters,
        )

    def gui_status_bar(self) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        text_height = imgui.get_text_line_height()
        center = imgui.ImVec2(cursor.x + 5, cursor.y + text_height / 2)
        if self._state.connected:
            pulse = 0.5 + 0.5 * math.sin(imgui.get_time() * 3.0)
            alpha = 0.4 + 0.6 * pulse
            draw_list.add_circle_filled(center, 4, color_u32(0.2, 0.8, 0.3, alpha))
            draw_list.add_circle_filled(
                center, 4 + pulse * 3, color_u32(0.2, 0.8, 0.3, 0.15 * (1 - pulse))
            )
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text(S.STATUS_CONNECTED.format(ip=self._state.controller_ip))
        else:
            draw_list.add_circle_filled(center, 4, color_u32(0.5, 0.5, 0.5, 1.0))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text_disabled(S.STATUS_DISCONNECTED)
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
            imgui.begin_disabled(self._project is None)
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

        if imgui.begin_menu(S.MENU_CONNECTION):
            if self._state.connected:
                imgui.text(S.STATUS_CONNECTED_TO.format(ip=self._state.controller_ip))
                if imgui.menu_item(S.MENU_DISCONNECT, "", False)[0]:
                    self._state.connected = False
            else:
                imgui.set_next_item_width(180)
                _, self._state.controller_ip = imgui.input_text(
                    "IP", self._state.controller_ip
                )
                if imgui.menu_item(S.MENU_CONNECT, "", False)[0]:
                    self._state.connected = True
            imgui.end_menu()

        self._poll_dialogs()
        self._handle_shortcuts()

    def gui_devices(self) -> None:
        self._devices_panel.render()

    def gui_catalog(self) -> None:
        self._catalog_panel.render()

    def gui_node_editor(self) -> None:
        self._node_editor_panel.render()

    def gui_telegrams(self) -> None:
        self._telegrams_panel.render()

    def gui_configure(self) -> None:
        self._sync_selected_device_from_editor()
        self._configure_panel.render()

    def gui_history(self) -> None:
        self._history_panel.render()


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
    runner_params.callbacks.show_status = app.gui_status_bar

    runner_params.docking_params.docking_splits = create_docking_splits()
    runner_params.docking_params.dockable_windows = create_dockable_windows(app)

    runner_params.callbacks.post_init = app.setup
    runner_params.callbacks.before_exit = app.shutdown

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
