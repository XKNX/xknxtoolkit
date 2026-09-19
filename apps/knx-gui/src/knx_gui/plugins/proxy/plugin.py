from imgui_bundle import imgui

from knx_gui.knxip_tunnelling_gateway import GatewayState, TunnellingGateway
from knx_gui.net import TelegramSource
from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.proxy.strings import S

_NAME = "xknxtoolkit proxy"


class ProxyPlugin:
    name = "proxy"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._log = Logger(api.log, "proxy")
        self._panels: list[PanelDefinition] = []

        self._proxy = TunnellingGateway(
            name=_NAME,
            on_cemi=self._api.connection.dispatch_proxy_cemi,
            forward_cemi=None,
            logger=self._log,
        )
        self._forward = False
        self._port_str = str(TunnellingGateway.DEFAULT_PORT)
        self._api.connection.add_raw_cemi_listener(self._relay_connection_cemi)

    def _forward_to_connection(self, raw: bytes) -> None:
        self._api.connection.send_cemi(raw)

    def _relay_connection_cemi(self, raw: bytes, source: TelegramSource) -> None:
        """
        The other half of "Forward to connection": frames received on the
        real connection also need relaying back to the client through the
        proxy, or point-to-point exchanges it initiates (e.g. reading a
        device's descriptor) never get a reply and time out. Filtered to
        CONNECTION so proxy/virtual traffic doesn't get echoed back into
        the proxy.
        """
        if source != TelegramSource.CONNECTION or not self._forward:
            return
        self._proxy.send_cemi(raw)

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def render_menu(self) -> None:
        if imgui.begin_menu(S.MENU_PROXY):
            self._render_proxy_section()
            imgui.end_menu()

    def _render_proxy_section(self) -> None:
        state = self._proxy.state
        if state == GatewayState.RUNNING:
            imgui.text_colored(imgui.ImVec4(0.4, 0.8, 0.4, 1.0), "Proxy: running")
            if self._proxy.connected:
                imgui.text_disabled("Client connected")
            else:
                imgui.text_disabled(
                    "Discoverable automatically, or add manually using this "
                    "machine's IP"
                )
            if self._proxy.local_ips:
                imgui.text_disabled("IP: " + ", ".join(self._proxy.local_ips))
        elif state == GatewayState.STARTING:
            imgui.text_disabled("Proxy: starting...")
        elif state == GatewayState.ERROR:
            imgui.text_colored(imgui.ImVec4(0.8, 0.2, 0.2, 1.0), "Proxy: error")
            if self._proxy.error:
                imgui.text_wrapped(self._proxy.error)
        else:
            imgui.text_disabled("Proxy: stopped")

        is_running = state in (GatewayState.RUNNING, GatewayState.STARTING)
        if is_running:
            imgui.begin_disabled()
        imgui.set_next_item_width(60)
        _, self._port_str = imgui.input_text("##proxyport", self._port_str)
        imgui.same_line()
        imgui.text_disabled("Port")
        if is_running:
            imgui.end_disabled()

        changed, self._forward = imgui.checkbox("Forward to connection", self._forward)
        if changed:
            self._proxy.set_forward(
                self._forward_to_connection if self._forward else None
            )

        if state in (GatewayState.STOPPED, GatewayState.ERROR):
            if imgui.menu_item("Start proxy", "", False)[0]:
                try:
                    port = int(self._port_str)
                except ValueError:
                    port = TunnellingGateway.DEFAULT_PORT
                self._start_proxy(port)
        else:
            if imgui.menu_item("Stop proxy", "", False)[0]:
                self._proxy.stop()

    def _start_proxy(self, port: int) -> None:
        """Construct and start a fresh gateway on ``port``, first tearing down
        any prior instance.

        Required on the restart-after-failure path: a failed ``start()`` leaves
        the old gateway's daemon thread and asyncio loop alive (and, if
        ``create_server`` succeeded before the failure, a listening ``_server``
        still bound to the old port), so reassigning ``self._proxy`` without
        stopping it would orphan that loop/thread/port for the rest of the
        process. ``stop_and_wait`` drives the old gateway's ``_stop_async`` to
        completion (closing its ``_server``) and joins its thread before the new
        instance is constructed.
        """
        self._proxy.stop_and_wait()
        self._proxy = TunnellingGateway(
            name=_NAME,
            on_cemi=self._api.connection.dispatch_proxy_cemi,
            forward_cemi=self._forward_to_connection if self._forward else None,
            port=port,
            logger=self._log,
        )
        self._proxy.start()

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        self.shutdown()

    def shutdown(self) -> None:
        self._proxy.stop()
