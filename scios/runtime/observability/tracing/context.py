"""
SciOS Runtime Observability
===========================

Trace execution context.

Responsibilities
----------------
- Store trace identity.
- Store span identity.
- Maintain parent relationship.
- Carry baggage propagation.
- Store trace metadata.
- Provide serialization foundation.

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# Part 1. Foundation
# ==============================================================================

import json
import uuid


from copy import deepcopy
from typing import Any, Iterator, TypeAlias


from .baggage import Baggage


__all__: list[str]



# ==============================================================================
# Part 2. Constants & Type Aliases
# ==============================================================================


DEFAULT_TRACE_FLAGS: int = 0


CONTEXT_VERSION: str = "1.0.0"


CONTEXT_API_VERSION: str = "1"



ContextMap: TypeAlias = dict[str, Any]


ContextJSON: TypeAlias = dict[str, Any]



# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class ContextError(Exception):
    """
    Base exception for TraceContext.
    """



class ContextValidationError(ContextError):
    """
    Raised when context validation fails.
    """



class ContextSerializationError(ContextError):
    """
    Raised when context serialization fails.
    """



# ==============================================================================
# Part 4. Core Class
# ==============================================================================


class TraceContext:
    """
    Distributed tracing execution context.

    TraceContext is the carrier object between tracing components.

    Contains
    --------
    trace_id:
        Global trace identifier.

    span_id:
        Current span identifier.

    parent_span_id:
        Parent span relationship.

    baggage:
        Distributed metadata container.

    attributes:
        Span/context attributes.

    metadata:
        Internal runtime metadata.

    flags:
        Trace execution flags.
    """


    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------


    def __init__(
        self,
        *,
        trace_id: str | None = None,
        span_id: str | None = None,
        parent_span_id: str | None = None,
        baggage: Baggage | None = None,
        attributes: ContextMap | None = None,
        metadata: ContextMap | None = None,
        flags: int = DEFAULT_TRACE_FLAGS,
    ) -> None:
        """
        Create trace context.
        """


        self._trace_id: str = (
            trace_id
            or self._generate_id()
        )


        self._span_id: str = (
            span_id
            or self._generate_id()
        )


        self._parent_span_id: str | None = (
            parent_span_id
        )


        self._baggage: Baggage = (
            baggage.copy()
            if baggage is not None
            else Baggage()
        )


        self._attributes: ContextMap = {}


        self._metadata: ContextMap = {}


        self._flags: int = flags



        if attributes is not None:

            if not isinstance(
                attributes,
                dict,
            ):
                raise TypeError(
                    "attributes must be dictionary."
                )


            self._attributes.update(
                deepcopy(attributes)
            )



        if metadata is not None:

            if not isinstance(
                metadata,
                dict,
            ):
                raise TypeError(
                    "metadata must be dictionary."
                )


            self._metadata.update(
                deepcopy(metadata)
            )



    # ------------------------------------------------------------------
    # Internal Utilities
    # ------------------------------------------------------------------


    @staticmethod
    def _generate_id() -> str:
        """
        Generate context identifier.
        """

        return uuid.uuid4().hex



    # ------------------------------------------------------------------
    # Internal State
    # ------------------------------------------------------------------


    def _clone_mapping(
        self,
        value: ContextMap,
    ) -> ContextMap:
        """
        Return deep copy mapping.
        """

        return deepcopy(
            value
        )
# ==============================================================================
# Part 5. Constructor & Properties
# ==============================================================================


    @property
    def trace_id(
        self,
    ) -> str:
        """
        Return trace identifier.
        """

        return self._trace_id



    @property
    def span_id(
        self,
    ) -> str:
        """
        Return span identifier.
        """

        return self._span_id



    @property
    def parent_span_id(
        self,
    ) -> str | None:
        """
        Return parent span identifier.
        """

        return self._parent_span_id



    @property
    def baggage(
        self,
    ) -> Baggage:
        """
        Return baggage container.
        """

        return self._baggage



    @property
    def attributes(
        self,
    ) -> ContextMap:
        """
        Return context attributes copy.
        """

        return deepcopy(
            self._attributes
        )



    @property
    def metadata(
        self,
    ) -> ContextMap:
        """
        Return context metadata copy.
        """

        return deepcopy(
            self._metadata
        )



    @property
    def flags(
        self,
    ) -> int:
        """
        Return trace flags.
        """

        return self._flags



    @property
    def empty(
        self,
    ) -> bool:
        """
        Return True when no attributes and metadata exist.
        """

        return (
            not self._attributes
            and
            not self._metadata
            and
            len(self._baggage) == 0
        )



    @property
    def size(
        self,
    ) -> int:
        """
        Return context item count.
        """

        return (
            len(self._attributes)
            +
            len(self._metadata)
            +
            len(self._baggage)
        )



    def count(
        self,
    ) -> int:
        """
        Alias of size.
        """

        return self.size



# ==============================================================================
# Part 6. Core API
# ==============================================================================


    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "TraceContext":
        """
        Set context attribute.
        """

        self._validate_key(
            key
        )

        self._attributes[key] = value

        return self



    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get context attribute.
        """

        self._validate_key(
            key
        )

        return self._attributes.get(
            key,
            default,
        )



    def remove_attribute(
        self,
        key: str,
    ) -> Any:
        """
        Remove context attribute.
        """

        self._validate_key(
            key
        )

        return self._attributes.pop(
            key,
            None,
        )



    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> "TraceContext":
        """
        Set metadata value.
        """

        self._validate_key(
            key
        )

        self._metadata[key] = value

        return self



    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get metadata value.
        """

        self._validate_key(
            key
        )

        return self._metadata.get(
            key,
            default,
        )



    def remove_metadata(
        self,
        key: str,
    ) -> Any:
        """
        Remove metadata.
        """

        self._validate_key(
            key
        )

        return self._metadata.pop(
            key,
            None,
        )



    def update_attributes(
        self,
        values: ContextMap,
    ) -> "TraceContext":
        """
        Update attributes.
        """

        self._validate_mapping(
            values
        )

        self._attributes.update(
            deepcopy(values)
        )

        return self



    def update_metadata(
        self,
        values: ContextMap,
    ) -> "TraceContext":
        """
        Update metadata.
        """

        self._validate_mapping(
            values
        )

        self._metadata.update(
            deepcopy(values)
        )

        return self



    def set_baggage(
        self,
        baggage: Baggage,
    ) -> "TraceContext":
        """
        Replace baggage.
        """

        if not isinstance(
            baggage,
            Baggage,
        ):
            raise TypeError(
                "baggage must be Baggage."
            )


        self._baggage = baggage.copy()

        return self



    def child(
        self,
        *,
        span_id: str | None = None,
    ) -> "TraceContext":
        """
        Create child span context.
        """

        return TraceContext(
            trace_id=self._trace_id,
            span_id=(
                span_id
                or self._generate_id()
            ),
            parent_span_id=self._span_id,
            baggage=self._baggage,
            attributes=self._attributes,
            metadata=self._metadata,
            flags=self._flags,
        )



    def clear(
        self,
    ) -> "TraceContext":
        """
        Clear mutable context data.
        """

        self._attributes.clear()

        self._metadata.clear()

        self._baggage.clear()

        return self



# ==============================================================================
# Part 7. Validation
# ==============================================================================


    @staticmethod
    def _validate_key(
        key: Any,
    ) -> str:
        """
        Validate context key.
        """

        if not isinstance(
            key,
            str,
        ):
            raise ContextValidationError(
                "Key must be string."
            )


        key = key.strip()


        if not key:
            raise ContextValidationError(
                "Key cannot be empty."
            )


        return key



    @classmethod
    def _validate_mapping(
        cls,
        mapping: ContextMap,
    ) -> None:
        """
        Validate mapping.
        """

        if not isinstance(
            mapping,
            dict,
        ):
            raise ContextValidationError(
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
        Validate context state.

        Returns:
            bool:
                True  -> valid context
                False -> invalid identity state

        Raises:
            ContextValidationError:
                invalid structure/type.
        """


        # --------------------------------------------------------------
        # Identity validation
        # --------------------------------------------------------------

        if not isinstance(
            self._trace_id,
            str,
        ):
            raise ContextValidationError(
                "Invalid trace_id type."
            )


        if not self._trace_id.strip():
            return False



        if not isinstance(
            self._span_id,
            str,
        ):
            raise ContextValidationError(
                "Invalid span_id type."
            )


        if not self._span_id.strip():
            return False



        # --------------------------------------------------------------
        # Mapping validation
        # --------------------------------------------------------------

        self._validate_mapping(
            self._attributes
        )


        self._validate_mapping(
            self._metadata
        )


        # --------------------------------------------------------------
        # Baggage validation
        # --------------------------------------------------------------

        if self._baggage is not None:
            if not self._baggage.validate():
                return False


        return True

