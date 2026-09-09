"""Every section of the Configure panel, each extracted into its own file.

Kept inside `knx_gui.plugins.project` (not `knx_gui.widgets`) because most of them
need `knx_gui.plugins.project.strings` - importing that from `knx_gui.widgets`
creates a real circular import, since other plugins (e.g. node_editor) import
`knx_gui.widgets` eagerly before `knx_gui.plugins.project` has finished loading.
Keeping every section here, even Load Procedures and Parameters (neither needs
`project.strings`), keeps "which section is this" the only thing you need to know
to find one, rather than also having to remember which ones needed the workaround.

A related, narrower rule for `parameters_section.py`: it builds on
`render_param_widget`/`EnumPopupRequest` from `knx_gui.widgets.parameter_widgets`,
which stay in `knx_gui.widgets` rather than moving here too, because the Node
Editor's own per-node enum popup (`knx_gui.plugins.node_editor.ui.EnumPopup`) also
needs them - moving them here would make `knx_gui.widgets` (and, transitively, the
Node Editor) depend on this package, recreating the same hazard from the other
direction.
"""

from knx_gui.plugins.project.ui.components.com_flags_section import ComFlagsTable
from knx_gui.plugins.project.ui.components.load_procedures_section import (
    LoadProceduresSection,
)
from knx_gui.plugins.project.ui.components.metadata_section import MetadataSection
from knx_gui.plugins.project.ui.components.parameters_section import (
    count_parameters,
    render_ui_tree,
)
from knx_gui.plugins.project.ui.components.program_section import (
    ProgramRequest,
    ProgramSection,
)
from knx_gui.plugins.project.ui.components.restart_section import (
    RestartRequest,
    RestartSection,
)

__all__ = [
    "ComFlagsTable",
    "LoadProceduresSection",
    "MetadataSection",
    "ProgramRequest",
    "ProgramSection",
    "RestartRequest",
    "RestartSection",
    "count_parameters",
    "render_ui_tree",
]
