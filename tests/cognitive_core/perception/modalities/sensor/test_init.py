"""Contract tests for the sensor modality package boundary."""


def test_sensor_package_imports() -> None:
    import scios.cognitive_core.perception.modalities.sensor as sensor

    assert sensor is not None


def test_public_exports_are_deferred() -> None:
    from scios.cognitive_core.perception.modalities.sensor import (
        __all__,
    )

    assert __all__ == []
