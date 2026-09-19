"""
SciOS-NG Logging Configuration

Runtime-managed configuration object for the logging subsystem.

Responsibilities
----------------
• Manage logging configuration values
• Runtime lifecycle
• Configuration registry
• Snapshot / restore
• Statistics
• Event hooks
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
    List,
    Mapping,
    MutableMapping,
    Optional,
    TypeAlias,
)

# =============================================================================
# Constants
# =============================================================================

DEFAULT_CONFIG_NAME = "logging"

DEFAULT_ENABLED = True

DEFAULT_FROZEN = False

DEFAULT_CLOSED = False

DEFAULT_LEVEL = "INFO"

DEFAULT_MAX_CONFIGS = 256

# =============================================================================
# Type Aliases
# =============================================================================

ConfigValue: TypeAlias = Any

Configuration: TypeAlias = Dict[str, ConfigValue]

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

Hook: TypeAlias = Callable[..., Any]

# =============================================================================
# LoggingConfig
# =============================================================================


class LoggingConfig:
    """
    Runtime-managed logging configuration.

    Provides a centralized configuration registry for the
    SciOS-NG logging subsystem.

    Managed configuration includes:

        • logger
        • formatter
        • serializer
        • filter
        • handlers
        • log level
        • rotation
        • structured logging
        • buffering
        • metadata
    """

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_CONFIG_NAME,
        *,
        enabled: bool = DEFAULT_ENABLED,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:

        # -----------------------------------------------------------------
        # Identity
        # -----------------------------------------------------------------

        self.id = str(uuid.uuid4())

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

        # -----------------------------------------------------------------
        # Configuration Registry
        # -----------------------------------------------------------------

        self._configs: Configuration = {

            "level": DEFAULT_LEVEL,

            "logger": "default",

            "formatter": "default",

            "serializer": "json",

            "filter": None,

            "handlers": [],

            "structured": False,

            "json": False,

            "async": False,

            "rotation": False,

            "compression": False,

            "buffer_size": 1024,

            "flush_interval": 1.0,

        }

        self._registry: Dict[str, Dict[str, Any]] = {}

        self._hooks: Dict[str, List[Hook]] = {}

        self._capacity = DEFAULT_MAX_CONFIGS

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

            "updates": 0,

            "reads": 0,

            "applies": 0,

            "errors": 0,

            "latency": 0.0,

        }

    # -------------------------------------------------------------------------
    # Foundation Helpers
    # -------------------------------------------------------------------------

    def _touch(
        self,
    ) -> None:
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
        Record elapsed execution time.
        """

        self._statistics["latency"] += (

            time.perf_counter()

            -

            started

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
        Unique configuration identifier.
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
        Configuration name.
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
        Whether this configuration is enabled.
        """

        return self._enabled

    # -------------------------------------------------------------------------
    # Default Level
    # -------------------------------------------------------------------------

    @property
    def default_level(
        self,
    ) -> str:
        """
        Default logging level.
        """

        return self._configs.get(
            "level",
            DEFAULT_LEVEL,
        )

    @default_level.setter
    def default_level(
        self,
        value: str,
    ) -> None:
        """
        Update default logging level.
        """

        self._configs["level"] = str(value).upper()

        self._statistics["updates"] += 1

        self._touch()

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Configuration metadata.
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
        Configuration lifetime (seconds).
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()

    # -------------------------------------------------------------------------
    # Config Count
    # -------------------------------------------------------------------------

    @property
    def config_count(
        self,
    ) -> int:
        """
        Number of registered configuration entries.
        """

        return len(
            self._configs
        )
# =============================================================================
# Part 3. Configuration API
# =============================================================================

    # -------------------------------------------------------------------------
    # Get
    # -------------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a configuration value.
        """

        self._statistics["reads"] += 1

        return self._configs.get(
            key,
            default,
        )

    # -------------------------------------------------------------------------
    # Set
    # -------------------------------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> "LoggingConfig":
        """
        Set a configuration value.
        """

        if self._frozen:

            raise RuntimeError(
                "Configuration is frozen."
            )

        self._configs[key] = value

        self._statistics["updates"] += 1

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(
        self,
        values: Mapping[str, Any],
    ) -> "LoggingConfig":
        """
        Update multiple configuration values.
        """

        if self._frozen:

            raise RuntimeError(
                "Configuration is frozen."
            )

        self._configs.update(
            dict(values)
        )

        self._statistics["updates"] += len(values)

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Remove
    # -------------------------------------------------------------------------

    def remove(
        self,
        key: str,
    ) -> Any:
        """
        Remove a configuration entry.

        Returns the removed value or None.
        """

        if self._frozen:

            raise RuntimeError(
                "Configuration is frozen."
            )

        value = self._configs.pop(
            key,
            None,
        )

        self._touch()

        return value

    # -------------------------------------------------------------------------
    # Contains
    # -------------------------------------------------------------------------

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Check whether a configuration exists.
        """

        return key in self._configs

    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
    ) -> "LoggingConfig":
        """
        Remove every configuration entry.
        """

        if self._frozen:

            raise RuntimeError(
                "Configuration is frozen."
            )

        self._configs.clear()

        self._statistics["updates"] += 1

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Merge
    # -------------------------------------------------------------------------

    def merge(
        self,
        other: Mapping[str, Any],
        *,
        overwrite: bool = True,
    ) -> "LoggingConfig":
        """
        Merge another configuration mapping.
        """

        if self._frozen:

            raise RuntimeError(
                "Configuration is frozen."
            )

        for key, value in other.items():

            if overwrite or key not in self._configs:

                self._configs[key] = value

        self._statistics["updates"] += len(other)

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
    ) -> "LoggingConfig":
        """
        Restore default logging configuration.
        """

        if self._frozen:

            raise RuntimeError(
                "Configuration is frozen."
            )

        self._configs = {

            "level": DEFAULT_LEVEL,

            "logger": "default",

            "formatter": "default",

            "serializer": "json",

            "filter": None,

            "handlers": [],

            "structured": False,

            "json": False,

            "async": False,

            "rotation": False,

            "compression": False,

            "buffer_size": 1024,

            "flush_interval": 1.0,

        }

        self._statistics["updates"] += 1

        self._touch()

        return self
# =============================================================================
# Part 4. Registry API
# =============================================================================

    # -------------------------------------------------------------------------
    # Register
    # -------------------------------------------------------------------------

    def register(
        self,
        name: str,
        config: Mapping[str, Any],
        *,
        enabled: bool = True,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "LoggingConfig":
        """
        Register a named configuration profile.
        """

        if self._frozen:
            raise RuntimeError("Configuration is frozen.")

        if len(self._registry) >= self._capacity:
            raise RuntimeError("Configuration registry is full.")

        self._registry[name] = {
            "config": dict(config),
            "enabled": enabled,
            "metadata": dict(metadata or {}),
            "created_at": datetime.now(timezone.utc),
        }

        self._statistics["updates"] += 1
        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Unregister
    # -------------------------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> bool:
        """
        Remove a registered configuration.
        """

        if self._frozen:
            raise RuntimeError("Configuration is frozen.")

        if name not in self._registry:
            return False

        del self._registry[name]

        self._statistics["updates"] += 1
        self._touch()

        return True

    # -------------------------------------------------------------------------
    # Config
    # -------------------------------------------------------------------------

    def config(
        self,
        name: str,
    ) -> Configuration:
        """
        Return a registered configuration.
        """

        if name not in self._registry:
            raise KeyError(f"Unknown configuration: {name}")

        self._statistics["reads"] += 1

        return copy.deepcopy(
            self._registry[name]["config"]
        )

    # -------------------------------------------------------------------------
    # Configs
    # -------------------------------------------------------------------------

    def configs(
        self,
    ) -> Dict[str, Configuration]:
        """
        Return all registered configurations.
        """

        self._statistics["reads"] += 1

        return {
            name: copy.deepcopy(entry["config"])
            for name, entry in self._registry.items()
        }

    # -------------------------------------------------------------------------
    # Has Config
    # -------------------------------------------------------------------------

    def has_config(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a configuration exists.
        """

        return name in self._registry

    # -------------------------------------------------------------------------
    # Enable Config
    # -------------------------------------------------------------------------

    def enable_config(
        self,
        name: str,
    ) -> "LoggingConfig":
        """
        Enable a registered configuration.
        """

        if name not in self._registry:
            raise KeyError(name)

        self._registry[name]["enabled"] = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Disable Config
    # -------------------------------------------------------------------------

    def disable_config(
        self,
        name: str,
    ) -> "LoggingConfig":
        """
        Disable a registered configuration.
        """

        if name not in self._registry:
            raise KeyError(name)

        self._registry[name]["enabled"] = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Config Names
    # -------------------------------------------------------------------------

    def config_names(
        self,
    ) -> List[str]:
        """
        Return registered configuration names.
        """

        return sorted(
            self._registry.keys()
        )

    # -------------------------------------------------------------------------
    # Config Count
    # -------------------------------------------------------------------------

    def config_count(
        self,
    ) -> int:
        """
        Return the number of registered configurations.
        """

        return len(
            self._registry
        )

    # -------------------------------------------------------------------------
    # Clear Configs
    # -------------------------------------------------------------------------

    def clear_configs(
        self,
    ) -> "LoggingConfig":
        """
        Remove all registered configurations.
        """

        if self._frozen:
            raise RuntimeError("Configuration is frozen.")

        self._registry.clear()

        self._statistics["updates"] += 1

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Apply
    # -------------------------------------------------------------------------

    def apply(
        self,
        name: str,
    ) -> "LoggingConfig":
        """
        Apply a registered configuration profile.
        """

        if name not in self._registry:
            raise KeyError(f"Unknown configuration: {name}")

        entry = self._registry[name]

        if not entry["enabled"]:
            raise RuntimeError(
                f"Configuration '{name}' is disabled."
            )

        started = time.perf_counter()

        try:

            self._configs.update(
                copy.deepcopy(entry["config"])
            )

            self._statistics["applies"] += 1

            return self

        finally:

            self._record_latency(started)

            self._touch()
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================

    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "LoggingConfig":
        """
        Enable this configuration manager.
        """

        if self._closed:
            raise RuntimeError(
                "Cannot enable a closed configuration."
            )

        self._enabled = True

        self._statistics["updates"] += 1

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "LoggingConfig":
        """
        Disable this configuration manager.
        """

        self._enabled = False

        self._statistics["updates"] += 1

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "LoggingConfig":
        """
        Freeze configuration changes.
        """

        if self._closed:
            raise RuntimeError(
                "Configuration is closed."
            )

        self._frozen = True

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "LoggingConfig":
        """
        Allow configuration modifications again.
        """

        if self._closed:
            raise RuntimeError(
                "Configuration is closed."
            )

        self._frozen = False

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "LoggingConfig":
        """
        Close this configuration manager.

        A closed configuration cannot be modified until reopened.
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
    ) -> "LoggingConfig":
        """
        Reopen a previously closed configuration manager.
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

            "configs": copy.deepcopy(
                self._configs
            ),

            "registry": copy.deepcopy(
                self._registry
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
    ) -> "LoggingConfig":
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

        self._configs = copy.deepcopy(
            snapshot.get(
                "configs",
                {},
            )
        )

        self._registry = copy.deepcopy(
            snapshot.get(
                "registry",
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

        self.created_at = snapshot.get(
            "created_at",
            self.created_at,
        )

        self.updated_at = snapshot.get(
            "updated_at",
            self.updated_at,
        )

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LoggingConfig":
        """
        Create a deep clone with a new identity.
        """

        cloned = self.__class__(

            name=self.name,

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
    ) -> "LoggingConfig":
        """
        Alias of clone().
        """

        return self.clone()

    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "LoggingConfig":
        """
        Optimize the configuration registry.

        - Remove invalid entries
        - Normalize configuration keys
        """

        optimized = {}

        for name, entry in self._registry.items():

            if not isinstance(
                entry,
                Mapping,
            ):
                continue

            if "config" not in entry:
                continue

            optimized[str(name)] = {

                "config": dict(
                    entry["config"]
                ),

                "enabled": bool(
                    entry.get(
                        "enabled",
                        True,
                    )
                ),

                "metadata": dict(
                    entry.get(
                        "metadata",
                        {},
                    )
                ),

                "created_at": entry.get(
                    "created_at",
                    datetime.now(
                        timezone.utc
                    ),
                ),

            }

        self._registry = optimized

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "LoggingConfig":
        """
        Cleanup transient runtime data.
        """

        self._statistics["latency"] = 0.0

        self._touch()

        return self

    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "LoggingConfig":
        """
        Compact the registry by removing disabled profiles.
        """

        self._registry = {

            name: entry

            for name, entry

            in self._registry.items()

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

            "default_level": self.default_level,

            "config_count": self.config_count,

            "update_count": self.update_count,

            "error_count": self.error_count,

            "uptime": self.uptime,

            "latency": self.latency,

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

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

            },

            "configuration": copy.deepcopy(
                self._configs
            ),

            "registry": {

                "count": self.config_count,

                "names": self.config_names(),

            },

            "statistics": copy.deepcopy(
                self.statistics
            ),

            "metadata": copy.deepcopy(
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
        Return runtime health information.
        """

        healthy = (

            self._enabled

            and

            not self._closed

            and

            self.error_count == 0

        )

        return {

            "healthy": healthy,

            "status": self.status(),

            "config_count": self.config_count,

            "update_count": self.update_count,

            "error_count": self.error_count,

            "uptime": self.uptime,

            "latency": self.latency,

        }

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return current runtime status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if not self._enabled:

            return "disabled"

        return "active"

    # -------------------------------------------------------------------------
    # Config Count
    # -------------------------------------------------------------------------

    @property
    def config_count(
        self,
    ) -> int:
        """
        Number of registered configuration profiles.
        """

        return len(
            self._registry
        )

    # -------------------------------------------------------------------------
    # Update Count
    # -------------------------------------------------------------------------

    @property
    def update_count(
        self,
    ) -> int:
        """
        Number of configuration updates.
        """

        return self._statistics.get(
            "updates",
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
        Number of runtime errors.
        """

        return self._statistics.get(
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
        Average runtime latency.
        """

        operations = max(

            1,

            self._statistics.get(
                "applies",
                0,
            ),

        )

        return (

            self._statistics.get(
                "latency",
                0.0,
            )

            /

            operations

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
        Validate the entire LoggingConfig instance.

        Returns
        -------
        bool
            True if both configuration and runtime integrity are valid.
        """

        return (

            self.check_configuration()

            and

            self.check_integrity()

        )

    # -------------------------------------------------------------------------
    # Validate Config
    # -------------------------------------------------------------------------

    def validate_config(
        self,
        config: Mapping[str, Any],
    ) -> bool:
        """
        Validate a configuration mapping.
        """

        if not isinstance(
            config,
            Mapping,
        ):

            return False

        for key, value in config.items():

            if not isinstance(
                key,
                str,
            ):

                return False

            if not self.validate_value(
                key,
                value,
            ):

                return False

        return True

    # -------------------------------------------------------------------------
    # Validate Value
    # -------------------------------------------------------------------------

    def validate_value(
        self,
        key: str,
        value: Any,
    ) -> bool:
        """
        Validate a single configuration value.
        """

        validators = {

            "level": lambda v: isinstance(v, str),

            "logger": lambda v: isinstance(v, str),

            "formatter": lambda v: isinstance(v, str),

            "serializer": lambda v: isinstance(v, str),

            "filter": lambda v: (
                v is None
                or
                isinstance(v, str)
            ),

            "handlers": lambda v: isinstance(v, list),

            "structured": lambda v: isinstance(v, bool),

            "json": lambda v: isinstance(v, bool),

            "async": lambda v: isinstance(v, bool),

            "rotation": lambda v: isinstance(v, bool),

            "compression": lambda v: isinstance(v, bool),

            "buffer_size": lambda v: (
                isinstance(v, int)
                and
                v >= 0
            ),

            "flush_interval": lambda v: (
                isinstance(v, (int, float))
                and
                v >= 0
            ),

        }

        validator = validators.get(key)

        if validator is None:

            #
            # Unknown configuration keys are allowed
            # to support future extensions.
            #
            return True

        try:

            return bool(
                validator(value)
            )

        except Exception:

            return False

    # -------------------------------------------------------------------------
    # Check Configuration
    # -------------------------------------------------------------------------

    def check_configuration(
        self,
    ) -> bool:
        """
        Validate all runtime configurations.
        """

        if not self.validate_config(
            self._configs
        ):

            return False

        for entry in self._registry.values():

            config = entry.get(
                "config",
                {},
            )

            if not self.validate_config(
                config
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
        Validate internal runtime state.
        """

        required_statistics = {

            "updates",

            "reads",

            "applies",

            "errors",

            "latency",

        }

        if not required_statistics.issubset(
            self._statistics.keys()
        ):

            return False

        if not isinstance(
            self._metadata,
            dict,
        ):

            return False

        if not isinstance(
            self._registry,
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
    # Before Update
    # -------------------------------------------------------------------------

    def before_update(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Emit event before updating a configuration value.
        """

        self.emit(
            "before_update",
            config=self,
            key=key,
            value=value,
        )

    # -------------------------------------------------------------------------
    # After Update
    # -------------------------------------------------------------------------

    def after_update(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Emit event after updating a configuration value.
        """

        self.emit(
            "after_update",
            config=self,
            key=key,
            value=value,
        )

    # -------------------------------------------------------------------------
    # Before Apply
    # -------------------------------------------------------------------------

    def before_apply(
        self,
        name: str,
    ) -> None:
        """
        Emit event before applying a configuration profile.
        """

        self.emit(
            "before_apply",
            config=self,
            profile=name,
        )

    # -------------------------------------------------------------------------
    # After Apply
    # -------------------------------------------------------------------------

    def after_apply(
        self,
        name: str,
    ) -> None:
        """
        Emit event after applying a configuration profile.
        """

        self.emit(
            "after_apply",
            config=self,
            profile=name,
        )

    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> "LoggingConfig":
        """
        Register an event hook.
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
        Remove a registered hook.
        """

        hooks = self._hooks.get(event)

        if hooks is None:
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
        Emit an event to all registered hooks.
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
    ) -> "LoggingConfig":
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
    # Representation
    # -------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Return developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"enabled={self.enabled}, "
            f"default_level={self.default_level!r}, "
            f"configs={self.config_count})"
        )

    # -------------------------------------------------------------------------
    # String
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Return human-readable representation.
        """

        return (
            f"{self.name}"
            f" [{self.default_level}] "
            f"({self.config_count} configs)"
        )

    # -------------------------------------------------------------------------
    # Length
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of configuration entries.
        """

        return len(self._configs)

    # -------------------------------------------------------------------------
    # Iterator
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate over configuration entries.
        """

        return iter(self._configs.items())

    # -------------------------------------------------------------------------
    # Contains
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Support 'in' operator.
        """

        return self.contains(key)

    # -------------------------------------------------------------------------
    # Get Item
    # -------------------------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style configuration lookup.
        """

        if key not in self._configs:
            raise KeyError(key)

        return self.get(key)

    # -------------------------------------------------------------------------
    # Set Item
    # -------------------------------------------------------------------------

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style configuration update.
        """

        self.set(key, value)

    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "LoggingConfig":
        """
        Return a shallow copy.
        """

        copied = self.__class__(
            name=self.name,
            enabled=self.enabled,
            metadata=copy.copy(self.metadata),
        )

        copied.restore(self.snapshot())

        return copied

    # -------------------------------------------------------------------------
    # Deep Copy
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "LoggingConfig":
        """
        Return a deep copy.
        """

        if id(self) in memo:
            return memo[id(self)]

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                            