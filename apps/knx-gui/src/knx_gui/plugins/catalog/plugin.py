from knx_gui.knxprod import parse_application_xml
from knx_gui.plugins.base import PluginAPI
from knx_gui.plugins.catalog.db import ApplicationModel
from knx_gui.plugins.catalog.ui import CatalogPanel


class CatalogPlugin:
    name = "catalog"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._panel = CatalogPanel(
            get_entries=api.catalog.get_entries,
            on_select=self._on_select,
        )

    def _on_select(self, application_id: str) -> None:
        xml_data = self._api.catalog.get_application_xml(application_id)
        if not xml_data:
            print(f"[catalog] application not found: {application_id}")
            return

        app_model = (
            self._api.catalog.session.query(ApplicationModel)
            .filter_by(application_id=application_id)
            .first()
        )
        if not app_model:
            return

        apps = parse_application_xml(xml_data, app_model.manufacturer_id)
        if not apps:
            print(f"[catalog] no applications parsed from {application_id}")
            return

        app = apps[0]
        device_id = self._api.project.add_device(
            template_id=application_id,
            name=app.name,
            app=app,
        )
        if device_id:
            print(f"[catalog] added device {app.name} (id={device_id})")

    def create_panel(self) -> CatalogPanel:
        return self._panel

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
