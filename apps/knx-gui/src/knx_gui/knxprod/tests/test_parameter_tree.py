import pytest

from knx_gui.knxprod.parameter_tree import (
    TreeNode,
    VisibleNode,
    always_visible,
    build_tree,
    combine_conditions,
    evaluate_tree,
    evaluate_tree_cached,
    make_condition,
    _build_children,
    _build_node,
    _collect_visible_refs,
    _evaluate_nodes,
    _find_matching_when,
    _flatten_generic,
    _number_duplicates,
    _resolve_name,
)
from knx_gui.knxprod.types import (
    DynamicChoose,
    DynamicElement,
    DynamicWhen,
    Parameter,
)


def make_param(id: str, value: str = "", text: str = "") -> Parameter:
    return Parameter(
        id=id,
        ref_id=id,
        name=id,
        text=text,
        value=value,
        param_type_id="",
        param_type=None,
    )


def make_element(
    id: str | None = None,
    name: str | None = None,
    text: str | None = None,
    param_ref_ids: list[str] | None = None,
    com_object_ref_ids: list[str] | None = None,
    children: list[DynamicElement] | None = None,
    chooses: list[DynamicChoose] | None = None,
    header_param_ref_id: str | None = None,
) -> DynamicElement:
    return DynamicElement(
        id=id,
        name=name,
        text=text,
        header_param_ref_id=header_param_ref_id,
        param_ref_ids=param_ref_ids or [],
        com_object_ref_ids=com_object_ref_ids or [],
        children=children or [],
        chooses=chooses or [],
    )


class TestAlwaysVisible:
    def test_returns_true_for_empty_dict(self):
        assert always_visible({}) is True

    def test_returns_true_for_any_values(self):
        assert always_visible({"a": "1", "b": "2"}) is True


class TestMakeCondition:
    def test_default_with_no_test_values_returns_always_visible(self):
        condition = make_condition("param", [], is_default=True)
        assert condition is always_visible

    def test_non_default_with_test_values_checks_value(self):
        condition = make_condition("param", ["1", "2"], is_default=False)
        assert condition({"param": "1"}) is True
        assert condition({"param": "2"}) is True
        assert condition({"param": "3"}) is False

    def test_param_not_in_values_returns_true(self):
        condition = make_condition("param", ["1"], is_default=False)
        assert condition({}) is True
        assert condition({"other": "1"}) is True

    def test_default_with_test_values_checks_value(self):
        condition = make_condition("param", ["1"], is_default=True)
        assert condition({"param": "1"}) is True
        assert condition({"param": "2"}) is False


class TestCombineConditions:
    def test_parent_always_visible_returns_child(self):
        child = make_condition("p", ["1"], is_default=False)
        result = combine_conditions(always_visible, child)
        assert result is child

    def test_child_always_visible_returns_parent(self):
        parent = make_condition("p", ["1"], is_default=False)
        result = combine_conditions(parent, always_visible)
        assert result is parent

    def test_both_always_visible_returns_always_visible(self):
        result = combine_conditions(always_visible, always_visible)
        assert result is always_visible

    def test_both_custom_combines_with_and(self):
        parent = make_condition("a", ["1"], is_default=False)
        child = make_condition("b", ["2"], is_default=False)
        result = combine_conditions(parent, child)

        assert result({"a": "1", "b": "2"}) is True
        assert result({"a": "1", "b": "X"}) is False
        assert result({"a": "X", "b": "2"}) is False
        assert result({"a": "X", "b": "X"}) is False


