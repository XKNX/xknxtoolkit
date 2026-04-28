def test_import():
    from xknx.keys import __version__

    assert __version__ is not None


def test_models_dependency():
    from xknx.models import __version__

    assert __version__ is not None
