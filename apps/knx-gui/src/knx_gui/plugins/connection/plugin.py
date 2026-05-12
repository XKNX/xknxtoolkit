import asyncio
import math
import threading
from collections.abc import Callable, Coroutine
from enum import Enum
from typing import Any

from imgui_bundle import imgui

from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.connection.interface import ObservableKNXIPInterfaceThreaded
from knx_gui.strings import S
from knx_gui.types import color_u32
from xknx import XKNX
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.io.gateway_scanner import GatewayDescriptor
from xknx.io.self_description import request_description


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class ConnectionPlugin:
    name = "connection"

    def __init__(
        self,
        api: PluginAPI,
        raw_cemi_callback: Callable[[bytes], None] | None = None,
    ) -> None:
        self._api = api
        self._raw_cemi_callback = raw_cemi_callback
        self._state = ConnectionState.DISCONNECTED
        self._error_message: str | None = None
        self._controller_ip: str = "192.168.1.1"
        self._panels: list[PanelDefinition] = []

        self._xknx: XKNX | None = None
        self._interface: ObservableKNXIPInterfaceThreaded | None = None
        self._gateway_info: GatewayDescriptor | None = None
        self._async_loop: asyncio.AbstractEventLoop | None = None
        self._async_thread: threading.Thread | None = None

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
        if self._state in (ConnectionState.CONNECTING, ConnectionState.CONNECTED):
            return
        self._state = ConnectionState.CONNECTING
        self._error_message = None
        self._run_async(self._connect_async())

    async def _connect_async(self) -> None:
        try:
            self._xknx = XKNX()
            config = ConnectionConfig(
                connection_type=ConnectionType.TUNNELING,
                gateway_ip=self._controller_ip,
                threaded=True,
            )
            self._interface = ObservableKNXIPInterfaceThreaded(
                xknx=self._xknx,
                connection_config=config,
                raw_cemi_callback=self._raw_cemi_callback,
            )
            await self._interface.start()
            try:
                self._gateway_info = await request_description(self._controller_ip)
            except Exception:
                self._gateway_info = None
            self._state = ConnectionState.CONNECTED
        except Exception as e:
            self._state = ConnectionState.ERROR
            self._error_message = str(e)
            self._interface = None
            self._gateway_info = None
            self._xknx = None

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

    def shutdown(self) -> None:
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
            imgui.text(S.STATUS_CONNECTED.format(ip=self._controller_ip))
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
            error_short = self._error_message[:60] if self._error_message else "Unknown error"
            imgui.text_colored(imgui.ImVec4(0.8, 0.2, 0.2, 1.0), f"Error: {error_short}")
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
                imgui.text(S.STATUS_CONNECTED_TO.format(ip=self._controller_ip))
                if self._gateway_info:
                    imgui.separator()
                    imgui.text_disabled("Gateway")
                    imgui.text(f"  Name: {self._gateway_info.name}")
                    if self._gateway_info.individual_address:
                        imgui.text(f"  KNX Address: {self._gateway_info.individual_address}")
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
                imgui.set_next_item_width(180)
                _, self._controller_ip = imgui.input_text("IP", self._controller_ip)
                if imgui.menu_item("Retry", "", False)[0]:
                    self.connect()
            else:
                imgui.set_next_item_width(180)
                _, self._controller_ip = imgui.input_text("IP", self._controller_ip)
                if imgui.menu_item(S.MENU_CONNECT, "", False)[0]:
                    self.connect()
            imgui.end_menu()

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        self.shutdown()
