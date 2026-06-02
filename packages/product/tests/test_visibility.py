"""Visibility-evaluation tests over the dynamic tree (the algorithm `Application.visible_*`
delegates to). They operate on synthetic DynamicElement/Parameter/ComObject value objects,
independent of IR loading."""

from xknxmono.product import (
    ComObject,
    ComObjectFlags,
    DynamicChoose,
    DynamicElement,
    DynamicWhen,
    Parameter,
)
from xknxmono.product.parser import dynamic as dy


def make_param(id: str, value: str = "", text: str = "Test") -> Parameter:
    return Parameter(
        id=id,
        ref_id=id,
        name=id,
        text=text,
        value=value,
        param_type_id="",
        param_type=None,
    )


def make_com_object(id: str, name: str = "Test CO") -> ComObject:
    return ComObject(
        id=id,
        name=name,
        number=0,
        dpt_codes=[],
        flags=ComObjectFlags(),
    )


class TestVisibilityEvaluation:
    def test_no_dynamic_returns_all_params(self):
        params = [make_param("p1"), make_param("p2"), make_param("p3")]
        result = dy.visible_parameters(params, None)
        assert len(result) == 3
        assert {p.id for p in result} == {"p1", "p2", "p3"}

    def test_choose_filters_by_param_value(self):
        selector = make_param("selector", value="1")
        param_a = make_param("param_a", text="Option A Param")
        param_b = make_param("param_b", text="Option B Param")
        params = [selector, param_a, param_b]

        dynamic = DynamicElement(
            chooses=[
                DynamicChoose(
                    param_ref_id="selector",
                    conditions=[
                        DynamicWhen(
                            test_values=["0"],
                            content=DynamicElement(param_ref_ids=["param_a"]),
                        ),
                        DynamicWhen(
                            test_values=["1"],
                            content=DynamicElement(param_ref_ids=["param_b"]),
                        ),
                    ],
                )
            ]
        )

        result = dy.visible_parameters(params, dynamic)
        assert {p.id for p in result} == {"param_b"}

    def test_choose_uses_default_when_no_match(self):
        selector = make_param("selector", value="99")
        param_a = make_param("param_a")
        param_default = make_param("param_default")
        params = [selector, param_a, param_default]

        dynamic = DynamicElement(
            chooses=[
                DynamicChoose(
                    param_ref_id="selector",
                    conditions=[
                        DynamicWhen(
                            test_values=["0"],
                            content=DynamicElement(param_ref_ids=["param_a"]),
                        ),
                        DynamicWhen(
                            test_values=[],
                            is_default=True,
                            content=DynamicElement(param_ref_ids=["param_default"]),
                        ),
                    ],
                )
            ]
        )

        result = dy.visible_parameters(params, dynamic)
        assert {p.id for p in result} == {"param_default"}

    def test_nested_chooses(self):
        mode = make_param("mode", value="1")
        channel = make_param("channel", value="A")
        param_1a = make_param("p1a")
        param_1b = make_param("p1b")
        params = [mode, channel, param_1a, param_1b]

        dynamic = DynamicElement(
            chooses=[
                DynamicChoose(
                    param_ref_id="mode",
                    conditions=[
                        DynamicWhen(
                            test_values=["0"],
                            content=DynamicElement(param_ref_ids=["p1a"]),
                        ),
                        DynamicWhen(
                            test_values=["1"],
                            content=DynamicElement(
                                chooses=[
                                    DynamicChoose(
                                        param_ref_id="channel",
                                        conditions=[
                                            DynamicWhen(
                                                test_values=["A"],
                                                content=DynamicElement(
                                                    param_ref_ids=["p1a"]
                                                ),
                                            ),
                                            DynamicWhen(
                                                test_values=["B"],
                                                content=DynamicElement(
                                                    param_ref_ids=["p1b"]
                                                ),
                                            ),
                                        ],
                                    )
                                ]
                            ),
                        ),
                    ],
                )
            ]
        )

        result = dy.visible_parameters(params, dynamic)
        assert {p.id for p in result} == {"p1a"}

    def test_custom_param_values_override(self):
        selector = make_param("selector", value="0")
        param_a = make_param("param_a")
        param_b = make_param("param_b")
        params = [selector, param_a, param_b]

        dynamic = DynamicElement(
            chooses=[
                DynamicChoose(
                    param_ref_id="selector",
                    conditions=[
                        DynamicWhen(
                            test_values=["0"],
                            content=DynamicElement(param_ref_ids=["param_a"]),
                        ),
                        DynamicWhen(
                            test_values=["1"],
                            content=DynamicElement(param_ref_ids=["param_b"]),
                        ),
                    ],
                )
            ]
        )

        result = dy.visible_parameters(params, dynamic, {"selector": "1"})
        assert {p.id for p in result} == {"param_b"}

    def test_multi_value_test(self):
        mode = make_param("mode", value="2")
        param_a = make_param("param_a")
        param_b = make_param("param_b")
        params = [mode, param_a, param_b]

        dynamic = DynamicElement(
            chooses=[
                DynamicChoose(
                    param_ref_id="mode",
                    conditions=[
                        DynamicWhen(
                            test_values=["0"],
                            content=DynamicElement(param_ref_ids=["param_a"]),
                        ),
                        DynamicWhen(
                            test_values=["1", "2", "3"],
                            content=DynamicElement(param_ref_ids=["param_b"]),
                        ),
                    ],
                )
            ]
        )

        result = dy.visible_parameters(params, dynamic)
        assert {p.id for p in result} == {"param_b"}

    def test_direct_refs_always_visible(self):
        selector = make_param("selector", value="0")
        always_visible = make_param("always")
        conditional = make_param("conditional")
        params = [selector, always_visible, conditional]

        dynamic = DynamicElement(
            param_ref_ids=["always"],
            chooses=[
                DynamicChoose(
                    param_ref_id="selector",
                    conditions=[
                        DynamicWhen(
                            test_values=["1"],
                            content=DynamicElement(param_ref_ids=["conditional"]),
                        ),
                    ],
                )
            ],
        )

        result = dy.visible_parameters(params, dynamic)
        assert {p.id for p in result} == {"always"}


