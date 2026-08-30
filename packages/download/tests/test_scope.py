"""Tests for download scope filtering (by target loadable part)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from xknxmono.download.scope import DownloadScope, control_in_scope


def _ctrl(**attrs: int) -> object:
    return SimpleNamespace(**attrs)


@pytest.mark.parametrize(
    ("control", "scope", "expected"),
    [
        # framing controls (no target object) always run
        (_ctrl(), DownloadScope.PARAMETERS, True),
        (_ctrl(), DownloadScope.GROUP_COMMUNICATION, True),
        # device object (0) is framing (fingerprint compare) -> always
        (_ctrl(obj_idx=0), DownloadScope.PARAMETERS, True),
        (_ctrl(obj_idx=0), DownloadScope.GROUP_COMMUNICATION, True),
        # group communication objects: address(1), association(2), group object(9)
        (_ctrl(obj_type=1), DownloadScope.GROUP_COMMUNICATION, True),
        (_ctrl(obj_type=2), DownloadScope.GROUP_COMMUNICATION, True),
        (_ctrl(lsm_idx=9), DownloadScope.GROUP_COMMUNICATION, True),
        (_ctrl(obj_type=1), DownloadScope.PARAMETERS, False),
        # application program object (3) holds parameters
        (_ctrl(obj_type=3), DownloadScope.PARAMETERS, True),
        (_ctrl(lsm_idx=3), DownloadScope.PARAMETERS, True),
        (_ctrl(obj_type=3), DownloadScope.GROUP_COMMUNICATION, False),
        # full download runs everything
        (_ctrl(obj_type=1), DownloadScope.FULL, True),
        (_ctrl(obj_type=3), DownloadScope.FULL, True),
    ],
)
def test_control_in_scope(
    control: object, scope: DownloadScope, expected: bool
) -> None:
    assert control_in_scope(control, scope) is expected
