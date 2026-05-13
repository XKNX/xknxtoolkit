from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .types import DynamicChoose, DynamicElement, DynamicWhen

if TYPE_CHECKING:
    from .types import Parameter


class ParameterTreeDepthError(Exception):
    pass


@dataclass
class ParameterSection:
    id: str | None
    name: str | None
    text: str | None
    header_param_ref_id: str | None
    param_ref_ids: list[str] = field(default_factory=list)
    com_object_ref_ids: list[str] = field(default_factory=list)


@dataclass
class ParameterBlock:
    id: str | None
    name: str | None
    text: str | None
    header_param_ref_id: str | None
    param_ref_ids: list[str] = field(default_factory=list)
    com_object_ref_ids: list[str] = field(default_factory=list)
    sections: list[ParameterSection] = field(default_factory=list)
    chooses: list[DynamicChoose] = field(default_factory=list)


@dataclass
class ParameterChannel:
    id: str | None
    name: str | None
    text: str | None
    param_ref_ids: list[str] = field(default_factory=list)
    com_object_ref_ids: list[str] = field(default_factory=list)
    blocks: list[ParameterBlock] = field(default_factory=list)
    chooses: list[DynamicChoose] = field(default_factory=list)


@dataclass
class ParameterTree:
    channels: list[ParameterChannel] = field(default_factory=list)


def build_parameter_tree(dynamic: DynamicElement | None) -> ParameterTree:
    if dynamic is None:
        return ParameterTree()

    channels: list[ParameterChannel] = []

    for child in dynamic.children:
        channel = _build_channel(child)
        channels.append(channel)

    if not channels and (dynamic.param_ref_ids or dynamic.children or dynamic.chooses):
        channel = _build_channel(dynamic)
        channels.append(channel)

    return ParameterTree(channels=channels)


def _build_channel(element: DynamicElement) -> ParameterChannel:
    blocks: list[ParameterBlock] = []

    for child in element.children:
        block = _build_block(child)
        blocks.append(block)

    return ParameterChannel(
        id=element.id,
        name=element.name,
        text=element.text,
        param_ref_ids=list(element.param_ref_ids),
        com_object_ref_ids=list(element.com_object_ref_ids),
        blocks=blocks,
        chooses=list(element.chooses),
    )


def _build_block(element: DynamicElement) -> ParameterBlock:
    sections: list[ParameterSection] = []

    for child in element.children:
        section = _build_section(child)
        sections.append(section)

    for choose in element.chooses:
        for when in choose.conditions:
            if when.content:
                for nested_child in when.content.children:
                    _check_no_deeper_nesting(nested_child)

    return ParameterBlock(
        id=element.id,
        name=element.name,
        text=element.text,
        header_param_ref_id=element.header_param_ref_id,
        param_ref_ids=list(element.param_ref_ids),
        com_object_ref_ids=list(element.com_object_ref_ids),
        sections=sections,
        chooses=list(element.chooses),
    )


def _build_section(element: DynamicElement) -> ParameterSection:
    _check_no_deeper_nesting(element)

    return ParameterSection(
        id=element.id,
        name=element.name,
        text=element.text,
        header_param_ref_id=element.header_param_ref_id,
        param_ref_ids=list(element.param_ref_ids),
        com_object_ref_ids=list(element.com_object_ref_ids),
    )


def _check_no_deeper_nesting(element: DynamicElement) -> None:
    if element.children:
        raise ParameterTreeDepthError(
            f"Parameter tree exceeds maximum depth of 3 levels. "
            f"Found nested children in element: {element.id or 'unknown'}"
        )
    for choose in element.chooses:
        for when in choose.conditions:
            if when.content and when.content.children:
                raise ParameterTreeDepthError(
                    "Parameter tree exceeds maximum depth of 3 levels. "
                    "Found nested children in choose/when branch."
                )


@dataclass
class VisibleSection:
    id: str
    display_name: str
    param_ref_ids: list[str]
    com_object_ref_ids: list[str]


@dataclass
class VisibleBlock:
    id: str
    display_name: str
    param_ref_ids: list[str]
    com_object_ref_ids: list[str]
    sections: list[VisibleSection]


@dataclass
class VisibleChannel:
    id: str
    display_name: str
    param_ref_ids: list[str]
    com_object_ref_ids: list[str]
    blocks: list[VisibleBlock]


@dataclass
class VisibleTree:
    channels: list[VisibleChannel]


def _resolve_display_name(
    text: str | None,
    name: str | None,
    element_id: str | None,
    header_param_ref_id: str | None,
    params_by_id: dict[str, Parameter],
    fallback: str,
) -> str:
    if header_param_ref_id:
        param = params_by_id.get(header_param_ref_id)
        if param and param.text:
            return param.text
    return text or name or element_id or fallback


def evaluate_tree(
    tree: ParameterTree,
    param_values: dict[str, str],
    parameters: list[Parameter],
) -> VisibleTree:
    params_by_id = {p.id: p for p in parameters}
    channels: list[VisibleChannel] = []

    for channel in tree.channels:
        visible_channel = _evaluate_channel(channel, param_values, params_by_id)
        channels.append(visible_channel)

    _number_duplicate_names(channels)
    return VisibleTree(channels=channels)


