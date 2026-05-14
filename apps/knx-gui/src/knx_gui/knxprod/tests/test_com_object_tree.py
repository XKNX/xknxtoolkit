from knx_gui.knxprod.com_object_tree import (
    filter_visible_com_objects,
    visible_com_object_ids,
)
from knx_gui.knxprod.types import (
    ComObject,
    ComObjectFlags,
    DynamicChoose,
    DynamicElement,
    DynamicWhen,
)


def make_com_object(id: str, name: str = "Test") -> ComObject:
    return ComObject(id=id, name=name, number=0, dpt_codes=[], flags=ComObjectFlags())


def make_element(
    com_object_ref_ids: list[str] | None = None,
    children: list[DynamicElement] | None = None,
    chooses: list[DynamicChoose] | None = None,
) -> DynamicElement:
    return DynamicElement(
        com_object_ref_ids=com_object_ref_ids or [],
        children=children or [],
        chooses=chooses or [],
    )


class TestVisibleComObjectIds:
    def test_none_dynamic_returns_empty(self):
        result = visible_com_object_ids(None, {})
        assert result == set()

    def test_returns_direct_refs(self):
        element = make_element(com_object_ref_ids=["co1", "co2"])
        result = visible_com_object_ids(element, {})
        assert result == {"co1", "co2"}

    def test_returns_refs_from_children(self):
        child = make_element(com_object_ref_ids=["child_co"])
        element = make_element(com_object_ref_ids=["root_co"], children=[child])
        result = visible_com_object_ids(element, {})
        assert result == {"root_co", "child_co"}

    def test_returns_refs_from_matching_choose(self):
        content = make_element(com_object_ref_ids=["nested_co"])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(com_object_ref_ids=["root_co"], chooses=[choose])

        result = visible_com_object_ids(element, {"sel": "1"})
        assert result == {"root_co", "nested_co"}

    def test_excludes_refs_from_non_matching_choose(self):
        content = make_element(com_object_ref_ids=["nested_co"])
        choose = DynamicChoose(
            param_ref_id="sel",
            conditions=[DynamicWhen(test_values=["1"], content=content)],
        )
        element = make_element(com_object_ref_ids=["root_co"], chooses=[choose])

        result = visible_com_object_ids(element, {"sel": "2"})
        assert result == {"root_co"}


class TestFilterVisibleComObjects:
    def test_none_dynamic_returns_all(self):
        com_objects = [make_com_object("co1"), make_com_object("co2")]
        result = filter_visible_com_objects(com_objects, None, {})
        assert len(result) == 2

    def test_filters_by_visibility(self):
        co1 = make_com_object("co1")
        co2 = make_com_object("co2")
        element = make_element(com_object_ref_ids=["co1"])

        result = filter_visible_com_objects([co1, co2], element, {})

        assert len(result) == 1
        assert result[0].id == "co1"

    def test_preserves_order(self):
        co1 = make_com_object("co1")
        co2 = make_com_object("co2")
        co3 = make_com_object("co3")
        element = make_element(com_object_ref_ids=["co3", "co1"])

        result = filter_visible_com_objects([co1, co2, co3], element, {})

        assert [co.id for co in result] == ["co1", "co3"]
