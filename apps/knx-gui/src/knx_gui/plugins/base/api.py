from dataclasses import dataclass
from typing import TYPE_CHECKING

from knx_gui.plugins.base.events import EventBus

if TYPE_CHECKING:
    from knx_gui.plugins.catalog.service import CatalogService
    from knx_gui.plugins.project.service import ProjectService
    from knx_gui.state import AppState

API_VERSION = 1


@dataclass
class PluginAPI:
    api_version: int
    state: "AppState"
    project: "ProjectService"
    catalog: "CatalogService"
    events: EventBus
