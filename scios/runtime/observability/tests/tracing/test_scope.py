"""
SciOS Runtime Observability
===========================

Tracing Test - Scope

Tests:

- BaseScope
- TraceScope
- SpanScope
- Context manager behavior
- Decorator behavior
- Lifecycle state
- Attributes
- Nested scopes
- Exception propagation
- Functional API
- Diagnostics
- Python protocols

Python 3.11+
"""

from __future__ import annotations


import pytest


from scios.runtime.observability.tracing.manager import (
    TraceManager,
)

from scios.runtime.observability.tracing.scope import (
    BaseScope,
    TraceScope,
    SpanScope,
    trace_scope,
    span_scope,
    ScopeError,
    ScopeValidationError,
    ScopeStateError,
    ScopeClosedError,
    ScopeEnterError,
    ScopeExitError,
    TraceScopeError,
    SpanScopeError,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def manager() -> TraceManager:
    """
    TraceManager fixture.
    """

    return TraceManager()


@pytest.fixture
def trace_scope_instance(
    manager,
) -> TraceScope:
    """
    TraceScope fixture.
    """

    return TraceScope(
        manager,
        "test-trace",
    )


@pytest.fixture
def span_scope_instance(
    manager,
) -> SpanScope:
    """
    SpanScope fixture.
    """

    return SpanScope(
        manager,
        "test-span",
    )


# ============================================================
# Creation
# ============================================================


def test_base_scope_creation(
    manager,
):

    scope = BaseScope(
        manager,
        "base",
    )

    assert scope is not None


def test_trace_scope_creation(
    trace_scope_instance,
):

    assert trace_scope_instance is not None

    assert isinstance(
        trace_scope_instance,
        TraceScope,
    )


def test_span_scope_creation(
    span_scope_instance,
):

    assert span_scope_instance is not None

    assert isinstance(
        span_scope_instance,
        SpanScope,
    )


# ============================================================
# Validation
# ============================================================


def test_invalid_manager():

    with pytest.raises(
        ScopeValidationError,
    ):

        BaseScope(
            object(),
            "scope",
        )


def test_invalid_name_empty(
    manager,
):

    with pytest.raises(
        ScopeValidationError,
    ):

        BaseScope(
            manager,
            "",
        )


def test_invalid_name_whitespace(
    manager,
):

    with pytest.raises(
        ScopeValidationError,
    ):

        BaseScope(
            manager,
            "   ",
        )


def test_name_is_normalized(
    manager,
):

    scope = BaseScope(
        manager,
        "  runtime  ",
    )

    assert scope.name == "runtime"


# ============================================================
# Properties
# ============================================================


def test_manager_property(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    assert (
        scope.manager
        is
        manager
    )


def test_name_property(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    assert (
        scope.name
        ==
        "scope"
    )


def test_attributes_property(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
        service="scios",
        version="0.3",
    )

    attrs = scope.attributes

    assert (
        attrs["service"]
        ==
        "scios"
    )

    assert (
        attrs["version"]
        ==
        "0.3"
    )


def test_attributes_property_returns_copy(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
        service="scios",
    )

    attrs = scope.attributes

    attrs["service"] = "changed"

    assert (
        scope.attributes["service"]
        ==
        "scios"
    )


def test_runtime_object_initially_none(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    assert (
        scope.runtime_object
        is None
    )


def test_initial_scope_inactive(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    assert (
        scope.active
        is False
    )


# ============================================================
# Internal Lifecycle
# ============================================================


def test_set_runtime_object(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    obj = object()

    result = scope._set_runtime_object(
        obj
    )

    assert (
        result
        is
        obj
    )

    assert (
        scope.runtime_object
        is
        obj
    )

    assert (
        scope.active
        is True
    )


def test_clear_runtime_object(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    obj = object()

    scope._set_runtime_object(
        obj
    )

    scope._clear_runtime_object()

    assert (
        scope.runtime_object
        is None
    )

    assert (
        scope.active
        is False
    )


def test_ensure_entered_fails_before_enter(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    with pytest.raises(
        ScopeStateError,
    ):

        scope._ensure_entered()


def test_ensure_open_succeeds_when_open(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    scope._ensure_open()


def test_ensure_open_fails_after_close(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    scope._set_runtime_object(
        object()
    )

    scope._clear_runtime_object()

    with pytest.raises(
        ScopeClosedError,
    ):

        scope._ensure_open()


# ============================================================
# BaseScope Diagnostics
# ============================================================


def test_summary_initial(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
        service="scios",
    )

    result = scope.summary()

    assert isinstance(
        result,
        dict,
    )

    assert (
        result["scope"]
        ==
        "BaseScope"
    )

    assert (
        result["name"]
        ==
        "scope"
    )

    assert (
        result["active"]
        is False
    )

    assert (
        result["closed"]
        is False
    )

    assert (
        result["runtime_object"]
        is False
    )

    assert (
        result["attribute_count"]
        ==
        1
    )


def test_health(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    assert (
        scope.health()
        is True
    )


def test_bool(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    assert bool(scope) is True


# ============================================================
# Python Protocols
# ============================================================


def test_repr(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    result = repr(scope)

    assert isinstance(
        result,
        str,
    )

    assert (
        "BaseScope"
        in result
    )

    assert (
        "scope"
        in result
    )


def test_str(
    manager,
):

    scope = BaseScope(
        manager,
        "scope",
    )

    result = str(scope)

    assert isinstance(
        result,
        str,
    )

    assert (
        "BaseScope"
        in result
    )


# ============================================================
# TraceScope Functional API
# ============================================================


def test_trace_scope_factory(
    manager,
):

    scope = trace_scope(
        manager,
        "factory-trace",
    )

    assert isinstance(
        scope,
        TraceScope,
    )

    assert (
        scope.name
        ==
        "factory-trace"
    )


def test_trace_scope_factory_attributes(
    manager,
):

    scope = trace_scope(
        manager,
        "factory-trace",
        service="scios",
        version="0.3",
    )

    assert (
        scope.attributes["service"]
        ==
        "scios"
    )

    assert (
        scope.attributes["version"]
        ==
        "0.3"
    )


# ============================================================
# SpanScope Functional API
# ============================================================


def test_span_scope_factory(
    manager,
):

    scope = span_scope(
        manager,
        "factory-span",
    )

    assert isinstance(
        scope,
        SpanScope,
    )

    assert (
        scope.name
        ==
        "factory-span"
    )


def test_span_scope_factory_attributes(
    manager,
):

    scope = span_scope(
        manager,
        "factory-span",
        service="scios",
    )

    assert (
        scope.attributes["service"]
        ==
        "scios"
    )


# ============================================================
# TraceScope Context Manager
# ============================================================


def test_trace_scope_enter_exit(
    manager,
):

    scope = TraceScope(
        manager,
        "runtime-trace",
    )

    with scope as trace:

        assert trace is not None

        assert (
            scope.runtime_object
            is
            trace
        )

        assert (
            scope.active
            is True
        )

    assert (
        scope.runtime_object
        is None
    )

    assert (
        scope.active
        is False
    )


def test_trace_scope_name(
    manager,
):

    with TraceScope(
        manager,
        "named-trace",
    ) as trace:

        assert (
            trace.name
            ==
            "named-trace"
        )


def test_trace_scope_attributes(
    manager,
):

    with TraceScope(
        manager,
        "attribute-trace",
        service="scios",
        version="0.3",
    ) as trace:

        assert (
            trace.attributes.get(
                "service"
            )
            ==
            "scios"
        )

        assert (
            trace.attributes.get(
                "version"
            )
            ==
            "0.3"
        )


def test_trace_scope_exception_propagates(
    manager,
):

    scope = TraceScope(
        manager,
        "exception-trace",
    )

    with pytest.raises(
        RuntimeError,
    ):

        with scope:

            raise RuntimeError(
                "boom"
            )

    assert (
        scope.active
        is False
    )


def test_trace_scope_double_enter(
    manager,
):

    scope = TraceScope(
        manager,
        "double-enter",
    )

    with scope:

        with pytest.raises(
            ScopeStateError,
        ):

            scope.__enter__()


# ============================================================
# SpanScope Context Manager
# ============================================================


def test_span_scope_enter_exit(
    manager,
):

    manager.start_trace(
        "runtime-trace",
    )

    scope = SpanScope(
        manager,
        "runtime-span",
    )

    with scope as span:

        assert span is not None

        assert (
            scope.runtime_object
            is
            span
        )

        assert (
            scope.active
            is True
        )

    assert (
        scope.runtime_object
        is None
    )

    assert (
        scope.active
        is False
    )

def test_span_scope_creates_implicit_trace(
    manager,
):

    assert getattr(
        manager,
        "_current_trace",
        None,
    ) is None

    with SpanScope(
        manager,
        "implicit-span",
    ) as span:

        assert span is not None

        assert getattr(
            manager,
            "_current_trace",
            None,
        ) is not None

    assert getattr(
        manager,
        "_current_trace",
        None,
    ) is None

def test_span_scope_name(
    manager,
):

    with SpanScope(
        manager,
        "named-span",
    ) as span:

        assert (
            span.name
            ==
            "named-span"
        )


def test_span_scope_attributes(
    manager,
):

    with SpanScope(
        manager,
        "attribute-span",
        service="scios",
        version="0.3",
    ) as span:

        assert (
            span.attributes.get(
                "service"
            )
            ==
            "scios"
        )

        assert (
            span.attributes.get(
                "version"
            )
            ==
            "0.3"
        )


def test_span_scope_exception_propagates(
    manager,
):

    scope = SpanScope(
        manager,
        "exception-span",
    )

    with pytest.raises(
        RuntimeError,
    ):

        with scope:

            raise RuntimeError(
                "boom"
            )

    assert (
        scope.active
        is False
    )


def test_span_scope_double_enter(
    manager,
):

    scope = SpanScope(
        manager,
        "double-enter",
    )

    with scope:

        with pytest.raises(
            ScopeStateError,
        ):

            scope.__enter__()

def test_span_scope_preserves_parent_trace(
    manager,
):

    with TraceScope(
        manager,
        "parent",
    ) as trace:

        with SpanScope(
            manager,
            "child",
        ):
            pass

        current_trace = getattr(
            manager,
            "_current_trace",
            None,
        )

        assert current_trace is trace

# ============================================================
# Nested Scopes
# ============================================================


def test_nested_trace_and_span_scopes(
    manager,
):

    with TraceScope(
        manager,
        "parent-trace",
    ) as trace:

        assert trace is not None

        with SpanScope(
            manager,
            "child-span",
        ) as span:

            assert span is not None

            assert (
                span.name
                ==
                "child-span"
            )

        assert (
            manager.current_trace
            is
            trace
        )


# ============================================================
# TraceScope Decorator
# ============================================================


def test_trace_scope_decorator(
    manager,
):

    scope = TraceScope(
        manager,
        "decorated-trace",
    )

    @scope
    def function(
        value,
    ):

        return value * 2

    result = function(
        21
    )

    assert (
        result
        ==
        42
    )


def test_trace_scope_decorator_preserves_name(
    manager,
):

    scope = TraceScope(
        manager,
        "decorated-trace",
    )

    @scope
    def calculate(
        value,
    ):

        return value

    assert (
        calculate.__name__
        ==
        "calculate"
    )


def test_trace_scope_decorator_exception(
    manager,
):

    scope = TraceScope(
        manager,
        "decorated-trace",
    )

    @scope
    def failing():

        raise ValueError(
            "failure"
        )

    with pytest.raises(
        ValueError,
    ):

        failing()


# ============================================================
# SpanScope Decorator
# ============================================================


def test_span_scope_decorator(
    manager,
):

    scope = SpanScope(
        manager,
        "decorated-span",
    )

    @scope
    def function(
        value,
    ):

        return value + 1

    result = function(
        41
    )

    assert (
        result
        ==
        42
    )


def test_span_scope_decorator_preserves_name(
    manager,
):

    scope = SpanScope(
        manager,
        "decorated-span",
    )

    @scope
    def calculate(
        value,
    ):

        return value

    assert (
        calculate.__name__
        ==
        "calculate"
    )


def test_span_scope_decorator_exception(
    manager,
):

    scope = SpanScope(
        manager,
        "decorated-span",
    )

    @scope
    def failing():

        raise ValueError(
            "failure"
        )

    with pytest.raises(
        ValueError,
    ):

        failing()


# ============================================================
# Lifecycle State
# ============================================================


def test_trace_scope_closed_after_exit(
    manager,
):

    scope = TraceScope(
        manager,
        "closed-trace",
    )

    with scope:

        assert (
            scope.active
            is True
        )

    assert (
        scope.active
        is False
    )

    assert (
        scope.runtime_object
        is None
    )


def test_span_scope_closed_after_exit(
    manager,
):

    scope = SpanScope(
        manager,
        "closed-span",
    )

    with scope:

        assert (
            scope.active
            is True
        )

    assert (
        scope.active
        is False
    )

    assert (
        scope.runtime_object
        is None
    )


# ============================================================
# Exceptions / Public Classes
# ============================================================


def test_scope_exceptions_exist():

    assert issubclass(
        ScopeValidationError,
        ScopeError,
    )

    assert issubclass(
        ScopeStateError,
        ScopeError,
    )

    assert issubclass(
        ScopeClosedError,
        ScopeStateError,
    )

    assert issubclass(
        ScopeEnterError,
        ScopeStateError,
    )

    assert issubclass(
        ScopeExitError,
        ScopeStateError,
    )

    assert issubclass(
        TraceScopeError,
        ScopeError,
    )

    assert issubclass(
        SpanScopeError,
        ScopeError,
    )