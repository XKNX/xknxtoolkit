"""A small pulsing status dot, shared by `ConnectionPlugin.render_status_indicator`
and `knx_gui.plugins.tasks.ui` - see apps/knx-gui/CLAUDE.md's "Tasks plugin"
section."""

from __future__ import annotations

import math

from imgui_bundle import imgui

from knx_gui.color import color_u32


def render_pulsing_dot(
    color: imgui.ImVec4, *, center: imgui.ImVec2, radius: float = 4.0
) -> None:
    """Caller reserves its own layout space (e.g. `imgui.dummy`) around `center`."""
    pulse = 0.5 + 0.5 * math.sin(imgui.get_time() * 3.0)
    alpha = 0.4 + 0.6 * pulse
    draw_list = imgui.get_window_draw_list()
    draw_list.add_circle_filled(
        center, radius, color_u32(color.x, color.y, color.z, alpha)
    )
    draw_list.add_circle_filled(
        center,
        radius + pulse * 3,
        color_u32(color.x, color.y, color.z, 0.15 * (1 - pulse)),
    )
