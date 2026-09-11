from xknxmono.models.intermediate import Button
from xknxmono.product.parser_v2.nodes import EvalContext, GlobalState
from xknxmono.product.parser_v2.nodes.button import ButtonNode
from xknxmono.product.parser_v2.ui.button import UiButton


def test_button_node_eval_returns_ui_button() -> None:
    node = ButtonNode(Button(id="BTN-1", text="Restart"))
    result = node.eval(EvalContext(GlobalState()))
    assert result == [UiButton(id="BTN-1", text="Restart")]