class TestBuildTree:
    def test_none_dynamic_returns_empty_list(self):
        result = build_tree(None)
        assert result == []

    def test_element_with_children(self):
        child = make_element(id="child", name="Child", param_ref_ids=["p1"])
        root = make_element(children=[child])

        result = build_tree(root)

        assert len(result) == 1
        assert result[0].id == "child"
        assert result[0].name == "Child"

    def test_element_with_chooses(self):
        content = make_element(id="content", param_ref_ids=["p1"])
        choose = DynamicChoose(
            param_ref_id="selector",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        root = make_element(chooses=[choose])

        result = build_tree(root)

        assert len(result) == 0

    def test_element_with_nested_children_in_choose(self):
        nested = make_element(id="nested", param_ref_ids=["p1"])
        content = make_element(children=[nested])
        choose = DynamicChoose(
            param_ref_id="selector",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        root = make_element(chooses=[choose])

        result = build_tree(root)

        assert len(result) == 1
        assert result[0].id == "nested"


class TestBuildNode:
    def test_creates_tree_node_with_element_data(self):
        element = make_element(
            id="test",
            name="Test Name",
            text="Test Text",
            header_param_ref_id="header",
            param_ref_ids=["p1"],
        )

        node = _build_node(element, always_visible)

        assert node.id == "test"
        assert node.name == "Test Name"
        assert node.text == "Test Text"
        assert node.header_param_ref_id == "header"
        assert node.element is element
        assert node.visibility is always_visible

    def test_none_id_becomes_node(self):
        element = make_element(id=None)
        node = _build_node(element, always_visible)
        assert node.id == "node"

    def test_builds_children_recursively(self):
        child = make_element(id="child", param_ref_ids=["p1"])
        parent = make_element(id="parent", children=[child])

        node = _build_node(parent, always_visible)

        assert len(node.children) == 1
        assert node.children[0].id == "child"


class TestBuildChildren:
    def test_empty_element_returns_empty_list(self):
        element = make_element()
        result = _build_children(element, always_visible)
        assert result == []

    def test_processes_direct_children(self):
        child1 = make_element(id="c1", param_ref_ids=["p1"])
        child2 = make_element(id="c2", param_ref_ids=["p2"])
        element = make_element(children=[child1, child2])

        result = _build_children(element, always_visible)

        assert len(result) == 2
        assert result[0].id == "c1"
        assert result[1].id == "c2"

    def test_processes_choose_conditions(self):
        nested = make_element(id="nested", param_ref_ids=["p1"])
        content = make_element(children=[nested])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(chooses=[choose])

        result = _build_children(element, always_visible)

        assert len(result) == 1
        assert result[0].id == "nested"

    def test_skips_when_without_content(self):
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=None)],
        )
        element = make_element(chooses=[choose])

        result = _build_children(element, always_visible)
        assert result == []

    def test_combines_conditions_for_nested(self):
        nested = make_element(id="nested", param_ref_ids=["p1"])
        content = make_element(children=[nested])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(chooses=[choose])

        parent_cond = make_condition("parent", ["A"], is_default=False)
        result = _build_children(element, parent_cond)

        assert result[0].visibility({"parent": "A", "sel": "1"}) is True
        assert result[0].visibility({"parent": "A", "sel": "X"}) is False
        assert result[0].visibility({"parent": "X", "sel": "1"}) is False


class TestEvaluateTree:
    def test_none_dynamic_returns_empty(self):
        result = evaluate_tree(None, {}, {})
        assert result == []

    def test_evaluates_and_returns_visible_nodes(self):
        child = make_element(id="child", text="Child", param_ref_ids=["p1"])
        root = make_element(children=[child])

        result = evaluate_tree(root, {}, {})

        assert len(result) == 1
        assert result[0].display_name == "Child"


class TestEvaluateTreeCached:
    def test_processes_tree_nodes(self):
        element = make_element(id="test", text="Test", param_ref_ids=["p1"])
        node = TreeNode(
            id="test",
            name=None,
            text="Test",
            header_param_ref_id=None,
            element=element,
            visibility=always_visible,
        )

        result = evaluate_tree_cached([node], {}, {})

        assert len(result) == 1
        assert result[0].display_name == "Test"

    def test_flattens_generic_nodes(self):
        inner_elem = make_element(id="inner", text="Inner", param_ref_ids=["p1"])
        inner = TreeNode(
            id="inner",
            name=None,
            text="Inner",
            header_param_ref_id=None,
            element=inner_elem,
            visibility=always_visible,
        )
        outer_elem = make_element(id="outer", text="Generic")
        outer = TreeNode(
            id="outer",
            name=None,
            text="Generic",
            header_param_ref_id=None,
            element=outer_elem,
            visibility=always_visible,
            children=[inner],
        )

        result = evaluate_tree_cached([outer], {}, {})

        assert len(result) == 1
        assert result[0].display_name == "Inner"

    def test_numbers_duplicates(self):
        elem1 = make_element(id="a", text="Same", param_ref_ids=["p1"])
        elem2 = make_element(id="b", text="Same", param_ref_ids=["p2"])
        node1 = TreeNode(
            id="a", name=None, text="Same", header_param_ref_id=None,
            element=elem1, visibility=always_visible,
        )
        node2 = TreeNode(
            id="b", name=None, text="Same", header_param_ref_id=None,
            element=elem2, visibility=always_visible,
        )

        result = evaluate_tree_cached([node1, node2], {}, {})

        assert result[0].display_name == "Same 1"
        assert result[1].display_name == "Same 2"


