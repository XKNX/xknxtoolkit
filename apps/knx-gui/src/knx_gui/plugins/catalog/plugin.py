from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.catalog.strings import S
from knx_gui.plugins.catalog.ui import CatalogPanel
from xknxmono.catalog import ProductSummary


class CatalogPlugin:
    name = "catalog"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._log = Logger(api.log, "catalog")
        self._panel = CatalogPanel(
            get_products=api.catalog.get_products,
            on_select=self._on_select,
        )
        self._panels = [
            PanelDefinition(
                name="catalog",
                label=S.PANEL_CATALOG,
                dock="LeftSpace",
                render=self._panel.render,
            ),
        ]

    def _on_select(self, product: ProductSummary) -> None:
        if product.application_id is None:
            self._log.warning("product has no application", product=product.product_ref_id)
            return
        app = self._api.catalog.get_application(product.application_id)
        if app is None:
            self._log.warning(
                "application not found", application_id=product.application_id
            )
            return

        device_id = self._api.project.add_device(
            template_id=product.application_id,
            name=app.name,
            app=app,
        )
        if device_id:
            self._api.project.add_device_to_state_with_id(
                app=app, node_id=device_id, individual_address=""
            )
            self._log.info("device added", name=app.name, id=device_id)

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
