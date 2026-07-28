"""
SciOS Runtime Observability
===========================

Trace baggage container.

Baggage stores contextual metadata propagated
across tracing boundaries.

Responsibilities
----------------
- Store distributed tracing context.
- Maintain validated key/value metadata.
- Support serialization and snapshot lifecycle.
- Provide stable tracing context propagation API.

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# Part 1. Foundation
# ==============================================================================

import json

from collections.abc import Mapping
from copy import deepcopy
from typing import Any, ClassVar, TypeAlias


__all__: list[str]



# ==============================================================================
# Part 2. Constants & Type Aliases
# ==============================================================================


DEFAULT_BAGGAGE: dict[str, Any] = {}


BAGGAGE_VERSION = "1.0.0"


BAGGAGE_API_VERSION = "1"



BaggageMap: TypeAlias = dict[str, Any]


BaggageJSON: TypeAlias = dict[str, Any]



# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class BaggageError(Exception):
    """
    Base exception for baggage operations.
    """



class BaggageValidationError(BaggageError):
    """
    Raised when baggage validation fails.
    """



class BaggageSerializationError(BaggageError):
    """
    Raised when baggage serialization fails.
    """



# ==============================================================================
# Part 4. Core Class
# ==============================================================================


class Baggage:
    """
    Distributed trace baggage container.

    Baggage carries contextual metadata across
    distributed tracing boundaries.

    Typical keys
    ------------

    - service.name
    - service.version
    - trace.id
    - user.id
    - tenant.id
    - workflow.id


    Notes
    -----

    Keys are normalized and validated.

    Values should preferably remain JSON compatible.
    """


    VERSION: ClassVar[str] = BAGGAGE_VERSION

    API_VERSION: ClassVar[str] = BAGGAGE_API_VERSION


    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------


    def __init__(
        self,
        initial: BaggageMap | Mapping[str, Any] | None = None,
    ) -> None:
        """
        Create a baggage container.

        Parameters
        ----------
        initial:
            Optional initial baggage mapping.
        """


        self._items: BaggageMap = {}


        if initial is None:
            return


        if not isinstance(
            initial,
            Mapping,
        ):
            raise TypeError(
                "initial must be a mapping."
            )


        self.update(
            dict(initial)
        )

# ==============================================================================
# Part 5. Constructor & Properties
# ==============================================================================

    @property
    def data(
        self,
    ) -> BaggageMap:
        """
        Return deep copy of baggage data.
        """
        return deepcopy(
            self._items
        )


    @property
    def empty(
        self,
    ) -> bool:
        """
        Return True if baggage has no items.
        """
        return not bool(
            self._items
        )


    @property
    def size(
        self,
    ) -> int:
        """
        Return number of baggage items.
        """
        return len(
            self._items
        )


    def count(
        self,
    ) -> int:
        """
        Return number of baggage items.

        Alias of size.
        """
        return len(
            self._items
        )


    def keys(
        self,
    ):
        """
        Return baggage keys view.
        """
        return self._items.keys()


    def values(
        self,
    ):
        """
        Return baggage values view.
        """
        return self._items.values()


    def items(
        self,
    ):
        """
        Return baggage items view.
        """
        return self._items.items()



# ==============================================================================
# Part 6. Core API
# ==============================================================================


    def set(
        self,
        key: str,
        value: Any,
    ) -> "Baggage":
        """
        Set baggage value.
        """

        key = self._validate_key(
            key
        )

        self._items[key] = value

        return self



    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get baggage value.
        """

        key = self._validate_key(
            key
        )

        return self._items.get(
            key,
            default,
        )



    def get_or_set(
        self,
        key: str,
        default: Any,
    ) -> Any:
        """
        Get existing value or create default.
        """

        key = self._validate_key(
            key
        )

        return self._items.setdefault(
            key,
            default,
        )



    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Check whether key exists.
        """

        key = self._validate_key(
            key
        )

        return key in self._items



    def remove(
        self,
        key: str,
    ) -> Any:
        """
        Remove baggage value.
        """

        key = self._validate_key(
            key
        )

        return self._items.pop(
            key,
            None,
        )



    def pop(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Pop baggage value.
        """

        key = self._validate_key(
            key
        )

        return self._items.pop(
            key,
            default,
        )



    def clear(
        self,
    ) -> "Baggage":
        """
        Clear all baggage.
        """

        self._items.clear()

        return self



    def update(
        self,
        other: BaggageMap | "Baggage",
    ) -> "Baggage":
        """
        Update baggage values.
        """

        if isinstance(
            other,
            Baggage,
        ):

            source = other._items

        elif isinstance(
            other,
            dict,
        ):

            source = other

        else:

            raise TypeError(
                "Expected dict or Baggage."
            )


        self._validate_mapping(
            source
        )


        for key, value in source.items():

            self._items[key] = deepcopy(
                value
            )


        return self



    def merge(
        self,
        other: BaggageMap | "Baggage",
        *,
        overwrite: bool = False,
    ) -> "Baggage":
        """
        Merge baggage values.
        """

        if isinstance(
            other,
            Baggage,
        ):

            source = other._items

        elif isinstance(
            other,
            dict,
        ):

            source = other

        else:

            raise TypeError(
                "Expected dict or Baggage."
            )


        self._validate_mapping(
            source
        )


        for key, value in source.items():

            if (
                overwrite
                or key not in self._items
            ):

                self._items[key] = deepcopy(
                    value
                )


        return self



