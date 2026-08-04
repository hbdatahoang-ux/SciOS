# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any, TypeAlias
from copy import copy as _copy
from copy import deepcopy as _deepcopy

__all__ = [
    "Schema",
    "DEFAULT_SCHEMA_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_STRICT",
    "DEFAULT_ALLOW_EXTRA",
]

DEFAULT_SCHEMA_NAME: str = "default"
DEFAULT_VERSION: str = "1.0"
DEFAULT_STRICT: bool = True
DEFAULT_ALLOW_EXTRA: bool = False


# ==============================================================================
# Part 2. Type Aliases
# ==============================================================================

FieldName: TypeAlias = str
FieldType: TypeAlias = type[Any] | tuple[type[Any], ...] | Any
FieldDefinition: TypeAlias = FieldType
SchemaMapping: TypeAlias = dict[FieldName, FieldDefinition]
ValidationResult: TypeAlias = tuple[bool, list[str]]


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


class Schema:

    __slots__ = (
        "_name",
        "_version",
        "_strict",
        "_allow_extra",
        "_fields",
    )

    __annotations__ = {
        "_name": str,
        "_version": str,
        "_strict": bool,
        "_allow_extra": bool,
        "_fields": SchemaMapping,
    }

    def __init__(
        self,
        *,
        name: str = DEFAULT_SCHEMA_NAME,
        version: str = DEFAULT_VERSION,
        strict: bool = DEFAULT_STRICT,
        allow_extra: bool = DEFAULT_ALLOW_EXTRA,
        fields: Mapping[str, FieldDefinition] | None = None,
    ) -> None:
        self._name = str(name)
        self._version = str(version)
        self._strict = bool(strict)
        self._allow_extra = bool(allow_extra)
        self._fields: SchemaMapping = dict(fields or {})


# ==============================================================================
# Part 4. Properties
# ==============================================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def strict(self) -> bool:
        return self._strict

    @property
    def allow_extra(self) -> bool:
        return self._allow_extra

    @property
    def fields(self) -> SchemaMapping:
        return self._fields

    @property
    def size(self) -> int:
        return len(self._fields)


# ==============================================================================
# Part 5. Field Management
# ==============================================================================

    def add_field(
        self,
        name: FieldName,
        definition: FieldDefinition,
    ) -> "Schema":
        self.validate_name(name)
        self.validate_field(definition)

        if self._strict and name in self._fields:
            raise KeyError(name)

        self._fields[name] = definition
        return self

    def remove_field(
        self,
        name: FieldName,
    ) -> FieldDefinition:
        return self._fields.pop(name)

    def replace_field(
        self,
        name: FieldName,
        definition: FieldDefinition,
    ) -> "Schema":
        self.validate_name(name)
        self.validate_field(definition)

        if self._strict and name not in self._fields:
            raise KeyError(name)

        self._fields[name] = definition
        return self

    def update(
        self,
        mapping: Mapping[str, FieldDefinition],
    ) -> "Schema":
        for name, definition in mapping.items():
            self.validate_name(name)
            self.validate_field(definition)

        self._fields.update(mapping)
        return self

    def clear(self) -> "Schema":
        self._fields.clear()
        return self


# ==============================================================================
# Part 6. Lookup API
# ==============================================================================

    def get(
        self,
        name: FieldName,
        default: Any = None,
    ) -> Any:
        return self._fields.get(name, default)

    def require(
        self,
        name: FieldName,
    ) -> FieldDefinition:
        try:
            return self._fields[name]
        except KeyError:
            raise KeyError(f"Unknown field: {name!r}") from None

    def contains(
        self,
        name: FieldName,
    ) -> bool:
        return name in self._fields

    def exists(
        self,
        name: FieldName,
    ) -> bool:
        return self.contains(name)

    def resolve(
        self,
        name: FieldName,
    ) -> FieldDefinition:
        return self.require(name)

