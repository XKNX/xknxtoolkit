from xknxmono.models.intermediate import Rename
from xknxmono.product.parser_v2.nodes import EvalContext, GlobalState, ModuleState
from xknxmono.product.parser_v2.nodes.rename import RenameNode


def test_rename_node_eval_returns_empty_list() -> None:
    node = RenameNode(Rename(id="RN-1", ref_id="CO-1", text="New Name"))
    assert node.eval(EvalContext(GlobalState())) == []


def test_rename_node_sets_text_on_target_ref() -> None:
    node = RenameNode(Rename(id="RN-1", ref_id="CO-1", text="New Name"))
    state = GlobalState()
    node.eval(EvalContext(state))
    assert state.get_text("CO-1") == "New Name"


def test_rename_node_substitutes_text_args() -> None:
    node = RenameNode(Rename(id="RN-1", ref_id="CO-1", text="Channel {{ChName}}"))
    ms = ModuleState("M1_MI-1", arg_defaults={"ChName": "A"})
    node.eval(EvalContext(ms))
    assert ms.get_text("CO-1") == "Channel A"
