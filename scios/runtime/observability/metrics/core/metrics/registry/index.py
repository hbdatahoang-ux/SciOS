"""
Metric Registry Index
=====================

Index container binding MetricKey and MetricFilter objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias

from .key import MetricKey
from .filter import MetricFilter


__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_NAMESPACE",
    "MetricSnapshot",
    "MetricIndex",
]


# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

DEFAULT_NAME: str = ""

DEFAULT_NAMESPACE: str = ""

MetricSnapshot: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 2. MetricIndex
# ==============================================================================


@dataclass(slots=True)
class MetricIndex:
    """
    Registry index.

    Maintains a collection of MetricKey objects.
    """

    name: str = DEFAULT_NAME

    namespace: str = DEFAULT_NAMESPACE

    key: MetricKey = field(
        default_factory=MetricKey,
    )

    filters: list[MetricKey] = field(
        default_factory=list,
    )

    state: MetricSnapshot = field(
        default_factory=dict,
    )


    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:

        self._normalize()

        self._validate()



    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self) -> None:
        """
        Normalize internal values.
        """


        if isinstance(
            self.name,
            str,
        ):

            self.name = (
                self.name
                .strip()
                .lower()
            )


        if isinstance(
            self.namespace,
            str,
        ):

            self.namespace = (
                self.namespace
                .strip()
                .lower()
            )



        if isinstance(
            self.key,
            MetricKey,
        ):

            self.key.normalize()

        else:

            self.key = MetricKey()



        if not isinstance(
            self.filters,
            list,
        ):

            self.filters = []



        normalized: list[MetricKey] = []



        for item in self.filters:


            if isinstance(
                item,
                MetricKey,
            ):

                item.normalize()

                normalized.append(item)



        self.filters = normalized



        if not isinstance(
            self.state,
            dict,
        ):

            self.state = {}



    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:


        if not isinstance(
            self.name,
            str,
        ):

            raise TypeError(
                "name must be string"
            )


        if not isinstance(
            self.namespace,
            str,
        ):

            raise TypeError(
                "namespace must be string"
            )


        if not isinstance(
            self.key,
            MetricKey,
        ):

            raise TypeError(
                "key must be MetricKey"
            )


        if not isinstance(
            self.filters,
            list,
        ):

            raise TypeError(
                "filters must be list"
            )


        if not all(
            isinstance(
                item,
                MetricKey,
            )
            for item in self.filters
        ):

            raise TypeError(
                "filters must contain MetricKey"
            )


        if not isinstance(
            self.state,
            dict,
        ):

            raise TypeError(
                "state must be dict"
            )



# ==============================================================================
# Part 3. Properties
# ==============================================================================


    @property
    def size(self) -> int:
        """
        Number of indexed keys.
        """

        return len(
            self.filters
        )



# ==============================================================================
# Part 4. Operations
# ==============================================================================


    def add(
        self,
        key: MetricKey,
    ) -> "MetricIndex":
        """
        Add MetricKey.
        """


        if not isinstance(
            key,
            MetricKey,
        ):

            raise TypeError(
                "key must be MetricKey"
            )



        key.normalize()



        if key not in self.filters:

            self.filters.append(
                key
            )



        return self



    def remove(
        self,
        key: MetricKey,
    ) -> "MetricIndex":
        """
        Remove MetricKey.
        """


        if key in self.filters:

            self.filters.remove(
                key
            )


        return self



    def get(
        self,
        key: MetricKey,
    ) -> MetricKey | None:
        """
        Get MetricKey.
        """


        for item in self.filters:


            if item == key:

                return item



        return None



    def contains(
        self,
        key: MetricKey,
    ) -> bool:
        """
        Check MetricKey existence.
        """


        return key in self.filters



    def clear(self) -> "MetricIndex":
        """
        Clear indexed keys.
        """


        self.filters.clear()

        return self



    def normalize(self) -> "MetricIndex":
        """
        Normalize index.
        """


        self._normalize()

        return self



# ==============================================================================
# Part 5. Serialization
# ==============================================================================


    def to_dict(self) -> dict:
        """
        Convert index to dictionary.
        """


        return {

            "name":
                self.name,


            "namespace":
                self.namespace,


            "key":
                (
                    self.key.to_dict()
                    if self.key
                    else None
                ),


            "filters":
                [
                    item.to_dict()
                    for item in self.filters
                ],


            "state":
                dict(
                    self.state
                ),
        }



    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "MetricIndex":
        """
        Restore from dictionary.
        """


        key_data = data.get(
            "key"
        )


        index = cls(

            name=data.get(
                "name",
                "",
            ),


            namespace=data.get(
                "namespace",
                "",
            ),


            key=(
                MetricKey.from_dict(
                    key_data
                )
                if key_data
                else MetricKey()
            ),
        )



        index.filters = [

            MetricKey.from_dict(
                item
            )

            for item in data.get(
                "filters",
                [],
            )

        ]



        index.state = dict(

            data.get(
                "state",
                {},
            )

        )



        index._normalize()

        return index



    def to_tuple(self) -> tuple:
        """
        Convert index to tuple.
        """


        return (

            self.name,

            self.namespace,

            self.key.to_tuple(),

            tuple(

                item.to_tuple()

                for item in self.filters

            ),

            dict(
                self.state
            ),

        )



    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "MetricIndex":
        """
        Restore from tuple.
        """


        (
            name,
            namespace,
            key,
            filters,
            state,

        ) = value



        index = cls(

            name=name,

            namespace=namespace,

            key=MetricKey.from_tuple(
                key
            ),

        )



        index.filters = [

            MetricKey.from_tuple(
                item
            )

            for item in filters

        ]



        index.state = dict(
            state
        )


        index._normalize()

        return index



    def snapshot(self) -> dict:
        """
        Create snapshot.
        """


        return self.to_dict()



    def restore(
        self,
        snapshot: dict,
    ) -> "MetricIndex":
        """
        Restore snapshot.
        """


        restored = self.from_dict(
            snapshot
        )


        self.name = restored.name

        self.namespace = restored.namespace

        self.key = restored.key

        self.filters = restored.filters

        self.state = restored.state


        return self 

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_name(name: Any) -> bool:
        """
        Validate index name.
        """
        return (
            name is None
            or isinstance(name, str)
        )


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
        Validate MetricKey.
        """
        return isinstance(key, MetricKey)


    @staticmethod
    def validate_filters(filters: Any) -> bool:
        """
        Validate filter collection.
        """
        if filters is None:
            return True

        if not isinstance(filters, (list, tuple, set)):
            return False

        return all(
            isinstance(item, MetricFilter)
            for item in filters
        )


    @classmethod
    def validate_index(
        cls,
        index: Any,
    ) -> bool:
        """
        Validate MetricIndex instance.
        """

        return (
            isinstance(index, cls)
            and cls.validate_name(index.name)
            and cls.validate_namespace(index.namespace)
            and cls.validate_filters(index.filters)
        )


    def validate(self) -> bool:
        """
        Validate current index.
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
            key=self.key.clone()
            if self.key
            else None,
            filters=[
                item.clone()
                for item in self.filters
            ],
        )


    copy = clone


    def merge(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        key: MetricKey | None = None,
        filters: list[MetricFilter] | None = None,
    ) -> "MetricIndex":
        """
        Return merged copy.
        """

        return MetricIndex(
            name=(
                name
                if name is not None
                else self.name
            ),
            namespace=(
                namespace
                if namespace is not None
                else self.namespace
            ),
            key=(
                key.clone()
                if key is not None
                else (
                    self.key.clone()
                    if self.key
                    else None
                )
            ),
            filters=(
                list(filters)
                if filters is not None
                else [
                    item.clone()
                    for item in self.filters
                ]
            ),
        )


    def update(
        self,
        *,
        name: str | None = None,
        namespace: str | None = None,
        key: MetricKey | None = None,
        filters: list[MetricFilter] | None = None,
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
            self.filters = list(filters)

        self.normalize()
        self.validate()

        return self


    def clear(self) -> "MetricIndex":
        """
        Reset index.
        """

        self.name = ""
        self.namespace = ""
        self.key = None
        self.filters.clear()

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
                tuple(self.filters),
            )
        )


    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, MetricIndex):
            return NotImplemented

        return (
            self.name == other.name
            and self.namespace == other.namespace
            and self.key == other.key
            and self.filters == other.filters
        )


    def __lt__(
        self,
        other: "MetricIndex",
    ) -> bool:

        return (
            self.ordering()
            <
            other.ordering()
        )


    def __repr__(self) -> str:

        return (
            "MetricIndex("
            f"name={self.name!r}, "
            f"namespace={self.namespace!r}, "
            f"size={self.size})"
        )


    def __str__(self) -> str:

        return self.fullname


    def __bool__(self) -> bool:

        return bool(
            self.name
            or self.namespace
            or self.key
        )



# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self.name,
            "namespace": self.namespace,
            "fullname": self.fullname,
            "size": self.size,
            "key": self.key,
            "filters": len(self.filters),
        }


    def diagnostics(self) -> dict[str, Any]:
        """
        Diagnostic information.
        """

        return {
            "valid": self.validate(),
            "summary": self.summary(),
            "state": self.state,
        }


    def index_report(self) -> dict[str, Any]:

        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }


    def overall_status(self) -> bool:
        """
        Overall health.
        """

        return self.validate()



# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_INDEX_NAME",
    "DEFAULT_NAMESPACE",
    "MetricIndex",
]            