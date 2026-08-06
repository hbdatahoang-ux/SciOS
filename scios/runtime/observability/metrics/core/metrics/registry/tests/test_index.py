"""
MetricIndex Tests
=================

Tests for MetricIndex registry index object.
"""

from __future__ import annotations

import pytest

from ..index import MetricIndex
from ..key import MetricKey
from ..filter import MetricFilter


# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    index = MetricIndex()

    assert isinstance(index, MetricIndex)


def test_custom_constructor():

    index = MetricIndex(
        name="cpu",
        namespace="system",
    )

    assert index.name == "cpu"
    assert index.namespace == "system"


def test_slots():

    assert hasattr(MetricIndex, "__slots__")


def test_annotations():

    assert hasattr(MetricIndex, "__annotations__")


def test_signature():

    index = MetricIndex()

    assert index is not None


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property():

    index = MetricIndex("cpu")

    assert index.name == "cpu"


def test_namespace_property():

    index = MetricIndex(
        "cpu",
        "system",
    )

    assert index.namespace == "system"


def test_key_property():

    index = MetricIndex(
        "cpu",
        "system",
    )

    assert isinstance(index.key, MetricKey)


def test_filters_property():

    index = MetricIndex()

    assert isinstance(index.filters, list)


def test_size_property():

    index = MetricIndex()

    assert index.size == 0


def test_state_property():

    index = MetricIndex()

    assert isinstance(index.state, dict)


# ==============================================================================
# Part 3. Operations
# ==============================================================================


def test_add():

    index = MetricIndex()

    key = MetricKey("cpu")

    index.add(key)

    assert index.size == 1


def test_remove():

    index = MetricIndex()

    key = MetricKey("cpu")

    index.add(key)

    index.remove(key)

    assert index.size == 0


def test_get():

    index = MetricIndex()

    key = MetricKey("cpu")

    index.add(key)

    result = index.get(key)

    assert result == key


def test_contains():

    index = MetricIndex()

    key = MetricKey("cpu")

    index.add(key)

    assert index.contains(key)


def test_clear():

    index = MetricIndex()

    index.add(
        MetricKey("cpu")
    )

    index.clear()

    assert index.size == 0


def test_normalize():

    index = MetricIndex(
        " CPU ",
        " SYSTEM ",
    )

    index.normalize()

    assert index.name == "cpu"
    assert index.namespace == "system"


# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_to_dict():

    index = MetricIndex(
        "cpu",
        "system",
    )

    data = index.to_dict()

    assert isinstance(data, dict)

    assert data["name"] == "cpu"


def test_from_dict():

    data = {
        "name": "cpu",
        "namespace": "system",
        "filters": [],
        "state": {},
    }

    index = MetricIndex.from_dict(data)

    assert index.name == "cpu"


def test_to_tuple():

    index = MetricIndex("cpu")

    value = index.to_tuple()

    assert isinstance(value, tuple)


def test_from_tuple():

    index = MetricIndex("cpu")

    restored = MetricIndex.from_tuple(
        index.to_tuple()
    )

    assert restored == index


def test_snapshot():

    index = MetricIndex("cpu")

    snap = index.snapshot()

    assert isinstance(snap, dict)


def test_restore():

    index = MetricIndex()

    index.restore(
        {
            "name": "memory",
            "namespace": "runtime",
            "filters": [],
            "state": {},
        }
    )

    assert index.name == "memory"


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_name():

    assert MetricIndex.validate_name("cpu")

    assert not MetricIndex.validate_name(123)


def test_validate_namespace():

    assert MetricIndex.validate_namespace(
        "system"
    )

    assert not MetricIndex.validate_namespace(
        123
    )


def test_validate_key():

    assert MetricIndex.validate_key(
        MetricKey("cpu")
    )

    assert not MetricIndex.validate_key(
        "cpu"
    )


def test_validate_filters():

    assert MetricIndex.validate_filters([])

    assert MetricIndex.validate_filters(
        [
            MetricFilter()
        ]
    )


