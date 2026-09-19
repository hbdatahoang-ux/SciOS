# =============================================================================
# scios/runtime/observability/logging/plugin.py
#
# Part 1. Foundation
# =============================================================================

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================

import copy
import time
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    TypeAlias,
)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_PLUGIN_MANAGER_NAME = (
    "logging_plugin_manager"
)

DEFAULT_ENABLED = True

DEFAULT_AUTO_LOAD = True

DEFAULT_PRIORITY = 100


# =============================================================================
# Type Aliases
# =============================================================================

PluginId: TypeAlias = str

Metadata: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

PluginConfig: TypeAlias = Dict[str, Any]

Snapshot: TypeAlias = Dict[str, Any]

Hook: TypeAlias = Callable[..., None]


# =============================================================================
# LoggingPlugin
# =============================================================================


@dataclass
class LoggingPlugin:
    """
    Base logging plugin definition.

    A plugin represents an extension
    of the logging subsystem.
    """

    name: str

    version: str = "0.1.0"

    enabled: bool = True

    priority: int = DEFAULT_PRIORITY

    metadata: Metadata = field(
        default_factory=dict
    )

    id: PluginId = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )


    # -------------------------------------------------------------------------
    # Plugin Lifecycle
    # -------------------------------------------------------------------------

    def initialize(
        self,
        runtime: Any,
    ) -> None:
        """
        Initialize plugin with runtime.
        """

        pass


    def start(
        self,
    ) -> None:
        """
        Start plugin.
        """

        pass


    def stop(
        self,
    ) -> None:
        """
        Stop plugin.
        """

        pass


    def cleanup(
        self,
    ) -> None:
        """
        Cleanup plugin resources.
        """

        pass



# =============================================================================
# PluginManager
# =============================================================================


class PluginManager:
    """
    Runtime manager for logging plugins.

    Responsibilities:

    - register plugins
    - manage lifecycle
    - track statistics
    - provide plugin registry
    """


    # =========================================================================
    # __init__
    # =========================================================================

    def __init__(
        self,
        *,
        name: str = DEFAULT_PLUGIN_MANAGER_NAME,
        enabled: bool = DEFAULT_ENABLED,
        auto_load: bool = DEFAULT_AUTO_LOAD,
        metadata: Optional[
            Metadata
        ] = None,
    ) -> None:


        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name


        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self._enabled = enabled

        self._frozen = False

        self._closed = False

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at


        self._plugins: Dict[
            PluginId,
            LoggingPlugin,
        ] = {}


        self._hooks: Dict[
            str,
            List[Hook],
        ] = {}


        # ---------------------------------------------------------------------
        # Plugin Configuration
        # ---------------------------------------------------------------------

        self._auto_load = auto_load

        self._priority = DEFAULT_PRIORITY


        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self._metadata: Metadata = (

            copy.deepcopy(metadata)

            if metadata

            else {}

        )


        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self._statistics: Statistics = {

            "registered": 0,

            "loaded": 0,

            "unloaded": 0,

            "enabled": 0,

            "disabled": 0,

            "errors": 0,

            "latency": 0.0,

        }


    # =========================================================================
    # Internal Helpers
    # =========================================================================


    def _touch(
        self,
    ) -> None:
        """
        Update modification time.
        """

        self.updated_at = datetime.now(
            timezone.utc
        )


    def _record_latency(
        self,
        started: float,
    ) -> None:
        """
        Track execution latency.
        """

        self._statistics["latency"] += (

            time.perf_counter()

            -

            started

        )


    def _validate_plugin_object(
        self,
        plugin: LoggingPlugin,
    ) -> None:
        """
        Validate plugin instance.
        """

        if not isinstance(
            plugin,
            LoggingPlugin,
        ):

            raise TypeError(
                "Plugin must inherit LoggingPlugin."
            )
# =============================================================================
# Part 2. Properties
# =============================================================================


