from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.plugins.catalog.strings import S

if TYPE_CHECKING:
    from knx_gui.plugins.catalog.online_catalog import OnlineManufacturer
    from xknxmono.catalog import ProductSummary


def _label(product: ProductSummary) -> str:
    return product.name or product.order_number or product.product_ref_id


class CatalogPanel:
    def __init__(
        self,
        get_products: Callable[[], list[ProductSummary]],
        on_select: Callable[[ProductSummary], None],
        get_online_manufacturers: Callable[[], list[OnlineManufacturer] | None]
        | None = None,
        on_online_refresh: Callable[[], None] | None = None,
    ) -> None:
        self._get_products = get_products
        self._on_select = on_select
        self._search: str = ""
        # Online catalog (manufacturer list from the KNX service).
        self._get_online_manufacturers = get_online_manufacturers
        self._on_online_refresh = on_online_refresh
        self._online_loading = False
        self._online_error = False
        self._online_shown = False

    def render(self) -> None:
        if self._get_online_manufacturers is not None:
            self._render_online_catalog()
            imgui.separator()

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

        products = self._get_products()
        if not products:
            return

        by_manufacturer: dict[str, list[ProductSummary]] = {}
        manufacturer_labels: dict[str, str] = {}
        for product in products:
            if product.manufacturer_id not in by_manufacturer:
                by_manufacturer[product.manufacturer_id] = []
                manufacturer_labels[product.manufacturer_id] = (
                    product.manufacturer_name or product.manufacturer_id
                )
            by_manufacturer[product.manufacturer_id].append(product)

        sorted_mfrs = sorted(
            by_manufacturer.keys(), key=lambda m: manufacturer_labels[m]
        )

        if search:
            for mfr_id in sorted_mfrs:
                mfr_label = manufacturer_labels[mfr_id]
                for product in by_manufacturer[mfr_id]:
                    name = _label(product)
                    if search in name.lower() or search in mfr_label.lower():
                        imgui.tree_node_ex(f"{mfr_label} - {name}", leaf_flags)
                        if imgui.is_item_clicked() and imgui.is_mouse_double_clicked(0):
                            self._on_select(product)
        else:
            for mfr_id in sorted_mfrs:
                mfr_label = manufacturer_labels[mfr_id]
                if imgui.tree_node(mfr_label):
                    for product in by_manufacturer[mfr_id]:
                        imgui.tree_node_ex(_label(product), leaf_flags)
                        if imgui.is_item_clicked() and imgui.is_mouse_double_clicked(0):
                            self._on_select(product)
                    imgui.tree_pop()

    def _render_online_catalog(self) -> None:
        """Online manufacturer list from the KNX catalog service (button + tree).

        ``get_online_manufacturers`` is called every frame; it must return the cached list
        (or None) without touching the network. The fetch itself runs on a worker thread."""
        online = (
            self._get_online_manufacturers()
            if (self._get_online_manufacturers is not None)
            else None
        )
        imgui.set_next_item_width(160.0)
        if imgui.button(S.BTN_ONLINE_CATALOG):
            self._start_online_refresh()
        if self._online_loading:
            imgui.same_line()
            imgui.text_disabled(S.ONLINE_LOADING)
        elif self._online_error:
            imgui.same_line()
            imgui.text_colored(S.ONLINE_FAILED, 1.0, 0.4, 0.4)

        if online is None or not self._online_shown:
            return
        leaf_flags = (
            imgui.TreeNodeFlags_.leaf
            | imgui.TreeNodeFlags_.no_tree_push_on_open
            | imgui.TreeNodeFlags_.span_avail_width
        )
        imgui.text_disabled(S.ONLINE_COUNT.format(count=len(online)))
        for mfr in online:
            imgui.tree_node_ex(
                f"{mfr.name}  (M-{mfr.id:04d})##online_mfr_{mfr.id}", leaf_flags
            )

    def _start_online_refresh(self) -> None:
        """Fetch the manufacturer list off the UI thread (urllib blocks)."""
        if self._online_loading or self._on_online_refresh is None:
            return
        self._online_loading = True
        self._online_error = False
        threading.Thread(target=self._fetch_online, daemon=True).start()

    def _fetch_online(self) -> None:
        try:
            self._on_online_refresh()
            self._online_shown = True
        except Exception:
            self._online_error = True
        finally:
            self._online_loading = False
