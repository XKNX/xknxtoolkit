import re


def test_import():
    from xknx.project import __version__

    assert __version__ is not None


def test_models_dependency():
    from xknx.models import __version__

    assert __version__ is not None
