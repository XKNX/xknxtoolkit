from __future__ import annotations

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramChannel,
    ApplicationProgramDynamic,
    Assign,
    BinaryDataRef,
    Button,
    ChannelChoose,
    ChannelIndependentBlock,
    ComObjectParameterBlock,
    ComObjectParameterChoose,
    ComObjectRefRef,
    DependentChannelChoose,
    Module,
    ModuleArg,
    ModuleDef,
    ParameterRefRef,
    ParameterSeparator,
    Rename,
    Repeat,
)

from .context import EvalContext, GlobalState
from .nodes import (
    AssignNode,
    BinaryDataRefNode,
    ButtonNode,
    ChooseWhenNode,
    ComObjectRefRefNode,
    DynamicNode,
    GenericCollectionNode,
    ModuleNode,
    ParameterRefRefNode,
    ParameterSeparatorNode,
    RenameNode,
    RepeatNode,
)

__all__ = [
    "AssignNode",
    "BinaryDataRefNode",
    "ButtonNode",
    "ChooseWhenNode",
    "ComObjectRefRefNode",
    "DynamicNode",
    "DynamicTreeBuilder",
    "DynamicUI",
    "EvalContext",
    "GenericCollectionNode",
    "ModuleNode",
    "ParameterRefRefNode",
    "ParameterSeparatorNode",
    "RenameNode",
    "RepeatNode",
]


class DynamicTreeBuilder:
    """Builds the evaluation tree for an ApplicationProgram, resolving Module references
    into pre-built subtrees so the eval path never touches the IR again."""

    def __init__(self, app: ApplicationProgram) -> None:
        assert app.dynamic is not None, "app has no dynamic section"
        self._module_defs: dict[str, ModuleDef] = {}
        if app.module_defs is not None:
            for md in app.module_defs.module_def:
                self._index_module_def(md)
        node = self._build(app.dynamic)
        assert node is not None, "dynamic section produced no tree"
        self.tree: DynamicNode = node

    def _index_module_def(self, md: ModuleDef) -> None:
        if md.id:
            self._module_defs[md.id] = md
        if md.sub_module_defs is not None:
            for sub in md.sub_module_defs.module_def:
                self._index_module_def(sub)

    def _build(self, elem: object) -> DynamicNode | None:
        if isinstance(
            elem,
            (
                ApplicationProgramDynamic,
                ChannelIndependentBlock,
                ApplicationProgramChannel,
                ComObjectParameterBlock,
            ),
        ):
            return GenericCollectionNode([self._build(child) for child in elem.choice])
        elif isinstance(
            elem, (DependentChannelChoose, ChannelChoose, ComObjectParameterChoose)
        ):
            # A Choose block conditionally shows content based on a parameter value.
            # DependentChannelChoose: switches which channels are shown (root level)
            # ChannelChoose: switches content within a channel
            # ComObjectParameterChoose: switches content within a parameter block
            default_condition: str | None = None
            condition_to_nodes: dict = {}
            for when in elem.when:
                if when.default:
                    assert default_condition is None, (
                        "default when-condition already exists"
                    )
                    default_condition = when.test
                assert condition_to_nodes.get(when.test) is None, (
                    "when-condition already exists"
                )
                condition_to_nodes[when.test] = [
                    self._build(node) for node in when.choice
                ]
            return ChooseWhenNode(
                elem.param_ref_id, condition_to_nodes, default_condition
            )
        elif isinstance(elem, Repeat):
            # TODO: index substitution for non-Module children not yet implemented
            return RepeatNode(elem, [self._build(child) for child in elem.choice])
        elif isinstance(elem, Module):
            mod_def = self._module_defs.get(elem.ref_id or "")
            if mod_def is None or mod_def.dynamic is None:
                return None
            children = [self._build(child) for child in mod_def.dynamic.choice]
            arguments: dict[str, ModuleArg] = {arg.ref_id: arg for arg in elem.choice}
            return ModuleNode(elem.id, GenericCollectionNode(children), arguments)
        elif isinstance(elem, ParameterRefRef):
            # Leaf: a parameter widget; ref_id points to the ParameterRef in Static
            return ParameterRefRefNode(elem)
        elif isinstance(elem, ComObjectRefRef):
            # Leaf: a communication object entry; ref_id points to the ComObjectRef in Static
            return ComObjectRefRefNode(elem)
        elif isinstance(elem, ParameterSeparator):
            # Leaf: a static label or visual divider between parameters
            return ParameterSeparatorNode(elem)
        elif isinstance(elem, Button):
            # Leaf: an interactive button that can trigger a load-procedure action
            return ButtonNode(elem)
        elif isinstance(elem, BinaryDataRef):
            # Leaf: embeds a binary data blob defined in the application's Static section
            return BinaryDataRefNode(elem)
        elif isinstance(elem, Assign):
            # Leaf: forces a parameter to a fixed value — no visible UI, affects state only
            return AssignNode(elem)
        elif isinstance(elem, Rename):
            # Leaf: overrides the display name of a channel or element within a choose branch
            return RenameNode(elem)
        return None


class DynamicUI:
    __slots__ = ("_tree",)

    def __init__(self, app: ApplicationProgram) -> None:
        self._tree = DynamicTreeBuilder(app).tree

    def ui(self, state: GlobalState | None = None) -> list:
        return self._tree.ui(EvalContext(state or GlobalState()))

    def params(self, state: GlobalState | None = None) -> list:
        return self._tree.params(EvalContext(state or GlobalState()))

    def com_objects(self, state: GlobalState | None = None) -> list:
        return self._tree.com_objects(EvalContext(state or GlobalState()))