class TestEvaluateNodes:
    def test_filters_by_visibility(self):
        elem = make_element(id="test", text="Test", param_ref_ids=["p1"])
        visible = TreeNode(
            id="visible", name=None, text="Visible", header_param_ref_id=None,
            element=elem, visibility=always_visible,
        )
        hidden_elem = make_element(id="hidden", text="Hidden", param_ref_ids=["p2"])
        hidden = TreeNode(
            id="hidden", name=None, text="Hidden", header_param_ref_id=None,
            element=hidden_elem,
            visibility=make_condition("show", ["1"], is_default=False),
        )

        result = _evaluate_nodes([visible, hidden], {"show": "0"}, {})

        assert len(result) == 1
        assert result[0].id == "visible"

    def test_skips_empty_nodes(self):
        elem = make_element(id="empty", text="Empty")
        node = TreeNode(
            id="empty", name=None, text="Empty", header_param_ref_id=None,
            element=elem, visibility=always_visible,
        )

        result = _evaluate_nodes([node], {}, {})
        assert result == []

    def test_includes_nodes_with_children_only(self):
        child_elem = make_element(id="child", text="Child", param_ref_ids=["p1"])
        child = TreeNode(
            id="child", name=None, text="Child", header_param_ref_id=None,
            element=child_elem, visibility=always_visible,
        )
        parent_elem = make_element(id="parent", text="Parent")
        parent = TreeNode(
            id="parent", name=None, text="Parent", header_param_ref_id=None,
            element=parent_elem, visibility=always_visible, children=[child],
        )

        result = _evaluate_nodes([parent], {}, {})

        assert len(result) == 1
        assert result[0].id == "parent"
        assert len(result[0].children) == 1

    def test_fallback_display_name(self):
        elem = make_element(id="test", param_ref_ids=["p1"])
        node = TreeNode(
            id="test", name=None, text=None, header_param_ref_id=None,
            element=elem, visibility=always_visible,
        )

        result = _evaluate_nodes([node], {}, {})

        assert result[0].display_name == "?"


class TestCollectVisibleRefs:
    def test_returns_direct_refs(self):
        element = make_element(param_ref_ids=["p1", "p2"], com_object_ref_ids=["co1"])

        params, coms = _collect_visible_refs(element, {})

        assert params == ["p1", "p2"]
        assert coms == ["co1"]

    def test_includes_refs_from_matching_when(self):
        content = make_element(param_ref_ids=["nested_p"], com_object_ref_ids=["nested_co"])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(param_ref_ids=["p1"], chooses=[choose])

        params, coms = _collect_visible_refs(element, {"sel": "1"})

        assert "p1" in params
        assert "nested_p" in params
        assert "nested_co" in coms

    def test_excludes_refs_from_non_matching_when(self):
        content = make_element(param_ref_ids=["nested_p"])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(param_ref_ids=["p1"], chooses=[choose])

        params, _ = _collect_visible_refs(element, {"sel": "2"})

        assert params == ["p1"]

    def test_does_not_include_refs_from_children(self):
        child = make_element(param_ref_ids=["child_p"])
        element = make_element(param_ref_ids=["root_p"], children=[child])

        params, _ = _collect_visible_refs(element, {})

        assert "root_p" in params
        assert "child_p" not in params


class TestCollectAllVisibleRefs:
    def test_includes_refs_from_children(self):
        from knx_gui.knxprod.parameter_tree import collect_all_visible_refs

        child1 = make_element(param_ref_ids=["child1_p"], com_object_ref_ids=["child1_co"])
        child2 = make_element(param_ref_ids=["child2_p"])
        element = make_element(param_ref_ids=["root_p"], children=[child1, child2])

        params, coms = collect_all_visible_refs(element, {})

        assert "root_p" in params
        assert "child1_p" in params
        assert "child2_p" in params
        assert "child1_co" in coms

    def test_includes_refs_from_nested_children(self):
        from knx_gui.knxprod.parameter_tree import collect_all_visible_refs

        grandchild = make_element(param_ref_ids=["gc_p"])
        child = make_element(children=[grandchild])
        element = make_element(param_ref_ids=["root_p"], children=[child])

        params, _ = collect_all_visible_refs(element, {})

        assert "root_p" in params
        assert "gc_p" in params

    def test_includes_refs_from_chooses(self):
        from knx_gui.knxprod.parameter_tree import collect_all_visible_refs

        content = make_element(param_ref_ids=["nested_p"])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(param_ref_ids=["root_p"], chooses=[choose])

        params, _ = collect_all_visible_refs(element, {"sel": "1"})

        assert "root_p" in params
        assert "nested_p" in params

    def test_includes_refs_from_children_inside_choose_content(self):
        from knx_gui.knxprod.parameter_tree import collect_all_visible_refs

        grandchild = make_element(param_ref_ids=["gc_p"], com_object_ref_ids=["gc_co"])
        child = make_element(param_ref_ids=["child_p"], children=[grandchild])
        content = make_element(param_ref_ids=["content_p"], children=[child])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(param_ref_ids=["root_p"], chooses=[choose])

        params, coms = collect_all_visible_refs(element, {"sel": "1"})

        assert "root_p" in params
        assert "content_p" in params
        assert "child_p" in params
        assert "gc_p" in params
        assert "gc_co" in coms


