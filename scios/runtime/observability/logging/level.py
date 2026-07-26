"""
SciOS-NG
runtime/observability/logging/level.py

Part 1. Foundation
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

from enum import IntEnum
from typing import Dict
from typing import Final
from typing import Mapping


# =============================================================================
# Constants
# =============================================================================

TRACE: Final[int] = 5
DEBUG: Final[int] = 10
INFO: Final[int] = 20
WARNING: Final[int] = 30
ERROR: Final[int] = 40
CRITICAL: Final[int] = 50
OFF: Final[int] = 100

DEFAULT_LEVEL: Final[int] = INFO


# =============================================================================
# Level Mapping
# =============================================================================

LEVEL_MAPPING: Dict[str, int] = {
    "TRACE": TRACE,
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL,
    "OFF": OFF,
}


# =============================================================================
# Level Names
# =============================================================================

LEVEL_NAMES: Mapping[int, str] = {
    TRACE: "TRACE",
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL",
    OFF: "OFF",
}


# =============================================================================
# Level Values
# =============================================================================

LEVEL_VALUES = tuple(LEVEL_NAMES.keys())


# =============================================================================
# LogLevel
# =============================================================================

class LogLevel(IntEnum):
    """
    Standard logging levels for SciOS-NG.

    The numeric values are compatible with the Python logging
    convention while adding TRACE and OFF.
    """

    TRACE = TRACE
    DEBUG = DEBUG
    INFO = INFO
    WARNING = WARNING
    ERROR = ERROR
    CRITICAL = CRITICAL
    OFF = OFF
# =============================================================================
# Part 2. Constructors
# =============================================================================

    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------

    @classmethod
    def from_name(
        cls,
        name: str,
    ) -> "LogLevel":
        """
        Create a LogLevel from its name.

        Parameters
        ----------
        name:
            Log level name (case-insensitive).

        Raises
        ------
        ValueError
            If the name is not a valid log level.
        """

        if not isinstance(name, str):
            raise TypeError("Log level name must be a string.")

        key = name.strip().upper()

        try:
            return cls(LEVEL_MAPPING[key])

        except KeyError as exc:
            raise ValueError(
                f"Unknown log level: {name!r}"
            ) from exc

    # -------------------------------------------------------------------------

    @classmethod
    def from_value(
        cls,
        value: int,
    ) -> "LogLevel":
        """
        Create a LogLevel from an integer value.

        Raises
        ------
        ValueError
            If the value is unsupported.
        """

        try:
            return cls(int(value))

        except ValueError as exc:
            raise ValueError(
                f"Unknown log level value: {value}"
            ) from exc

    # -------------------------------------------------------------------------

    @classmethod
    def normalize(
        cls,
        level: "LogLevel | str | int",
    ) -> "LogLevel":
        """
        Normalize a level into a LogLevel instance.

        Accepted types
        --------------
        - LogLevel
        - str
        - int
        """

        if isinstance(level, cls):
            return level

        if isinstance(level, str):
            return cls.from_name(level)

        if isinstance(level, int):
            return cls.from_value(level)

        raise TypeError(
            "Expected LogLevel, str or int."
        )

    # -------------------------------------------------------------------------

    @classmethod
    def parse(
        cls,
        value: object,
        *,
        default: "LogLevel | None" = None,
    ) -> "LogLevel":
        """
        Parse any supported object into a LogLevel.

        If parsing fails and a default is supplied,
        the default value is returned.
        """

        try:
            return cls.normalize(value)

        except Exception:

            if default is not None:
                return cls.normalize(default)

            raise
# =============================================================================
# Part 3. Properties
# =============================================================================

    # -------------------------------------------------------------------------
    # Basic Properties
    # -------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Return the canonical level name.
        """

        return LEVEL_NAMES[int(self)]

    # -------------------------------------------------------------------------

    @property
    def value(self) -> int:
        """
        Return the numeric value of this log level.
        """

        return int(self)

    # -------------------------------------------------------------------------

    @property
    def label(self) -> str:
        """
        Human-readable label.

        Example
        -------
        LogLevel.WARNING.label -> "Warning"
        """

        return self.name.title()

    # -------------------------------------------------------------------------
    # Level Classification
    # -------------------------------------------------------------------------

    @property
    def is_trace(self) -> bool:
        """
        Whether this is TRACE.
        """

        return self is LogLevel.TRACE

    # -------------------------------------------------------------------------

    @property
    def is_debug(self) -> bool:
        """
        Whether this is DEBUG.
        """

        return self is LogLevel.DEBUG

    # -------------------------------------------------------------------------

    @property
    def is_info(self) -> bool:
        """
        Whether this is INFO.
        """

        return self is LogLevel.INFO

    # -------------------------------------------------------------------------

    @property
    def is_warning(self) -> bool:
        """
        Whether this is WARNING.
        """

        return self is LogLevel.WARNING

    # -------------------------------------------------------------------------

    @property
    def is_error(self) -> bool:
        """
        Whether this is ERROR.
        """

        return self is LogLevel.ERROR

    # -------------------------------------------------------------------------

    @property
    def is_critical(self) -> bool:
        """
        Whether this is CRITICAL.
        """

        return self is LogLevel.CRITICAL