# ==============================================================================
# Part 8. Serialization
# ==============================================================================


    def to_dict(
        self,
    ) -> ContextJSON:
        """
        Convert context to dictionary.
        """

        return {

            "trace_id":
                self._trace_id,


            "span_id":
                self._span_id,


            "parent_span_id":
                self._parent_span_id,


            "flags":
                self._flags,


            "baggage":
                self._baggage.to_dict(),


            "attributes":
                deepcopy(
                    self._attributes
                ),


            "metadata":
                deepcopy(
                    self._metadata
                ),
        }



    @classmethod
    def from_dict(
        cls,
        data: ContextJSON,
    ) -> "TraceContext":
        """
        Restore context from dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise ContextValidationError(
                "Context data must be dictionary."
            )


        return cls(
            trace_id=data.get(
                "trace_id"
            ),
            span_id=data.get(
                "span_id"
            ),
            parent_span_id=data.get(
                "parent_span_id"
            ),
            flags=data.get(
                "flags",
                DEFAULT_TRACE_FLAGS,
            ),
            baggage=Baggage.from_dict(
                data.get(
                    "baggage",
                    {},
                )
            ),
            attributes=data.get(
                "attributes",
                {},
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )



    def to_json(
        self,
        *,
        indent: int | None = 4,
        sort_keys: bool = True,
    ) -> str:
        """
        Serialize context to JSON.
        """

        try:

            return json.dumps(
                self.to_dict(),
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=False,
            )

        except Exception as exc:

            raise ContextSerializationError(
                "Failed to serialize context."
            ) from exc



    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "TraceContext":
        """
        Restore context from JSON.
        """

        try:

            data = json.loads(
                value
            )

        except Exception as exc:

            raise ContextSerializationError(
                "Invalid JSON."
            ) from exc


        return cls.from_dict(
            data
        )
# ==============================================================================
# Part 9. Snapshot / Clone
# ==============================================================================


    def snapshot(
        self,
    ) -> ContextJSON:
        """
        Create immutable snapshot representation.
        """

        return self.to_dict()



    @classmethod
    def restore(
        cls,
        snapshot: ContextJSON,
    ) -> "TraceContext":
        """
        Restore context from snapshot.
        """

        return cls.from_dict(
            snapshot
        )



    def copy(
        self,
    ) -> "TraceContext":
        """
        Create independent context copy.
        """

        return self.__class__.from_dict(
            deepcopy(
                self.to_dict()
            )
        )



    def clone(
        self,
    ) -> "TraceContext":
        """
        Clone context.

        Alias of copy().
        """

        return self.copy()



    def __copy__(
        self,
    ) -> "TraceContext":
        """
        Support copy.copy().
        """

        return self.copy()



    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "TraceContext":
        """
        Support copy.deepcopy().
        """

        result = self.__class__.from_dict(
            deepcopy(
                self.to_dict(),
                memo,
            )
        )


        memo[id(self)] = result


        return result



# ==============================================================================
# Part10. Diagnostics
# ==============================================================================


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed diagnostics.
        """

        return {

            "valid":
                self.validate(),


            "trace_id":
                self.trace_id,


            "span_id":
                self.span_id,


            "parent_span_id":
                self.parent_span_id,


            "flags":
                self.flags,


            "size":
                self.size,


            "count":
                self.count(),


            "empty":
                self.empty,


            "attributes":
                list(
                    self._attributes.keys()
                ),


            "metadata":
                list(
                    self._metadata.keys()
                ),


            "baggage_size":
                len(
                    self._baggage
                ),
        }



    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return compact context summary.
        """

        return {

            "trace_id":
                self.trace_id,


            "span_id":
                self.span_id,


            "parent_span_id":
                self.parent_span_id,


            "size":
                self.size,


            "empty":
                self.empty,


            "valid":
                self.validate(),
        }



# ==============================================================================
# Part11. Python Protocols
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"("
            f"trace_id={self.trace_id!r}, "
            f"span_id={self.span_id!r}"
            f")"
        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (
            f"TraceContext("
            f"trace_id={self.trace_id}, "
            f"span_id={self.span_id}, "
            f"size={self.size}"
            f")"
        )



    def __len__(
        self,
    ) -> int:
        """
        Return total context entries.
        """

        return len(
            self.to_dict()
        )



    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate all context keys.
        """

        return iter(
            self.to_dict()
        )



    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Check context key existence.
        """

        return key in self.to_dict()



    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary style lookup.
        """

        self._validate_key(
            key
        )


        if key in self._attributes:
            return self._attributes[key]


        if key == "trace_id":
            return self.trace_id


        if key == "span_id":
            return self.span_id


        if key == "parent_span_id":
            return self.parent_span_id


        if key in self._metadata:
            return self._metadata[key]


        raise KeyError(
            key
        )



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary style assignment.
        """

        self.set_attribute(
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

        if key in self._attributes:
            self.remove_attribute(
                key
            )
            return


        if key == "trace_id":
            self._trace_id = ""
            return


        if key == "span_id":
            self._span_id = ""
            return


        if key == "parent_span_id":
            self._parent_span_id = None
            return


        raise KeyError(
            key
        )



    def __bool__(
        self,
    ) -> bool:
        """
        Return True when context contains identity or data.
        """

        return bool(
            self.trace_id
            or
            self.span_id
            or
            self._attributes
            or
            self._metadata
        )



    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare contexts.
        """

        if not isinstance(
            other,
            TraceContext,
        ):
            return NotImplemented


        return (
            self.to_dict()
            ==
            other.to_dict()
        )



    def __hash__(
        self,
    ) -> int:
        """
        Return deterministic hash.
        """

        return hash(
            json.dumps(
                self.to_dict(),
                sort_keys=True,
                default=str,
                ensure_ascii=False,
            )
        )