# =============================================================================
# PluginManager Properties
# =============================================================================


    # -------------------------------------------------------------------------
    # id
    # -------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> PluginId:
        """
        Return plugin manager identity.
        """

        return self._id


    # -------------------------------------------------------------------------
    # name
    # -------------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Return plugin manager name.
        """

        return self._name


    # -------------------------------------------------------------------------
    # enabled
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Return manager enabled state.
        """

        return self._enabled


    # -------------------------------------------------------------------------
    # plugins
    # -------------------------------------------------------------------------

    @property
    def plugins(
        self,
    ) -> Mapping[PluginId, LoggingPlugin]:
        """
        Return registered plugins.

        Read-only view.
        """

        return dict(
            self._plugins
        )


    # -------------------------------------------------------------------------
    # plugin_count
    # -------------------------------------------------------------------------

    @property
    def plugin_count(
        self,
    ) -> int:
        """
        Return total registered plugins.
        """

        return len(
            self._plugins
        )


    # -------------------------------------------------------------------------
    # metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Metadata:
        """
        Return plugin manager metadata.
        """

        return copy.deepcopy(
            self._metadata
        )


    # -------------------------------------------------------------------------
    # statistics
    # -------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> Statistics:
        """
        Return runtime statistics.
        """

        return copy.deepcopy(
            self._statistics
        )


    # -------------------------------------------------------------------------
    # age
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Return manager age in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()


    # -------------------------------------------------------------------------
    # active_plugins
    # -------------------------------------------------------------------------

    @property
    def active_plugins(
        self,
    ) -> List[LoggingPlugin]:
        """
        Return enabled plugins.
        """

        return [

            plugin

            for plugin in self._plugins.values()

            if plugin.enabled

        ]
# =============================================================================
# Part 3. Plugin API
# =============================================================================


    # -------------------------------------------------------------------------
    # Register
    # -------------------------------------------------------------------------

    def register(
        self,
        plugin: LoggingPlugin,
    ) -> LoggingPlugin:
        """
        Register a logging plugin.
        """

        self._validate_plugin_object(
            plugin
        )


        if plugin.id in self._plugins:

            raise ValueError(
                f"Plugin already registered: {plugin.id}"
            )


        self._plugins[plugin.id] = plugin


        self._statistics[
            "registered"
        ] += 1


        self._touch()


        return plugin



    # -------------------------------------------------------------------------
    # Unregister
    # -------------------------------------------------------------------------

    def unregister(
        self,
        plugin_id: PluginId,
    ) -> bool:
        """
        Remove a plugin from registry.
        """

        plugin = self._plugins.get(
            plugin_id
        )


        if plugin is None:

            return False


        try:

            plugin.stop()

        except Exception:

            self._statistics[
                "errors"
            ] += 1


        del self._plugins[
            plugin_id
        ]


        self._statistics[
            "unloaded"
        ] += 1


        self._touch()


        return True



    # -------------------------------------------------------------------------
    # Load
    # -------------------------------------------------------------------------

    def load(
        self,
        plugin: LoggingPlugin,
        runtime: Any = None,
    ) -> LoggingPlugin:
        """
        Load and initialize plugin.
        """

        started = time.perf_counter()


        self._validate_plugin_object(
            plugin
        )


        if plugin.id not in self._plugins:

            self.register(
                plugin
            )


        try:

            plugin.initialize(
                runtime
            )

            plugin.start()


            plugin.enabled = True


            self._statistics[
                "loaded"
            ] += 1


        except Exception:

            self._statistics[
                "errors"
            ] += 1

            raise


        finally:

            self._record_latency(
                started
            )


        self._touch()


        return plugin



    # -------------------------------------------------------------------------
    # Unload
    # -------------------------------------------------------------------------

    def unload(
        self,
        plugin_id: PluginId,
    ) -> bool:
        """
        Stop and unload plugin.
        """

        plugin = self._plugins.get(
            plugin_id
        )


        if plugin is None:

            return False


        started = time.perf_counter()


        try:

            plugin.stop()

            plugin.cleanup()


        except Exception:

            self._statistics[
                "errors"
            ] += 1


        finally:

            self._record_latency(
                started
            )


        plugin.enabled = False


        self._statistics[
            "unloaded"
        ] += 1


        self._touch()


        return True



    # -------------------------------------------------------------------------
    # Enable Plugin
    # -------------------------------------------------------------------------

    def enable_plugin(
        self,
        plugin_id: PluginId,
    ) -> bool:
        """
        Enable a registered plugin.
        """

        plugin = self._plugins.get(
            plugin_id
        )


        if plugin is None:

            return False


        plugin.enabled = True


        self._statistics[
            "enabled"
        ] += 1


        self._touch()


        return True



    # -------------------------------------------------------------------------
    # Disable Plugin
    # -------------------------------------------------------------------------

    def disable_plugin(
        self,
        plugin_id: PluginId,
    ) -> bool:
        """
        Disable a registered plugin.
        """

        plugin = self._plugins.get(
            plugin_id
        )


        if plugin is None:

            return False


        plugin.enabled = False


        self._statistics[
            "disabled"
        ] += 1


        self._touch()


        return True



    # -------------------------------------------------------------------------
    # Get Plugin
    # -------------------------------------------------------------------------

    def get_plugin(
        self,
        plugin_id: PluginId,
    ) -> Optional[LoggingPlugin]:
        """
        Retrieve plugin by id.
        """

        return self._plugins.get(
            plugin_id
        )



    # -------------------------------------------------------------------------
    # List Plugins
    # -------------------------------------------------------------------------

    def list_plugins(
        self,
        *,
        active_only: bool = False,
    ) -> List[LoggingPlugin]:
        """
        Return registered plugins.
        """

        if active_only:

            return [

                plugin

                for plugin in self._plugins.values()

                if plugin.enabled

            ]


        return list(
            self._plugins.values()
        )



    # -------------------------------------------------------------------------
    # Clear Plugins
    # -------------------------------------------------------------------------

    def clear_plugins(
        self,
    ) -> "PluginManager":
        """
        Stop and remove all plugins.
        """

        for plugin_id in list(
            self._plugins.keys()
        ):

            self.unregister(
                plugin_id
            )


        self._touch()


        return self