# =============================================================================
# Part 4. Comparison API
# =============================================================================

    # -------------------------------------------------------------------------
    # Comparison API
    # -------------------------------------------------------------------------

    def equals(
        self,
        other: "LogLevel | str | int",
    ) -> bool:
        """
        Check whether this level is equal to another level.

        Parameters
        ----------
        other:
            LogLevel, level name or numeric value.
        """

        other = self.normalize(other)

        return self is other

    # -------------------------------------------------------------------------

    def higher_than(
        self,
        other: "LogLevel | str | int",
    ) -> bool:
        """
        Return True if this level has a higher severity than
        the specified level.
        """

        other = self.normalize(other)

        return self.value > other.value

    # -------------------------------------------------------------------------

    def lower_than(
        self,
        other: "LogLevel | str | int",
    ) -> bool:
        """
        Return True if this level has a lower severity than
        the specified level.
        """

        other = self.normalize(other)

        return self.value < other.value

    # -------------------------------------------------------------------------

    def allows(
        self,
        message_level: "LogLevel | str | int",
    ) -> bool:
        """
        Determine whether a message should be emitted.

        This instance is treated as the minimum configured
        logging level.

        Examples
        --------
        LogLevel.INFO.allows(LogLevel.ERROR) -> True
        LogLevel.INFO.allows(LogLevel.DEBUG) -> False
        """

        message_level = self.normalize(message_level)

        return message_level.value >= self.value

    # -------------------------------------------------------------------------

    def compare(
        self,
        other: "LogLevel | str | int",
    ) -> int:
        """
        Compare this level with another.

        Returns
        -------
        int
            1  : self > other
            0  : self == other
           -1  : self < other
        """

        other = self.normalize(other)

        if self.value > other.value:
            return 1

        if self.value < other.value:
            return -1

        return 0
# =============================================================================
# Part 5. Conversion API
# =============================================================================

    # -------------------------------------------------------------------------
    # Conversion API
    # -------------------------------------------------------------------------

    def to_int(self) -> int:
        """
        Convert this log level to its integer value.

        Returns
        -------
        int
            Numeric representation of the log level.
        """

        return int(self)

    # -------------------------------------------------------------------------

    def to_str(self) -> str:
        """
        Convert this log level to its canonical string name.

        Returns
        -------
        str
            Canonical log level name.
        """

        return self.name

    # -------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, object]:
        """
        Convert this log level to a dictionary.

        Returns
        -------
        Dict[str, object]
            Dictionary representation.
        """

        return {
            "name": self.name,
            "value": self.value,
            "label": self.label,
        }

    # -------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int | None = None,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Convert this log level to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
        )

    # -------------------------------------------------------------------------

    def serialize(self) -> Dict[str, object]:
        """
        Generic serialization interface.

        Alias of :meth:`to_dict`.
        """

        return self.to_dict()
# =============================================================================
# Part 6. Validation
# =============================================================================

    # -------------------------------------------------------------------------
    # Validation API
    # -------------------------------------------------------------------------

    @classmethod
    def is_valid(
        cls,
        value: object,
    ) -> bool:
        """
        Check whether a value is a valid log level.

        Accepted values:
        - LogLevel instance
        - Integer level value
        - String level name
        """

        try:

            cls.normalize(value)

            return True

        except (TypeError, ValueError):

            return False

    # -------------------------------------------------------------------------

    @classmethod
    def validate(
        cls,
        value: object,
    ) -> "LogLevel":
        """
        Validate and return a normalized LogLevel.

        Raises
        ------
        ValueError
            If value is not a valid log level.
        """

        if not cls.is_valid(value):

            raise ValueError(
                f"Invalid log level: {value!r}"
            )

        return cls.normalize(value)

    # -------------------------------------------------------------------------

    @classmethod
    def supported_levels(
        cls,
    ) -> list["LogLevel"]:
        """
        Return all supported logging levels.
        """

        return list(cls)

    # -------------------------------------------------------------------------

    @classmethod
    def default_level(
        cls,
    ) -> "LogLevel":
        """
        Return the default logging level.
        """

        return cls(DEFAULT_LEVEL)
