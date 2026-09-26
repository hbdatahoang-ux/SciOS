"""Contract tests for the perception.core public API."""

from __future__ import annotations

from scios.cognitive_core import perception
from scios.cognitive_core.perception import core


EXPECTED_EXPORTS = {
    "BasePerceptor",
    "Embedding",
    "Entities",
    "Entity",
    "Features",
    "Metadata",
    "Modality",
    "PerceptionConfigurationError",
    "PerceptionContext",
    "PerceptionError",
    "PerceptionInputError",
    "PerceptionProcessingError",
    "PerceptionResult",
    "PerceptionStatus",
    "PerceptionValidationError",
    "RawInput",
    "Relation",
    "Relations",
}


def test_core_all_is_exact() -> None:
    assert set(core.__all__) == EXPECTED_EXPORTS
    assert len(core.__all__) == len(EXPECTED_EXPORTS)


def test_all_exports_are_available() -> None:
    for name in core.__all__:
        assert hasattr(core, name)


def test_core_exports_are_not_empty() -> None:
    assert core.__all__


def test_core_package_is_importable() -> None:
    assert perception is not None
    assert core is not None