# =============================================================================
# Part 4. Discovery API
# =============================================================================


# =============================================================================
# Plugin Discovery
# =============================================================================


    # -------------------------------------------------------------------------
    # Discover
    # -------------------------------------------------------------------------

    def discover(
        self,
        source: Any = None,
    ) -> List[LoggingPlugin]:
        """
        Discover plugins from a source.

        Supported sources:

        - iterable plugins
        - module
        - package path
        - entry points
        """

        discovered = []


        if source is None:

            return self.find_entrypoints()


        if isinstance(
            source,
            (list, tuple, set),
        ):

            for item in source:

                if self.validate_plugin(
                    item
                ):

                    discovered.append(
                        item
                    )


        elif isinstance(
            source,
            str,
        ):

            discovered.extend(
                self.scan(
                    source
                )
            )


        else:

            if self.validate_plugin(
                source
            ):

                discovered.append(
                    source
                )


        return discovered



    # -------------------------------------------------------------------------
    # Scan
    # -------------------------------------------------------------------------

    def scan(
        self,
        path: str,
    ) -> List[LoggingPlugin]:
        """
        Scan a package/module path for plugins.

        Expected plugin format:

        module.LoggingPlugin
        """

        plugins = []


        try:

            module = self.import_plugin(
                path
            )


            candidates = [

                value

                for value in vars(
                    module
                ).values()

                if isinstance(
                    value,
                    type,
                )

                and issubclass(
                    value,
                    LoggingPlugin,
                )

                and value is not LoggingPlugin

            ]


            for plugin_cls in candidates:

                plugins.append(
                    plugin_cls()
                )


        except Exception:

            self._statistics[
                "errors"
            ] += 1


        return plugins



    # -------------------------------------------------------------------------
    # Import Plugin
    # -------------------------------------------------------------------------

    def import_plugin(
        self,
        module_path: str,
    ) -> Any:
        """
        Dynamically import plugin module.
        """

        import importlib


        return importlib.import_module(
            module_path
        )



    # -------------------------------------------------------------------------
    # Find Entrypoints
    # -------------------------------------------------------------------------

    def find_entrypoints(
        self,
        group: str = "scios.logging",
    ) -> List[LoggingPlugin]:
        """
        Discover plugins from Python entry points.

        Compatible with:

        - setuptools
        - pyproject.toml plugins
        - package extensions
        """

        plugins = []


        try:

            from importlib.metadata import (
                entry_points,
            )


            points = entry_points()


            if hasattr(
                points,
                "select",
            ):

                selected = points.select(
                    group=group
                )

            else:

                selected = points.get(
                    group,
                    []
                )


            for entry in selected:

                try:

                    plugin_cls = entry.load()

                    plugin = plugin_cls()

                    if self.validate_plugin(
                        plugin
                    ):

                        plugins.append(
                            plugin
                        )

                except Exception:

                    self._statistics[
                        "errors"
                    ] += 1


        except Exception:

            pass


        return plugins



    # -------------------------------------------------------------------------
    # Resolve
    # -------------------------------------------------------------------------

    def resolve(
        self,
        plugin: Any,
    ) -> LoggingPlugin:
        """
        Resolve plugin object.

        Accepts:

        - instance
        - class
        - import path
        """

        if isinstance(
            plugin,
            LoggingPlugin,
        ):

            return plugin


        if isinstance(
            plugin,
            type,
        ):

            instance = plugin()

            if self.validate_plugin(
                instance
            ):

                return instance



        if isinstance(
            plugin,
            str,
        ):

            module = self.import_plugin(
                plugin
            )


            for obj in vars(
                module
            ).values():

                if isinstance(
                    obj,
                    type,
                )

                and issubclass(
                    obj,
                    LoggingPlugin,
                )

                and obj is not LoggingPlugin:

                    return obj()



        raise TypeError(
            "Unable to resolve plugin."
        )



    # -------------------------------------------------------------------------
    # Dependencies
    # -------------------------------------------------------------------------

    def dependencies(
        self,
        plugin: LoggingPlugin,
    ) -> List[str]:
        """
        Return plugin dependencies.
        """

        self.validate_plugin(
            plugin
        )


        return list(

            getattr(
                plugin,
                "dependencies",
                [],
            )

        )



    # -------------------------------------------------------------------------
    # Validate Plugin
    # -------------------------------------------------------------------------

    def validate_plugin(
        self,
        plugin: Any,
    ) -> bool:
        """
        Validate plugin contract.
        """

        if not isinstance(
            plugin,
            LoggingPlugin,
        ):

            return False



        if not isinstance(
            plugin.name,
            str,
        ):

            return False



        if not plugin.name.strip():

            return False



        if not isinstance(
            plugin.version,
            str,
        ):

            return False



        if not callable(
            getattr(
                plugin,
                "initialize",
                None,
            )
        ):

            return False



        if not callable(
            getattr(
                plugin,
                "start",
                None,
            )
        ):

            return False



        if not callable(
            getattr(
                plugin,
                "stop",
                None,
            )
        ):

            return False



        return True
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================


