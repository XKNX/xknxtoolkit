"""Unit tests for resolve_widget: maps a ParameterType.choice variant to its UI widget
descriptor. Builds minimal instances of each ParameterTypeType* variant directly - no
fixture files needed."""

from __future__ import annotations

from xknxmono.models.intermediate import (
    HorizontalAlignment,
    ParameterTypeTypeColor,
    ParameterTypeTypeColorSpace,
    ParameterTypeTypeDate,
    ParameterTypeTypeDateEncoding,
    ParameterTypeTypeFloat,
    ParameterTypeTypeFloatEncoding,
    ParameterTypeTypeFloatUihint,
    ParameterTypeTypeIpaddress,
    ParameterTypeTypeIpaddressAddressType,
    ParameterTypeTypeIpaddressVersion,
    ParameterTypeTypeNumber,
    ParameterTypeTypeNumberType,
    ParameterTypeTypeNumberUihint,
    ParameterTypeTypePicture,
    ParameterTypeTypeRawData,
    ParameterTypeTypeRestriction,
    ParameterTypeTypeRestrictionBase,
    ParameterTypeTypeText,
    ParameterTypeTypeTime,
    ParameterTypeTypeTimeUnit,
)
from xknxmono.models.intermediate.parameter_type_t import ParameterType
from xknxmono.models.intermediate.parameter_type_t_type_restriction_enumeration import (
    ParameterTypeTypeRestrictionEnumeration,
)
from xknxmono.product.parser_v2.ui.parameter import (
    CheckBoxWidget,
    ColorWidget,
    DateWidget,
    EnumChoice,
    EnumWidget,
    FloatSliderWidget,
    FloatWidget,
    IpAddressWidget,
    NumberSliderWidget,
    NumberWidget,
    PictureWidget,
    ProgressBarWidget,
    RawDataWidget,
    TextWidget,
    TimeWidget,
    resolve_widget,
)


def _pt(choice: object) -> ParameterType:
    return ParameterType(id="PT1", name="T", choice=choice)  # pyright: ignore[reportArgumentType]


def test_restriction_without_enumeration_is_a_plain_number_widget() -> None:
    restriction = ParameterTypeTypeRestriction(
        enumeration=[], base=ParameterTypeTypeRestrictionBase.VALUE, size_in_bit=4
    )
    widget = resolve_widget(_pt(restriction))
    assert widget == NumberWidget(min=0, max=15)


def test_restriction_with_enumeration_is_an_enum_widget_sorted_by_display_order() -> (
    None
):
    e1 = ParameterTypeTypeRestrictionEnumeration(
        value=1, id="E1", text="First", display_order=2
    )
    e2 = ParameterTypeTypeRestrictionEnumeration(
        value=2, id="E2", text=None, display_order=1
    )  # no text -> label falls back to str(value)
    restriction = ParameterTypeTypeRestriction(
        enumeration=[e1, e2],
        base=ParameterTypeTypeRestrictionBase.VALUE,
        size_in_bit=4,
    )
    widget = resolve_widget(_pt(restriction))
    assert widget == EnumWidget(
        choices=(
            EnumChoice(value=2, label="2", id="E2"),
            EnumChoice(value=1, label="First", id="E1"),
        ),
        base=ParameterTypeTypeRestrictionBase.VALUE,
    )


def test_number_slider_uihint() -> None:
    number = ParameterTypeTypeNumber(
        size_in_bit=8,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=255,
        uihint=ParameterTypeTypeNumberUihint.SLIDER,
    )
    widget = resolve_widget(_pt(number))
    assert widget == NumberSliderWidget(
        min=0, max=255, increment=1, type_value=number.type_value
    )


def test_number_progress_bar_uihint() -> None:
    number = ParameterTypeTypeNumber(
        size_in_bit=8,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=100,
        uihint=ParameterTypeTypeNumberUihint.PROGRESS_BAR,
    )
    widget = resolve_widget(_pt(number))
    assert widget == ProgressBarWidget(min=0, max=100)