# ==============================================================================
# Part 7. Validation
# ==============================================================================


    @staticmethod
    def _validate_key(
        key: Any,
    ) -> str:
        """
        Validate baggage key.
        """

        if not isinstance(
            key,
            str,
        ):

            raise BaggageValidationError(
                "Baggage key must be string."
            )


        key = key.strip()


        if not key:

            raise BaggageValidationError(
                "Baggage key cannot be empty."
            )


        return key



    @classmethod
    def _validate_mapping(
        cls,
        mapping: BaggageMap,
    ) -> None:
        """
        Validate baggage mapping.
        """

        if not isinstance(
            mapping,
            dict,
        ):

            raise BaggageValidationError(
                "Expected dictionary."
            )


        for key in mapping:

            cls._validate_key(
                key
            )



    def validate(
        self,
    ) -> bool:
        """
        Validate current baggage.
        """

        self._validate_mapping(
            self._items
        )

        return True



# ==============================================================================
# Part 8. Serialization
# ==============================================================================


    def to_dict(
        self,
    ) -> BaggageMap:
        """
        Convert baggage into dictionary.
        """

        return deepcopy(
            self._items
        )



    @classmethod
    def from_dict(
        cls,
        data: BaggageMap,
    ) -> "Baggage":
        """
        Restore baggage from dictionary.
        """

        cls._validate_mapping(
            data
        )

        return cls(
            deepcopy(data)
        )



    def to_json(
        self,
        *,
        indent: int | None = 4,
        sort_keys: bool = True,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize baggage into JSON.
        """

        try:

            return json.dumps(
                self._items,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii,
                default=str,
            )

        except Exception as exc:

            raise BaggageSerializationError(
                "Failed to serialize baggage."
            ) from exc



    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "Baggage":
        """
        Restore baggage from JSON.
        """

        try:

            data = json.loads(
                value
            )

        except Exception as exc:

            raise BaggageSerializationError(
                "Invalid JSON."
            ) from exc


        if not isinstance(
            data,
            dict,
        ):

            raise BaggageSerializationError(
                "JSON must decode to dictionary."
            )


        return cls.from_dict(
            data
        )

# ==============================================================================
# Part 9. Snapshot / Clone
# ==============================================================================


    def snapshot(
        self,
    ) -> BaggageJSON:
        """
        Create immutable-style baggage snapshot.
        """

        return deepcopy(
            self._items
        )



    @classmethod
    def restore(
        cls,
        snapshot: BaggageJSON,
    ) -> "Baggage":
        """
        Restore baggage from snapshot.
        """

        return cls.from_dict(
            snapshot
        )



    def copy(
        self,
    ) -> "Baggage":
        """
        Create independent baggage copy.
        """

        return self.__class__(
            deepcopy(
                self._items
            )
        )



    def clone(
        self,
    ) -> "Baggage":
        """
        Create baggage clone.
        """

        return self.copy()



    def __copy__(
        self,
    ) -> "Baggage":
        """
        Support copy.copy().
        """

        return self.copy()



    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "Baggage":
        """
        Support copy.deepcopy().
        """

        if id(self) in memo:
            return memo[id(self)]


        result = self.__class__(
            deepcopy(
                self._items,
                memo,
            )
        )


        memo[id(self)] = result


        return result



# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return full diagnostic information.
        """

        valid = self.validate()


        return {

            "valid":
                valid,

            "count":
                self.count(),

            "size":
                self.size,

            "empty":
                self.empty,

            "keys":
                list(
                    self._items.keys()
                ),

            "types":
                {
                    key:
                    type(value).__name__

                    for key, value
                    in self._items.items()
                },
        }



    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return compact baggage summary.
        """

        return {

            "count":
                self.count(),

            "size":
                self.size,

            "empty":
                self.empty,

            "valid":
                self.validate(),

            "keys":
                list(
                    self._items.keys()
                ),
        }



# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"({self._items!r})"
        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (
            f"Baggage("
            f"count={self.count()}, "
            f"empty={self.empty}"
            f")"
        )



    def __len__(
        self,
    ) -> int:
        """
        Return number of baggage entries.
        """

        return self.size



    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate baggage keys.
        """

        return iter(
            self._items
        )



    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Check key existence.
        """

        return key in self._items



    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary style access.
        """

        key = self._validate_key(
            key
        )

        return self._items[key]



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary style assignment.
        """

        self.set(
            key,
            value,
        )



    def __delitem__(
        self,
        key: str,
    ) -> None:
        """
        Dictionary style deletion.
        """

        self.remove(
            key
        )



    def __bool__(
        self,
    ) -> bool:
        """
        True when baggage contains data.
        """

        return bool(
            self._items
        )



    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare baggage containers.
        """

        if not isinstance(
            other,
            Baggage,
        ):
            return NotImplemented


        return (
            self._items
            ==
            other._items
        )



    def __hash__(
        self,
    ) -> int:
        """
        Generate deterministic hash.
        """

        return hash(
            json.dumps(
                self._items,
                sort_keys=True,
                default=str,
                ensure_ascii=False,
            )
        )



# ==============================================================================
# Part 12. Public API
# ==============================================================================


__all__ = [

    # Constants

    "DEFAULT_BAGGAGE",
    "BAGGAGE_VERSION",
    "BAGGAGE_API_VERSION",


    # Type aliases

    "BaggageMap",
    "BaggageJSON",


    # Exceptions

    "BaggageError",
    "BaggageValidationError",
    "BaggageSerializationError",


    # Main class

    "Baggage",

]