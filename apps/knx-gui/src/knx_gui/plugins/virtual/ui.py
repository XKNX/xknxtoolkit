import contextlib
from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.knxip_tunnelling_gateway import GatewayState, TunnellingGateway
from knx_gui.plugins.virtual.strings import S
from knx_gui.plugins.virtual.virtual_device import VirtualDevice


class VirtualPanel:
    def __init__(
        self,
        get_gateway_state: Callable[[], GatewayState],
        get_gateway_error: Callable[[], str | None],
        get_gateway_connected: Callable[[], bool],
        get_gateway_local_ips: Callable[[], list[str]],
        on_start: Callable[[str, int, str], None],
        on_stop: Callable[[], None],
        get_device: Callable[[], VirtualDevice],
    ) -> None:
        self._get_gateway_state = get_gateway_state
        self._get_gateway_error = get_gateway_error
        self._get_gateway_connected = get_gateway_connected
        self._get_gateway_local_ips = get_gateway_local_ips
        self._on_start = on_start
        self._on_stop = on_stop
        self._get_device = get_device
        self._name = "xknxtoolkit virtual network"
        self._port_str = str(TunnellingGateway.DEFAULT_PORT)
        self._multicast_group = TunnellingGateway.DEFAULT_MCAST_GROUP
        self._device_serial_hex = get_device().serial_number.hex()

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
        is_running = state in (GatewayState.RUNNING, GatewayState.STARTING)

        if is_running:
            imgui.begin_disabled()
        imgui.text(S.LABEL_NAME)
        imgui.set_next_item_width(-1)
        _, self._name = imgui.input_text("##vgateway-name", self._name)
        imgui.text(S.LABEL_PORT)
        imgui.set_next_item_width(-1)
        _, self._port_str = imgui.input_text("##vgateway-port", self._port_str)
        imgui.text(S.LABEL_MULTICAST_GROUP)
        imgui.set_next_item_width(-1)
        _, self._multicast_group = imgui.input_text(
            "##vgateway-mcast", self._multicast_group
        )
        if is_running:
            imgui.end_disabled()

        if state == GatewayState.RUNNING:
            imgui.text_colored(imgui.ImVec4(0.4, 0.8, 0.4, 1.0), S.STATUS_RUNNING)
            if self._get_gateway_connected():
                imgui.text_disabled("Client connected")
            local_ips = self._get_gateway_local_ips()
            if local_ips:
                imgui.text_disabled("IP: " + ", ".join(local_ips))
            if imgui.button(S.BTN_STOP):
                self._on_stop()
        elif state == GatewayState.STARTING:
            imgui.text_disabled(S.STATUS_STARTING)
        else:
            if state == GatewayState.ERROR:
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
            port = TunnellingGateway.DEFAULT_PORT
        self._on_start(self._name, port, self._multicast_group)

    def _render_devices_section(self) -> None:
        device = self._get_device()

        imgui.text(S.LABEL_NAME)
        imgui.set_next_item_width(-1)
        _, device.name = imgui.input_text("##device-name", device.name)

        imgui.text(S.LABEL_SERIAL_NUMBER)
        imgui.set_next_item_width(-1)
        changed, self._device_serial_hex = imgui.input_text(
            "##device-serial", self._device_serial_hex
        )
        if changed:
            with contextlib.suppress(ValueError):
                device.serial_number = bytes.fromhex(self._device_serial_hex)

        changed, programming_mode = imgui.checkbox(
            S.LABEL_PROGRAMMING_MODE, device.programming_mode
        )
        if changed:
            device.programming_mode = programming_mode

        if device.programming_mode:
            imgui.text_colored(
                imgui.ImVec4(0.9, 0.7, 0.3, 1.0), S.STATUS_PROGRAMMING_MODE
            )
