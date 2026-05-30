from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.hawk_configuration_data_t_resources_resource_access_rights import (
    HawkConfigurationDataResourcesResourceAccessRights,
)
from xknxmono.models.intermediate.hawk_configuration_data_t_resources_resource_resource_type import (
    HawkConfigurationDataResourcesResourceResourceType,
)
from xknxmono.models.intermediate.resource_location_t import ResourceLocation


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataResourcesResource:
    class Meta:
        global_type = False

    location: None | ResourceLocation = field(
        default=None,
        metadata={
            "name": "Location",
            "type": "Element",
        },
    )
    img_location: None | ResourceLocation = field(
        default=None,
        metadata={
            "name": "ImgLocation",
            "type": "Element",
        },
    )
    resource_type: HawkConfigurationDataResourcesResourceResourceType = field(
        metadata={
            "name": "ResourceType",
            "type": "Element",
        }
    )
    access_rights: HawkConfigurationDataResourcesResourceAccessRights = field(
        metadata={
            "name": "AccessRights",
            "type": "Element",
        }
    )
