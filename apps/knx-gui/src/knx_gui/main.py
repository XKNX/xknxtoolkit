import math

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import imgui_node_editor as ed
from imgui_bundle import portable_file_dialogs as pfd

from knx_gui.constants import LINK_INVALID_COLOR
from knx_gui.dpt import DPT_UNKNOWN, lookup_or_make_dpt

NAVIGATE_TO_NODE_DURATION = 0.3
from knx_gui.knxprod import DeviceApplication, parse_archive
from knx_gui.panels import (
    CatalogPanel,
    ConfigurePanel,
    DevicesPanel,
    NodeEditorPanel,
    TelegramsPanel,
)
from knx_gui.templates import DEVICE_TEMPLATES
from knx_gui.types import (
    ComObject,
    ComObjectFlags,
    Device,
    DeviceConfig,
    DeviceTemplate,
    Parameter,
    Telegram,
    color_u32,
)
from xknx.product.errors import ArchiveError


class KnxGuiApp:
    def __init__(self) -> None:
        self._devices: list[Device] = []
        self._links: list[tuple[int, int, int]] = []
        self._next_link_id: int = 1000
        self._telegrams: list[Telegram] = []
        self._connected: bool = False
        self._controller_ip: str = "192.168.1.1"
        self._selected_device: Device | None = None

        self._open_file_dialog: pfd.open_file | None = None
        self._archive_candidates: list[DeviceApplication] = []
        self._archive_path: str | None = None
        self._archive_load_error: str | None = None
        self._show_archive_popup: bool = False

        self._init_devices()
        self._init_sample_telegrams()

        self._node_editor_panel = NodeEditorPanel(
            get_devices=lambda: self._devices,
            get_links=lambda: self._links,
            add_link=self._add_link,
            remove_link=self._remove_link,
            on_param_change=self._check_param_change,
        )
        self._devices_panel = DevicesPanel(
            get_devices=lambda: self._devices,
            on_select_device=self._select_and_navigate_to_device,
        )
        self._catalog_panel = CatalogPanel(
            on_add_device=self._add_device_from_template,
        )
        self._telegrams_panel = TelegramsPanel(
            get_telegrams=lambda: self._telegrams,
            on_focus_source=self._focus_device_by_address,
        )
        self._configure_panel = ConfigurePanel(
            get_devices=lambda: self._devices,
            get_selected_device=lambda: self._selected_device,
            set_selected_device=self._set_selected_device,
            on_param_change=self._on_config_param_change,
        )

    def _init_devices(self) -> None:
        self._devices = [
            Device(1, "Living Room Light", DEVICE_TEMPLATES["switch_actuator"], "1.1.1"),
            Device(2, "Kitchen Dimmer", DEVICE_TEMPLATES["dimmer_actuator"], "1.1.2"),
            Device(3, "Bedroom Temp", DEVICE_TEMPLATES["temperature_sensor"], "1.1.3"),
            Device(4, "Entry Button", DEVICE_TEMPLATES["push_button"], "1.2.1"),
            Device(5, "Living Room Thermo", DEVICE_TEMPLATES["thermostat"], "1.2.2"),
            Device(6, "RGB Strip", DEVICE_TEMPLATES["rgb_controller"], "2.1.1"),
            Device(7, "Bedroom Blinds", DEVICE_TEMPLATES["blinds_actuator"], "1.2.3"),
            Device(8, "Shutter Button", DEVICE_TEMPLATES["shutter_button"], "1.2.4"),
            Device(9, "Logic AND", DEVICE_TEMPLATES["logic_gate"], "1.3.1"),
        ]

    def _init_sample_telegrams(self) -> None:
        self._telegrams = [
            Telegram("12:34:01.123", "1.1.1", "1/0/1", "GroupValueWrite", "1.001", "On"),
            Telegram("12:34:01.456", "1.1.1", "1/0/2", "GroupValueResponse", "1.001", "Off"),
            Telegram("12:34:02.001", "1.2.1", "2/0/1", "GroupValueWrite", "5.001", "75%"),
            Telegram("12:34:02.345", "1.1.3", "3/0/1", "GroupValueWrite", "9.001", "21.5°C"),
            Telegram("12:34:03.012", "1.2.2", "4/0/1", "GroupValueRead", "1.001", ""),
            Telegram("12:34:03.234", "1.2.2", "4/0/1", "GroupValueResponse", "1.001", "On"),
            Telegram("12:34:04.567", "2.1.1", "5/0/1", "GroupValueWrite", "232.600", "#FF8800"),
            Telegram("12:34:05.123", "1.1.2", "1/1/1", "GroupValueWrite", "3.007", "Up"),
        ]

    def _add_link(self, start_pin: int, end_pin: int) -> int:
        link_id = self._next_link_id
        self._next_link_id += 1
        self._links.append((link_id, start_pin, end_pin))
        return link_id

    def _remove_link(self, link_id: int) -> None:
        self._links = [link for link in self._links if link[0] != link_id]

    def _check_param_change(self, device: Device, param_id: str, value: str) -> list[ComObject]:
        return device.would_hide_com_objects(param_id, value)

    def _select_and_navigate_to_device(self, device: Device) -> None:
        self._selected_device = device
        self._node_editor_panel.select_node(device.node_id, False)
        self._node_editor_panel.navigate_to_selection(False, NAVIGATE_TO_NODE_DURATION)

    def _set_selected_device(self, device: Device) -> None:
        self._selected_device = device
        self._node_editor_panel.select_node(device.node_id, False)

    def _on_config_param_change(self, device: Device, param_id: str, value: str) -> None:
        device.set_param_value(param_id, value)

    def _focus_device_by_address(self, address: str) -> None:
        for device in self._devices:
            if device.address == address:
                self._selected_device = device
                self._node_editor_panel.select_node(device.node_id, False)
                self._node_editor_panel.navigate_to_selection(False, NAVIGATE_TO_NODE_DURATION)
                return

    def _add_device_from_template(self, key: str, template: DeviceTemplate) -> None:
        next_id = max((d.node_id for d in self._devices), default=0) + 1
        self._devices.append(
            Device(
                node_id=next_id,
                name=template.name,
                template=template,
                address="",
            )
        )

    def setup(self) -> None:
        self._node_editor_panel.setup()

    def shutdown(self) -> None:
        self._node_editor_panel.shutdown()

    def _sync_selected_device_from_editor(self) -> None:
        selected_ids = self._node_editor_panel.get_selected_node_ids()
        if len(selected_ids) != 1:
            return
        node_id = selected_ids[0]
        if self._selected_device and self._selected_device.node_id == node_id:
            return
        for device in self._devices:
            if device.node_id == node_id:
                self._selected_device = device
                return

    def _poll_open_file_dialog(self) -> None:
        if self._open_file_dialog is None:
            return
        if not self._open_file_dialog.ready():
            return
        result = self._open_file_dialog.result()
        self._open_file_dialog = None
        if not result:
            return
        self._load_knxprod(result[0])

    def _load_knxprod(self, path: str) -> None:
        self._archive_load_error = None
        self._archive_candidates = []
        self._archive_path = path
        print(f"[knxprod] parsing {path}")
        try:
            self._archive_candidates = parse_archive(path)
            print(f"[knxprod] parsed {len(self._archive_candidates)} candidate(s)")
            for c in self._archive_candidates:
                print(f"[knxprod]   {c.name}: {len(c.com_objects)} com objects, {len(c.parameters)} parameters")
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
        next_id = max((d.node_id for d in self._devices), default=0) + 1
        self._devices.append(
            Device(
                node_id=next_id,
                name=app.name,
                template=template,
                address="",
                app=app,
            )
        )
        print(f"[knxprod] device added; total devices: {len(self._devices)}")

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
            unique_supported: list[ComObject] = []
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
        imgui.set_next_window_size_constraints(imgui.ImVec2(400, 0), imgui.ImVec2(800, 600))
        if imgui.begin_popup("##ArchivePopup"):
            if self._archive_load_error:
                imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
                imgui.text("Failed to load archive")
                imgui.pop_style_color()
                imgui.text(self._archive_load_error)
            else:
                imgui.text(f"Loaded: {self._archive_path}")
                imgui.text(f"Found {len(self._archive_candidates)} application(s)")
                imgui.separator()
                for i, candidate in enumerate(self._archive_candidates):
                    imgui.text(candidate.name)
                    imgui.same_line()
                    imgui.text_disabled(f"  ({len(candidate.com_objects)} com objects)")
                    imgui.same_line()
                    if imgui.small_button(f"Add##{i}"):
                        self._add_candidate_as_device(candidate)
                        imgui.close_current_popup()
            imgui.spacing()
            if imgui.button("Close", imgui.ImVec2(120, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

    def gui_status_bar(self) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        text_height = imgui.get_text_line_height()
        center = imgui.ImVec2(cursor.x + 5, cursor.y + text_height / 2)
        if self._connected:
            pulse = 0.5 + 0.5 * math.sin(imgui.get_time() * 3.0)
            alpha = 0.4 + 0.6 * pulse
            draw_list.add_circle_filled(center, 4, color_u32(0.2, 0.8, 0.3, alpha))
            draw_list.add_circle_filled(center, 4 + pulse * 3, color_u32(0.2, 0.8, 0.3, 0.15 * (1 - pulse)))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text(f"Connected: {self._controller_ip}")
        else:
            draw_list.add_circle_filled(center, 4, color_u32(0.5, 0.5, 0.5, 1.0))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text_disabled("Disconnected")
        imgui.same_line()
        imgui.text(f"| Devices: {len(self._devices)} | Links: {len(self._links)}")

    def gui_menu(self) -> None:
        if imgui.begin_menu("File"):
            if imgui.menu_item("New Project", "", False)[0]:
                pass
            if imgui.menu_item("Open Project", "", False)[0]:
                pass
            if imgui.menu_item("Save Project", "", False)[0]:
                pass
            imgui.separator()
            if imgui.menu_item("Load .knxprod...", "", False)[0]:
                self._open_file_dialog = pfd.open_file(
                    "Open KNX product archive",
                    "",
                    ["KNX product (*.knxprod)", "*.knxprod", "All files", "*"],
                )
            imgui.separator()
            if imgui.menu_item("Exit", "", False)[0]:
                hello_imgui.get_runner_params().app_shall_exit = True
            imgui.end_menu()

        if imgui.begin_menu("Edit"):
            if imgui.menu_item("Undo", "Ctrl+Z", False)[0]:
                pass
            if imgui.menu_item("Redo", "Ctrl+Y", False)[0]:
                pass
            imgui.end_menu()

        if imgui.begin_menu("Connection"):
            if self._connected:
                imgui.text(f"Connected to {self._controller_ip}")
                if imgui.menu_item("Disconnect", "", False)[0]:
                    self._connected = False
            else:
                imgui.set_next_item_width(180)
                _, self._controller_ip = imgui.input_text("IP", self._controller_ip)
                if imgui.menu_item("Connect", "", False)[0]:
                    self._connected = True
            imgui.end_menu()

        self._poll_open_file_dialog()

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
    devices_window.label = "Devices"
    devices_window.dock_space_name = "LeftSpace"
    devices_window.gui_function = app.gui_devices

    catalog_window = hello_imgui.DockableWindow()
    catalog_window.label = "Catalog"
    catalog_window.dock_space_name = "LeftSpace"
    catalog_window.gui_function = app.gui_catalog

    editor_window = hello_imgui.DockableWindow()
    editor_window.label = "Node Editor"
    editor_window.dock_space_name = "MainDockSpace"
    editor_window.gui_function = app.gui_node_editor

    telegrams_window = hello_imgui.DockableWindow()
    telegrams_window.label = "Telegrams"
    telegrams_window.dock_space_name = "BottomSpace"
    telegrams_window.gui_function = app.gui_telegrams

    configure_window = hello_imgui.DockableWindow()
    configure_window.label = "Configure"
    configure_window.dock_space_name = "RightSpace"
    configure_window.gui_function = app.gui_configure

    return [devices_window, catalog_window, editor_window, telegrams_window, configure_window]


def main() -> None:
    app = KnxGuiApp()

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "XKNX Toolkit"
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
