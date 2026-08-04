"""
Schema definition and validation engine.

Python 3.11+
"""

from __future__ import annotations


import copy
import json
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    TypeAlias,
)


# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================


DEFAULT_SCHEMA_NAME = "default"

DEFAULT_VERSION = "1.0"

DEFAULT_STRICT = True

DEFAULT_ALLOW_EXTRA = False



__all__ = [
    "Schema",
    "DEFAULT_SCHEMA_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_STRICT",
    "DEFAULT_ALLOW_EXTRA",
]



# ==============================================================================
# Part 2. Type Aliases
# ==============================================================================


FieldName: TypeAlias = str

FieldType: TypeAlias = type | tuple[type, ...]

FieldDefinition: TypeAlias = dict[str, Any]

SchemaMapping: TypeAlias = dict[str, FieldDefinition]

ValidationResult: TypeAlias = dict[str, Any]



# ==============================================================================
# Part 3. Constructor
# ==============================================================================


class Schema:
    """
    Runtime schema definition.

    Stores field definitions and validates data.
    """


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
        name: str = DEFAULT_SCHEMA_NAME,
        version: str = DEFAULT_VERSION,
        strict: bool = DEFAULT_STRICT,
        allow_extra: bool = DEFAULT_ALLOW_EXTRA,
        fields: Mapping[str, FieldDefinition] | None = None,
    ) -> None:


        self._name = name

        self._version = version

        self._strict = strict

        self._allow_extra = allow_extra

        self._fields = dict(fields or {})


        self.validate_name(name)



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
        return dict(self._fields)



    @property
    def size(self) -> int:
        return len(self._fields)

# ==============================================================================
# Part 5. Validation
# ==============================================================================


    def validate_name(
        self,
        name: str,
    ) -> bool:

        if not isinstance(name, str):
            raise TypeError("Schema name must be str")

        if not name:
            raise ValueError("Schema name cannot be empty")

        return True



    def validate_field(
        self,
        field: FieldDefinition,
    ) -> bool:

        if not isinstance(field, dict):
            raise TypeError("Field definition must be dict")


        if "type" not in field:
            if self._strict:
                raise ValueError(
                    "Field definition requires 'type'"
                )


        return True



    def validate_data(
        self,
        data: Mapping[str, Any],
    ) -> ValidationResult:


        if not isinstance(data, Mapping):
            raise TypeError(
                "Data must be mapping"
            )


        errors: list[str] = []


        for name, definition in self._fields.items():

            if name not in data:

                if definition.get(
                    "required",
                    False
                ):
                    errors.append(
                        f"missing field: {name}"
                    )

                continue


            expected = definition.get(
                "type"
            )


            if expected is not None:

                if not isinstance(
                    data[name],
                    expected,
                ):
                    errors.append(
                        f"invalid type: {name}"
                    )


        if not self._allow_extra:

            for key in data:

                if key not in self._fields:

                    errors.append(
                        f"extra field: {key}"
                    )


        return {
            "valid": not errors,
            "errors": errors,
        }



    def validate(
        self,
        data: Mapping[str, Any],
    ) -> bool:

        return bool(
            self.validate_data(data)["valid"]
        )



    def is_empty(self) -> bool:

        return not bool(self._fields)



# ==============================================================================
# Part 6. Snapshot / Copy
# ==============================================================================


    def snapshot(self) -> dict[str, Any]:

        return {

            "name": self._name,

            "version": self._version,

            "strict": self._strict,

            "allow_extra": self._allow_extra,

            "fields": copy.deepcopy(
                self._fields
            ),

        }



    def restore(
        self,
        state: Mapping[str, Any],
    ) -> None:


        self._name = state["name"]

        self._version = state["version"]

        self._strict = state["strict"]

        self._allow_extra = state["allow_extra"]

        self._fields = copy.deepcopy(
            state["fields"]
        )



    def copy(self) -> "Schema":

        return Schema(
            name=self._name,
            version=self._version,
            strict=self._strict,
            allow_extra=self._allow_extra,
            fields=self._fields,
        )



    def deepcopy(self) -> "Schema":

        return Schema(
            name=self._name,
            version=self._version,
            strict=self._strict,
            allow_extra=self._allow_extra,
            fields=copy.deepcopy(
                self._fields
            ),
        )



    def clone(self) -> "Schema":

        return self.deepcopy()



# ==============================================================================
# Part 7. Python Protocols
# ==============================================================================


    def __contains__(
        self,
        name: object,
    ) -> bool:

        if not isinstance(name, str):

            return False

        return name in self._fields



    def __getitem__(
        self,
        name: str,
    ) -> FieldDefinition:

        return self._fields[name]



    def __setitem__(
        self,
        name: str,
        field: FieldDefinition,
    ) -> None:

        self.validate_field(field)

        self._fields[name] = field



    def __delitem__(
        self,
        name: str,
    ) -> None:

        del self._fields[name]



    def __iter__(self):

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
            f"size={self.size!r}, "
            f"strict={self._strict!r}, "
            f"allow_extra={self._allow_extra!r})"
        )



    __str__ = __repr__



    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            Schema,
        ):
            return NotImplemented


        return (

            self._name,

            self._version,

            self._strict,

            self._allow_extra,

            self._fields,

        ) == (

            other._name,

            other._version,

            other._strict,

            other._allow_extra,

            other._fields,

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
# Part 8. Diagnostics
# ==============================================================================


    def summary(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "version": self._version,
            "size": self.size,
            "strict": self._strict,
            "allow_extra": self._allow_extra,
            "empty": self.is_empty(),
        }



    def diagnostics(self) -> dict[str, Any]:

        return {

            "schema": self._name,

            "version": self._version,

            "fields": list(
                self._fields.keys()
            ),

            "field_count": self.size,

            "validation": {

                "strict": self._strict,

                "allow_extra": self._allow_extra,

            },

            "status": self.overall_status(),

        }



    def schema_report(self) -> dict[str, Any]:

        return {

            "schema": self._name,

            "version": self._version,

            "fields": self.fields,

            "summary": self.summary(),

        }



    def overall_status(self) -> str:

        if self.validate_name(
            self._name
        ):

            return "ready"

        return "invalid"



# ==============================================================================
# Part 9. Public API
# ==============================================================================


__all__ = [

    "Schema",

    "DEFAULT_SCHEMA_NAME",

    "DEFAULT_VERSION",

    "DEFAULT_STRICT",

    "DEFAULT_ALLOW_EXTRA",

]                