# =============================================================================
# Part 7. Utilities
# =============================================================================

    # -------------------------------------------------------------------------
    # Utility API
    # -------------------------------------------------------------------------

    def next_level(self) -> "LogLevel":
        """
        Return the next higher severity level.

        Example
        -------
        INFO -> WARNING
        WARNING -> ERROR
        """

        levels = list(LogLevel)

        try:
            index = levels.index(self)

            return levels[
                min(index + 1, len(levels) - 1)
            ]

        except ValueError:
            return self

    # -------------------------------------------------------------------------

    def previous_level(self) -> "LogLevel":
        """
        Return the previous lower severity level.

        Example
        -------
        WARNING -> INFO
        INFO -> DEBUG
        """

        levels = list(LogLevel)

        try:
            index = levels.index(self)

            return levels[
                max(index - 1, 0)
            ]

        except ValueError:
            return self

    # -------------------------------------------------------------------------

    @classmethod
    def min_level(
        cls,
    ) -> "LogLevel":
        """
        Return the lowest supported log level.
        """

        return cls(min(LEVEL_VALUES))

    # -------------------------------------------------------------------------

    @classmethod
    def max_level(
        cls,
    ) -> "LogLevel":
        """
        Return the highest supported log level.
        """

        return cls(max(LEVEL_VALUES))

    # -------------------------------------------------------------------------

    @classmethod
    def clamp(
        cls,
        value: "LogLevel | str | int",
        minimum: "LogLevel | str | int",
        maximum: "LogLevel | str | int",
    ) -> "LogLevel":
        """
        Clamp a log level between minimum and maximum.

        Examples
        --------
        clamp(DEBUG, INFO, ERROR)
        -> INFO

        clamp(CRITICAL, INFO, ERROR)
        -> ERROR
        """

        value = cls.normalize(value)
        minimum = cls.normalize(minimum)
        maximum = cls.normalize(maximum)

        if minimum.value > maximum.value:
            raise ValueError(
                "Minimum level cannot be greater than maximum level."
            )

        if value.value < minimum.value:
            return minimum

        if value.value > maximum.value:
            return maximum

        return value
# =============================================================================
# Part 8. Serialization
# =============================================================================

    # -------------------------------------------------------------------------
    # Serialization API
    # -------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, object],
    ) -> "LogLevel":
        """
        Create a LogLevel from a dictionary.

        Accepted formats
        ----------------
        {
            "name": "INFO",
            "value": 20
        }

        or

        {
            "level": "ERROR"
        }
        """

        if not isinstance(data, dict):
            raise TypeError(
                "Serialized LogLevel data must be a dictionary."
            )

        if "name" in data:
            return cls.from_name(
                str(data["name"])
            )

        if "level" in data:
            return cls.normalize(
                data["level"]
            )

        if "value" in data:
            return cls.from_value(
                int(data["value"])
            )

        raise ValueError(
            "Invalid serialized LogLevel data."
        )

    # -------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "LogLevel":
        """
        Create a LogLevel from JSON string.
        """

        if not isinstance(data, str):
            raise TypeError(
                "JSON data must be a string."
            )

        return cls.from_dict(
            json.loads(data)
        )

    # -------------------------------------------------------------------------

    @classmethod
    def deserialize(
        cls,
        data: Dict[str, object] | str | int,
    ) -> "LogLevel":
        """
        Generic deserialization interface.

        Supports:
        - dict
        - JSON string
        - integer value
        - string name
        """

        if isinstance(data, dict):
            return cls.from_dict(data)

        if isinstance(data, str):

            try:
                return cls.from_json(data)

            except json.JSONDecodeError:

                return cls.from_name(data)

        if isinstance(data, int):

            return cls.from_value(data)

        raise TypeError(
            f"Unsupported deserialization type: {type(data)}"
        )

    # -------------------------------------------------------------------------

    def copy(
        self,
    ) -> "LogLevel":
        """
        Return a copy of this LogLevel.

        Enum members are immutable, therefore
        returning self is safe.
        """

        return self
