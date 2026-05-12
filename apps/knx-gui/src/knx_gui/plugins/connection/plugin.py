import math

from imgui_bundle import imgui

from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.strings import S
from knx_gui.types import color_u32


class ConnectionPlugin:
    name = "connection"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._connected: bool = False
        self._controller_ip: str = "192.168.1.1"
        self._panels: list[PanelDefinition] = []

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def controller_ip(self) -> str:
        return self._controller_ip

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def render_status_indicator(self) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        text_height = imgui.get_text_line_height()
        center = imgui.ImVec2(cursor.x + 5, cursor.y + text_height / 2)

        if self._connected:
            pulse = 0.5 + 0.5 * math.sin(imgui.get_time() * 3.0)
            alpha = 0.4 + 0.6 * pulse
            draw_list.add_circle_filled(center, 4, color_u32(0.2, 0.8, 0.3, alpha))
            draw_list.add_circle_filled(
                center, 4 + pulse * 3, color_u32(0.2, 0.8, 0.3, 0.15 * (1 - pulse))
            )
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text(S.STATUS_CONNECTED.format(ip=self._controller_ip))
        else:
            draw_list.add_circle_filled(center, 4, color_u32(0.5, 0.5, 0.5, 1.0))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text_disabled(S.STATUS_DISCONNECTED)

    def render_menu(self) -> None:
        if imgui.begin_menu(S.MENU_CONNECTION):
            if self._connected:
                imgui.text(S.STATUS_CONNECTED_TO.format(ip=self._controller_ip))
                if imgui.menu_item(S.MENU_DISCONNECT, "", False)[0]:
                    self.disconnect()
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
        pass
