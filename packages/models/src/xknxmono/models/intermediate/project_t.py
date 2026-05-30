from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.project_t_add_in_data_1 import ProjectAddInData1
from xknxmono.models.intermediate.project_t_addin_data_2 import ProjectAddinData2
from xknxmono.models.intermediate.project_t_installations import ProjectInstallations
from xknxmono.models.intermediate.project_t_project_information import ProjectProjectInformation
from xknxmono.models.intermediate.project_t_user_files import ProjectUserFiles


@dataclass(slots=True, kw_only=True)
class Project:
    class Meta:
        name = "Project_t"

    project_information: None | ProjectProjectInformation = field(
        default=None,
        metadata={
            "name": "ProjectInformation",
            "type": "Element",
        },
    )
    installations: None | ProjectInstallations = field(
        default=None,
        metadata={
            "name": "Installations",
            "type": "Element",
        },
    )
    user_files: None | ProjectUserFiles = field(
        default=None,
        metadata={
            "name": "UserFiles",
            "type": "Element",
        },
    )
    addin_data_element: None | ProjectAddinData2 = field(
        default=None,
        metadata={
            "name": "AddinData",
            "type": "Element",
        },
    )
    add_in_data: None | ProjectAddInData1 = field(
        default=None,
        metadata={
            "name": "AddInData",
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
