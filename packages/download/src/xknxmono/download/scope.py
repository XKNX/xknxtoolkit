"""Download scope: full download versus a partial parameter/group download.

A partial download runs only the Load Controls that target a given category of
loadable part (KNX Standard v3.0.0, Chapter 3/5/3 "Configuration Procedures",
section 3.5.3 "Load procedure for partial download"), classifying a control by
the interface object it addresses:

- the Address Table, Association Table and Group Object Table objects hold the
  group communication;
- the Application Program object holds the parameters;
- the Device Object and connection/restart controls are framing and always run.

The applies_to marker (``LdCtrlProcType``) is uniform on many products, so the
object a control targets - not applies_to - is what distinguishes a partial
parameter download from a partial group communication download.
"""

from __future__ import annotations

from enum import Enum

# Interface object types (and their conventional indices) that hold group
# communication: address table (1), association table (2), group object
# table (9), group object responder table (also object type 9).
_GROUP_COMMUNICATION_OBJECTS = frozenset({1, 2, 9})
# The device object is framing (fingerprint compare) and always runs.
_DEVICE_OBJECT = 0


class DownloadScope(Enum):
    """Which part of a Load Procedure to execute."""

    FULL = "full"
    PARAMETERS = "par"
    GROUP_COMMUNICATION = "grp"


def control_in_scope(control: object, scope: DownloadScope) -> bool:
    """Return whether a control runs in ``scope``.

    Controls that do not target a loadable part (Connect/Disconnect/Restart/
    Delay and Device Object compares) are framing and always run. Targeted
    controls run only when the object they address belongs to the requested
    category; a full download runs everything.
    """
    if scope is DownloadScope.FULL:
        return True
    target = _target_object(control)
    if target is None or target == _DEVICE_OBJECT:
        return True
    is_group_communication = target in _GROUP_COMMUNICATION_OBJECTS
    if scope is DownloadScope.GROUP_COMMUNICATION:
        return is_group_communication
    return not is_group_communication


def _target_object(control: object) -> int | None:
    """The interface object type/index a control addresses, or None if framing."""
    obj_type = getattr(control, "obj_type", None)
    if obj_type is not None:
        return obj_type
    lsm_idx = getattr(control, "lsm_idx", None)
    if lsm_idx is not None:
        return lsm_idx
    obj_idx = getattr(control, "obj_idx", None)
    return obj_idx