class TestComObjectVisibility:
    def _values(self, params: list[Parameter]) -> dict[str, str]:
        return {p.id: p.value for p in params}

    def test_no_dynamic_returns_all_com_objects(self):
        com_objects = [
            make_com_object("co1"),
            make_com_object("co2"),
            make_com_object("co3"),
        ]
        result = dy.filter_visible_com_objects(com_objects, None, {})
        assert len(result) == 3
        assert {co.id for co in result} == {"co1", "co2", "co3"}

    def test_choose_filters_com_objects_by_param_value(self):
        selector = make_param("selector", value="1")
        co_a = make_com_object("co_a", "Object A")
        co_b = make_com_object("co_b", "Object B")

        dynamic = DynamicElement(
            chooses=[
                DynamicChoose(
                    param_ref_id="selector",
                    conditions=[
                        DynamicWhen(
                            test_values=["0"],
                            content=DynamicElement(com_object_ref_ids=["co_a"]),
                        ),
                        DynamicWhen(
                            test_values=["1"],
                            content=DynamicElement(com_object_ref_ids=["co_b"]),
                        ),
                    ],
                )
            ]
        )

        result = dy.filter_visible_com_objects(
            [co_a, co_b], dynamic, self._values([selector])
        )
        assert {co.id for co in result} == {"co_b"}

    def test_direct_co_refs_always_visible(self):
        selector = make_param("selector", value="0")
        always_visible = make_com_object("always", "Always Visible")
        conditional = make_com_object("conditional", "Conditional")

        dynamic = DynamicElement(
            com_object_ref_ids=["always"],
            chooses=[
                DynamicChoose(
                    param_ref_id="selector",
                    conditions=[
                        DynamicWhen(
                            test_values=["1"],
                            content=DynamicElement(com_object_ref_ids=["conditional"]),
                        ),
                    ],
                )
            ],
        )

        result = dy.filter_visible_com_objects(
            [always_visible, conditional], dynamic, self._values([selector])
        )
        assert {co.id for co in result} == {"always"}
