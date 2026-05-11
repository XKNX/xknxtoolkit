from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui


@dataclass
class CatalogEntry:
    application_id: str
    manufacturer_id: str
    name: str


class CatalogPanel:
    def __init__(
        self,
        get_catalog_entries: Callable[[], list[CatalogEntry]],
        on_add_from_catalog: Callable[[str], None],
    ) -> None:
        self._get_catalog_entries = get_catalog_entries
        self._on_add_from_catalog = on_add_from_catalog
        self._search: str = ""

    def render(self) -> None:
        imgui.set_next_item_width(-1)
        _, self._search = imgui.input_text_with_hint(
            "##catalog_search", "Search...", self._search
        )

        search = self._search.lower().strip()
        leaf_flags = (
            imgui.TreeNodeFlags_.leaf
            | imgui.TreeNodeFlags_.no_tree_push_on_open
            | imgui.TreeNodeFlags_.span_avail_width
        )

        entries = self._get_catalog_entries()
        if not entries:
            return

        by_manufacturer: dict[str, list[CatalogEntry]] = {}
        for entry in entries:
            if entry.manufacturer_id not in by_manufacturer:
                by_manufacturer[entry.manufacturer_id] = []
            by_manufacturer[entry.manufacturer_id].append(entry)

        if search:
            for mfr in sorted(by_manufacturer.keys()):
                for entry in by_manufacturer[mfr]:
                    if search in entry.name.lower() or search in mfr.lower():
                        label = f"{mfr} - {entry.name}"
                        imgui.tree_node_ex(label, leaf_flags)
                        if imgui.is_item_clicked() and imgui.is_mouse_double_clicked(0):
                            self._on_add_from_catalog(entry.application_id)
        else:
            for mfr in sorted(by_manufacturer.keys()):
                if imgui.tree_node(mfr):
                    for entry in by_manufacturer[mfr]:
                        imgui.tree_node_ex(entry.name, leaf_flags)
                        if imgui.is_item_clicked() and imgui.is_mouse_double_clicked(0):
                            self._on_add_from_catalog(entry.application_id)
                    imgui.tree_pop()
