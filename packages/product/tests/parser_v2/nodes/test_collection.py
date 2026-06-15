from xknxmono.product.parser_v2.nodes import DynamicNode, EvalContext, GenericCollectionNode, GlobalState


class LeafNode(DynamicNode):
    """Test stub: a leaf that returns [] from eval and itself from params."""

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []

    def params(self, ctx: EvalContext) -> list:
        return [self]


class TestGenericCollectionNode:
    def test_eval_empty_children_returns_empty_list(self):
        node = GenericCollectionNode([])
        assert node.eval(EvalContext(GlobalState())) == []

    def test_eval_returns_direct_children(self):
        a = LeafNode()
        b = LeafNode()
        node = GenericCollectionNode([a, b])
        assert node.eval(EvalContext(GlobalState())) == [a, b]

    def test_eval_filters_none_children(self):
        a = LeafNode()
        node = GenericCollectionNode([a, None])
        assert node.eval(EvalContext(GlobalState())) == [a]

    def test_params_flatmaps_through_children(self):
        a = LeafNode()
        b = LeafNode()
        node = GenericCollectionNode([a, b])
        assert node.params(EvalContext(GlobalState())) == [a, b]

    def test_params_recurses_into_nested_collection(self):
        leaf = LeafNode()
        inner = GenericCollectionNode([leaf])
        outer = GenericCollectionNode([inner])
        assert outer.params(EvalContext(GlobalState())) == [leaf]