# ==============================================================================
# Part 13. TraceScope
# ==============================================================================


class TraceScope:
    """
    Runtime scope for a TraceContext.
    """


    def __init__(
        self,
        context: TraceContext,
    ) -> None:

        if not isinstance(
            context,
            TraceContext,
        ):
            raise ContextValidationError(
                "context must be TraceContext."
            )

        self._context = context

        self._active = False


    @property
    def context(
        self,
    ) -> TraceContext:

        return self._context


    @property
    def active(
        self,
    ) -> bool:

        return self._active


    def activate(
        self,
    ) -> "TraceScope":

        self._active = True

        return self


    def deactivate(
        self,
    ) -> "TraceScope":

        self._active = False

        return self


    def __enter__(
        self,
    ) -> TraceContext:

        self.activate()

        return self._context


    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> bool:

        self.deactivate()

        return False


    def __bool__(
        self,
    ) -> bool:

        return self._active


    def __repr__(
        self,
    ) -> str:

        return (
            f"TraceScope("
            f"active={self._active}, "
            f"trace_id={self._context.trace_id!r}"
            f")"
        )

# ==============================================================================
# Part 14. SpanScope
# ==============================================================================


class SpanScope:
    """
    Runtime scope for span-like objects.
    """


    def __init__(
        self,
        span: Any,
    ) -> None:

        self._span = span

        self._active = False


    @property
    def span(
        self,
    ) -> Any:

        return self._span


    @property
    def active(
        self,
    ) -> bool:

        return self._active


    def activate(
        self,
    ) -> "SpanScope":

        self._active = True

        if hasattr(
            self._span,
            "start",
        ):
            self._span.start()

        return self


    def deactivate(
        self,
    ) -> "SpanScope":

        self._active = False

        if hasattr(
            self._span,
            "finish",
        ):
            self._span.finish()

        return self


    def __enter__(
        self,
    ) -> Any:

        self.activate()

        return self._span


    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> bool:

        if (
            exc is not None
            and
            hasattr(
                self._span,
                "record_exception",
            )
        ):
            self._span.record_exception(
                exc
            )

        self.deactivate()

        return False


    def __bool__(
        self,
    ) -> bool:

        return self._active


    def __repr__(
        self,
    ) -> str:

        return (
            f"SpanScope("
            f"active={self._active}"
            f")"
        )

# ==============================================================================
# Part 12. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_TRACE_FLAGS",

    "CONTEXT_VERSION",

    "CONTEXT_API_VERSION",


    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "ContextMap",

    "ContextJSON",


    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "ContextError",

    "ContextValidationError",

    "ContextSerializationError",


    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    "TraceContext",

    "TraceScope",

    "SpanScope",
]