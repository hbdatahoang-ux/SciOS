# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

from __future__ import annotations

import copy

from collections.abc import Iterable
from typing import Any, TypeAlias

from .decoder import Decoder
from .encoder import Encoder
from .serializer import Serializer

DEFAULT_REGISTRY_NAME: str = "default"
DEFAULT_STRICT: bool = True
DEFAULT_CASE_SENSITIVE: bool = True

__all__ = [
    "DEFAULT_REGISTRY_NAME",
    "DEFAULT_STRICT",
    "DEFAULT_CASE_SENSITIVE",
    "EncoderType",
    "DecoderType",
    "SerializerType",
    "RegistryItem",
    "RegistryDict",
    "Registry",
]


# ==============================================================================
# Part 2. Type Aliases
# ==============================================================================

EncoderType: TypeAlias = Encoder
DecoderType: TypeAlias = Decoder
SerializerType: TypeAlias = Serializer

RegistryItem: TypeAlias = (
    EncoderType
    | DecoderType
    | SerializerType
    | Any
)

RegistryDict: TypeAlias = dict[str, RegistryItem]


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


class Registry:
    """
    Generic serialization registry.
    """

    __slots__ = (
        "_name",
        "_strict",
        "_case_sensitive",
        "_items",
    )

    _name: str
    _strict: bool
    _case_sensitive: bool
    _items: RegistryDict

    def __init__(
        self,
        *,
        name: str = DEFAULT_REGISTRY_NAME,
        strict: bool = DEFAULT_STRICT,
        case_sensitive: bool = DEFAULT_CASE_SENSITIVE,
        items: RegistryDict | None = None,
    ) -> None:
        self._name = str(name)
        self._strict = bool(strict)
        self._case_sensitive = bool(case_sensitive)
        self._items = dict(items or {})


# ==============================================================================
# Part 4. Properties
# ==============================================================================

    @property
    def name(self) -> str:
        """Registry name."""
        return self._name

    @property
    def strict(self) -> bool:
        """Strict lookup mode."""
        return self._strict

    @property
    def case_sensitive(self) -> bool:
        """Case-sensitive registry."""
        return self._case_sensitive

    @property
    def size(self) -> int:
        """Number of registered items."""
        return len(self._items)

    @property
    def items(self) -> RegistryDict:
        """Registered items."""
        return dict(self._items)

    @property
    def mapping(self) -> RegistryDict:
        """Registry mapping."""
        return self._items        


# ==============================================================================
# Part 5. Registration API
# ==============================================================================

    def _normalize(self, name: str) -> str:
        if self._case_sensitive:
            return name
        return name.lower()

    def register(
        self,
        name: str,
        item: RegistryItem,
    ) -> RegistryItem:
        """
        Register an item.
        """
        key = self._normalize(name)

        if self._strict and key in self._items:
            raise KeyError(f"{name!r} already registered.")

        self._items[key] = item
        return item

    def unregister(
        self,
        name: str,
    ) -> RegistryItem:
        """
        Remove an item.
        """
        key = self._normalize(name)

        if self._strict:
            return self._items.pop(key)

        return self._items.pop(key, None)

    def replace(
        self,
        name: str,
        item: RegistryItem,
    ) -> RegistryItem:
        """
        Replace or insert an item.
        """
        key = self._normalize(name)
        self._items[key] = item
        return item

    def update(
        self,
        mapping: RegistryDict | Iterable[tuple[str, RegistryItem]],
    ) -> "Registry":
        """
        Bulk update registry.
        """
        if isinstance(mapping, dict):
            iterable = mapping.items()
        else:
            iterable = mapping

        for name, item in iterable:
            self.replace(name, item)

        return self

    def clear(self) -> None:
        """Remove all registered items."""
        self._items.clear()


# ==============================================================================
# Part 6. Lookup API
# ==============================================================================

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> RegistryItem | Any:
        """
        Lookup item.
        """
        return self._items.get(
            self._normalize(name),
            default,
        )

    def require(
        self,
        name: str,
    ) -> RegistryItem:
        """
        Lookup item or raise KeyError.
        """
        key = self._normalize(name)

        if key not in self._items:
            raise KeyError(name)

        return self._items[key]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return True if registered.
        """
        return self._normalize(name) in self._items

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains().
        """
        return self.contains(name)

    def resolve(
        self,
        value: str | RegistryItem,
    ) -> RegistryItem:
        """
        Resolve registry item.

        If value is already an object,
        return it unchanged.
        """
        if isinstance(value, str):
            return self.require(value)

        return value

