import re


def test_import():
    from xknx.models import __version__

    assert __version__ is not None


def test_version_format():
    from xknx.models import __version__

    assert re.match(r"^\d+\.\d+\.\d+", __version__)
