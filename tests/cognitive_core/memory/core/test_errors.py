from scios.cognitive_core.memory.core.errors import (
    MemoryCapacityError,
    MemoryError,
    MemoryNotFoundError,
    MemorySerializationError,
    MemoryValidationError,
)


def test_memory_error_inherits_from_exception() -> None:
    assert issubclass(MemoryError, Exception)


def test_memory_validation_error_inherits_from_memory_error() -> None:
    assert issubclass(MemoryValidationError, MemoryError)


def test_memory_not_found_error_inherits_from_memory_error() -> None:
    assert issubclass(MemoryNotFoundError, MemoryError)


def test_memory_capacity_error_inherits_from_memory_error() -> None:
    assert issubclass(MemoryCapacityError, MemoryError)


def test_memory_serialization_error_inherits_from_memory_error() -> None:
    assert issubclass(MemorySerializationError, MemoryError)


def test_memory_error_hierarchy() -> None:
    errors = (
        MemoryValidationError,
        MemoryNotFoundError,
        MemoryCapacityError,
        MemorySerializationError,
    )

    for error_type in errors:
        assert issubclass(error_type, MemoryError)
        assert issubclass(error_type, Exception)


def test_memory_errors_are_distinct_types() -> None:
    errors = {
        MemoryValidationError,
        MemoryNotFoundError,
        MemoryCapacityError,
        MemorySerializationError,
    }

    assert len(errors) == 4