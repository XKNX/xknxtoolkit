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
    ParameterRefRef,
    ParameterSeparator,
    Rename,
    Repeat,
)

from .application_indexer import ApplicationIndexer

from .context import EvalContext, GlobalState
from .ui import UiNode
from .nodes import (
    AssignNode,
    BinaryDataRefNode,
    ButtonNode,
    ChannelNode,
    ChooseWhenNode,
    ComObjectParameterBlockNode,
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
        self._idx = ApplicationIndexer(app)
        self._app_id = app.id
        node = self._build(app.dynamic)
        assert node is not None, "dynamic section produced no tree"
        self.tree: DynamicNode = node

    def _build(self, elem: object) -> DynamicNode | None:
        if isinstance(elem, ApplicationProgramDynamic):
            return GenericCollectionNode([self._build(child) for child in elem.choice])
        elif isinstance(elem, ChannelIndependentBlock):
            return ChannelNode(
                [self._build(child) for child in elem.choice],
                id=f"{self._app_id}_general",
                name="General",
            )
        elif isinstance(elem, ApplicationProgramChannel):
            return ChannelNode(
                [self._build(child) for child in elem.choice],
                id=elem.id,
                name=elem.name,
                text=elem.text,
                number=elem.number,
                icon=elem.icon,
                text_parameter_ref_id=elem.text_parameter_ref_id,
            )
        elif isinstance(elem, ComObjectParameterBlock):
            return ComObjectParameterBlockNode(elem, [self._build(child) for child in elem.choice])
        elif isinstance(
            elem, (DependentChannelChoose, ChannelChoose, ComObjectParameterChoose)
        ):
            # A Choose block conditionally shows content based on a parameter value.
            # DependentChannelChoose: switches which channels are shown (root level)
            # ChannelChoose: switches content within a channel
            # ComObjectParameterChoose: switches content within a parameter block
            default_nodes: list[DynamicNode | None] | None = None
            condition_to_nodes: dict[str, list[DynamicNode | None]] = {}
            for when in elem.when:
                built = [self._build(node) for node in when.choice]
                if when.default:
                    assert default_nodes is None, "duplicate default when-branch"
                    default_nodes = built
                if when.test is not None:
                    assert condition_to_nodes.get(when.test) is None, (
                        "when-condition already exists"
                    )
                    condition_to_nodes[when.test] = built
            return ChooseWhenNode(
                elem.param_ref_id, condition_to_nodes, default_nodes
            )
        elif isinstance(elem, Repeat):
            # TODO: index substitution for non-Module children not yet implemented
            return RepeatNode(elem, [self._build(child) for child in elem.choice])
        elif isinstance(elem, Module):
            mod_def = self._idx.module_defs.get(elem.ref_id or "")
            if mod_def is None or mod_def.dynamic is None:
                return None
            children = [self._build(child) for child in mod_def.dynamic.choice]
            arguments: dict[str, ModuleArg] = {arg.ref_id: arg for arg in elem.choice}
            return ModuleNode(elem.id, GenericCollectionNode(children), arguments)
        elif isinstance(elem, ParameterRefRef):
            # Leaf: a parameter widget; resolve ParameterRef → Parameter → ParameterType at build time
            pr = self._idx.parameter_refs.get(elem.ref_id)
            assert pr is not None, f"ParameterRef {elem.ref_id!r} not found in static"
            param = self._idx.parameters.get(pr.ref_id)
            assert param is not None, f"Parameter {pr.ref_id!r} not found in static"
            pt = self._idx.parameter_types.get(param.parameter_type)
            assert pt is not None, f"ParameterType {param.parameter_type!r} not found in static"
            assert pt.plugin is None, f"ParameterType {param.parameter_type!r} uses unsupported plugin {pt.plugin!r}"
            return ParameterRefRefNode(elem, pr, param, pt)
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
    __slots__ = ("_state", "_tree", "_ui")

    def __init__(self, app: ApplicationProgram, state: GlobalState | None = None) -> None:
        self._tree = DynamicTreeBuilder(app).tree
        self._state = state or GlobalState()
        self._ui: list[UiNode] | None = None

    def ui(self) -> list[UiNode]:
        if self._ui is None:
            self._state.reset_active()
            self._ui = self._tree.eval(EvalContext(self._state))
            self._state.trim_to_active()
        return self._ui

    def set_parameter_ref(self, ref_id: str, value: str) -> None:
        active = self._state.active_param_refs()
        if active and ref_id not in active:
            raise ValueError(f"parameter ref {ref_id!r} is not active in the current UI state")
        self._state.set_instance_ref(ref_id, value)
        self._ui = None
