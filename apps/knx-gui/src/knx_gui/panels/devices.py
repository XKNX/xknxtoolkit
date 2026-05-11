from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.types import Device


class DevicesPanel:
    def __init__(
        self,
        get_devices: Callable[[], list[Device]],
        on_select_device: Callable[[Device], None],
    ) -> None:
        self._get_devices = get_devices
        self._on_select_device = on_select_device

    def render(self) -> None:
        devices = self._get_devices()
        tree, unassigned = self._build_address_tree(devices)

        leaf_flags = (
            imgui.TreeNodeFlags_.leaf
            | imgui.TreeNodeFlags_.no_tree_push_on_open
            | imgui.TreeNodeFlags_.span_avail_width
        )

        for area in sorted(tree.keys()):
            area_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
            if imgui.tree_node_ex(f"Area {area}", area_flags):
                for line in sorted(tree[area].keys()):
                    line_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
                    if imgui.tree_node_ex(f"Line {area}.{line}", line_flags):
                        for device in tree[area][line]:
                            imgui.tree_node_ex(f"{device.name} ({device.address})", leaf_flags)
                            if imgui.is_item_clicked():
                                self._on_select_device(device)
                        imgui.tree_pop()
                imgui.tree_pop()

        if unassigned:
            unassigned_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
            if imgui.tree_node_ex(f"Unassigned ({len(unassigned)})", unassigned_flags):
                for device in unassigned:
                    imgui.tree_node_ex(device.name, leaf_flags)
                    if imgui.is_item_clicked():
                        self._on_select_device(device)
                imgui.tree_pop()

    def _build_address_tree(
        self, devices: list[Device]
    ) -> tuple[dict[int, dict[int, list[Device]]], list[Device]]:
        tree: dict[int, dict[int, list[Device]]] = {}
        unassigned: list[Device] = []

        for device in devices:
            if not device.address:
                unassigned.append(device)
                continue
            parts = device.address.split(".")
            if len(parts) < 2:
                unassigned.append(device)
                continue
            try:
                area, line = int(parts[0]), int(parts[1])
            except ValueError:
                unassigned.append(device)
                continue
            if area not in tree:
                tree[area] = {}
            if line not in tree[area]:
                tree[area][line] = []
            tree[area][line].append(device)

        return tree, unassigned
