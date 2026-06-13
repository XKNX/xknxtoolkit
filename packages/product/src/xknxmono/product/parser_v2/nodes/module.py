from __future__ import annotations

from .base import DynamicNode


class ModuleNode(DynamicNode):
    def __init__(self, module_definition_id, args):
        # TODO: resolve module definition and store its eval tree
        self._module_definition_id = module_definition_id
        self._args = args

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        # TODO: evaluate the spliced module def subtree
        return []

    def params(self, state: dict[str, str]) -> list:
        # TODO: delegate to the resolved module def subtree
        return []

    def com_objects(self, state: dict[str, str]) -> list:
        # TODO: delegate to the resolved module def subtree
        return []

    def ui(self, state: dict[str, str]) -> list:
        # TODO: delegate to the resolved module def subtree
        return []
