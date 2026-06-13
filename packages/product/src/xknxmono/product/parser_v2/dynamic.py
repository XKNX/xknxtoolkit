from xknxmono.models.intermediate import (
    ApplicationProgram,
    ChannelIndependentBlock,
    ApplicationProgramChannel,
    DependentChannelChoose,
    Module,
    Repeat,
)

class DynamicNode(ABC):
    """
    DynamicNode is the base class for all nodes inside dynamic tree.
    An "eval" method must be provided by the child class, which evaluates
    the activity/visibility of the items under it. A few methods
    have been added such as ui(), params(), and com_objects() which recursively
    evaluate the state of the tree and extracts or maps them to their domain.
    """
    def eval(self, state) -> Optional[list[DynamicNode]]:
        raise Exception("Unimplemented DynamicNode eval")

    def ui(self, state):
        nodes = self.eval(state)
        if nodes is not None:
            return [node.ui() for node in nodes]

    def params(self, state):
        nodes = self.eval(state)
        if nodes is not None:
            return [node.params() for node in nodes]

    def com_objects(self, state):
        nodes = self.eval(state)
        if nodes is not None:
            return [node.com_objects() for node in nodes]

class ModuleNode(DynamicNode):
    def __init__(self, module_definition_id, args):
        # TODO: fetch module definition

    def eval(self, state): ...
    def ui(self, state): ...
    def params(self, state): ...
    def com_objects(self, state): ...
    return None

class ChooseWhenNode(DynamicNode):
    def __init__(self, x, condition_to_nodes, default_condition):
        self._x = x
        self._condition_to_nodes = condition_to_nodes
        self._default_condition = default_condition

    def eval(self, state):
        # Iterate over conditon_with_node [condition, node] and
        # checks conditions satisfaction, and return the corresponding nodes.
        # TODO: create satisfies() defintion
        for condition, nodes in self._condition_to_nodes.items():
            if satisfies(condition, state[self._x]):
                return nodes

        if _default_condition is not None:
            return self._condition_to_nodes[self._default_condition]

        return None

class GenericCollectionNode(DynamicNode):
    """
    GenericCollectionNode is a node that is just a collection of
    children to be evaluate, e.g Dynamic section in itself.
    """
    def __init__(self, children):
        self._children = children

    def eval(self, state):
        return [child.eval(state) for child in self._children]

def create_dynamic_node(elem):
    if isinstance(elem, Dynamic) or
       isinstance(elem, ChannelIndependentBlock):
           # A ChannelIndependentBlock contains application global settings
           # they are not tied to a specific channel but can contain parameters
           # that enable or disable channels from showing up.
           return GenericCollectionNode([create_dynamic_node(child) for child in elem.choice])
    elif isinstance(elem, ApplicationProgramChannel):
        # TODO
    elif isinstance(elem, DependentChannelChoose) or
        isinstance(elem, ChannelChoose) or
        isinstance(elem, ComObjectParameterChoose) or
        isinstance(elem, DependentChannelChoose) or
        isinstance(elem, LdCtrlBaseChoose) or
        isinstance(elem, ModuleDefLdCtrlBaseChoose):
            # A DependentChannelChoose is a <Choose> block, typically used
            # at the root to dynamically add Channel entries.
            # TODO: consider moving all of this to __init__ of ChooseWhenNode
            # every Choose structure has elem.param_ref_id, elem.when but
            # the typing of when.choice may be problematic.
            # But keeping the recursion with create_dynamic_node might be a bit cleaner?
            default_condition: str = None
            condition_to_nodes = {}
            # ChannelChooseWhen |
            # ComObjectParameterChooseWhen |
            # DependentChannelChooseWhen |
            # LdCtrlBaseChooseWhen |
            # ModuleDefLdCtrlBaseChooseWhen
            for when in elem.when:
                if when.default:
                    assert default_condition is None, "default when-condition already exists"
                    default_condition = when.test
                assert condition_with_nodes[when.test] is None, "when-condition already exists"
                condition_with_nodes[when.test] = [create_dynamic_node(node) for node in when.choice]

            return ChooseWhenNode(elem.param_ref_id, condition_to_nodes, default_condition)
    elif isinstance(elem, Module):
        # Instantiation of a module
        module_definition_id = elem.ref_id
        args = module.choice
        return create_module(module_definition_id, args)
    elif isinstance(elem, ComObjectParameterBlock):
        # TODO:
    elif isinstance(elem, ComObjectRefRef):
        #TODO
    elif isinstance(elem, BinaryDataRef):
        #TODO
    elif isinstance(elem, Rename):
        #TODO
    elif isinstance(elem, Repeat):
        # Generate a repetition of Modules, ComObjectParameters or other Repeats.
        assert len(elem.choice) is 1, "multiple children found in repeat"
        # elem.choice: ComObjectParameterChoose | Module | Repeat
        # TODO: implement Repeat
    elif isinstance(elemn ):

def build_evaluation_tree(app: ApplicationProgram) -> DynamicNode:
    """
    The evaluation tree is computed once per application, it produces a tree of
    dynamic nodes that hold their activity logic.
    """
    assert app.dynamic is not None, "app has no dynamic section"

    children = []
    for elem in app.dynamic.choice:
        if isinstance(elem, ChannelIndependentBlock):

            children.append(create_dynamic_node())


    element = None
    return element

class DynamicUI:
     __slots__ = ("_tree", "_state",)

    def __init__(self, app: ApplicationProgram) -> DynamicNode:
        assert app.dynamic is not None, "app has no dynamic section"
        self._tree = build_evaluation_tree(app)

    def ui():
        return self._tree.ui()

    def params():
        return self._tree.params()

    def com_objects():
        return self._tree.com_objects()