def test_validate_index():

    index = MetricIndex("cpu")

    assert MetricIndex.validate_index(index)

    assert not MetricIndex.validate_index(
        None
    )


def test_validate():

    index = MetricIndex("cpu")

    assert index.validate()

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_name(name: Any) -> bool:
        """
        Validate index name.
        """
        return isinstance(name, str) and bool(name.strip())


    @staticmethod
    def validate_namespace(namespace: Any) -> bool:
        """
        Validate namespace.
        """
        return (
            namespace is None
            or isinstance(namespace, str)
        )


    @staticmethod
    def validate_key(key: Any) -> bool:
        """
        Validate metric key.
        """
        return isinstance(key, MetricKey)


    @staticmethod
    def validate_filters(filters: Any) -> bool:
        """
        Validate filters collection.
        """
        if filters is None:
            return True

        if not isinstance(filters, dict):
            return False

        return all(
            isinstance(k, str)
            for k in filters.keys()
        )


    @classmethod
    def validate_index(cls, index: Any) -> bool:
        """
        Validate MetricIndex instance.
        """
        return (
            isinstance(index, cls)
            and cls.validate_name(index.name)
            and cls.validate_namespace(index.namespace)
            and cls.validate_key(index.key)
            and cls.validate_filters(index.filters)
        )


    def validate(self) -> bool:
        """
        Validate current instance.
        """
        self._validate()
        return self.validate_index(self)



# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricIndex":
        """
        Deep clone.
        """

        return MetricIndex(
            name=self.name,
            namespace=self.namespace,
            key=self.key.clone(),
            filters=dict(self.filters),
            state=dict(self.state),
        )


    copy = clone


    def merge(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        key: MetricKey | None = None,
        filters: dict | None = None,
        state: dict | None = None,
    ) -> "MetricIndex":
        """
        Return merged copy.
        """

        return MetricIndex(
            name=name if name is not None else self.name,
            namespace=(
                namespace
                if namespace is not None
                else self.namespace
            ),
            key=(
                key.clone()
                if key is not None
                else self.key.clone()
            ),
            filters=(
                dict(filters)
                if filters is not None
                else dict(self.filters)
            ),
            state=(
                dict(state)
                if state is not None
                else dict(self.state)
            ),
        )


    def update(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        key: MetricKey | None = None,
        filters: dict | None = None,
        state: dict | None = None,
    ) -> "MetricIndex":
        """
        Update in-place.
        """

        if name is not None:
            self.name = name

        if namespace is not None:
            self.namespace = namespace

        if key is not None:
            self.key = key

        if filters is not None:
            self.filters = dict(filters)

        if state is not None:
            self.state = dict(state)

        self.normalize()
        self.validate()

        return self


    def clear(self) -> "MetricIndex":
        """
        Clear index.
        """

        self.filters.clear()
        self.state.clear()

        return self



# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __hash__(self) -> int:

        return hash(
            (
                self.name,
                self.namespace,
                self.key,
                tuple(sorted(self.filters.items())),
            )
        )


    def __eq__(self, other: object) -> bool:

        if not isinstance(other, MetricIndex):
            return NotImplemented

        return (
            self.name == other.name
            and self.namespace == other.namespace
            and self.key == other.key
            and self.filters == other.filters
        )


    def __lt__(self, other: object) -> bool:

        if not isinstance(other, MetricIndex):
            return NotImplemented

        return (
            self.fullname
            <
            other.fullname
        )


    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"namespace={self.namespace!r}, "
            f"key={self.key!r}, "
            f"filters={self.filters!r})"
        )


    def __str__(self) -> str:

        return self.fullname


    def __bool__(self) -> bool:

        return bool(self.key)



# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self.name,
            "namespace": self.namespace,
            "fullname": self.fullname,
            "key": self.key,
            "filters": self.filters,
            "size": self.size,
            "state": self.state,
        }


    def diagnostics(self) -> dict[str, Any]:

        return {
            "valid": self.validate(),
            **self.summary(),
        }


    def index_report(self) -> dict[str, Any]:

        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }


    def overall_status(self) -> bool:

        return self.validate()



# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "MetricIndex",
]    