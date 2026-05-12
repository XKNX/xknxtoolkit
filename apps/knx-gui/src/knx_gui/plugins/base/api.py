from dataclasses import dataclass
from typing import TYPE_CHECKING

from knx_gui.plugins.base.events import EventBus

if TYPE_CHECKING:
    from knx_gui.plugins.catalog.service import CatalogService
    from knx_gui.plugins.project.service import ProjectService

API_VERSION = 1


@dataclass
class PluginAPI:
    api_version: int
    project: "ProjectService"
    catalog: "CatalogService"
    events: EventBus