# ==============================================================================
# Part 7. Collection API
# ==============================================================================

    def keys(self):
        """Return registry keys."""
        return self._items.keys()

    def values(self):
        """Return registry values."""
        return self._items.values()

    def items(self):
        """Return registry items."""
        return self._items.items()

    def names(self) -> list[str]:
        """Return registered names."""
        return list(self._items.keys())

    def list(self) -> list[RegistryItem]:
        """Return registered objects."""
        return list(self._items.values())


# ==============================================================================
# Part 8. Export / Import
# ==============================================================================

    def snapshot(self) -> dict[str, Any]:
        """Create registry snapshot."""
        return {
            "name": self._name,
            "strict": self._strict,
            "case_sensitive": self._case_sensitive,
            "items": copy.deepcopy(self._items),
        }

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Registry":
        """Restore registry from snapshot."""
        self._name = snapshot["name"]
        self._strict = snapshot["strict"]
        self._case_sensitive = snapshot["case_sensitive"]
        self._items = copy.deepcopy(snapshot["items"])
        return self

    def copy(self) -> "Registry":
        return Registry(
            name=self._name,
            strict=self._strict,
            case_sensitive=self._case_sensitive,
            items=self._items.copy(),
        )


    def deepcopy(self) -> "Registry":
        return Registry(
            name=self._name,
            strict=self._strict,
            case_sensitive=self._case_sensitive,
            items=copy.deepcopy(self._items),
        )


    def clone(self) -> "Registry":
        return self.deepcopy()


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate_name(
        self,
        name: Any,
    ) -> bool:
        """Validate registry name."""
        return isinstance(name, str) and bool(name.strip())

    def validate_item(
        self,
        item: Any,
    ) -> bool:
        """Validate registry item."""
        return item is not None

    def validate(self) -> bool:
        """Validate registry."""
        return all(
            self.validate_name(name)
            and self.validate_item(item)
            for name, item in self._items.items()
        )

    def is_registered(
        self,
        name: str,
    ) -> bool:
        """Return True if registered."""
        return self.contains(name)

    def is_empty(self) -> bool:
        """Return True if registry is empty."""
        return not self._items


    # ==============================================================================
    # Part 10. Python Protocols
    # ==============================================================================

    def __contains__(
        self,
        name: object,
    ) -> bool:
        if not isinstance(name, str):
            return False
        return self.contains(name)


    def __getitem__(
        self,
        name: str,
    ) -> RegistryItem:
        return self.require(name)


    def __setitem__(
        self,
        name: str,
        item: RegistryItem,
    ) -> None:
        self.replace(name, item)


    def __delitem__(
        self,
        name: str,
    ) -> None:
        self.unregister(name)


    def __iter__(self):
        return iter(self._items)


    def __len__(self) -> int:
        return len(self._items)


    def __bool__(self) -> bool:
        return bool(self._items)


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"size={len(self)!r}, "
            f"strict={self._strict!r}, "
            f"case_sensitive={self._case_sensitive!r})"
        )


    __str__ = __repr__


    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, Registry):
            return NotImplemented

        return (
            self._name,
            self._strict,
            self._case_sensitive,
            self._items,
        ) == (
            other._name,
            other._strict,
            other._case_sensitive,
            other._items,
        )


    def __hash__(self) -> int:
        return hash(
            (
                self._name,
                self._strict,
                self._case_sensitive,
            )
        )


    def __getstate__(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "strict": self._strict,
            "case_sensitive": self._case_sensitive,
            "items": self.snapshot(),
        }


    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        self.__init__(
            name=state["name"],
            strict=state["strict"],
            case_sensitive=state["case_sensitive"],
        )

        self.restore(state["items"])


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:
        """Registry summary."""
        return {
            "type": self.__class__.__name__,
            "name": self._name,
            "size": len(self),
            "strict": self._strict,
            "case_sensitive": self._case_sensitive,
        }

    def diagnostics(self) -> dict[str, Any]:
        """Registry diagnostics."""
        return {
            "type": self.__class__.__name__,
            "summary": self.summary(),
            "registered": self.names(),
            "hash": hash(self),
        }

    def registry_report(self) -> dict[str, Any]:
        """Registry report."""
        return {
            "registry": self.summary(),
            "items": self.names(),
            "count": len(self),
            "status": self.overall_status(),
        }

    def overall_status(self) -> str:
        """Overall registry status."""
        return "ready" if self.validate() else "error"


# ==============================================================================
# Part 12. Public API
# ==============================================================================

__all__ = tuple(__all__)        