# =============================================================================
# Part 9. Events
# =============================================================================

    # -------------------------------------------------------------------------
    # Event Hooks
    # -------------------------------------------------------------------------

    def before_change(
        self,
        new_level: "LogLevel | str | int",
    ) -> None:
        """
        Emit event before changing log level.

        Note:
        LogLevel is immutable, so this event is intended
        for external controllers or configuration managers.
        """

        self.emit(
            "before_change",
            current=self,
            new=self.normalize(new_level),
        )

    # -------------------------------------------------------------------------

    def after_change(
        self,
        new_level: "LogLevel | str | int",
    ) -> None:
        """
        Emit event after changing log level.
        """

        self.emit(
            "after_change",
            current=self,
            new=self.normalize(new_level),
        )

    # -------------------------------------------------------------------------
    # Hook Registry
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Callable[..., object],
    ) -> Callable[..., object]:
        """
        Register an event callback.

        Parameters
        ----------
        event:
            Event name.

        callback:
            Function executed when event occurs.
        """

        if not callable(callback):
            raise TypeError(
                "Hook callback must be callable."
            )

        if not hasattr(self, "_hooks"):

            self._hooks = {}

        self._hooks.setdefault(
            event,
            [],
        ).append(callback)

        return callback

    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback: Callable[..., object],
    ) -> bool:
        """
        Remove a registered hook.
        """

        hooks = getattr(
            self,
            "_hooks",
            {},
        )

        callbacks = hooks.get(event)

        if not callbacks:
            return False

        try:

            callbacks.remove(callback)

            if not callbacks:
                hooks.pop(event, None)

            return True

        except ValueError:

            return False

    # -------------------------------------------------------------------------

    def emit(
        self,
        event: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Emit an event to registered callbacks.
        """

        hooks = getattr(
            self,
            "_hooks",
            {},
        )

        callbacks = tuple(
            hooks.get(event, [])
        )

        for callback in callbacks:

            try:

                callback(
                    *args,
                    **kwargs,
                )

            except Exception:
                # Event failures must not break logging runtime.
                continue
# =============================================================================
# Part 10. Python Protocols
# =============================================================================

    # -------------------------------------------------------------------------
    # Representation Protocols
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}."
            f"{self.name}"
            f"({self.value})"
        )

    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return self.name

    # -------------------------------------------------------------------------
    # Numeric Protocol
    # -------------------------------------------------------------------------

    def __int__(self) -> int:
        """
        Return numeric logging value.
        """

        return self.value

    # -------------------------------------------------------------------------
    # Hash Protocol
    # -------------------------------------------------------------------------

    def __hash__(self) -> int:
        """
        Return hash value.

        Enables usage as:
        - dictionary key
        - set member
        """

        return hash(self.value)

    # -------------------------------------------------------------------------
    # Comparison Protocols
    # -------------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality comparison.
        """

        if isinstance(other, LogLevel):

            return self.value == other.value

        if isinstance(other, (str, int)):

            try:

                return self.value == self.normalize(
                    other
                ).value

            except Exception:

                return False

        return False

    # -------------------------------------------------------------------------

    def __lt__(
        self,
        other: object,
    ) -> bool:
        """
        Less-than comparison.
        """

        return (
            self.value
            <
            self.normalize(other).value
        )

    # -------------------------------------------------------------------------

    def __le__(
        self,
        other: object,
    ) -> bool:
        """
        Less-than or equal comparison.
        """

        return (
            self.value
            <=
            self.normalize(other).value
        )

    # -------------------------------------------------------------------------

    def __gt__(
        self,
        other: object,
    ) -> bool:
        """
        Greater-than comparison.
        """

        return (
            self.value
            >
            self.normalize(other).value
        )

    # -------------------------------------------------------------------------

    def __ge__(
        self,
        other: object,
    ) -> bool:
        """
        Greater-than or equal comparison.
        """

        return (
            self.value
            >=
            self.normalize(other).value
        )

    # -------------------------------------------------------------------------
    # Boolean Protocol
    # -------------------------------------------------------------------------

    def __bool__(self) -> bool:
        """
        Boolean evaluation.

        OFF is considered disabled.
        """

        return self is not LogLevel.OFF                                                                        