def test_number_check_box_uihint() -> None:
    number = ParameterTypeTypeNumber(
        size_in_bit=1,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=1,
        uihint=ParameterTypeTypeNumberUihint.CHECK_BOX,
    )
    widget = resolve_widget(_pt(number))
    assert widget == CheckBoxWidget()


def test_number_default_widget() -> None:
    number = ParameterTypeTypeNumber(
        size_in_bit=8,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=255,
    )
    widget = resolve_widget(_pt(number))
    assert widget == NumberWidget(
        min=0, max=255, increment=1, type_value=number.type_value
    )


def test_float_slider_uihint() -> None:
    f = ParameterTypeTypeFloat(
        encoding=ParameterTypeTypeFloatEncoding.DPT_9,
        min_inclusive=-20.0,
        max_inclusive=20.0,
        uihint=ParameterTypeTypeFloatUihint.SLIDER,
    )
    widget = resolve_widget(_pt(f))
    assert widget == FloatSliderWidget(min=-20.0, max=20.0, encoding=f.encoding)


def test_float_default_widget() -> None:
    f = ParameterTypeTypeFloat(
        encoding=ParameterTypeTypeFloatEncoding.DPT_9,
        min_inclusive=-20.0,
        max_inclusive=20.0,
    )
    widget = resolve_widget(_pt(f))
    assert widget == FloatWidget(min=-20.0, max=20.0, encoding=f.encoding)


def test_text_widget() -> None:
    t = ParameterTypeTypeText(size_in_bit=64, pattern=r"\d+")
    widget = resolve_widget(_pt(t))
    assert widget == TextWidget(max_length=8, pattern=r"\d+")


def test_time_widget() -> None:
    t = ParameterTypeTypeTime(
        size_in_bit=24,
        unit=ParameterTypeTypeTimeUnit.SECONDS,
        min_inclusive=0,
        max_inclusive=3600,
    )
    widget = resolve_widget(_pt(t))
    assert widget == TimeWidget(
        unit=ParameterTypeTypeTimeUnit.SECONDS, min=0, max=3600, hint=None
    )


def test_date_widget() -> None:
    d = ParameterTypeTypeDate(encoding=ParameterTypeTypeDateEncoding.DPT_11)
    widget = resolve_widget(_pt(d))
    assert widget == DateWidget(encoding=ParameterTypeTypeDateEncoding.DPT_11)


def test_ip_address_widget() -> None:
    ip = ParameterTypeTypeIpaddress(
        address_type=ParameterTypeTypeIpaddressAddressType.HOST_ADDRESS,
        version=ParameterTypeTypeIpaddressVersion.IPV4,
    )
    widget = resolve_widget(_pt(ip))
    assert widget == IpAddressWidget(
        address_type=ParameterTypeTypeIpaddressAddressType.HOST_ADDRESS,
        version=ParameterTypeTypeIpaddressVersion.IPV4,
    )


def test_picture_widget() -> None:
    p = ParameterTypeTypePicture(
        ref_id="BD-1", horizontal_alignment=HorizontalAlignment.MIDDLE
    )
    widget = resolve_widget(_pt(p))
    assert widget == PictureWidget(
        ref_id="BD-1", horizontal_alignment=HorizontalAlignment.MIDDLE
    )


def test_color_widget() -> None:
    c = ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGB)
    widget = resolve_widget(_pt(c))
    assert widget == ColorWidget(space=ParameterTypeTypeColorSpace.RGB)


def test_raw_data_widget() -> None:
    r = ParameterTypeTypeRawData(max_size=16)
    widget = resolve_widget(_pt(r))
    assert widget == RawDataWidget(max_size=16)


def test_unrecognised_choice_returns_none() -> None:
    widget = resolve_widget(_pt(None))
    assert widget is None
