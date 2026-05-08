from dataclasses import dataclass
from enum import Enum

from imgui_bundle import imgui, hello_imgui, imgui_node_editor as ed

NODE_PADDING = 8.0
HEADER_INSET = 1.0
PIN_RADIUS = 5.0
LINK_COLOR = imgui.ImVec4(0.6, 0.6, 0.6, 1.0)
LINK_INVALID_COLOR = imgui.ImVec4(0.9, 0.2, 0.2, 1.0)


class DPT(Enum):
    BOOL = "1"
    DIMMING = "3"
    PERCENT = "5"
    FLOAT = "9"
    SCENE = "17"
    RGB = "232"


DPT_COLORS: dict[DPT, imgui.ImVec4] = {
    DPT.BOOL: imgui.ImVec4(0.9, 0.3, 0.3, 1.0),
    DPT.DIMMING: imgui.ImVec4(0.9, 0.6, 0.2, 1.0),
    DPT.PERCENT: imgui.ImVec4(0.2, 0.8, 0.4, 1.0),
    DPT.FLOAT: imgui.ImVec4(0.2, 0.6, 0.9, 1.0),
    DPT.SCENE: imgui.ImVec4(0.7, 0.3, 0.9, 1.0),
    DPT.RGB: imgui.ImVec4(0.9, 0.2, 0.6, 1.0),
}

DPT_LABELS: dict[DPT, str] = {
    DPT.BOOL: "bool",
    DPT.DIMMING: "dim",
    DPT.PERCENT: "%",
    DPT.FLOAT: "°C",
    DPT.SCENE: "scene",
    DPT.RGB: "rgb",
}


class PinDir(Enum):
    INPUT = "input"
    OUTPUT = "output"


@dataclass
class Pin:
    name: str
    dpt: DPT
    direction: PinDir


@dataclass
class DeviceTemplate:
    name: str
    pins: list[Pin]


DEVICE_TEMPLATES: dict[str, DeviceTemplate] = {
    "switch_actuator": DeviceTemplate(
        name="Switch Actuator",
        pins=[
            Pin("Switch", DPT.BOOL, PinDir.INPUT),
            Pin("Status", DPT.BOOL, PinDir.OUTPUT),
        ],
    ),
    "dimmer_actuator": DeviceTemplate(
        name="Dimmer Actuator",
        pins=[
            Pin("Switch", DPT.BOOL, PinDir.INPUT),
            Pin("Dimming", DPT.DIMMING, PinDir.INPUT),
            Pin("Brightness", DPT.PERCENT, PinDir.INPUT),
            Pin("Status", DPT.BOOL, PinDir.OUTPUT),
            Pin("Value", DPT.PERCENT, PinDir.OUTPUT),
        ],
    ),
    "temperature_sensor": DeviceTemplate(
        name="Temperature Sensor",
        pins=[
            Pin("Temperature", DPT.FLOAT, PinDir.OUTPUT),
        ],
    ),
    "push_button": DeviceTemplate(
        name="Push Button",
        pins=[
            Pin("Press", DPT.BOOL, PinDir.OUTPUT),
            Pin("Long Press", DPT.BOOL, PinDir.OUTPUT),
            Pin("Scene", DPT.SCENE, PinDir.OUTPUT),
        ],
    ),
    "rgb_controller": DeviceTemplate(
        name="RGB Controller",
        pins=[
            Pin("Switch", DPT.BOOL, PinDir.INPUT),
            Pin("Color", DPT.RGB, PinDir.INPUT),
            Pin("Brightness", DPT.PERCENT, PinDir.INPUT),
            Pin("Status", DPT.BOOL, PinDir.OUTPUT),
            Pin("Color Status", DPT.RGB, PinDir.OUTPUT),
        ],
    ),
    "thermostat": DeviceTemplate(
        name="Thermostat",
        pins=[
            Pin("Setpoint", DPT.FLOAT, PinDir.INPUT),
            Pin("Actual Temp", DPT.FLOAT, PinDir.OUTPUT),
            Pin("Heating", DPT.BOOL, PinDir.OUTPUT),
            Pin("Valve", DPT.PERCENT, PinDir.OUTPUT),
        ],
    ),
}


def color_u32(r: float, g: float, b: float, a: float = 1.0) -> int:
    return imgui.get_color_u32(imgui.ImVec4(r, g, b, a))


def color_from_vec4(c: imgui.ImVec4) -> int:
    return imgui.get_color_u32(c)