# =============================================================================
# PluginManager Lifecycle
# =============================================================================


    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "PluginManager":
        """
        Enable plugin manager.

        Allows plugin execution.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot enable closed PluginManager."
            )


        self._enabled = True


        self._touch()


        self.emit_event(
            "enabled"
        )


        return self



    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "PluginManager":
        """
        Disable plugin manager.

        Plugins remain registered but
        execution is suspended.
        """

        self._enabled = False


        self._statistics[
            "disabled"
        ] += 1


        self._touch()


        self.emit_event(
            "disabled"
        )


        return self



    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "PluginManager":
        """
        Freeze plugin manager.

        Prevents plugin mutation operations.
        """

        if self._closed:

            raise RuntimeError(
                "Cannot freeze closed PluginManager."
            )


        self._frozen = True


        self._touch()


        self.emit_event(
            "frozen"
        )


        return self



    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "PluginManager":
        """
        Unfreeze plugin manager.

        Allows plugin modifications again.
        """

        self._frozen = False


        self._touch()


        self.emit_event(
            "unfrozen"
        )


        return self



    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "PluginManager":
        """
        Close plugin manager.

        Stops all loaded plugins and
        releases runtime resources.
        """

        if self._closed:

            return self



        for plugin in self._plugins.values():

            try:

                plugin.stop()

                plugin.cleanup()


            except Exception:

                self._statistics[
                    "errors"
                ] += 1



            plugin.enabled = False



        self._enabled = False

        self._closed = True

        self._frozen = False


        self._touch()


        self.emit_event(
            "closed"
        )


        return self



    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "PluginManager":
        """
        Reopen a closed plugin manager.

        Restores runtime availability.
        """

        if not self._closed:

            return self



        self._closed = False

        self._enabled = True

        self._frozen = False


        self._touch()


        self.emit_event(
            "reopened"
        )


        return self
# =============================================================================
# Part 6. Runtime Operations
# =============================================================================


# =============================================================================
# PluginManager Runtime Operations
# =============================================================================


    # -------------------------------------------------------------------------
    # Snapshot
    # -------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> Snapshot:
        """
        Capture complete PluginManager runtime state.
        """

        return {

            "id": self._id,

            "name": self._name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "auto_load": self._auto_load,

            "priority": self._priority,

            "metadata": copy.deepcopy(
                self._metadata
            ),

            "statistics": copy.deepcopy(
                self._statistics
            ),

            "plugins": copy.deepcopy(
                self._plugins
            ),

            "created_at": self.created_at,

            "updated_at": self.updated_at,

        }



    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Snapshot,
    ) -> "PluginManager":
        """
        Restore PluginManager from snapshot.
        """

        if not isinstance(
            snapshot,
            Mapping,
        ):

            raise TypeError(
                "Snapshot must be mapping."
            )


        self._id = snapshot[
            "id"
        ]

        self._name = snapshot[
            "name"
        ]

        self._enabled = snapshot[
            "enabled"
        ]

        self._frozen = snapshot[
            "frozen"
        ]

        self._closed = snapshot[
            "closed"
        ]


        self._auto_load = snapshot[
            "auto_load"
        ]

        self._priority = snapshot[
            "priority"
        ]


        self._metadata = copy.deepcopy(
            snapshot[
                "metadata"
            ]
        )


        self._statistics = copy.deepcopy(
            snapshot[
                "statistics"
            ]
        )


        self._plugins = copy.deepcopy(
            snapshot[
                "plugins"
            ]
        )


        self.created_at = snapshot[
            "created_at"
        ]

        self.updated_at = snapshot[
            "updated_at"
        ]


        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "PluginManager":
        """
        Create independent PluginManager clone.
        """

        cloned = self.__class__(
            name=self.name,
            enabled=self.enabled,
            auto_load=self._auto_load,
            metadata=self.metadata,
        )


        cloned.restore(
            self.snapshot()
        )


        #
        # New runtime identity.
        #

        cloned._id = str(
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
    ) -> "PluginManager":
        """
        Alias for clone().
        """

        return self.clone()



    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "PluginManager":
        """
        Optimize plugin registry.

        Operations:

        - remove invalid plugins
        - synchronize statistics
        - normalize ordering
        """

        valid_plugins = {}


        for plugin_id, plugin in self._plugins.items():

            if self.validate_plugin(
                plugin
            ):

                valid_plugins[
                    plugin_id
                ] = plugin



        self._plugins = dict(
            sorted(
                valid_plugins.items(),
                key=lambda item:
                    item[1].priority,
            )
        )


        self._statistics[
            "registered"
        ] = len(
            self._plugins
        )


        self._statistics[
            "enabled"
        ] = len(
            self.active_plugins
        )


        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "PluginManager":
        """
        Cleanup transient runtime resources.
        """

        #
        # Clear hooks.
        #

        self._hooks.clear()


        #
        # Cleanup plugin resources.
        #

        for plugin in self._plugins.values():

            try:

                plugin.cleanup()


            except Exception:

                self._statistics[
                    "errors"
                ] += 1



        self._touch()


        return self



    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "PluginManager":
        """
        Compact plugin runtime memory.

        Removes disabled plugins that
        are no longer active.
        """

        removable = [

            plugin_id

            for plugin_id, plugin

            in self._plugins.items()

            if not plugin.enabled

        ]


        for plugin_id in removable:

            self._plugins.pop(
                plugin_id,
                None,
            )


        self._statistics[
            "registered"
        ] = len(
            self._plugins
        )


        self._touch()


        return self
# =============================================================================
# Part 7. Statistics & Diagnostics
# =============================================================================


# =============================================================================
# PluginManager Statistics & Diagnostics
# =============================================================================


    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return compact runtime summary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "enabled": self.enabled,

            "plugin_count": self.plugin_count,

            "active_plugins": len(
                self.active_plugins
            ),

            "loaded_count": self.loaded_count,

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
        Generate complete diagnostics report.
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

                "uptime": self.uptime,

            },


            "plugins": {

                "total": self.plugin_count,

                "active": len(
                    self.active_plugins
                ),

                "names": [

                    plugin.name

                    for plugin

                    in self._plugins.values()

                ],

            },


            "statistics": self.statistics,


            "health": self.health(),

        }



    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime health status.
        """

        healthy = (

            self._enabled

            and not self._closed

            and self.error_count == 0

        )


        return {

            "healthy": healthy,

            "state": self.status(),

            "plugin_count": self.plugin_count,

            "active_plugins": len(
                self.active_plugins
            ),

            "errors": self.error_count,

        }



    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return current manager state.
        """

        if self._closed:

            return "closed"


        if self._frozen:

            return "frozen"


        if not self._enabled:

            return "disabled"


        return "running"



    # -------------------------------------------------------------------------
    # loaded_count
    # -------------------------------------------------------------------------

    @property
    def loaded_count(
        self,
    ) -> int:
        """
        Number of successfully loaded plugins.
        """

        return self._statistics.get(
            "loaded",
            0,
        )



    # -------------------------------------------------------------------------
    # error_count
    # -------------------------------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:
        """
        Total plugin errors.
        """

        return self._statistics.get(
            "errors",
            0,
        )



    # -------------------------------------------------------------------------
    # uptime
    # -------------------------------------------------------------------------

    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime duration in seconds.
        """

        return (

            datetime.now(
                timezone.utc
            )

            -

            self.created_at

        ).total_seconds()



    # -------------------------------------------------------------------------
    # latency
    # -------------------------------------------------------------------------

    @property
    def latency(
        self,
    ) -> float:
        """
        Total accumulated operation latency.
        """

        return self._statistics.get(
            "latency",
            0.0,
        )