class TestFindMatchingWhen:
    def test_finds_matching_value(self):
        when1 = DynamicWhen(test_values=["1"])
        when2 = DynamicWhen(test_values=["2"])
        choose = DynamicChoose(param_ref_id="sel", conditions=[when1, when2])

        result = _find_matching_when(choose, {"sel": "2"})
        assert result is when2

    def test_returns_default_when_no_match(self):
        when1 = DynamicWhen(test_values=["1"])
        when_default = DynamicWhen(test_values=[], is_default=True)
        choose = DynamicChoose(param_ref_id="sel", conditions=[when1, when_default])

        result = _find_matching_when(choose, {"sel": "99"})
        assert result is when_default

    def test_returns_none_when_no_match_and_no_default(self):
        when1 = DynamicWhen(test_values=["1"])
        choose = DynamicChoose(param_ref_id="sel", conditions=[when1])

        result = _find_matching_when(choose, {"sel": "99"})
        assert result is None

    def test_uses_empty_string_for_missing_param(self):
        when_empty = DynamicWhen(test_values=[""])
        when_other = DynamicWhen(test_values=["1"])
        choose = DynamicChoose(param_ref_id="sel", conditions=[when_empty, when_other])

        result = _find_matching_when(choose, {})
        assert result is when_empty


class TestResolveName:
    def test_uses_header_param_text(self):
        param = make_param("header", text="Header Text")
        elem = make_element(id="test")
        node = TreeNode(
            id="test", name="Name", text="Text", header_param_ref_id="header",
            element=elem, visibility=always_visible,
        )

        result = _resolve_name(node, {"header": param})
        assert result == "Header Text"

    def test_uses_text_when_no_header_param(self):
        elem = make_element(id="test")
        node = TreeNode(
            id="test", name="Name", text="Text", header_param_ref_id=None,
            element=elem, visibility=always_visible,
        )

        result = _resolve_name(node, {})
        assert result == "Text"

    def test_uses_name_when_no_text(self):
        elem = make_element(id="test")
        node = TreeNode(
            id="test", name="Name", text=None, header_param_ref_id=None,
            element=elem, visibility=always_visible,
        )

        result = _resolve_name(node, {})
        assert result == "Name"

    def test_returns_none_when_no_name_or_text(self):
        elem = make_element(id="test")
        node = TreeNode(
            id="test", name=None, text=None, header_param_ref_id=None,
            element=elem, visibility=always_visible,
        )

        result = _resolve_name(node, {})
        assert result is None

    def test_ignores_header_param_without_text(self):
        param = make_param("header", text="")
        elem = make_element(id="test")
        node = TreeNode(
            id="test", name="Name", text="Text", header_param_ref_id="header",
            element=elem, visibility=always_visible,
        )

        result = _resolve_name(node, {"header": param})
        assert result == "Text"

    def test_ignores_missing_header_param(self):
        elem = make_element(id="test")
        node = TreeNode(
            id="test", name="Name", text="Text", header_param_ref_id="missing",
            element=elem, visibility=always_visible,
        )

        result = _resolve_name(node, {})
        assert result == "Text"