# ==============================================================================
# Part 7. Validation
# ==============================================================================

    @staticmethod
    def validate_name(
        name: FieldName,
    ) -> str:
        if not isinstance(name, str):
            raise TypeError("Field name must be a string.")

        if not name.strip():
            raise ValueError("Field name cannot be empty.")

        return name

    @staticmethod
    def validate_field(
        definition: FieldDefinition,
    ) -> FieldDefinition:
        if definition is None:
            raise ValueError("Field definition cannot be None.")
        return definition

    def validate_data(
        self,
        data: Mapping[str, Any],
    ) -> ValidationResult:
        errors: list[str] = []

        if not isinstance(data, Mapping):
            return False, ["Data must be a mapping."]

        for name, definition in self._fields.items():
            if name not in data:
                errors.append(f"Missing field: {name}")
                continue

            value = data[name]

            if isinstance(definition, type):
                if not isinstance(value, definition):
                    errors.append(
                        f"Field '{name}' must be {definition.__name__}"
                    )

            elif (
                isinstance(definition, tuple)
                and definition
                and all(isinstance(t, type) for t in definition)
            ):
                if not isinstance(value, definition):
                    names = ", ".join(t.__name__ for t in definition)
                    errors.append(
                        f"Field '{name}' must be one of ({names})"
                    )

        if not self._allow_extra:
            extras = set(data) - set(self._fields)
            for name in sorted(extras):
                errors.append(f"Unexpected field: {name}")

        return len(errors) == 0, errors

    def validate(self) -> bool:
        self.validate_name(self._name)

        if not isinstance(self._version, str):
            raise TypeError("Version must be a string.")

        for name, definition in self._fields.items():
            self.validate_name(name)
            self.validate_field(definition)

        return True

    def is_empty(self) -> bool:
        return not self._fields


# ==============================================================================
# Part 8. Snapshot / Copy
# ==============================================================================

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "version": self._version,
            "strict": self._strict,
            "allow_extra": self._allow_extra,
            "fields": _deepcopy(self._fields),
        }

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "Schema":
        self._name = snapshot["name"]
        self._version = snapshot["version"]
        self._strict = snapshot["strict"]
        self._allow_extra = snapshot["allow_extra"]
        self._fields = _deepcopy(snapshot["fields"])
        return self

    def copy(self) -> "Schema":
        return Schema(
            name=self._name,
            version=self._version,
            strict=self._strict,
            allow_extra=self._allow_extra,
            fields=self._fields.copy(),
        )

    def deepcopy(self) -> "Schema":
        return Schema(
            name=self._name,
            version=self._version,
            strict=self._strict,
            allow_extra=self._allow_extra,
            fields=_deepcopy(self._fields),
        )

    def clone(self) -> "Schema":
        return self.deepcopy()


# ==============================================================================
# Part 9. Python Protocols
# ==============================================================================

    def __contains__(
        self,
        name: object,
    ) -> bool:
        return isinstance(name, str) and self.contains(name)

    def __getitem__(
        self,
        name: FieldName,
    ) -> FieldDefinition:
        return self.require(name)

    def __setitem__(
        self,
        name: FieldName,
        definition: FieldDefinition,
    ) -> None:
        if name in self._fields:
            self.replace_field(name, definition)
        else:
            self.add_field(name, definition)

    def __delitem__(
        self,
        name: FieldName,
    ) -> None:
        self.remove_field(name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._fields)

    def __len__(self) -> int:
        return len(self._fields)

    def __bool__(self) -> bool:
        return bool(self._fields)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"version={self._version!r}, "
            f"size={len(self)!r}, "
            f"strict={self._strict!r}, "
            f"allow_extra={self._allow_extra!r})"
        )

    __str__ = __repr__

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, Schema):
            return NotImplemented

        return (
            self._name == other._name
            and self._version == other._version
            and self._strict == other._strict
            and self._allow_extra == other._allow_extra
            and self._fields == other._fields
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._name,
                self._version,
                self._strict,
                self._allow_extra,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return self.snapshot()

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        self.__init__(
            name=state["name"],
            version=state["version"],
            strict=state["strict"],
            allow_extra=state["allow_extra"],
            fields=state["fields"],
        )


# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "version": self._version,
            "fields": len(self),
            "strict": self._strict,
            "allow_extra": self._allow_extra,
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "valid": self.validate(),
            "empty": self.is_empty(),
            "size": len(self),
            "summary": self.summary(),
        }

    def schema_report(self) -> dict[str, Any]:
        return {
            "schema": self.summary(),
            "field_names": list(self._fields),
            "status": self.overall_status(),
        }

    def overall_status(self) -> str:
        return "ready"


# ==============================================================================
# Part 11. Public API
# ==============================================================================

__all__ = [
    "Schema",
    "DEFAULT_SCHEMA_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_STRICT",
    "DEFAULT_ALLOW_EXTRA",
]        