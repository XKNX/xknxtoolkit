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
    ParameterRefRef,
    ParameterSeparator,
    Rename,
    Repeat,
)

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
    "DynamicUI",
    "GenericCollectionNode",
    "ModuleNode",
    "ParameterRefRefNode",
    "ParameterSeparatorNode",
    "RenameNode",
    "RepeatNode",
    "build_evaluation_tree",
    "create_dynamic_node",
]


def create_dynamic_node(elem) -> DynamicNode | None:
    if isinstance(
        elem,
        (ApplicationProgramDynamic, ChannelIndependentBlock, ApplicationProgramChannel, ComObjectParameterBlock),
    ):
        return GenericCollectionNode([create_dynamic_node(child) for child in elem.choice])
    elif isinstance(elem, (DependentChannelChoose, ChannelChoose, ComObjectParameterChoose)):
        # A Choose block conditionally shows content based on a parameter value.
        # DependentChannelChoose: switches which channels are shown (root level)
        # ChannelChoose: switches content within a channel
        # ComObjectParameterChoose: switches content within a parameter block
        default_condition: str | None = None
        condition_to_nodes: dict = {}
        for when in elem.when:
            if when.default:
                assert default_condition is None, "default when-condition already exists"
                default_condition = when.test
            assert condition_to_nodes.get(when.test) is None, "when-condition already exists"
            condition_to_nodes[when.test] = [create_dynamic_node(node) for node in when.choice]
        return ChooseWhenNode(elem.param_ref_id, condition_to_nodes, default_condition)
    elif isinstance(elem, Repeat):
        # TODO: index substitution into ref_ids per repetition not yet implemented
        return RepeatNode(elem, [create_dynamic_node(child) for child in elem.choice])
    elif isinstance(elem, Module):
        # Instantiation of a module definition; choice holds NumericArg/TextArg arguments.
        # TODO: resolve the module definition and splice its dynamic subtree in place
        return ModuleNode(elem.ref_id, elem.choice)
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


def build_evaluation_tree(app: ApplicationProgram) -> DynamicNode:
    """
    The evaluation tree is computed once per application, it produces a tree of
    dynamic nodes that hold their activity logic.
    """
    assert app.dynamic is not None, "app has no dynamic section"
    node = create_dynamic_node(app.dynamic)
    assert node is not None, "dynamic section produced no tree"
    return node


class DynamicUI:
    __slots__ = ("_tree",)

    def __init__(self, app: ApplicationProgram) -> None:
        assert app.dynamic is not None, "app has no dynamic section"
        self._tree = build_evaluation_tree(app)

    def ui(self):
        return self._tree.ui()

    def params(self):
        return self._tree.params()

    def com_objects(self):
        return self._tree.com_objects()
