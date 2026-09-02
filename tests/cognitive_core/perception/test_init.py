"""Contract tests for the finalized perception package API."""


def test_perception_root_exports_core_contracts() -> None:
    import scios.cognitive_core.perception as perception

    assert perception.BasePerceptor is not None
    assert perception.PerceptionContext is not None
    assert perception.PerceptionResult is not None
    assert perception.Modality is not None
    assert perception.PerceptionStatus is not None


def test_perception_root_exports_orchestration_contracts() -> None:
    import scios.cognitive_core.perception as perception

    assert perception.PerceptionEngine is not None
    assert perception.PerceptionPipeline is not None


def test_perception_root_exports_registry_and_factory() -> None:
    import scios.cognitive_core.perception as perception

    assert perception.PerceptorRegistry is not None
    assert perception.PerceptorFactory is not None


def test_perception_root_all_is_explicit() -> None:
    from scios.cognitive_core.perception import __all__

    assert __all__ == [
        "BasePerceptor",
        "Modality",
        "PerceptionContext",
        "PerceptionEngine",
        "PerceptionPipeline",
        "PerceptionResult",
        "PerceptionStatus",
        "PerceptorFactory",
        "PerceptorRegistry",
    ]


def test_perception_root_does_not_flatten_modalities() -> None:
    import scios.cognitive_core.perception as perception

    assert not hasattr(perception, "TextPerceptor")
    assert not hasattr(perception, "ImagePerceptor")
    assert not hasattr(perception, "AudioPerceptor")
    assert not hasattr(perception, "VideoPerceptor")
    assert not hasattr(perception, "DocumentPerceptor")
    assert not hasattr(perception, "IoTSensor")
    assert not hasattr(perception, "RosSensor")
    assert not hasattr(perception, "SimulatorSensor")
