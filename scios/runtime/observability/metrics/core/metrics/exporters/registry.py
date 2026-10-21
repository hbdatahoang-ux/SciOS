# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import copy

from threading import RLock
from typing import Any
from typing import Callable
from typing import Final
from typing import TypeAlias

ExporterFactory: TypeAlias = Callable[..., Any]

ExporterType: TypeAlias = type[Any]

DEFAULT_VERSION: Final[str] = "1.0"

DEFAULT_CASE_SENSITIVE: Final[bool] = False

DEFAULT_ALLOW_OVERRIDE: Final[bool] = False

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_CASE_SENSITIVE",
    "DEFAULT_ALLOW_OVERRIDE",
    "ExporterFactory",
    "ExporterType",
    "ExporterRegistry",
]


# ==========================================================
# Part 2. Constructor
# ==========================================================

class ExporterRegistry:
    """
    Registry for exporter implementations.
    """

    __slots__ = (
        "_version",
        "_case_sensitive",
        "_allow_override",
        "_exporters",
        "_lock",
    )

    def __init__(
        self,
        *,
        version: str = DEFAULT_VERSION,
        case_sensitive: bool = DEFAULT_CASE_SENSITIVE,
        allow_override: bool = DEFAULT_ALLOW_OVERRIDE,
    ) -> None:

        self._version = version

        self._case_sensitive = bool(
            case_sensitive,
        )

        self._allow_override = bool(
            allow_override,
        )

        self._exporters: dict[
            str,
            ExporterFactory,
        ] = {}

        self._lock = RLock()


# ==========================================================
# Part 3. Properties
# ==========================================================

    @property
    def version(
        self,
    ) -> str:
        """
        Registry version.
        """
        return self._version

    @property
    def case_sensitive(
        self,
    ) -> bool:
        """
        Whether exporter names are case sensitive.
        """
        return self._case_sensitive

    @property
    def allow_override(
        self,
    ) -> bool:
        """
        Whether duplicate registrations are allowed.
        """
        return self._allow_override

    @property
    def exporters(
        self,
    ) -> dict[str, ExporterFactory]:
        """
        Registered exporters.
        """
        return dict(
            self._exporters,
        )

    @property
    def names(
        self,
    ) -> list[str]:
        """
        Registered exporter names.
        """
        return list(
            self._exporters.keys(),
        )

    @property
    def size(
        self,
    ) -> int:
        """
        Number of registered exporters.
        """
        return len(
            self._exporters,
        )

    @property
    def lock(
        self,
    ) -> RLock:
        """
        Internal synchronization lock.
        """
        return self._lock

# ==========================================================
# Part 4. Registration
# ==========================================================

    def _normalize_name(
        self,
        name: str,
    ) -> str:
        """
        Normalize exporter name.
        """
        return (
            name
            if self._case_sensitive
            else name.lower()
        )

    def register(
        self,
        name: str,
        factory: ExporterFactory,
    ) -> None:
        """
        Register exporter.
        """

        key = self._normalize_name(
            name,
        )

        with self._lock:

            if (
                key in self._exporters
                and not self._allow_override
            ):
                raise KeyError(
                    f"Exporter '{name}' already registered."
                )

            self._exporters[key] = factory

    def unregister(
        self,
        name: str,
    ) -> ExporterFactory | None:
        """
        Remove exporter.
        """

        key = self._normalize_name(
            name,
        )

        with self._lock:

            return self._exporters.pop(
                key,
                None,
            )

    def replace(
        self,
        name: str,
        factory: ExporterFactory,
    ) -> None:
        """
        Replace exporter registration.
        """

        key = self._normalize_name(
            name,
        )

        with self._lock:

            self._exporters[key] = factory

    def clear(
        self,
    ) -> None:
        """
        Remove all exporters.
        """

        with self._lock:

            self._exporters.clear()


