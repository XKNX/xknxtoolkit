from xknxmono.models.intermediate import BinaryDataRef
from xknxmono.product.parser_v2.nodes import EvalContext, GlobalState
from xknxmono.product.parser_v2.nodes.binary_data_ref import BinaryDataRefNode


def test_binary_data_ref_node_eval_returns_empty_list() -> None:
    node = BinaryDataRefNode(BinaryDataRef(ref_id="BD-1"))
    assert node.eval(EvalContext(GlobalState())) == []
