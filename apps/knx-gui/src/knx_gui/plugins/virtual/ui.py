from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.plugins.virtual.strings import S
from knx_gui.plugins.virtual.virtual_gateway import VirtualGatewayState


class VirtualPanel:
    def __init__(
        self,
        get_gateway_state: Callable[[], VirtualGatewayState],
        get_gateway_error: Callable[[], str | None],
        on_start: Callable[[str, int], None],
        on_stop: Callable[[], None],
    ) -> None:
        self._get_gateway_state = get_gateway_state
        self._get_gateway_error = get_gateway_error
        self._on_start = on_start
        self._on_stop = on_stop
        self._name = "xknxtoolkit virtual gateway"
        self._port_str = "3671"

    def render(self) -> None:
        imgui.text_disabled(S.SECTION_GATEWAY)
        imgui.separator()
        self._render_gateway_section()

        imgui.spacing()
        imgui.spacing()

        imgui.text_disabled(S.SECTION_DEVICES)
        imgui.separator()
        self._render_devices_section()

    def _render_gateway_section(self) -> None:
        state = self._get_gateway_state()
        is_running = state in (
            VirtualGatewayState.RUNNING,
            VirtualGatewayState.STARTING,
        )

        if is_running:
            imgui.begin_disabled()
        imgui.text(S.LABEL_NAME)
        imgui.set_next_item_width(-1)
        _, self._name = imgui.input_text("##vgw-name", self._name)
        imgui.text(S.LABEL_PORT)
        imgui.set_next_item_width(-1)
        _, self._port_str = imgui.input_text("##vgw-port", self._port_str)
        if is_running:
            imgui.end_disabled()

        if state == VirtualGatewayState.RUNNING:
            imgui.text_colored(imgui.ImVec4(0.4, 0.8, 0.4, 1.0), S.STATUS_RUNNING)
            if imgui.button(S.BTN_STOP):
                self._on_stop()
        elif state == VirtualGatewayState.STARTING:
            imgui.text_disabled(S.STATUS_STARTING)
        else:
            if state == VirtualGatewayState.ERROR:
                imgui.text_colored(imgui.ImVec4(0.8, 0.2, 0.2, 1.0), S.STATUS_ERROR)
                error = self._get_gateway_error()
                if error:
                    imgui.text_wrapped(error)
            else:
                imgui.text_disabled(S.STATUS_STOPPED)
            if imgui.button(S.BTN_START):
                self._start()

    def _start(self) -> None:
        try:
            port = int(self._port_str)
        except ValueError:
            port = 3671
        self._on_start(self._name, port)

    def _render_devices_section(self) -> None:
        imgui.text_disabled(S.DEVICES_EMPTY)
