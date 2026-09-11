"""A small pulsing status dot - solid center plus a soft halo that grows and
fades - for anything in the status bar that needs to say "this is live right
now" without a spinner. Shared by `ConnectionPlugin.render_status_indicator`
and `knx_gui.plugins.tasks.ui`, which both animated this by hand before.
"""

from __future__ import annotations

import math

from imgui_bundle import imgui

from knx_gui.color import color_u32


def render_pulsing_dot(
    color: imgui.ImVec4, *, center: imgui.ImVec2, radius: float = 4.0
) -> None:
    """Draws into the current window's draw list at `center` - callers are
    responsible for reserving the layout space (e.g. `imgui.dummy`) around it,
    since how much room to reserve and whether to `same_line` after varies."""
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
