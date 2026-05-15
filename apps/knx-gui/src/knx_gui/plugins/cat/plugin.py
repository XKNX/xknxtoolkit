from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.cat.follower import CatFollower


class CatPlugin:
    name = "cat"

    def __init__(self, api: PluginAPI) -> None:
        self._follower = CatFollower()

    @property
    def panels(self) -> list[PanelDefinition]:
        return []

    def on_load(self) -> None:
        self._follower.load()

    def on_unload(self) -> None:
        pass

    def render(self) -> None:
        self._follower.render()
