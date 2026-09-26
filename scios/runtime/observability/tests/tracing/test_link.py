"""
SciOS Runtime Observability
===========================

Tests for tracing.link.Link

Coverage
--------
- Creation
- Attributes
- Serialization
- Snapshot / Restore
- Clone / Copy
- Diagnostics
- Python protocols
"""

from __future__ import annotations

import copy

import pytest

from scios.runtime.observability.tracing.link import (
    Link,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def link() -> Link:
    return Link(
        trace_id="trace-001",
        span_id="span-001",
    )


# ============================================================
# Creation
# ============================================================

def test_link_creation(link):

    assert link.trace_id == "trace-001"

    assert link.span_id == "span-001"


def test_link_description():

    obj = Link(
        trace_id="t",
        span_id="s",
        description="parent",
    )

    assert obj.description == "parent"


# ============================================================
# Attributes
# ============================================================

def test_set_attribute(link):

    link.set_attribute(
        "service",
        "runtime",
    )

    assert (
        link.get_attribute("service")
        ==
        "runtime"
    )


def test_remove_attribute(link):

    link.set_attribute(
        "temp",
        True,
    )

    link.remove_attribute(
        "temp",
    )

    assert (
        link.get_attribute("temp")
        is None
    )


def test_clear_attributes(link):

    link.set_attribute(
        "a",
        1,
    )

    link.set_attribute(
        "b",
        2,
    )

    link.clear_attributes()

    assert (
        len(link.attributes)
        ==
        0
    )


# ============================================================
# Serialization
# ============================================================

def test_to_dict(link):

    data = link.to_dict()

    assert data["trace_id"] == "trace-001"

    assert data["span_id"] == "span-001"


def test_from_dict(link):

    restored = Link.from_dict(
        link.to_dict()
    )

    assert (
        restored.trace_id
        ==
        link.trace_id
    )

    assert (
        restored.span_id
        ==
        link.span_id
    )


# ============================================================
# Snapshot / Restore
# ============================================================

def test_snapshot(link):

    snapshot = link.snapshot()

    assert snapshot["trace_id"] == "trace-001"


def test_restore(link):

    restored = Link.restore(
        link.snapshot()
    )

    assert restored == link


# ============================================================
# Clone / Copy
# ============================================================

def test_clone(link):

    clone = link.clone()

    assert clone == link

    assert clone is not link


def test_copy(link):

    cloned = link.copy()

    assert cloned == link

    assert cloned is not link


def test_python_copy(link):

    cloned = copy.copy(
        link
    )

    assert cloned == link


def test_python_deepcopy(link):

    cloned = copy.deepcopy(
        link
    )

    assert cloned == link


# ============================================================
# Diagnostics
# ============================================================

def test_validate(link):

    assert (
        link.validate()
        is True
    )


def test_summary(link):

    result = link.summary()

    assert isinstance(
        result,
        dict,
    )


def test_diagnostics(link):

    result = link.diagnostics()

    assert (
        result["valid"]
        is True
    )


# ============================================================
# Python Protocols
# ============================================================

def test_repr(link):

    assert (
        "Link"
        in repr(link)
    )


def test_str(link):

    assert isinstance(
        str(link),
        str,
    )


def test_len(link):

    link.set_attribute(
        "a",
        1,
    )

    assert len(link) == 1


def test_contains(link):

    link.set_attribute(
        "k",
        "v",
    )

    assert "k" in link


def test_getitem(link):

    link["mode"] = "test"

    assert (
        link["mode"]
        ==
        "test"
    )


def test_setitem(link):

    link["enabled"] = True

    assert (
        link["enabled"]
        is True
    )


def test_hash(link):

    assert isinstance(
        hash(link),
        int,
    )


def test_equality():

    first = Link(
        trace_id="t1",
        span_id="s1",
    )

    second = Link(
        trace_id="t1",
        span_id="s1",
    )

    assert first == second