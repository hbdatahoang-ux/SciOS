"""
SciOS-NG Logging Filter

Runtime-managed logging filter with lifecycle, rule registry,
statistics, metadata, and hook support.
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

import copy
import json
import time
import uuid

from datetime import datetime, timezone
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    TypeAlias,
)

# =============================================================================
# Constants
# =============================================================================

DEFAULT_FILTER_NAME = "filter"

DEFAULT_PRIORITY = 100

DEFAULT_ENABLED = True

DEFAULT_FROZEN = False

DEFAULT_CLOSED = False

DEFAULT_RULE_CAPACITY = 1024

# =============================================================================
# Type Aliases
# =============================================================================

LogRecord: TypeAlias = Mapping[str, Any]

FilterRule: TypeAlias = Callable[[LogRecord], bool]

Hook: TypeAlias = Callable[..., Any]

Statistics: TypeAlias = Dict[str, Any]

Metadata: TypeAlias = Dict[str, Any]

# =============================================================================
# LogFilter
# =============================================================================


class LogFilter:
    """
    Runtime-managed logging filter.

    Responsibilities
    ----------------
    • Filter log records
    • Manage filter rules
    • Lifecycle management
    • Runtime statistics
    • Snapshot / restore
    • Event hooks

    A filter returns:

        True  -> record accepted

        False -> record rejected
    """

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_FILTER_NAME,
        *,
        priority: int = DEFAULT_PRIORITY,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:

        # -----------------------------------------------------------------
        # Identity
        # -----------------------------------------------------------------

        self.id = str(
            uuid.uuid4()
        )

        self.name = name

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at

        # -----------------------------------------------------------------
        # Runtime State
        # -----------------------------------------------------------------

        self._enabled = enabled

        self._frozen = DEFAULT_FROZEN

        self._closed = DEFAULT_CLOSED

        self._priority = priority

        # -----------------------------------------------------------------
        # Filter Configuration
        # -----------------------------------------------------------------

        self._rules: Dict[str, Dict[str, Any]] = {}

        self._hooks: Dict[str, List[Hook]] = {}

        self._capacity = DEFAULT_RULE_CAPACITY

        # -----------------------------------------------------------------
        # Metadata
        # -----------------------------------------------------------------

        self._metadata: Metadata = dict(
            metadata or {}
        )

        # -----------------------------------------------------------------
        # Statistics
        # -----------------------------------------------------------------

        self._statistics: Statistics = {

            "evaluated": 0,

            "accepted": 0,

            "rejected": 0,

            "errors": 0,

            "rule_calls": 0,

            "latency": 0.0,

        }

    # -------------------------------------------------------------------------
    # Foundation Helpers
    # -------------------------------------------------------------------------

    def _touch(self) -> None:
        """
        Update modification timestamp.
        """

        self.updated_at = datetime.now(
            timezone.utc
        )

    def _record_latency(
        self,
        started: float,
    ) -> None:
        """
        Update accumulated execution latency.
        """

        self._statistics["latency"] += (
            time.perf_counter() - started
        )
# =============================================================================
# Part 2. Properties
# =============================================================================

    # -------------------------------------------------------------------------
    # ID
    # -------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> str:
        """
        Unique filter identifier.
        """

        return self._id


    @id.setter
    def id(
        self,
        value: str,
    ) -> None:

        self._id = str(value)


    # -------------------------------------------------------------------------
    # Name
    # -------------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Filter name.
        """

        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        self._name = str(value)


    # -------------------------------------------------------------------------
    # Enabled
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Whether the filter is enabled.
        """

        return self._enabled


    # -------------------------------------------------------------------------
    # Priority
    # -------------------------------------------------------------------------

    @property
    def priority(
        self,
    ) -> int:
        """
        Filter execution priority.
        Lower values execute first.
        """

        return self._priority


    @priority.setter
    def priority(
        self,
        value: int,
    ) -> None:

        self._priority = int(value)

        self._touch()


    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Filter metadata.
        """

        return self._metadata


    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> Statistics:
        """
        Runtime statistics.
        """

        return self._statistics


    # -------------------------------------------------------------------------
    # Age
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Filter lifetime in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()


    # -------------------------------------------------------------------------
    # Filter Count
    # -------------------------------------------------------------------------

    @property
    def filter_count(
        self,
    ) -> int:
        """
        Number of registered rules.
        """

        return len(
            self._rules
        )
