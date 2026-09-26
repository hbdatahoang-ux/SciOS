import pytest

from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver


def test_resolver_resolves_registered_operation():
    registry = OperationRegistry()

    def analyze():
        return "ok"

    ref = OperationRef(
        name="data.analyze",
        version="1.0",
    )

    registry.register(ref, analyze)

    resolver = OperationResolver(registry)

    resolved = resolver.resolve(ref)

    assert resolved is analyze


def test_resolver_does_not_execute_operation():
    registry = OperationRegistry()
    calls = []

    def analyze():
        calls.append("executed")
        return "ok"

    ref = OperationRef(
        name="data.analyze",
        version="1.0",
    )

    registry.register(ref, analyze)

    resolver = OperationResolver(registry)

    resolved = resolver.resolve(ref)

    assert resolved is analyze
    assert calls == []


def test_resolver_fails_for_missing_operation():
    registry = OperationRegistry()
    resolver = OperationResolver(registry)

    ref = OperationRef(
        name="data.missing",
        version="1.0",
    )

    with pytest.raises(KeyError, match="Operation not found"):
        resolver.resolve(ref)


def test_resolver_exists_delegates_to_registry():
    registry = OperationRegistry()

    ref = OperationRef(
        name="data.analyze",
        version="1.0",
    )

    registry.register(ref, lambda: "ok")

    resolver = OperationResolver(registry)

    assert resolver.exists(ref) is True
    assert resolver.exists(
        OperationRef(name="data.missing", version="1.0")
    ) is False
