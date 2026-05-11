from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.templates import DEVICE_TEMPLATES
from knx_gui.types import DeviceTemplate


class CatalogPanel:
    def __init__(
        self,
        on_add_device: Callable[[str, DeviceTemplate], None],
    ) -> None:
        self._on_add_device = on_add_device
        self._search: str = ""

    def render(self) -> None:
        imgui.set_next_item_width(-1)
        _, self._search = imgui.input_text_with_hint(
            "##catalog_search", "Search...", self._search
        )

        by_manufacturer: dict[str, list[tuple[str, DeviceTemplate]]] = {}
        for key, template in DEVICE_TEMPLATES.items():
            mfr = template.config.manufacturer
            if mfr not in by_manufacturer:
                by_manufacturer[mfr] = []
            by_manufacturer[mfr].append((key, template))

        search = self._search.lower().strip()
        leaf_flags = (
            imgui.TreeNodeFlags_.leaf
            | imgui.TreeNodeFlags_.no_tree_push_on_open
            | imgui.TreeNodeFlags_.span_avail_width
        )

        if search:
            for mfr in sorted(by_manufacturer.keys()):
                for key, template in by_manufacturer[mfr]:
                    if search in template.name.lower() or search in mfr.lower():
                        label = f"{mfr} - {template.name}"
                        imgui.tree_node_ex(label, leaf_flags)
                        if imgui.is_item_clicked() and imgui.is_mouse_double_clicked(0):
                            self._on_add_device(key, template)
        else:
            for mfr in sorted(by_manufacturer.keys()):
                if imgui.tree_node(mfr):
                    for key, template in by_manufacturer[mfr]:
                        imgui.tree_node_ex(template.name, leaf_flags)
                        if imgui.is_item_clicked() and imgui.is_mouse_double_clicked(0):
                            self._on_add_device(key, template)
                    imgui.tree_pop()