class TestFlattenGeneric:
    def test_flattens_generic_node(self):
        child = VisibleNode(id="child", display_name="Child", param_ref_ids=["p1"], com_object_ref_ids=[])
        generic = VisibleNode(id="generic", display_name="Generic", param_ref_ids=[], com_object_ref_ids=[], children=[child])
        nodes = [generic]

        _flatten_generic(nodes)

        assert len(nodes) == 1
        assert nodes[0].display_name == "Child"

    def test_flattens_channel_node(self):
        child = VisibleNode(id="child", display_name="Child", param_ref_ids=["p1"], com_object_ref_ids=[])
        channel = VisibleNode(id="channel", display_name="Channel", param_ref_ids=[], com_object_ref_ids=[], children=[child])
        nodes = [channel]

        _flatten_generic(nodes)

        assert len(nodes) == 1
        assert nodes[0].display_name == "Child"

    def test_flattens_question_mark_node(self):
        child = VisibleNode(id="child", display_name="Child", param_ref_ids=["p1"], com_object_ref_ids=[])
        unknown = VisibleNode(id="unknown", display_name="?", param_ref_ids=[], com_object_ref_ids=[], children=[child])
        nodes = [unknown]

        _flatten_generic(nodes)

        assert len(nodes) == 1
        assert nodes[0].display_name == "Child"

    def test_does_not_flatten_with_params(self):
        child = VisibleNode(id="child", display_name="Child", param_ref_ids=["p1"], com_object_ref_ids=[])
        generic = VisibleNode(id="generic", display_name="Generic", param_ref_ids=["p2"], com_object_ref_ids=[], children=[child])
        nodes = [generic]

        _flatten_generic(nodes)

        assert len(nodes) == 1
        assert nodes[0].display_name == "Generic"

    def test_does_not_flatten_without_children(self):
        generic = VisibleNode(id="generic", display_name="Generic", param_ref_ids=[], com_object_ref_ids=[])
        nodes = [generic]

        _flatten_generic(nodes)

        assert len(nodes) == 1
        assert nodes[0].display_name == "Generic"

    def test_flattens_nested_generic(self):
        inner = VisibleNode(id="inner", display_name="Inner", param_ref_ids=["p1"], com_object_ref_ids=[])
        middle = VisibleNode(id="middle", display_name="generic", param_ref_ids=[], com_object_ref_ids=[], children=[inner])
        outer = VisibleNode(id="outer", display_name="CHANNEL", param_ref_ids=[], com_object_ref_ids=[], children=[middle])
        nodes = [outer]

        _flatten_generic(nodes)

        assert len(nodes) == 1
        assert nodes[0].display_name == "Inner"

    def test_keeps_regular_nodes(self):
        node = VisibleNode(id="test", display_name="Settings", param_ref_ids=["p1"], com_object_ref_ids=[])
        nodes = [node]

        _flatten_generic(nodes)

        assert len(nodes) == 1
        assert nodes[0].display_name == "Settings"

    def test_flattens_in_children_recursively(self):
        grandchild = VisibleNode(id="gc", display_name="GrandChild", param_ref_ids=["p1"], com_object_ref_ids=[])
        generic_child = VisibleNode(id="gen", display_name="Generic", param_ref_ids=[], com_object_ref_ids=[], children=[grandchild])
        parent = VisibleNode(id="parent", display_name="Parent", param_ref_ids=["p2"], com_object_ref_ids=[], children=[generic_child])
        nodes = [parent]

        _flatten_generic(nodes)

        assert nodes[0].display_name == "Parent"
        assert len(nodes[0].children) == 1
        assert nodes[0].children[0].display_name == "GrandChild"


class TestNumberDuplicates:
    def test_numbers_duplicate_names(self):
        node1 = VisibleNode(id="a", display_name="Channel", param_ref_ids=[], com_object_ref_ids=[])
        node2 = VisibleNode(id="b", display_name="Channel", param_ref_ids=[], com_object_ref_ids=[])
        node3 = VisibleNode(id="c", display_name="Channel", param_ref_ids=[], com_object_ref_ids=[])
        nodes = [node1, node2, node3]

        _number_duplicates(nodes)

        assert nodes[0].display_name == "Channel 1"
        assert nodes[1].display_name == "Channel 2"
        assert nodes[2].display_name == "Channel 3"

    def test_leaves_unique_names_unchanged(self):
        node1 = VisibleNode(id="a", display_name="Settings", param_ref_ids=[], com_object_ref_ids=[])
        node2 = VisibleNode(id="b", display_name="Advanced", param_ref_ids=[], com_object_ref_ids=[])
        nodes = [node1, node2]

        _number_duplicates(nodes)

        assert nodes[0].display_name == "Settings"
        assert nodes[1].display_name == "Advanced"

    def test_handles_mixed_duplicates(self):
        node1 = VisibleNode(id="a", display_name="Channel", param_ref_ids=[], com_object_ref_ids=[])
        node2 = VisibleNode(id="b", display_name="Settings", param_ref_ids=[], com_object_ref_ids=[])
        node3 = VisibleNode(id="c", display_name="Channel", param_ref_ids=[], com_object_ref_ids=[])
        nodes = [node1, node2, node3]

        _number_duplicates(nodes)

        assert nodes[0].display_name == "Channel 1"
        assert nodes[1].display_name == "Settings"
        assert nodes[2].display_name == "Channel 2"

    def test_empty_list(self):
        nodes: list[VisibleNode] = []
        _number_duplicates(nodes)
        assert nodes == []