# =============================================================================
# Part 8. Validation
# =============================================================================


# =============================================================================
# PluginManager Validation API
# =============================================================================


    # -------------------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------------------

    def validate(
        self,
    ) -> bool:
        """
        Validate complete PluginManager state.
        """

        return (

            self.validate_plugin_registry()

            and

            self.validate_dependencies()

            and

            self.check_configuration()

            and

            self.check_integrity()

        )



    # -------------------------------------------------------------------------
    # Validate Plugin
    # -------------------------------------------------------------------------

    def validate_plugin(
        self,
        plugin: LoggingPlugin,
    ) -> bool:
        """
        Validate single plugin contract.
        """

        if not isinstance(
            plugin,
            LoggingPlugin,
        ):

            return False



        #
        # Identity
        #

        if not isinstance(
            plugin.id,
            str,
        ):

            return False


        if not plugin.id.strip():

            return False



        #
        # Name
        #

        if not isinstance(
            plugin.name,
            str,
        ):

            return False


        if not plugin.name.strip():

            return False



        #
        # Version
        #

        if not isinstance(
            plugin.version,
            str,
        ):

            return False



        #
        # Lifecycle API
        #

        required_methods = (

            "initialize",

            "start",

            "stop",

            "cleanup",

        )


        for method in required_methods:

            if not callable(
                getattr(
                    plugin,
                    method,
                    None,
                )
            ):

                return False



        #
        # Metadata
        #

        if not isinstance(
            plugin.metadata,
            Mapping,
        ):

            return False



        return True



    # -------------------------------------------------------------------------
    # Validate Plugin Registry
    # -------------------------------------------------------------------------

    def validate_plugin_registry(
        self,
    ) -> bool:
        """
        Validate all registered plugins.
        """

        for plugin_id, plugin in self._plugins.items():


            if plugin_id != plugin.id:

                return False



            if not self.validate_plugin(
                plugin
            ):

                return False



        return True



    # -------------------------------------------------------------------------
    # Validate Dependencies
    # -------------------------------------------------------------------------

    def validate_dependencies(
        self,
    ) -> bool:
        """
        Validate plugin dependencies.
        """

        available = {

            plugin.name

            for plugin

            in self._plugins.values()

        }


        for plugin in self._plugins.values():

            dependencies = self.dependencies(
                plugin
            )


            for dependency in dependencies:

                if dependency not in available:

                    return False



        return True



    # -------------------------------------------------------------------------
    # Check Configuration
    # -------------------------------------------------------------------------

    def check_configuration(
        self,
    ) -> bool:
        """
        Validate manager configuration.
        """

        #
        # Identity
        #

        if not isinstance(
            self._name,
            str,
        ):

            return False


        if not self._name.strip():

            return False



        #
        # Runtime flags
        #

        flags = (

            self._enabled,

            self._frozen,

            self._closed,

            self._auto_load,

        )


        for flag in flags:

            if not isinstance(
                flag,
                bool,
            ):

                return False



        #
        # Priority
        #

        if not isinstance(
            self._priority,
            int,
        ):

            return False



        #
        # Metadata
        #

        if not isinstance(
            self._metadata,
            Mapping,
        ):

            return False



        #
        # Statistics
        #

        if not isinstance(
            self._statistics,
            Mapping,
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
        Verify internal consistency.
        """

        #
        # Timestamp validation
        #

        if self.created_at > self.updated_at:

            return False



        #
        # Plugin registry integrity
        #

        if len(
            self._plugins
        ) != self.plugin_count:

            return False



        #
        # Statistics integrity
        #

        counters = (

            "registered",

            "loaded",

            "unloaded",

            "enabled",

            "disabled",

            "errors",

        )


        for counter in counters:

            value = self._statistics.get(
                counter,
                0,
            )


            if not isinstance(
                value,
                int,
            ):

                return False


            if value < 0:

                return False



        #
        # Registered count consistency
        #

        if self._statistics.get(
            "registered",
            0,
        ) < self.plugin_count:

            return False



        #
        # Active plugin consistency
        #

        for plugin in self.active_plugins:

            if not plugin.enabled:

                return False



        return True
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================


# =============================================================================
# PluginManager Event System
# =============================================================================


    # -------------------------------------------------------------------------
    # Before Load
    # -------------------------------------------------------------------------

    def before_load(
        self,
        plugin: LoggingPlugin,
    ) -> None:
        """
        Execute hooks before plugin loading.
        """

        self.emit_event(
            "before_load",
            plugin=plugin,
        )



    # -------------------------------------------------------------------------
    # After Load
    # -------------------------------------------------------------------------

    def after_load(
        self,
        plugin: LoggingPlugin,
    ) -> None:
        """
        Execute hooks after plugin loading.
        """

        self.emit_event(
            "after_load",
            plugin=plugin,
        )



    # -------------------------------------------------------------------------
    # Before Unload
    # -------------------------------------------------------------------------

    def before_unload(
        self,
        plugin: LoggingPlugin,
    ) -> None:
        """
        Execute hooks before plugin unloading.
        """

        self.emit_event(
            "before_unload",
            plugin=plugin,
        )



    # -------------------------------------------------------------------------
    # After Unload
    # -------------------------------------------------------------------------

    def after_unload(
        self,
        plugin: LoggingPlugin,
    ) -> None:
        """
        Execute hooks after plugin unloading.
        """

        self.emit_event(
            "after_unload",
            plugin=plugin,
        )



    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Hook,
    ) -> None:
        """
        Register event callback.
        """

        if not callable(
            callback
        ):

            raise TypeError(
                "Hook must be callable."
            )


        if event not in self._hooks:

            self._hooks[
                event
            ] = []


        self._hooks[
            event
        ].append(
            callback
        )



    # -------------------------------------------------------------------------
    # Remove Hook
    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback: Hook,
    ) -> bool:
        """
        Remove event callback.
        """

        callbacks = self._hooks.get(
            event,
            [],
        )


        if callback not in callbacks:

            return False


        callbacks.remove(
            callback
        )


        if not callbacks:

            self._hooks.pop(
                event,
                None,
            )


        return True



    # -------------------------------------------------------------------------
    # Emit Event
    # -------------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Dispatch event to subscribers.
        """

        callbacks = self._hooks.get(
            event,
            [],
        )


        for callback in list(
            callbacks
        ):

            try:

                callback(
                    **payload
                )


            except Exception:

                self._statistics[
                    "errors"
                ] += 1



    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback: Hook,
    ) -> Callable[[], bool]:
        """
        Subscribe callback and return unsubscribe function.
        """

        self.add_hook(
            event,
            callback,
        )


        def unsubscribe() -> bool:

            return self.remove_hook(
                event,
                callback,
            )


        return unsubscribe
