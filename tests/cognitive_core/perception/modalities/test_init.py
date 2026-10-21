"""Contract tests for the perception modalities package boundary."""


def test_modalities_package_imports() -> None:
    import scios.cognitive_core.perception.modalities as modalities

    assert modalities is not None


def test_public_exports_are_deferred() -> None:
    from scios.cognitive_core.perception.modalities import __all__

    assert __all__ == []
