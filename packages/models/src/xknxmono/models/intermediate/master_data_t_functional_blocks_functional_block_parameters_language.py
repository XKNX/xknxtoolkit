from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionalBlocksFunctionalBlockParametersLanguage:
    class Meta:
        global_type = False

    identifier: None | str = field(
        default=None,
        metadata={
            "name": "Identifier",
            "type": "Attribute",
        },
    )
