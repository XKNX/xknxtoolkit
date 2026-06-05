from collections.abc import Callable

from imgui_bundle import imgui

from xknxmono.catalog import ProductSummary


def _label(product: ProductSummary) -> str:
    return product.name or product.order_number or product.product_ref_id


class CatalogPanel:
    def __init__(
        self,
        get_products: Callable[[], list[ProductSummary]],
        on_select: Callable[[ProductSummary], None],
    ) -> None:
        self._get_products = get_products
        self._on_select = on_select
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