# =============================================================================
# Part 3. Filter API
# =============================================================================

    # -------------------------------------------------------------------------
    # Filter
    # -------------------------------------------------------------------------

    def filter(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Evaluate a log record.

        Alias of evaluate().
        """

        return self.evaluate(
            record
        )


    # -------------------------------------------------------------------------
    # Allow
    # -------------------------------------------------------------------------

    def allow(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Explicitly allow a record.
        """

        self._statistics["accepted"] += 1

        return True


    # -------------------------------------------------------------------------
    # Reject
    # -------------------------------------------------------------------------

    def reject(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Explicitly reject a record.
        """

        self._statistics["rejected"] += 1

        return False


    # -------------------------------------------------------------------------
    # Matches
    # -------------------------------------------------------------------------

    def matches(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Check whether every enabled rule matches.

        Returns
        -------
        bool
            True if all enabled rules pass.
        """

        for entry in self._rules.values():

            if not entry["enabled"]:

                continue

            rule = entry["object"]

            self._statistics["rule_calls"] += 1

            if not rule(record):

                return False

        return True


    # -------------------------------------------------------------------------
    # Evaluate
    # -------------------------------------------------------------------------

    def evaluate(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Execute filter pipeline.
        """

        if not self._enabled:

            return True

        if self._closed:

            return False

        started = time.perf_counter()

        self._statistics["evaluated"] += 1

        try:

            accepted = self.matches(
                record
            )

            if accepted:

                self._statistics["accepted"] += 1

            else:

                self._statistics["rejected"] += 1

            return accepted

        except Exception:

            self._statistics["errors"] += 1

            return False

        finally:

            self._record_latency(
                started
            )


    # -------------------------------------------------------------------------
    # Apply
    # -------------------------------------------------------------------------

    def apply(
        self,
        record: LogRecord,
    ) -> Optional[LogRecord]:
        """
        Apply filter to a record.

        Returns
        -------
        LogRecord
            Original record if accepted.

        None
            If rejected.
        """

        if self.evaluate(
            record
        ):

            return record

        return None


    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
    ) -> "LogFilter":
        """
        Reset runtime statistics.
        """

        self._statistics = {

            "evaluated": 0,

            "accepted": 0,

            "rejected": 0,

            "errors": 0,

            "rule_calls": 0,

            "latency": 0.0,

        }

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
    ) -> "LogFilter":
        """
        Remove every registered rule.
        """

        if self._frozen:

            raise RuntimeError(
                "Filter is frozen"
            )

        self._rules.clear()

        self._touch()

        return self
# =============================================================================
# Part 4. Rule Registry API
# =============================================================================

    # -------------------------------------------------------------------------
    # Add Rule
    # -------------------------------------------------------------------------

    def add_rule(
        self,
        name: str,
        rule: FilterRule,
        *,
        enabled: bool = True,
        priority: int = 100,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "LogFilter":
        """
        Register a filter rule.
        """

        if self._frozen:

            raise RuntimeError(
                "Filter is frozen"
            )

        self._rules[name] = {

            "object": rule,

            "enabled": enabled,

            "priority": int(priority),

            "metadata": dict(
                metadata or {}
            ),

        }

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Remove Rule
    # -------------------------------------------------------------------------

    def remove_rule(
        self,
        name: str,
    ) -> bool:
        """
        Remove a registered rule.
        """

        if name not in self._rules:

            return False

        del self._rules[name]

        self._touch()

        return True


    # -------------------------------------------------------------------------
    # Rule
    # -------------------------------------------------------------------------

    def rule(
        self,
        name: str,
    ) -> FilterRule:
        """
        Return a rule object.
        """

        if name not in self._rules:

            raise KeyError(
                f"Unknown rule: {name}"
            )

        return self._rules[name]["object"]


    # -------------------------------------------------------------------------
    # Rules
    # -------------------------------------------------------------------------

    def rules(
        self,
    ) -> Dict[str, FilterRule]:
        """
        Return all registered rules.
        """

        return {

            name: item["object"]

            for name, item

            in self._rules.items()

        }


    # -------------------------------------------------------------------------
    # Has Rule
    # -------------------------------------------------------------------------

    def has_rule(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a rule exists.
        """

        return (

            name

            in

            self._rules

        )


    # -------------------------------------------------------------------------
    # Enable Rule
    # -------------------------------------------------------------------------

    def enable_rule(
        self,
        name: str,
    ) -> "LogFilter":
        """
        Enable a rule.
        """

        if name not in self._rules:

            raise KeyError(
                name
            )

        self._rules[name]["enabled"] = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Disable Rule
    # -------------------------------------------------------------------------

    def disable_rule(
        self,
        name: str,
    ) -> "LogFilter":
        """
        Disable a rule.
        """

        if name not in self._rules:

            raise KeyError(
                name
            )

        self._rules[name]["enabled"] = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Rule Names
    # -------------------------------------------------------------------------

    def rule_names(
        self,
    ) -> List[str]:
        """
        Return registered rule names.
        """

        return sorted(

            self._rules.keys()

        )


    # -------------------------------------------------------------------------
    # Rule Count
    # -------------------------------------------------------------------------

    def rule_count(
        self,
    ) -> int:
        """
        Number of registered rules.
        """

        return len(

            self._rules

        )


    # -------------------------------------------------------------------------
    # Clear Rules
    # -------------------------------------------------------------------------

    def clear_rules(
        self,
    ) -> "LogFilter":
        """
        Remove every rule.
        """

        if self._frozen:

            raise RuntimeError(
                "Filter is frozen"
            )

        self._rules.clear()

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Execute Rule
    # -------------------------------------------------------------------------

    def execute_rule(
        self,
        name: str,
        record: LogRecord,
    ) -> bool:
        """
        Execute a single rule.
        """

        if name not in self._rules:

            raise KeyError(
                name
            )

        entry = self._rules[name]

        if not entry["enabled"]:

            return True

        started = time.perf_counter()

        try:

            self._statistics["rule_calls"] += 1

            return bool(

                entry["object"](
                    record
                )

            )

        except Exception:

            self._statistics["errors"] += 1

            return False

        finally:

            self._statistics["latency"] += (

                time.perf_counter()

                -

                started

            )
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "LogFilter":
        """
        Enable the filter.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot enable a closed filter."
            )

        self._enabled = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "LogFilter":
        """
        Disable the filter.

        A disabled filter always accepts records.
        """

        self._enabled = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "LogFilter":
        """
        Freeze filter configuration.

        While frozen, rules cannot be added,
        removed, or modified.
        """

        self._frozen = True

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "LogFilter":
        """
        Unfreeze filter configuration.
        """

        self._frozen = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "LogFilter":
        """
        Close the filter.

        A closed filter rejects all evaluations.
        """

        self._closed = True

        self._enabled = False

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "LogFilter":
        """
        Reopen a previously closed filter.
        """

        self._closed = False

        self._enabled = True

        self._touch()

        return self
# =============================================================================
# Part 6. Runtime Operations
# =============================================================================

    # -------------------------------------------------------------------------
    # Snapshot
    # -------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Capture the current runtime state.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "priority": self._priority,

            "rules": copy.deepcopy(
                self._rules
            ),

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "created_at": self.created_at,

            "updated_at": self.updated_at,

        }


    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "LogFilter":
        """
        Restore runtime state from a snapshot.
        """

        self._enabled = snapshot.get(
            "enabled",
            DEFAULT_ENABLED,
        )

        self._frozen = snapshot.get(
            "frozen",
            DEFAULT_FROZEN,
        )

        self._closed = snapshot.get(
            "closed",
            DEFAULT_CLOSED,
        )

        self._priority = snapshot.get(
            "priority",
            DEFAULT_PRIORITY,
        )

        self._rules = copy.deepcopy(
            snapshot.get(
                "rules",
                {},
            )
        )

        self._metadata = copy.deepcopy(
            snapshot.get(
                "metadata",
                {},
            )
        )

        self._statistics = copy.deepcopy(
            snapshot.get(
                "statistics",
                {},
            )
        )

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LogFilter":
        """
        Create a deep clone of this filter.
        """

        cloned = self.__class__(

            name=self.name,

            priority=self.priority,

            enabled=self.enabled,

            metadata=copy.deepcopy(
                self.metadata
            ),

        )

        cloned.restore(
            self.snapshot()
        )

        cloned.id = str(
            uuid.uuid4()
        )

        cloned.created_at = datetime.now(
            timezone.utc
        )

        cloned.updated_at = cloned.created_at

        return cloned


    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def copy(
        self,
    ) -> "LogFilter":
        """
        Alias of clone().
        """

        return self.clone()


    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "LogFilter":
        """
        Optimize internal rule registry.

        - Remove invalid entries
        - Sort rules by priority
        """

        valid_rules = {}

        ordered = sorted(

            self._rules.items(),

            key=lambda item: (
                item[1].get(
                    "priority",
                    DEFAULT_PRIORITY,
                ),
                item[0],
            ),
        )

        for name, entry in ordered:

            if callable(
                entry.get("object")
            ):

                valid_rules[name] = entry

        self._rules = valid_rules

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "LogFilter":
        """
        Cleanup temporary runtime state.
        """

        self._statistics["latency"] = 0.0

        self._touch()

        return self


    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "LogFilter":
        """
        Compact internal registries.

        Removes disabled rules.
        """

        self._rules = {

            name: entry

            for name, entry

            in self._rules.items()

            if entry.get(
                "enabled",
                True,
            )

        }

        self._touch()

        return self
# =============================================================================
# Part 7. Statistics & Diagnostics
# =============================================================================

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return a concise runtime summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "priority": self.priority,

            "rules": self.rule_count,

            "evaluated": self.statistics.get(
                "evaluated",
                0,
            ),

            "accepted": self.statistics.get(
                "accepted",
                0,
            ),

            "rejected": self.statistics.get(
                "rejected",
                0,
            ),

            "errors": self.error_count,

            "uptime": self.uptime,

        }


    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Return a detailed diagnostic report.
        """

        return {

            "identity": {

                "id": self.id,

                "name": self.name,

            },

            "runtime": {

                "enabled": self.enabled,

                "priority": self.priority,

                "frozen": self._frozen,

                "closed": self._closed,

            },

            "rules": {

                "count": self.rule_count,

                "names": self.rule_names(),

            },

            "statistics": dict(
                self.statistics
            ),

            "metadata": dict(
                self.metadata
            ),

            "health": self.health(),

        }


    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime health.
        """

        return {

            "healthy": (

                self.enabled

                and

                not self._closed

            ),

            "errors": self.error_count,

            "latency": self.latency,

            "rule_count": self.rule_count,

            "evaluated": self.statistics.get(
                "evaluated",
                0,
            ),

        }


    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return runtime status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if not self._enabled:

            return "disabled"

        return "active"


    # -------------------------------------------------------------------------
    # Rule Count
    # -------------------------------------------------------------------------

    @property
    def rule_count(
        self,
    ) -> int:
        """
        Number of registered rules.
        """

        return len(
            self._rules
        )


    # -------------------------------------------------------------------------
    # Filter Count
    # -------------------------------------------------------------------------

    @property
    def filter_count(
        self,
    ) -> int:
        """
        Number of filter evaluations.
        """

        return self.statistics.get(
            "evaluated",
            0,
        )


    # -------------------------------------------------------------------------
    # Error Count
    # -------------------------------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:
        """
        Total filter errors.
        """

        return self.statistics.get(
            "errors",
            0,
        )


    # -------------------------------------------------------------------------
    # Uptime
    # -------------------------------------------------------------------------

    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime uptime in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()


    # -------------------------------------------------------------------------
    # Latency
    # -------------------------------------------------------------------------

    @property
    def latency(
        self,
    ) -> float:
        """
        Average evaluation latency.
        """

        evaluated = max(

            1,

            self.statistics.get(
                "evaluated",
                0,
            ),

        )

        return (

            self.statistics.get(
                "latency",
                0.0,
            )

            /

            evaluated

        )
# =============================================================================
# Part 8. Validation
# =============================================================================

    # -------------------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------------------

    def validate(
        self,
    ) -> bool:
        """
        Validate the overall filter configuration.

        Returns
        -------
        bool
            True if the filter is valid.
        """

        return (

            self.check_configuration()

            and

            self.check_integrity()

        )


    # -------------------------------------------------------------------------
    # Validate Rule
    # -------------------------------------------------------------------------

    def validate_rule(
        self,
        rule: FilterRule,
    ) -> bool:
        """
        Validate a filter rule.
        """

        return callable(rule)


    # -------------------------------------------------------------------------
    # Validate Record
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Validate an input log record.
        """

        if record is None:

            return False

        return isinstance(
            record,
            Mapping,
        )


    # -------------------------------------------------------------------------
    # Check Configuration
    # -------------------------------------------------------------------------

    def check_configuration(
        self,
    ) -> bool:
        """
        Validate runtime configuration.
        """

        if not isinstance(
            self._priority,
            int,
        ):

            return False

        if self._priority < 0:

            return False

        if not isinstance(
            self._rules,
            dict,
        ):

            return False

        for name, entry in self._rules.items():

            if not isinstance(
                name,
                str,
            ):

                return False

            if not isinstance(
                entry,
                dict,
            ):

                return False

            if "object" not in entry:

                return False

            if not self.validate_rule(
                entry["object"]
            ):

                return False

        return True


    # -------------------------------------------------------------------------
    # Check Integrity
    # -------------------------------------------------------------------------

    def check_integrity(
        self,
    ) -> bool:
        """
        Verify internal runtime integrity.
        """

        required = {

            "evaluated",

            "accepted",

            "rejected",

            "errors",

            "rule_calls",

            "latency",

        }

        if not required.issubset(
            self._statistics.keys()
        ):

            return False

        if not isinstance(
            self._metadata,
            dict,
        ):

            return False

        if self.created_at is None:

            return False

        if self.updated_at is None:

            return False

        return True
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================

    # -------------------------------------------------------------------------
    # Before Filter
    # -------------------------------------------------------------------------

    def before_filter(
        self,
        record: LogRecord,
    ) -> None:
        """
        Emit before-filter event.
        """

        self.emit(
            "before_filter",
            record=record,
            filter=self,
        )


    # -------------------------------------------------------------------------
    # After Filter
    # -------------------------------------------------------------------------

    def after_filter(
        self,
        record: LogRecord,
        accepted: bool,
    ) -> None:
        """
        Emit after-filter event.
        """

        self.emit(
            "after_filter",
            record=record,
            accepted=accepted,
            filter=self,
        )


    # -------------------------------------------------------------------------
    # Before Rule
    # -------------------------------------------------------------------------

    def before_rule(
        self,
        name: str,
        record: LogRecord,
    ) -> None:
        """
        Emit before-rule event.
        """

        self.emit(
            "before_rule",
            rule=name,
            record=record,
            filter=self,
        )


    # -------------------------------------------------------------------------
    # After Rule
    # -------------------------------------------------------------------------

    def after_rule(
        self,
        name: str,
        record: LogRecord,
        result: bool,
    ) -> None:
        """
        Emit after-rule event.
        """

        self.emit(
            "after_rule",
            rule=name,
            record=record,
            result=result,
            filter=self,
        )


    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "LogFilter":
        """
        Register an event callback.
        """

        self._hooks.setdefault(
            event,
            [],
        ).append(callback)

        return self


    # -------------------------------------------------------------------------
    # Remove Hook
    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback: Hook,
    ) -> bool:
        """
        Remove an event callback.
        """

        hooks = self._hooks.get(event)

        if not hooks:

            return False

        try:

            hooks.remove(callback)

            if not hooks:

                self._hooks.pop(
                    event,
                    None,
                )

            return True

        except ValueError:

            return False


    # -------------------------------------------------------------------------
    # Emit
    # -------------------------------------------------------------------------

    def emit(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Emit an event.
        """

        for callback in self._hooks.get(
            event,
            [],
        ):

            try:

                callback(
                    **payload
                )

            except Exception:

                self._statistics["errors"] += 1


    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Hook,
    ) -> "LogFilter":
        """
        Alias of add_hook().
        """

        return self.add_hook(
            event,
            callback,
        )
# =============================================================================
# Part 10. Python Protocols
# =============================================================================

    # -------------------------------------------------------------------------
    # Repr
    # -------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"name={self.name!r}, "

            f"rules={self.rule_count}, "

            f"enabled={self.enabled}, "

            f"priority={self.priority}"

            f")"

        )


    # -------------------------------------------------------------------------
    # Str
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.name} "

            f"[rules={self.rule_count}, "

            f"enabled={self.enabled}]"

        )


    # -------------------------------------------------------------------------
    # Len
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of registered rules.
        """

        return self.rule_count


    # -------------------------------------------------------------------------
    # Iterator
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over registered rules.

        Yields
        ------
        tuple[str, dict]
            (rule_name, rule_entry)
        """

        return iter(
            self._rules.items()
        )


    # -------------------------------------------------------------------------
    # Contains
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Membership test.

        Example
        -------
        "security" in filter
        """

        return self.has_rule(
            name
        )


    # -------------------------------------------------------------------------
    # Callable
    # -------------------------------------------------------------------------

    def __call__(
        self,
        record: LogRecord,
    ) -> bool:
        """
        Execute the filter.

        Equivalent to:

            filter.evaluate(record)
        """

        return self.evaluate(
            record
        )


    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "LogFilter":
        """
        Shallow copy.
        """

        cloned = self.__class__(

            name=self.name,

            priority=self.priority,

            enabled=self.enabled,

            metadata=dict(
                self.metadata
            ),

        )

        cloned._rules = dict(
            self._rules
        )

        cloned._statistics = dict(
            self.statistics
        )

        return cloned


    # -------------------------------------------------------------------------
    # Deep Copy
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ) -> "LogFilter":
        """
        Deep copy.
        """

        if id(self) in memo:

            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                            