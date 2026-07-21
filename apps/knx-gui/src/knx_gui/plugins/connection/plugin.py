import asyncio
import math
import threading
from collections.abc import Coroutine
from enum import Enum
from typing import Any

from imgui_bundle import imgui, imspinner
from xknx import XKNX
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.io.const import DEFAULT_MCAST_GRP
from xknx.io.gateway_scanner import GatewayDescriptor, GatewayScanner
from xknx.io.self_description import request_description

from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.connection.interface import ObservableKNXIPInterfaceThreaded
from knx_gui.plugins.connection.proxy import ProxyState, RoutingProxy
from knx_gui.plugins.connection.strings import S
from knx_gui.types import color_u32


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class ConnectionPlugin:
    name = "connection"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        api.connection.set_logger(Logger(api.log, "connection"))
        self._log = Logger(api.log, "connection")
        self._state = ConnectionState.DISCONNECTED
        self._error_message: str | None = None
        self._controller_ip: str = "192.168.1.1"
        self._connection_type: ConnectionType = ConnectionType.TUNNELING
        self._multicast_group: str = DEFAULT_MCAST_GRP
        self._selected_gateway: GatewayDescriptor | None = None
        self._panels: list[PanelDefinition] = []

        self._xknx: XKNX | None = None
        self._interface: ObservableKNXIPInterfaceThreaded | None = None
        self._gateway_info: GatewayDescriptor | None = None
        self._async_loop: asyncio.AbstractEventLoop | None = None
        self._async_thread: threading.Thread | None = None

        self._gateways: list[GatewayDescriptor] = []
        self._scanning = False

        self._proxy_log = Logger(api.log, "proxy")

        self._proxy = RoutingProxy(
            on_cemi=self._api.connection.dispatch_proxy_cemi,
            forward_cemi=None,
            logger=self._proxy_log,
        )
        self._proxy_forward = False
        self._proxy_multicast_group = RoutingProxy.DEFAULT_MCAST_GROUP
        self._proxy_multicast_port_str = str(RoutingProxy.DEFAULT_MCAST_PORT)

    @property
    def state(self) -> ConnectionState:
        return self._state

    @property
    def connected(self) -> bool:
        return self._state == ConnectionState.CONNECTED

    @property
    def controller_ip(self) -> str:
        return self._controller_ip

    def _ensure_async_loop(self) -> asyncio.AbstractEventLoop:
        if self._async_loop is not None and self._async_loop.is_running():
            return self._async_loop

        loop_ready = threading.Event()

        def run_loop() -> None:
            self._async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._async_loop)
            loop_ready.set()
            self._async_loop.run_forever()

        self._async_thread = threading.Thread(
            target=run_loop, daemon=True, name="KNX-Async"
        )
        self._async_thread.start()
        loop_ready.wait()
        return self._async_loop  # type: ignore

    def _run_async(self, coro: Coroutine[Any, Any, None]) -> None:
        loop = self._ensure_async_loop()
        asyncio.run_coroutine_threadsafe(coro, loop)

    def connect(self) -> None:
        """Connect using the manually entered IP (always tunneling)."""
        if self._state in (ConnectionState.CONNECTING, ConnectionState.CONNECTED):
            return
        self._connection_type = ConnectionType.TUNNELING
        self._selected_gateway = None
        self._state = ConnectionState.CONNECTING
        self._error_message = None
        self._run_async(self._connect_async())

    def connect_to_gateway(self, gateway: GatewayDescriptor) -> None:
        """Connect to a discovered gateway, using tunneling if it's offered,
        otherwise falling back to multicast routing (e.g. our virtual
        router, which only ever advertises routing)."""
        if self._state in (ConnectionState.CONNECTING, ConnectionState.CONNECTED):
            return
        if gateway.supports_tunnelling:
            self._connection_type = ConnectionType.TUNNELING
            self._controller_ip = gateway.ip_addr
        else:
            self._connection_type = ConnectionType.ROUTING
            self._multicast_group = gateway.multicast_address or DEFAULT_MCAST_GRP
        self._selected_gateway = gateway
        self._state = ConnectionState.CONNECTING
        self._error_message = None
        self._run_async(self._connect_async())

    @property
    def _connection_target(self) -> str:
        if self._connection_type == ConnectionType.ROUTING:
            return f"{self._multicast_group} (routing)"
        return self._controller_ip

    async def _connect_async(self) -> None:
        try:
            self._xknx = XKNX()
            if self._connection_type == ConnectionType.ROUTING:
                config = ConnectionConfig(
                    connection_type=ConnectionType.ROUTING,
                    multicast_group=self._multicast_group,
                    threaded=True,
                )
            else:
                config = ConnectionConfig(
                    connection_type=ConnectionType.TUNNELING,
                    gateway_ip=self._controller_ip,
                    threaded=True,
                )
            self._interface = ObservableKNXIPInterfaceThreaded(
                xknx=self._xknx,
                connection_config=config,
                raw_cemi_callback=self._api.connection.dispatch_raw_cemi,
            )
            await self._interface.start()
            if self._selected_gateway is not None:
                self._gateway_info = self._selected_gateway
            elif self._connection_type == ConnectionType.TUNNELING:
                try:
                    self._gateway_info = await request_description(self._controller_ip)
                except Exception:
                    self._gateway_info = None
            else:
                self._gateway_info = None
            self._state = ConnectionState.CONNECTED
            self._api.connection.set_connection(self._xknx, asyncio.get_running_loop())
            self._api.connection.dispatch_connected()
            self._log.info("connected", target=self._connection_target)
            if self._gateway_info:
                services = [
                    s
                    for s, enabled in [
                        ("tunneling", self._gateway_info.supports_tunnelling),
                        ("tunneling_tcp", self._gateway_info.supports_tunnelling_tcp),
                        ("routing", self._gateway_info.supports_routing),
                        ("secure", self._gateway_info.supports_secure),
                    ]
                    if enabled
                ]
                self._log.info(
                    "gateway info",
                    name=self._gateway_info.name,
                    knx_address=str(self._gateway_info.individual_address or ""),
                    core_version=str(self._gateway_info.core_version),
                    services=",".join(services),
                )
        except Exception as e:
            self._state = ConnectionState.ERROR
            self._error_message = str(e)
            self._interface = None
            self._gateway_info = None
            self._xknx = None
            self._log.error(
                "connection failed", target=self._connection_target, error=str(e)
            )

    def disconnect(self) -> None:
        if self._state in (ConnectionState.DISCONNECTED, ConnectionState.DISCONNECTING):
            return
        self._state = ConnectionState.DISCONNECTING
        self._run_async(self._disconnect_async())

    async def _disconnect_async(self) -> None:
        try:
            if self._interface is not None:
                await self._interface.stop()
        finally:
            self._interface = None
            self._gateway_info = None
            self._xknx = None
            self._state = ConnectionState.DISCONNECTED
            self._api.connection.set_connection(None, None)
            self._log.info("disconnected")

    def _forward_cemi(self, raw: bytes) -> None:
        self._api.connection.send_cemi(raw)

    def scan(self) -> None:
        if self._scanning:
            return
        self._scanning = True
        self._run_async(self._scan_async())

    async def _scan_async(self) -> None:
        try:
            xknx = XKNX()
            scanner = GatewayScanner(xknx, timeout_in_seconds=3.0)
            self._gateways = await scanner.scan()
        except Exception as e:
            self._log.error("gateway scan failed", error=str(e))
        finally:
            self._scanning = False

    def shutdown(self) -> None:
        self._proxy.stop()
        if self._interface is not None:
            self._run_async(self._disconnect_async())
        if self._async_loop is not None:
            self._async_loop.call_soon_threadsafe(self._async_loop.stop)

    def render_status_indicator(self) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        text_height = imgui.get_text_line_height()
        center = imgui.ImVec2(cursor.x + 5, cursor.y + text_height / 2)

        if self._state == ConnectionState.CONNECTED:
            pulse = 0.5 + 0.5 * math.sin(imgui.get_time() * 3.0)
            alpha = 0.4 + 0.6 * pulse
            draw_list.add_circle_filled(center, 4, color_u32(0.2, 0.8, 0.3, alpha))
            draw_list.add_circle_filled(
                center, 4 + pulse * 3, color_u32(0.2, 0.8, 0.3, 0.15 * (1 - pulse))
            )
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text(S.STATUS_CONNECTED.format(ip=self._connection_target))
        elif self._state == ConnectionState.CONNECTING:
            spin = (imgui.get_time() * 4) % 1.0
            draw_list.add_circle_filled(
                center, 4, color_u32(0.8, 0.7, 0.2, 0.5 + 0.5 * spin)
            )
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text_disabled("Connecting...")
        elif self._state == ConnectionState.ERROR:
            draw_list.add_circle_filled(center, 4, color_u32(0.8, 0.2, 0.2, 1.0))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            error_short = (
                self._error_message[:60] if self._error_message else "Unknown error"
            )
            imgui.text_colored(
                imgui.ImVec4(0.8, 0.2, 0.2, 1.0), f"Error: {error_short}"
            )
            if self._error_message and imgui.is_item_hovered():
                imgui.set_tooltip(self._error_message)
        else:
            draw_list.add_circle_filled(center, 4, color_u32(0.5, 0.5, 0.5, 1.0))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text_disabled(S.STATUS_DISCONNECTED)

    def render_menu(self) -> None:
        if imgui.begin_menu(S.MENU_CONNECTION):
            if self._state == ConnectionState.CONNECTED:
                imgui.text(S.STATUS_CONNECTED_TO.format(ip=self._connection_target))
                if self._gateway_info:
                    imgui.separator()
                    imgui.text_disabled("Gateway")
                    imgui.text(f"  Name: {self._gateway_info.name}")
                    if self._gateway_info.individual_address:
                        imgui.text(
                            f"  KNX Address: {self._gateway_info.individual_address}"
                        )
                    imgui.text(f"  Core Version: {self._gateway_info.core_version}")
                    services = []
                    if self._gateway_info.supports_tunnelling:
                        services.append("Tunneling")
                    if self._gateway_info.supports_tunnelling_tcp:
                        services.append("TCP Tunneling")
                    if self._gateway_info.supports_routing:
                        services.append("Routing")
                    if self._gateway_info.supports_secure:
                        services.append("Secure")
                    if services:
                        imgui.text(f"  Services: {', '.join(services)}")
                imgui.separator()
                if imgui.menu_item(S.MENU_DISCONNECT, "", False)[0]:
                    self.disconnect()
            elif self._state == ConnectionState.CONNECTING:
                imgui.text_disabled("Connecting...")
            elif self._state == ConnectionState.ERROR:
                imgui.text_colored(
                    imgui.ImVec4(0.8, 0.2, 0.2, 1.0), "Connection failed"
                )
                if self._error_message:
                    imgui.text_wrapped(self._error_message)
                imgui.separator()
                self._render_gateway_picker(retry_label="Retry")
            else:
                self._render_gateway_picker(retry_label=S.MENU_CONNECT)
            imgui.end_menu()

    def render_proxy_menu(self) -> None:
        if imgui.begin_menu(S.MENU_PROXY):
            self._render_proxy_section()
            imgui.end_menu()

    def _render_gateway_picker(self, retry_label: str) -> None:
        if imgui.is_window_appearing() and not self._scanning:
            self.scan()

        imgui.text_disabled(S.SECTION_DISCOVERED)
        if self._scanning:
            imgui.same_line()
            imspinner.spinner_ang(
                "##scan-spinner",
                6,
                2,
                color=imgui.ImColor(
                    imgui.get_style_color_vec4(imgui.Col_.tab_selected)
                ),
            )
        if self._gateways:
            for gw in self._gateways:
                tags: list[str] = []
                if gw.supports_tunnelling:
                    tags.append("T")
                if gw.supports_routing:
                    tags.append("R")
                if gw.supports_secure:
                    tags.append("S")
                tag_str = "/".join(tags)
                label = f"{gw.name}  ({gw.ip_addr})" + (f"  [{tag_str}]" if tag_str else "")
                is_connected_to = (
                    self._state == ConnectionState.CONNECTED
                    and self._selected_gateway is not None
                    and self._selected_gateway.ip_addr == gw.ip_addr
                    and self._selected_gateway.port == gw.port
                )
                if imgui.menu_item(label, "", is_connected_to)[0]:
                    self.connect_to_gateway(gw)
        elif not self._scanning:
            imgui.text_disabled(S.NO_GATEWAYS_FOUND)

        imgui.separator()
        imgui.text_disabled(S.SECTION_MANUAL)
        imgui.set_next_item_width(180)
        _, self._controller_ip = imgui.input_text("IP##manual", self._controller_ip)
        if imgui.menu_item(retry_label, "", False)[0]:
            self.connect()

    def _render_proxy_section(self) -> None:
        state = self._proxy.state
        if state == ProxyState.RUNNING:
            imgui.text_colored(imgui.ImVec4(0.4, 0.8, 0.4, 1.0), "Routing proxy: running")
        elif state == ProxyState.STARTING:
            imgui.text_disabled("Routing proxy: starting...")
        elif state == ProxyState.ERROR:
            imgui.text_colored(imgui.ImVec4(0.8, 0.2, 0.2, 1.0), "Routing proxy: error")
            if self._proxy.error:
                imgui.text_wrapped(self._proxy.error)
        else:
            imgui.text_disabled("Routing proxy: stopped")

        is_running = state in (ProxyState.RUNNING, ProxyState.STARTING)
        if is_running:
            imgui.begin_disabled()
        imgui.set_next_item_width(180)
        _, self._proxy_multicast_group = imgui.input_text(
            "##mcast", self._proxy_multicast_group
        )
        imgui.same_line()
        imgui.text_disabled("Multicast")

        imgui.set_next_item_width(60)
        _, self._proxy_multicast_port_str = imgui.input_text(
            "##port", self._proxy_multicast_port_str
        )
        imgui.same_line()
        imgui.text_disabled("Port")
        if is_running:
            imgui.end_disabled()

        changed, self._proxy_forward = imgui.checkbox("Forward to connection", self._proxy_forward)
        if changed:
            self._proxy.set_forward(
                self._forward_cemi if self._proxy_forward else None
            )

        if state in (ProxyState.STOPPED, ProxyState.ERROR):
            if imgui.menu_item("Start proxy", "", False)[0]:
                try:
                    port = int(self._proxy_multicast_port_str)
                except ValueError:
                    port = 3671
                self._proxy = RoutingProxy(
                    on_cemi=self._api.connection.dispatch_proxy_cemi,
                    forward_cemi=self._forward_cemi if self._proxy_forward else None,
                    multicast_group=self._proxy_multicast_group,
                    multicast_port=port,
                    logger=self._proxy_log,
                )
                self._proxy.start()
        else:
            if imgui.menu_item("Stop proxy", "", False)[0]:
                self._proxy.stop()

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        self.shutdown()
