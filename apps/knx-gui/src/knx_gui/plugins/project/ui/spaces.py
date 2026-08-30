"""ETS-like Buildings view: the imported location tree (building → floor → room → …) with the
devices placed in each space and the functions assigned to it."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.plugins.project.strings import S
from knx_gui.plugins.project.ui._filter import filter_box

if TYPE_CHECKING:
    from xknxmono.project.core.service import (
        FunctionInfo,
        SpaceDeviceInfo,
        SpaceInfo,
    )


class SpacesPanel:
    def __init__(
        self,
        get_space_tree: "Callable[[], list[SpaceInfo]]",
        on_select_device_id: Callable[[int], None],
    ) -> None:
        self._get_space_tree = get_space_tree
        self._on_select_device_id = on_select_device_id
        self._filter_text: str = ""

    def render(self) -> None:
        tree = self._get_space_tree()
        if not tree:
            imgui.text_disabled(S.SPACES_EMPTY)
            return
        self._filter_text = filter_box(
            "##spaces_filter", S.SPACES_FILTER_HINT, self._filter_text
        )
        flt = self._filter_text.strip().lower()
        for space in tree:
            self._render_space(space, flt)

    def _render_space(self, space: "SpaceInfo", flt: str = "") -> None:
        if flt and not self._space_has_match(space, flt):
            return  # while filtering, hide spaces with no match anywhere below
        # A space that matches by its own name shows all its contents; otherwise
        # only the matching devices/functions (and matching child spaces).
        self_match = not flt or self._space_matches_self(space, flt)
        label = space.name or space.space_type or "?"
        if space.space_type:
            label = f"{label}  [{space.space_type}]"
        if flt:
            imgui.set_next_item_open(True, imgui.Cond_.always)
        open_node = imgui.tree_node_ex(
            f"{label}##sp{space.id}", imgui.TreeNodeFlags_.default_open
        )
        if space.description and imgui.is_item_hovered():
            imgui.set_tooltip(space.description)
        if not open_node:
            return
        if space.description:
            imgui.text_disabled(space.description)
        for child in space.children:
            self._render_space(child, flt)
        for device in space.devices:
            if self_match or self._device_matches(device, flt):
                self._render_device(device)
        for function in space.functions:
            if self_match or self._function_matches(function, flt):
                self._render_function(function)
        imgui.tree_pop()

    @staticmethod
    def _space_matches_self(space: "SpaceInfo", flt: str) -> bool:
        return (
            flt in (space.name or "").lower() or flt in (space.space_type or "").lower()
        )

    @staticmethod
    def _device_matches(device: "SpaceDeviceInfo", flt: str) -> bool:
        fields = (
            device.name,
            device.individual_address,
            device.product_name,
            device.hardware_name,
            device.manufacturer_name,
        )
        return any(flt in (f or "").lower() for f in fields)

    @staticmethod
    def _function_matches(function: "FunctionInfo", flt: str) -> bool:
        fields = (function.usage_text, function.name, function.function_type)
        return any(flt in (f or "").lower() for f in fields)

    def _space_has_match(self, space: "SpaceInfo", flt: str) -> bool:
        if self._space_matches_self(space, flt):
            return True
        if any(self._device_matches(d, flt) for d in space.devices):
            return True
        if any(self._function_matches(fn, flt) for fn in space.functions):
            return True
        return any(self._space_has_match(child, flt) for child in space.children)

    def _render_device(self, device: "SpaceDeviceInfo") -> None:
        # Fall back to the product/hardware name when the device is unnamed (like ETS).
        ia = f"{device.individual_address}  " if device.individual_address else ""
        primary = (
            device.name
            or device.product_name
            or device.hardware_name
            or device.description
            or "?"
        )
        detail = (
            device.description
            if device.description and device.description != primary
            else ""
        )
        leaf = f"{ia}{primary}".strip()
        if detail:
            leaf = f"{leaf}  — {detail}"
        if imgui.selectable(f"{leaf}##spdev{device.id}", False)[0]:
            self._on_select_device_id(device.id)
        hovered = imgui.is_item_hovered()  # capture before the context menu below
        if device.individual_address and imgui.begin_popup_context_item(
            f"##spdev_ctx_{device.id}"
        ):
            if imgui.menu_item(S.CONTEXT_COPY_ADDRESS, "", False)[0]:
                imgui.set_clipboard_text(device.individual_address)
            imgui.end_popup()
        if hovered:
            parts = [
                p
                for p in (
                    device.manufacturer_name,
                    device.product_name,
                    device.hardware_name,
                    device.description,
                )
                if p
            ]
            if parts:
                imgui.set_tooltip("\n".join(parts))

    def _render_function(self, function: "FunctionInfo") -> None:
        label = function.usage_text or function.name or function.function_type
        if not imgui.tree_node_ex(f"ƒ {label}##fn{function.id}"):
            return
        for ref in function.group_addresses:
            role = f"  ({ref.role})" if ref.role else ""
            imgui.bullet_text(f"{ref.text}{role}")
        imgui.tree_pop()
