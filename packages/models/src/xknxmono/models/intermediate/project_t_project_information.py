from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.project_t_project_information_device_certificates import (
    ProjectProjectInformationDeviceCertificates,
)
from xknxmono.models.intermediate.project_t_project_information_history_entries import (
    ProjectProjectInformationHistoryEntries,
)
from xknxmono.models.intermediate.project_t_project_information_project_traces import (
    ProjectProjectInformationProjectTraces,
)
from xknxmono.models.intermediate.project_t_project_information_tags import (
    ProjectProjectInformationTags,
)
from xknxmono.models.intermediate.project_t_project_information_to_do_items import (
    ProjectProjectInformationToDoItems,
)


@dataclass(slots=True, kw_only=True)
class ProjectProjectInformation:
    class Meta:
        global_type = False

    tags: None | ProjectProjectInformationTags = field(
        default=None,
        metadata={
            "name": "Tags",
            "type": "Element",
        },
    )
    history_entries: None | ProjectProjectInformationHistoryEntries = field(
        default=None,
        metadata={
            "name": "HistoryEntries",
            "type": "Element",
        },
    )
    to_do_items: None | ProjectProjectInformationToDoItems = field(
        default=None,
        metadata={
            "name": "ToDoItems",
            "type": "Element",
        },
    )
    project_traces: None | ProjectProjectInformationProjectTraces = field(
        default=None,
        metadata={
            "name": "ProjectTraces",
            "type": "Element",
        },
    )
    device_certificates: None | ProjectProjectInformationDeviceCertificates = field(
        default=None,
        metadata={
            "name": "DeviceCertificates",
            "type": "Element",
        },
    )
