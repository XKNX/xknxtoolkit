import math
from pathlib import Path

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import portable_file_dialogs as pfd

from knx_gui.constants import LINK_INVALID_COLOR
from knx_gui.dpt import DPT, DPT_UNKNOWN, lookup_or_make_dpt
from knx_gui.knxprod import DeviceApplication, parse_archive
from knx_gui.panels import (
    CatalogPanel,
    ConfigurePanel,
    DevicesPanel,
    NodeEditorPanel,
    TelegramsPanel,
)
from knx_gui.project.database import ProjectDatabase
from knx_gui.project.events import (
    ComObjectFlagChanged,
    LinkCreated,
    LinkRemoved,
)
from knx_gui.state import AppState, create_empty_state
from knx_gui.strings import S
from knx_gui.templates import DEVICE_TEMPLATES
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
    def __init__(self, state: AppState) -> None:
        self._state = state
        self._project: ProjectDatabase | None = None
        self._project_path: Path | None = None

        self._open_file_dialog: pfd.open_file | None = None
        self._save_file_dialog: pfd.save_file | None = None
        self._open_project_dialog: pfd.open_file | None = None
        self._save_project_dialog: pfd.save_file | None = None
        self._archive_candidates: list[DeviceApplication] = []
        self._archive_path: str | None = None
        self._archive_load_error: str | None = None
        self._show_archive_popup: bool = False

        self._node_editor_panel = NodeEditorPanel(
            get_devices=lambda: self._state.devices,
            get_links=lambda: self._state.links,
            add_link=self._add_link,
            remove_link=self._remove_link,
            on_param_change=self._state.check_param_change_hides_com_objects,
        )
        self._devices_panel = DevicesPanel(
            get_devices=lambda: self._state.devices,
            on_select_device=self._select_and_navigate_to_device,
        )
        self._catalog_panel = CatalogPanel(
            on_add_device=self._add_device_from_template,
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

    def _add_device_from_template(self, _key: str, template: DeviceTemplate) -> None:
        self._state.add_device(template)

    def setup(self) -> None:
        self._node_editor_panel.setup()

    def shutdown(self) -> None:
        self._node_editor_panel.shutdown()
        if self._project:
            self._project.close()

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
        from knx_gui.project.models import DeviceModel

        selected_node_id = self._state.selected_device.node_id if self._state.selected_device else None
        self._state.devices.clear()
        for device_model in self._project.session.query(DeviceModel).all():
            template = DEVICE_TEMPLATES.get(device_model.template_id)
            if not template:
                print(f"[project] skipping device {device_model.id}: template '{device_model.template_id}' not found")
                continue
            device = Device(
                node_id=device_model.id,
                name=device_model.name,
                template=template,
                address=device_model.address or "",
            )
            self._state.devices.append(device)
        max_device_id = max((d.node_id for d in self._state.devices), default=9)
        self._state._next_device_id = max_device_id + 1
        if selected_node_id is not None:
            self._state.selected_device = self._state.find_device_by_node_id(selected_node_id)

    def _undo(self) -> None:
        if self._project and self._project.event_store.can_undo():
            self._project.event_store.undo()
            self._load_devices_from_db()
            self._load_links_from_db()

    def _redo(self) -> None:
        if self._project and self._project.event_store.can_redo():
            self._project.event_store.redo()
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
        self._archive_load_error = None
        self._archive_candidates = []
        self._archive_path = path
        print(f"[knxprod] parsing {path}")
        try:
            self._archive_candidates = parse_archive(path)
            print(f"[knxprod] parsed {len(self._archive_candidates)} candidate(s)")
            for c in self._archive_candidates:
                print(
                    f"[knxprod]   {c.name}: {len(c.com_objects)} com objects, "
                    f"{len(c.parameters)} parameters"
                )
        except ArchiveError as e:
            print(f"[knxprod] archive error: {e}")
            self._archive_load_error = str(e)
        except (OSError, ValueError) as e:
            print(f"[knxprod] error: {type(e).__name__}: {e}")
            self._archive_load_error = f"{type(e).__name__}: {e}"
        self._show_archive_popup = True

    def _add_candidate_as_device(self, app: DeviceApplication) -> None:
        print(f"[knxprod] adding {app.name} ({len(app.com_objects)} com objects)")
        template = self._app_to_template(app)
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

    def _render_archive_popup(self) -> None:
        if self._show_archive_popup:
            imgui.open_popup("##ArchivePopup")
            self._show_archive_popup = False
        center = imgui.get_main_viewport().get_center()
        imgui.set_next_window_pos(center, imgui.Cond_.appearing, imgui.ImVec2(0.5, 0.5))
        imgui.set_next_window_size_constraints(
            imgui.ImVec2(400, 0), imgui.ImVec2(800, 600)
        )
        if imgui.begin_popup("##ArchivePopup"):
            if self._archive_load_error:
                imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
                imgui.text(S.ARCHIVE_FAILED_TO_LOAD)
                imgui.pop_style_color()
                imgui.text(self._archive_load_error)
            else:
                imgui.text(S.ARCHIVE_LOADED.format(path=self._archive_path))
                imgui.text(
                    S.ARCHIVE_FOUND_APPS.format(count=len(self._archive_candidates))
                )
                imgui.separator()
                for i, candidate in enumerate(self._archive_candidates):
                    imgui.text(candidate.name)
                    imgui.same_line()
                    imgui.text_disabled(
                        f"  {S.ARCHIVE_COM_OBJECTS.format(count=len(candidate.com_objects))}"
                    )
                    imgui.same_line()
                    if imgui.small_button(f"{S.BTN_ADD}##{i}"):
                        self._add_candidate_as_device(candidate)
                        imgui.close_current_popup()
            imgui.spacing()
            if imgui.button(S.BTN_CLOSE, imgui.ImVec2(120, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

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
        self._render_archive_popup()

    def gui_telegrams(self) -> None:
        self._telegrams_panel.render()

    def gui_configure(self) -> None:
        self._sync_selected_device_from_editor()
        self._configure_panel.render()


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

    return [
        devices_window,
        catalog_window,
        editor_window,
        telegrams_window,
        configure_window,
    ]


def main() -> None:
    state = create_empty_state()
    app = KnxGuiApp(state)

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