# =============================================================================
# Part 10. Python Protocols
# =============================================================================


# =============================================================================
# PluginManager Python Data Model
# =============================================================================


    # -------------------------------------------------------------------------
    # __repr__
    # -------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"id={self.id!r}, "

            f"name={self.name!r}, "

            f"plugins={self.plugin_count}, "

            f"enabled={self.enabled}, "

            f"status={self.status()!r}"

            ")"

        )



    # -------------------------------------------------------------------------
    # __str__
    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (

            f"{self.name}: "

            f"{self.plugin_count} plugins "

            f"[{self.status()}]"

        )



    # -------------------------------------------------------------------------
    # __len__
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of registered plugins.
        """

        return self.plugin_count



    # -------------------------------------------------------------------------
    # __iter__
    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate through plugins.
        """

        return iter(
            self._plugins.values()
        )



    # -------------------------------------------------------------------------
    # __contains__
    # -------------------------------------------------------------------------

    def __contains__(
        self,
        item: object,
    ) -> bool:
        """
        Check plugin existence.

        Supports:

        - plugin id
        - plugin name
        - plugin instance
        """

        if isinstance(
            item,
            str,
        ):

            if item in self._plugins:

                return True


            return any(

                plugin.name == item

                for plugin

                in self._plugins.values()

            )



        if isinstance(
            item,
            LoggingPlugin,
        ):

            return item.id in self._plugins



        return False



    # -------------------------------------------------------------------------
    # __getitem__
    # -------------------------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> LoggingPlugin:
        """
        Retrieve plugin using index syntax.

        Examples:

        manager["json_logger"]
        manager[plugin_id]
        """

        #
        # ID lookup
        #

        if key in self._plugins:

            return self._plugins[
                key
            ]



        #
        # Name lookup
        #

        for plugin in self._plugins.values():

            if plugin.name == key:

                return plugin



        raise KeyError(
            key
        )



    # -------------------------------------------------------------------------
    # __call__
    # -------------------------------------------------------------------------

    def __call__(
        self,
        plugin: Optional[
            LoggingPlugin
        ] = None,
        *,
        load: bool = False,
    ):
        """
        Callable manager interface.

        Examples:

        manager(plugin)
        manager(plugin, load=True)
        """

        if plugin is None:

            return self.list_plugins()



        if load:

            return self.load(
                plugin
            )


        return self.register(
            plugin
        )



    # -------------------------------------------------------------------------
    # __copy__
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ):
        """
        Shallow copy protocol.
        """

        return self.copy()



    # -------------------------------------------------------------------------
    # __deepcopy__
    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy protocol.
        """

        cloned = self.clone()


        memo[id(self)] = cloned


        return cloned                                                                            