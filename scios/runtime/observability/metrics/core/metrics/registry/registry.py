"""
Metric Registry
===============

Central registry for metrics.

Python 3.11+
"""


from __future__ import annotations


from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
    TypeAlias,
)


from .index import MetricIndex
from .key import MetricKey


__all__ = [
    "MetricRegistry",
]


# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================


DEFAULT_NAME = ""

DEFAULT_NAMESPACE = ""


MetricState: TypeAlias = dict[str, Any]

MetricSnapshot: TypeAlias = dict[str, Any]

MetricStorage: TypeAlias = dict[str, MetricKey]



# ==============================================================================
# Part 2. MetricRegistry
# ==============================================================================


@dataclass(slots=True)
class MetricRegistry:
    """
    Metric registry.

    Stores and manages MetricKey objects.
    """

    name: str = DEFAULT_NAME

    namespace: str = DEFAULT_NAMESPACE

    index: MetricIndex = field(
        default_factory=MetricIndex,
    )

    metrics: dict[str, MetricKey] = field(
        default_factory=dict,
    )

    state: MetricState = field(
        default_factory=dict,
    )


    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:

        self._normalize()

        self._validate()


    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    def _storage_init(self) -> None:

        if not isinstance(
            self.metrics,
            dict,
        ):
            self.metrics = {}


    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self) -> None:


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


        if not isinstance(
            self.index,
            MetricIndex,
        ):

            self.index = MetricIndex()


        else:

            self.index.normalize()



        if not isinstance(
            self.metrics,
            dict,
        ):

            self.metrics = {}



        normalized: dict[str, MetricKey] = {}

        for key, value in self.metrics.items():


            if not isinstance(
                value,
                MetricKey,
            ):
                continue


            value.normalize()

            normalized[value.fullname] = value


        self.metrics = normalized



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
            self.index,
            MetricIndex,
        ):
            raise TypeError(
                "index must be MetricIndex"
            )


        if not isinstance(
            self.metrics,
            dict,
        ):
            raise TypeError(
                "metrics must be dict"
            )


        if not all(
            isinstance(k, str)
            for k in self.metrics.keys()
        ):
            raise TypeError(
                "metric keys must be strings"
            )


        if not all(
            isinstance(v, MetricKey)
            for v in self.metrics.values()
        ):
            raise TypeError(
                "metric values must be MetricKey"
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
        Number of registered metrics.
        """

        return len(
            self.metrics
        )



# ==============================================================================
# Part 4. Operations
# ==============================================================================


    def register(
        self,
        metric: MetricKey,
    ) -> "MetricRegistry":
        """
        Register metric.
        """

        if not isinstance(
            metric,
            MetricKey,
        ):
            raise TypeError(
                "metric must be MetricKey"
            )


        metric.normalize()


        self.metrics[
            metric.fullname
        ] = metric


        self.index.add(
            metric
        )


        return self



    def unregister(
        self,
        metric: MetricKey | str,
    ) -> "MetricRegistry":
        """
        Remove metric.
        """


        if isinstance(
            metric,
            MetricKey,
        ):

            key = metric.fullname


        else:

            key = str(metric)



        removed = self.metrics.pop(
            key,
            None,
        )


        if removed:

            self.index.remove(
                removed
            )


        return self



    def get(
        self,
        name: str,
    ) -> MetricKey | None:
        """
        Retrieve metric.
        """

        return self.metrics.get(
            name
        )



    def contains(
        self,
        metric: MetricKey | str,
    ) -> bool:
        """
        Check metric existence.
        """

        if isinstance(
            metric,
            MetricKey,
        ):

            metric = metric.fullname


        return (
            str(metric)
            in self.metrics
        )



    def clear(
        self,
    ) -> "MetricRegistry":
        """
        Clear registry.
        """

        self.metrics.clear()

        self.index.clear()

        return self



    def list(
        self,
    ) -> list[MetricKey]:
        """
        List registered metrics.
        """

        return list(
            self.metrics.values()
        )



    def normalize(
        self,
    ) -> "MetricRegistry":
        """
        Normalize registry.
        """

        self._normalize()

        return self



# ==============================================================================
# Part 5. Serialization
# ==============================================================================


    def to_dict(
        self,
    ) -> dict:

        return {

            "name":
                self.name,

            "namespace":
                self.namespace,

            "index":
                self.index.to_dict(),

            "metrics":
                {
                    key:
                    value.to_dict()

                    for key, value
                    in self.metrics.items()
                },

            "state":
                dict(self.state),
        }



    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "MetricRegistry":


        registry = cls(

            name=data.get(
                "name",
                "",
            ),

            namespace=data.get(
                "namespace",
                "",
            ),

            index=MetricIndex.from_dict(
                data.get(
                    "index",
                    {},
                )
            ),

        )


        registry.metrics = {

            key:
            MetricKey.from_dict(value)

            for key, value
            in data.get(
                "metrics",
                {},
            ).items()

        }


        registry.state = dict(
            data.get(
                "state",
                {},
            )
        )


        return registry



    def to_tuple(
        self,
    ) -> tuple:

        return (

            self.name,

            self.namespace,

            self.index.to_tuple(),

            tuple(

                (
                    key,
                    value.to_tuple(),
                )

                for key, value
                in self.metrics.items()

            ),

            dict(
                self.state
            ),
        )



    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "MetricRegistry":


        (
            name,
            namespace,
            index,
            metrics,
            state,

        ) = value



        registry = cls(

            name=name,

            namespace=namespace,

            index=MetricIndex.from_tuple(
                index
            ),

        )


        registry.metrics = {

            key:
            MetricKey.from_tuple(
                item
            )

            for key, item
            in metrics

        }


        registry.state = dict(
            state
        )


        return registry



    def snapshot(
        self,
    ) -> dict:
        """
        Create snapshot.
        """

        return self.to_dict()



    def restore(
        self,
        snapshot: dict,
    ) -> "MetricRegistry":
        """
        Restore snapshot.
        """

        restored = self.from_dict(
            snapshot
        )


        self.name = restored.name

        self.namespace = restored.namespace

        self.index = restored.index

        self.metrics = restored.metrics

        self.state = restored.state


        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================


    @staticmethod
    def validate_name(
        name: str,
    ) -> bool:
        """
        Validate registry name.
        """

        return isinstance(
            name,
            str,
        )



    @staticmethod
    def validate_namespace(
        namespace: str,
    ) -> bool:
        """
        Validate namespace.
        """

        return isinstance(
            namespace,
            str,
        )



    @staticmethod
    def validate_index(
        index: MetricIndex,
    ) -> bool:
        """
        Validate index.
        """

        return isinstance(
            index,
            MetricIndex,
        )



    @staticmethod
    def validate_metrics(
        metrics: dict,
    ) -> bool:
        """
        Validate metric storage.
        """

        if not isinstance(
            metrics,
            dict,
        ):
            return False


        return all(

            isinstance(key, str)

            and isinstance(
                value,
                MetricKey,
            )

            for key, value
            in metrics.items()

        )



    @classmethod
    def validate_registry(
        cls,
        registry: "MetricRegistry",
    ) -> bool:
        """
        Validate registry object.
        """

        return (

            cls.validate_name(
                registry.name
            )

            and

            cls.validate_namespace(
                registry.namespace
            )

            and

            cls.validate_index(
                registry.index
            )

            and

            cls.validate_metrics(
                registry.metrics
            )

            and

            isinstance(
                registry.state,
                dict,
            )

        )



    def validate(
        self,
    ) -> bool:
        """
        Validate current registry.
        """

        return self.validate_registry(
            self
        )



# ==============================================================================
# Part 7. Utilities
# ==============================================================================


    def clone(
        self,
    ) -> "MetricRegistry":
        """
        Deep clone registry.
        """

        return MetricRegistry.from_dict(
            self.to_dict()
        )



    def copy(
        self,
    ) -> "MetricRegistry":
        """
        Alias of clone.
        """

        return self.clone()



    def merge(
        self,
        other: "MetricRegistry",
    ) -> "MetricRegistry":
        """
        Merge another registry.
        """

        if not isinstance(
            other,
            MetricRegistry,
        ):
            raise TypeError(
                "other must be MetricRegistry"
            )


        for metric in other.list():

            self.register(
                metric
            )


        self.state.update(
            other.state
        )


        return self



    def update(
        self,
        metrics: dict[str, MetricKey],
    ) -> "MetricRegistry":
        """
        Bulk update metrics.
        """

        if not isinstance(
            metrics,
            dict,
        ):
            raise TypeError(
                "metrics must be dict"
            )


        for metric in metrics.values():

            self.register(
                metric
            )


        return self



    def reset(
        self,
    ) -> "MetricRegistry":
        """
        Reset registry state.
        """

        self.clear()

        self.state.clear()

        return self



# ==============================================================================
# Part 8. Protocols
# ==============================================================================


    def __hash__(
        self,
    ) -> int:
        """
        Hash registry.
        """

        return hash(
            (
                self.name,
                self.namespace,
            )
        )



    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.
        """

        if not isinstance(
            other,
            MetricRegistry,
        ):
            return False


        return (

            self.name
            ==
            other.name

            and

            self.namespace
            ==
            other.namespace

            and

            self.metrics
            ==
            other.metrics

            and

            self.state
            ==
            other.state

        )



    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            "MetricRegistry("
            f"name={self.name!r}, "
            f"namespace={self.namespace!r}, "
            f"size={self.size}"
            ")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human representation.
        """

        return (

            f"{self.namespace}:"
            f"{self.name}"
            f"({self.size})"

        )



    def __bool__(
        self,
    ) -> bool:
        """
        Registry truth value.
        """

        return bool(
            self.metrics
        )



# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================


    def summary(
        self,
    ) -> dict:
        """
        Registry summary.
        """

        return {

            "name":
                self.name,

            "namespace":
                self.namespace,

            "size":
                self.size,

            "valid":
                self.validate(),

        }



    def diagnostics(
        self,
    ) -> dict:
        """
        Detailed diagnostics.
        """

        return {

            "summary":
                self.summary(),

            "metrics":
                [
                    key

                    for key
                    in self.metrics.keys()

                ],

            "state":
                dict(
                    self.state
                ),

        }



    def registry_report(
        self,
    ) -> dict:
        """
        Generate registry report.
        """

        return {

            "registry":
                self.name,

            "namespace":
                self.namespace,

            "metric_count":
                self.size,

            "index_size":
                self.index.size,

            "status":
                self.overall_status(),

        }



    def overall_status(
        self,
    ) -> str:
        """
        Registry health status.
        """

        if self.validate():

            return "healthy"


        return "invalid"



# ==============================================================================
# Part 10. Public API
# ==============================================================================


__all__ = [

    "MetricRegistry",

]        