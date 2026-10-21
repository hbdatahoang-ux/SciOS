"""
SciOS Runtime Metrics
=====================

Metric metadata definition.
"""

from __future__ import annotations

# ==========================================================
# Part 1. Imports
# ==========================================================

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Final
from typing import TypeAlias
import copy
import json

# ==========================================================
# Part 2. Constants / Type Aliases
# ==========================================================

__all__ = [
    "MetricMetadata",
]

# ----------------------------------------------------------
# Default constants
# ----------------------------------------------------------

DEFAULT_NAME: Final[str] = ""

DEFAULT_DESCRIPTION: Final[str] = ""

DEFAULT_UNIT: Final[str] = ""

DEFAULT_NAMESPACE: Final[str] = ""

DEFAULT_CATEGORY: Final[str] = ""

DEFAULT_OWNER: Final[str] = ""

DEFAULT_VERSION: Final[str] = ""

DEFAULT_TAGS: Final[tuple[str, ...]] = ()

DEFAULT_EXTRAS: Final[dict[str, Any]] = {}

# ----------------------------------------------------------
# Type aliases
# ----------------------------------------------------------

MetricName: TypeAlias = str

MetricDescription: TypeAlias = str

MetricUnit: TypeAlias = str

MetricNamespace: TypeAlias = str

MetricCategory: TypeAlias = str

MetricOwner: TypeAlias = str

MetricVersion: TypeAlias = str

MetricTags: TypeAlias = tuple[str, ...]

MetricExtras: TypeAlias = dict[str, Any]


# ==========================================================
# Part 3. Dataclass + Validation
# ==========================================================

from .validation import MetricValidator
import json


@dataclass(slots=True)
class MetricMetadata:
    """
    Immutable metadata describing a Metric.
    """

    # --------------------------------------------------
    # Identity
    # --------------------------------------------------

    name: MetricName = DEFAULT_NAME

    # --------------------------------------------------
    # Description
    # --------------------------------------------------

    description: MetricDescription = DEFAULT_DESCRIPTION

    # --------------------------------------------------
    # Unit
    # --------------------------------------------------

    unit: MetricUnit = DEFAULT_UNIT

    # --------------------------------------------------
    # Namespace
    # --------------------------------------------------

    namespace: MetricNamespace = DEFAULT_NAMESPACE

    # --------------------------------------------------
    # Category
    # --------------------------------------------------

    category: MetricCategory = DEFAULT_CATEGORY

    # --------------------------------------------------
    # Owner
    # --------------------------------------------------

    owner: MetricOwner = DEFAULT_OWNER

    # --------------------------------------------------
    # Version
    # --------------------------------------------------

    version: MetricVersion = DEFAULT_VERSION

    # --------------------------------------------------
    # Tags
    # --------------------------------------------------

    tags: MetricTags = DEFAULT_TAGS

    # --------------------------------------------------
    # Extras
    # --------------------------------------------------

    extras: MetricExtras = field(default_factory=dict)

    # ==================================================
    # Validation
    # ==================================================

    def __post_init__(self) -> None:
        """
        Normalize and validate metadata.
        """

        self.name = str(self.name)
        self.description = str(self.description)
        self.unit = MetricValidator.validate_unit(str(self.unit))
        self.namespace = str(self.namespace)
        self.category = str(self.category)
        self.owner = str(self.owner)
        self.version = str(self.version)

        if not isinstance(self.tags, (list, tuple)):
            raise TypeError(
                "tags must be a list or tuple of strings."
            )

        validated_tags: list[str] = []

        for tag in self.tags:
            if not isinstance(tag, str):
                raise TypeError(
                    "all tags must be strings."
                )
            validated_tags.append(tag)

        self.tags = tuple(validated_tags)

        self.extras = MetricValidator.validate_metadata(
            dict(self.extras)
        )

    def validate(self) -> None:
        """
        Validate current metadata.
        """

        MetricValidator.validate_name(self.name)
        MetricValidator.validate_unit(self.unit)
        MetricValidator.validate_metadata(self.extras)

        if not isinstance(self.tags, tuple):
            raise TypeError(
                "tags must be tuple[str, ...]"
            )

        for tag in self.tags:
            if not isinstance(tag, str):
                raise TypeError(
                    "each tag must be str"
                )

    def is_valid(self) -> bool:
        """
        Return True if metadata is valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False

    # ==================================================
    # Part 4. Serialization
    # ==================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize metadata to dict.
        """

        return {
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
            "namespace": self.namespace,
            "category": self.category,
            "owner": self.owner,
            "version": self.version,
            "tags": list(self.tags),
            "extras": dict(self.extras),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricMetadata":

        return cls(
            name=data.get("name", DEFAULT_NAME),
            description=data.get(
                "description",
                DEFAULT_DESCRIPTION,
            ),
            unit=data.get(
                "unit",
                DEFAULT_UNIT,
            ),
            namespace=data.get(
                "namespace",
                DEFAULT_NAMESPACE,
            ),
            category=data.get(
                "category",
                DEFAULT_CATEGORY,
            ),
            owner=data.get(
                "owner",
                DEFAULT_OWNER,
            ),
            version=data.get(
                "version",
                DEFAULT_VERSION,
            ),
            tags=tuple(
                data.get(
                    "tags",
                    DEFAULT_TAGS,
                )
            ),
            extras=dict(
                data.get(
                    "extras",
                    {},
                )
            ),
        )

    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "MetricMetadata":

        return cls.from_dict(
            json.loads(text),
        )

    # ==========================================================
    # Part 5. Copy API
    # ==========================================================

    import copy as copy_module


    def copy(self) -> "MetricMetadata":
        """
        Return a shallow copy.
        """
        return self.__class__.from_dict(self.to_dict())


    def clone(self) -> "MetricMetadata":
        """
        Return a deep clone.
        """
        return copy.deepcopy(self)


    def deepcopy(self) -> "MetricMetadata":
        """
        Explicit deep copy.
        """
        return copy.deepcopy(self)


    def replace(
        self,
        **updates: Any,
    ) -> "MetricMetadata":
        """
        Return a copied metadata with updated fields.
        """
        data = self.to_dict()
        data.update(updates)
        return self.__class__.from_dict(data)

    # ==========================================================
    # Part 6. Comparison
    # ==========================================================

    def equals(
        self,
        other: object,
    ) -> bool:
        """
        Compare two metadata objects.
        """
        if not isinstance(other, MetricMetadata):
            return False

        return self.to_dict() == other.to_dict()


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality operator.
        """
        return self.equals(other)


    def __hash__(self) -> int:
        """
        Hash value.
        """
        return hash(
            (
                self.name,
                self.description,
                self.unit,
                self.namespace,
                self.category,
                self.owner,
                self.version,
                self.tags,
                tuple(sorted(self.extras.items())),
            )
        )

    # ==========================================================
    # Part 7. Python Protocols
    # ==========================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"unit={self.unit!r})"
        )


    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return self.name


    def __bool__(self) -> bool:
        """
        Truth value.
        """
        return bool(self.name)    