# ==========================================================
# Part 5. Lookup
# ==========================================================

    def get(
        self,
        name: str,
        default: ExporterFactory | None = None,
    ) -> ExporterFactory | None:
        """
        Get exporter.
        """

        key = self._normalize_name(
            name,
        )

        with self._lock:

            return self._exporters.get(
                key,
                default,
            )

    def require(
        self,
        name: str,
    ) -> ExporterFactory:
        """
        Get exporter or raise.
        """

        exporter = self.get(
            name,
        )

        if exporter is None:
            raise KeyError(
                f"Unknown exporter '{name}'."
            )

        return exporter

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check registration.
        """

        key = self._normalize_name(
            name,
        )

        with self._lock:

            return key in self._exporters

    def find(
        self,
        pattern: str,
    ) -> dict[str, ExporterFactory]:
        """
        Find exporters by partial name.
        """

        query = (
            pattern
            if self._case_sensitive
            else pattern.lower()
        )

        with self._lock:

            result: dict[str, ExporterFactory] = {}

            for factory in self._exporters.values():

                name = factory.__name__

                haystack = (
                    name
                    if self._case_sensitive
                    else name.lower()
                )

                if query in haystack:
                    result[name] = factory

            return result


# ==========================================================
# Part 6. Listing
# ==========================================================

    def list_exporters(
        self,
    ) -> list[ExporterFactory]:
        """
        Return registered exporters.
        """

        with self._lock:

            return list(
                self._exporters.values(),
            )

    def list_names(
        self,
    ) -> list[str]:
        """
        Return exporter names.
        """

        with self._lock:

            return list(
                self._exporters.keys(),
            )

    def items(
        self,
    ):
        """
        Registry items.
        """

        with self._lock:

            return tuple(
                self._exporters.items(),
            )

    def values(
        self,
    ):
        """
        Registry values.
        """

        with self._lock:

            return tuple(
                self._exporters.values(),
            )

    def keys(
        self,
    ):
        """
        Registry keys.
        """

        with self._lock:

            return tuple(
                self._exporters.keys(),
            )

# ==========================================================
# Part 7. Exporter Creation
# ==========================================================

    def create(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Create exporter instance.
        """

        factory = self.require(
            name,
        )

        return factory(
            *args,
            **kwargs,
        )

    def create_all(self):

        return [
            factory()
            for factory in self._exporters.values()
        ]


# ==========================================================
# Part 8. Validation
# ==========================================================

    def validate(self) -> bool:

        for name, factory in self._exporters.items():

            if not callable(factory):
                return False

        return True

    def is_valid(
        self,
    ) -> bool:
        """
        Safe validation.
        """

        try:
            return self.validate()
        except Exception:
            return False


# ==========================================================
# Part 9. Python Protocols
# ==========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(size={len(self)}, "
            f"case_sensitive={self._case_sensitive}, "
            f"allow_override={self._allow_override})"
        )

    def __str__(
        self,
    ) -> str:

        return self.__repr__()

    def __len__(
        self,
    ) -> int:

        return len(
            self._exporters,
        )

    def __iter__(
        self,
    ):

        return iter(
            self.list_names(),
        )

    def __contains__(
        self,
        item: object,
    ) -> bool:

        if not isinstance(
            item,
            str,
        ):
            return False

        return self.exists(
            item,
        )

    def __getitem__(
        self,
        name: str,
    ) -> ExporterFactory:

        return self.require(
            name,
        )

    def __setitem__(
        self,
        name: str,
        factory: ExporterFactory,
    ) -> None:

        self.register(
            name,
            factory,
        )

    def __delitem__(
        self,
        name: str,
    ) -> None:

        self.unregister(
            name,
        )

    def __copy__(
        self,
    ):

        copied = self.__class__(
            version=self._version,
            case_sensitive=self._case_sensitive,
            allow_override=self._allow_override,
        )

        copied._exporters = dict(
            self._exporters,
        )

        return copied

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ):

        copied = self.__class__(
            version=copy.deepcopy(
                self._version,
                memo,
            ),
            case_sensitive=copy.deepcopy(
                self._case_sensitive,
                memo,
            ),
            allow_override=copy.deepcopy(
                self._allow_override,
                memo,
            ),
        )

        copied._exporters = copy.deepcopy(
            self._exporters,
            memo,
        )

        return copied

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            ExporterRegistry,
        ):
            return False

        return (
            self._version == other._version
            and self._case_sensitive == other._case_sensitive
            and self._allow_override == other._allow_override
            and self._exporters == other._exporters
        )

    def __hash__(
        self,
    ) -> int:

        return hash(
            (
                self._version,
                self._case_sensitive,
                self._allow_override,
            )
        )

    def __getstate__(
        self,
    ) -> dict[str, Any]:

        return {
            "version": self._version,
            "case_sensitive": self._case_sensitive,
            "allow_override": self._allow_override,
            "exporters": self._exporters,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._version = state["version"]
        self._case_sensitive = state["case_sensitive"]
        self._allow_override = state["allow_override"]
        self._exporters = state["exporters"]
        self._lock = RLock()


# ==========================================================
# Part 10. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_CASE_SENSITIVE",
    "DEFAULT_ALLOW_OVERRIDE",
    "ExporterFactory",
    "ExporterType",
    "ExporterRegistry",
    "default_registry",
]  

# ==========================================================
# Part 11. Default Registry
# ==========================================================

default_registry = ExporterRegistry()