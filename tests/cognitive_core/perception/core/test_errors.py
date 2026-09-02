"""Contract tests for SciOS Cognitive Core Perception errors."""

from __future__ import annotations

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionConfigurationError,
    PerceptionError,
    PerceptionInputError,
    PerceptionProcessingError,
    PerceptionValidationError,
)


class TestPerceptionError:
    """Tests for the base perception exception."""

    def test_inherits_from_exception(self) -> None:
        assert issubclass(PerceptionError, Exception)

    def test_can_be_raised(self) -> None:
        with pytest.raises(PerceptionError):
            raise PerceptionError("perception failed")

    def test_message_is_preserved(self) -> None:
        error = PerceptionError("test error")
        assert str(error) == "test error"


class TestPerceptionInputError:
    """Tests for invalid-input errors."""

    def test_inherits_from_perception_error(self) -> None:
        assert issubclass(PerceptionInputError, PerceptionError)

    def test_can_be_raised(self) -> None:
        with pytest.raises(PerceptionInputError):
            raise PerceptionInputError("invalid input")


class TestPerceptionConfigurationError:
    """Tests for configuration errors."""

    def test_inherits_from_perception_error(self) -> None:
        assert issubclass(PerceptionConfigurationError, PerceptionError)

    def test_can_be_raised(self) -> None:
        with pytest.raises(PerceptionConfigurationError):
            raise PerceptionConfigurationError("invalid configuration")


class TestPerceptionProcessingError:
    """Tests for processing errors."""

    def test_inherits_from_perception_error(self) -> None:
        assert issubclass(PerceptionProcessingError, PerceptionError)

    def test_can_be_raised(self) -> None:
        with pytest.raises(PerceptionProcessingError):
            raise PerceptionProcessingError("processing failed")


class TestPerceptionValidationError:
    """Tests for validation errors."""

    def test_inherits_from_perception_error(self) -> None:
        assert issubclass(PerceptionValidationError, PerceptionError)

    def test_can_be_raised(self) -> None:
        with pytest.raises(PerceptionValidationError):
            raise PerceptionValidationError("validation failed")


class TestErrorHierarchy:
    """Tests for the complete exception hierarchy."""

    def test_all_specialized_errors_are_perception_errors(self) -> None:
        errors = (
            PerceptionConfigurationError,
            PerceptionInputError,
            PerceptionProcessingError,
            PerceptionValidationError,
        )

        for error_type in errors:
            assert issubclass(error_type, PerceptionError)

    def test_all_errors_are_exception_types(self) -> None:
        errors = (
            PerceptionError,
            PerceptionConfigurationError,
            PerceptionInputError,
            PerceptionProcessingError,
            PerceptionValidationError,
        )

        for error_type in errors:
            assert issubclass(error_type, Exception)


class TestPublicExports:
    """Tests for the explicit public API."""

    def test_all_is_exact(self) -> None:
        from scios.cognitive_core.perception.core import errors

        assert errors.__all__ == [
            "PerceptionConfigurationError",
            "PerceptionError",
            "PerceptionInputError",
            "PerceptionProcessingError",
            "PerceptionValidationError",
        ]

    def test_all_exports_are_available(self) -> None:
        from scios.cognitive_core.perception.core import errors

        for name in errors.__all__:
            assert hasattr(errors, name)