class KnxGuiApp:
    def __init__(self) -> None:
        self._editor_context: ed.EditorContext | None = None
        self._links: list[tuple[int, int, int]] = []
        self._next_link_id: int = 1000
        self._pin_dpt: dict[int, DPT] = {}

    def setup(self) -> None:
        config = ed.Config()
        self._editor_context = ed.create_editor(config)

    def shutdown(self) -> None:
        if self._editor_context:
            ed.destroy_editor(self._editor_context)
            self._editor_context = None

    def _draw_pin_icon(self, dpt: DPT) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        center = imgui.ImVec2(cursor.x + PIN_RADIUS, cursor.y + PIN_RADIUS + 2)
        color = color_from_vec4(DPT_COLORS[dpt])

        draw_list.add_circle_filled(center, PIN_RADIUS, color)
        draw_list.add_circle(center, PIN_RADIUS, color_u32(1, 1, 1, 0.3), 0, 1.5)
        imgui.dummy(imgui.ImVec2(PIN_RADIUS * 2, PIN_RADIUS * 2 + 4))

    def _render_input_pin(self, pin_id: int, pin: Pin) -> None:
        self._pin_dpt[pin_id] = pin.dpt
        ed.begin_pin(ed.PinId(pin_id), ed.PinKind.input)
        ed.pin_pivot_alignment(imgui.ImVec2(0.0, 0.5))
        self._draw_pin_icon(pin.dpt)
        imgui.same_line()
        imgui.text_unformatted(pin.name)
        imgui.same_line()
        imgui.text_disabled(f"[{DPT_LABELS[pin.dpt]}]")
        ed.end_pin()

    def _render_output_pin(self, pin_id: int, pin: Pin) -> None:
        self._pin_dpt[pin_id] = pin.dpt
        ed.begin_pin(ed.PinId(pin_id), ed.PinKind.output)
        ed.pin_pivot_alignment(imgui.ImVec2(1.0, 0.5))
        imgui.text_disabled(f"[{DPT_LABELS[pin.dpt]}]")
        imgui.same_line()
        imgui.text_unformatted(pin.name)
        imgui.same_line()
        self._draw_pin_icon(pin.dpt)
        ed.end_pin()

    def _render_device_node(
        self, node_id: int, template: DeviceTemplate, address: str
    ) -> None:
        ed.begin_node(ed.NodeId(node_id))

        imgui.begin_group()
        imgui.text(template.name)
        imgui.same_line()
        imgui.text_disabled(f"  {address}")
        imgui.end_group()

        header_rect_min = imgui.get_item_rect_min()
        header_rect_max = imgui.get_item_rect_max()

        imgui.spacing()

        pin_base = node_id * 100
        input_pins = [p for p in template.pins if p.direction == PinDir.INPUT]
        output_pins = [p for p in template.pins if p.direction == PinDir.OUTPUT]

        imgui.begin_group()
        for i, pin in enumerate(input_pins):
            self._render_input_pin(pin_base + i, pin)
        imgui.end_group()

        imgui.same_line(spacing=20)

        imgui.begin_group()
        for i, pin in enumerate(output_pins):
            self._render_output_pin(pin_base + 50 + i, pin)
        imgui.end_group()

        content_rect_max = imgui.get_item_rect_max()

        ed.end_node()

        draw_list = ed.get_node_background_draw_list(ed.NodeId(node_id))
        if draw_list:
            header_left = header_rect_min.x - NODE_PADDING + HEADER_INSET
            header_right = max(header_rect_max.x, content_rect_max.x) + NODE_PADDING - HEADER_INSET
            header_top = header_rect_min.y - NODE_PADDING + HEADER_INSET
            header_bottom = header_rect_max.y + 4

            draw_list.add_rect_filled(
                imgui.ImVec2(header_left, header_top),
                imgui.ImVec2(header_right, header_bottom),
                color_u32(0.2, 0.4, 0.7),
                ed.get_style().node_rounding - HEADER_INSET,
                imgui.ImDrawFlags_.round_corners_top,
            )

    def _are_pins_compatible(self, pin_a: int, pin_b: int) -> bool:
        dpt_a = self._pin_dpt.get(pin_a)
        dpt_b = self._pin_dpt.get(pin_b)
        if dpt_a is None or dpt_b is None:
            return False
        return dpt_a == dpt_b

    def _handle_link_creation(self) -> None:
        if ed.begin_create():
            start_pin_id = ed.PinId()
            end_pin_id = ed.PinId()
            if ed.query_new_link(start_pin_id, end_pin_id):
                if start_pin_id.id() != 0 and end_pin_id.id() != 0:
                    compatible = self._are_pins_compatible(
                        start_pin_id.id(), end_pin_id.id()
                    )
                    if compatible:
                        if ed.accept_new_item(LINK_COLOR, 2.0):
                            self._links.append(
                                (self._next_link_id, start_pin_id.id(), end_pin_id.id())
                            )
                            self._next_link_id += 1
                    else:
                        ed.reject_new_item(LINK_INVALID_COLOR, 3.0)
            ed.end_create()

    def _handle_link_deletion(self) -> None:
        if ed.begin_delete():
            link_id = ed.LinkId()
            while ed.query_deleted_link(link_id):
                if ed.accept_deleted_item():
                    self._links = [
                        link for link in self._links if link[0] != link_id.id()
                    ]
            ed.end_delete()

    def _render_links(self) -> None:
        for link_id, start_pin, end_pin in self._links:
            ed.link(ed.LinkId(link_id), ed.PinId(start_pin), ed.PinId(end_pin))


    def render(self) -> None:
        if not self._editor_context:
            return

        ed.set_current_editor(self._editor_context)
        ed.begin("KNX Node Editor", imgui.ImVec2(0, 0))

        self._render_device_node(1, DEVICE_TEMPLATES["switch_actuator"], "1.1.1")
        self._render_device_node(2, DEVICE_TEMPLATES["dimmer_actuator"], "1.1.2")
        self._render_device_node(3, DEVICE_TEMPLATES["temperature_sensor"], "1.1.3")
        self._render_device_node(4, DEVICE_TEMPLATES["push_button"], "1.1.4")
        self._render_device_node(5, DEVICE_TEMPLATES["thermostat"], "1.1.5")
        self._render_device_node(6, DEVICE_TEMPLATES["rgb_controller"], "1.1.6")

        self._render_links()
        self._handle_link_creation()
        self._handle_link_deletion()

        ed.end()


def main() -> None:
    app = KnxGuiApp()

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "KNX ETS Node Editor"
    runner_params.app_window_params.window_geometry.size = (1280, 720)

    runner_params.callbacks.post_init = app.setup
    runner_params.callbacks.before_exit = app.shutdown
    runner_params.callbacks.show_gui = app.render

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