def _number_duplicate_names(channels: list[VisibleChannel]) -> None:
    channel_counts: dict[str, int] = {}
    for ch in channels:
        channel_counts[ch.display_name] = channel_counts.get(ch.display_name, 0) + 1

    channel_indices: dict[str, int] = {}
    for ch in channels:
        if channel_counts[ch.display_name] > 1:
            idx = channel_indices.get(ch.display_name, 0) + 1
            channel_indices[ch.display_name] = idx
            ch.display_name = f"{ch.display_name} {idx}"

        block_counts: dict[str, int] = {}
        for blk in ch.blocks:
            block_counts[blk.display_name] = block_counts.get(blk.display_name, 0) + 1

        block_indices: dict[str, int] = {}
        for blk in ch.blocks:
            if block_counts[blk.display_name] > 1:
                idx = block_indices.get(blk.display_name, 0) + 1
                block_indices[blk.display_name] = idx
                blk.display_name = f"{blk.display_name} {idx}"


def _evaluate_channel(
    channel: ParameterChannel,
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> VisibleChannel:
    param_ref_ids = list(channel.param_ref_ids)
    com_object_ref_ids = list(channel.com_object_ref_ids)
    blocks: list[VisibleBlock] = []

    for block in channel.blocks:
        visible_block = _evaluate_block(block, param_values, params_by_id)
        blocks.append(visible_block)

    for choose in channel.chooses:
        matched = _find_matching_when(choose, param_values)
        if matched and matched.content:
            param_ref_ids.extend(matched.content.param_ref_ids)
            com_object_ref_ids.extend(matched.content.com_object_ref_ids)
            for child in matched.content.children:
                block_element = _dynamic_to_block(child)
                visible_block = _evaluate_block(block_element, param_values, params_by_id)
                blocks.append(visible_block)

    display_name = _resolve_display_name(
        channel.text, channel.name, channel.id, None, params_by_id, "Channel"
    )

    return VisibleChannel(
        id=channel.id or "channel",
        display_name=display_name,
        param_ref_ids=param_ref_ids,
        com_object_ref_ids=com_object_ref_ids,
        blocks=blocks,
    )


def _evaluate_block(
    block: ParameterBlock,
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> VisibleBlock:
    param_ref_ids = list(block.param_ref_ids)
    com_object_ref_ids = list(block.com_object_ref_ids)
    sections: list[VisibleSection] = []

    for section in block.sections:
        visible_section = _evaluate_section(section, param_values, params_by_id)
        sections.append(visible_section)

    for choose in block.chooses:
        matched = _find_matching_when(choose, param_values)
        if matched and matched.content:
            param_ref_ids.extend(matched.content.param_ref_ids)
            com_object_ref_ids.extend(matched.content.com_object_ref_ids)
            for child in matched.content.children:
                section_element = _dynamic_to_section(child)
                visible_section = _evaluate_section(
                    section_element, param_values, params_by_id
                )
                sections.append(visible_section)
            for nested_choose in matched.content.chooses:
                nested_matched = _find_matching_when(nested_choose, param_values)
                if nested_matched and nested_matched.content:
                    param_ref_ids.extend(nested_matched.content.param_ref_ids)
                    com_object_ref_ids.extend(nested_matched.content.com_object_ref_ids)

    display_name = _resolve_display_name(
        block.text, block.name, block.id, block.header_param_ref_id, params_by_id, "Block"
    )

    return VisibleBlock(
        id=block.id or "block",
        display_name=display_name,
        param_ref_ids=param_ref_ids,
        com_object_ref_ids=com_object_ref_ids,
        sections=sections,
    )


def _evaluate_section(
    section: ParameterSection,
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> VisibleSection:
    display_name = _resolve_display_name(
        section.text, section.name, section.id, section.header_param_ref_id, params_by_id, "Section"
    )

    return VisibleSection(
        id=section.id or "section",
        display_name=display_name,
        param_ref_ids=list(section.param_ref_ids),
        com_object_ref_ids=list(section.com_object_ref_ids),
    )


def _dynamic_to_block(element: DynamicElement) -> ParameterBlock:
    sections: list[ParameterSection] = []
    for child in element.children:
        sections.append(_dynamic_to_section(child))

    return ParameterBlock(
        id=element.id,
        name=element.name,
        text=element.text,
        header_param_ref_id=element.header_param_ref_id,
        param_ref_ids=list(element.param_ref_ids),
        com_object_ref_ids=list(element.com_object_ref_ids),
        sections=sections,
        chooses=list(element.chooses),
    )


def _dynamic_to_section(element: DynamicElement) -> ParameterSection:
    return ParameterSection(
        id=element.id,
        name=element.name,
        text=element.text,
        header_param_ref_id=element.header_param_ref_id,
        param_ref_ids=list(element.param_ref_ids),
        com_object_ref_ids=list(element.com_object_ref_ids),
    )


def _find_matching_when(
    choose: DynamicChoose, param_values: dict[str, str]
) -> DynamicWhen | None:
    current_value = param_values.get(choose.param_ref_id, "")

    for when in choose.conditions:
        if current_value in when.test_values:
            return when

    for when in choose.conditions:
        if when.is_default:
            return when

    return None
