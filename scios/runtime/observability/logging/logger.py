"""
SciOS-NG
runtime/observability/logging/logger.py

Core Logging Engine

Responsibilities:
- Create log records
- Dispatch logs
- Manage handlers
- Manage formatters
- Manage filters
- Runtime observability
"""


# =============================================================================
# Imports
# =============================================================================

from __future__ import annotations


import uuid


from datetime import datetime
from datetime import timezone


from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional



# =============================================================================
# Constants
# =============================================================================

DEFAULT_LOGGER_NAME = "scios"

DEFAULT_LEVEL = "INFO"


SUPPORTED_LEVELS = (

    "TRACE",

    "DEBUG",

    "INFO",

    "WARNING",

    "ERROR",

    "CRITICAL",

)



# =============================================================================
# Type Aliases
# =============================================================================

Metadata = Dict[str, Any]

Statistics = Dict[str, Any]

Handler = Any

Formatter = Any

Filter = Any



# =============================================================================
# Logger
# =============================================================================

class Logger:
    """
    SciOS-NG Logger.

    Central logging component.

    Pipeline:

        Application
             |
             ▼
          Logger
             |
             ├── Filter
             |
             ├── Record
             |
             ├── Formatter
             |
             └── Handler

    """



    # =========================================================================
    # Constructor
    # =========================================================================

    def __init__(
        self,
        name: str = DEFAULT_LOGGER_NAME,
        *,
        level: str = DEFAULT_LEVEL,
        enabled: bool = True,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        """
        Initialize Logger.
        """


        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self.id = str(
            uuid.uuid4()
        )

        self.name = name



        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self.enabled = enabled


        self.created_at = datetime.now(
            timezone.utc
        )


        self.updated_at = self.created_at


        self._frozen = False


        self._closed = False



        # ---------------------------------------------------------------------
        # Logging Configuration
        # ---------------------------------------------------------------------

        level = level.upper()


        if level not in SUPPORTED_LEVELS:

            raise ValueError(
                f"Unsupported log level: {level}"
            )


        self.level = level



        # ---------------------------------------------------------------------
        # Handler Registry
        # ---------------------------------------------------------------------

        self.handlers: Dict[str, Handler] = {}



        # ---------------------------------------------------------------------
        # Formatter Registry
        # ---------------------------------------------------------------------

        self.formatters: Dict[str, Formatter] = {}



        # ---------------------------------------------------------------------
        # Filter Registry
        # ---------------------------------------------------------------------

        self.filters: Dict[str, Filter] = {}



        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self.metadata: Metadata = dict(
            metadata or {}
        )



        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self.statistics: Statistics = {

            "records": 0,

            "emitted": 0,

            "filtered": 0,

            "errors": 0,

            "bytes": 0,

            "latency": 0.0,

        }



        # ---------------------------------------------------------------------
        # Hooks
        # ---------------------------------------------------------------------

        self._hooks = {}
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
        Return logger identity.
        """

        return self._id



    # -------------------------------------------------------------------------
    # Name
    # -------------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Return logger name.
        """

        return self._name



    # -------------------------------------------------------------------------
    # Level
    # -------------------------------------------------------------------------

    @property
    def level(
        self,
    ) -> str:
        """
        Return current logging level.
        """

        return self._level



    @level.setter
    def level(
        self,
        value: str,
    ):
        """
        Update logging level.
        """

        value = value.upper()


        if value not in SUPPORTED_LEVELS:

            raise ValueError(
                f"Unsupported log level: {value}"
            )


        self._level = value


        self.updated_at = datetime.now(
            timezone.utc
        )



    # -------------------------------------------------------------------------
    # Enabled
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Return logger enabled state.
        """

        return self._enabled



    @enabled.setter
    def enabled(
        self,
        value: bool,
    ):
        """
        Update logger state.
        """

        self._enabled = bool(
            value
        )


        self.updated_at = datetime.now(
            timezone.utc
        )



    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Return logger metadata.
        """

        return self._metadata



    @metadata.setter
    def metadata(
        self,
        value: Mapping[str, Any],
    ):
        """
        Update metadata.
        """

        self._metadata = dict(
            value
        )



    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime statistics.
        """

        return self._statistics



    @statistics.setter
    def statistics(
        self,
        value: Mapping[str, Any],
    ):
        """
        Replace statistics.
        """

        self._statistics = dict(
            value
        )



    # -------------------------------------------------------------------------
    # Handler Count
    # -------------------------------------------------------------------------

    @property
    def handler_count(
        self,
    ) -> int:
        """
        Number of registered handlers.
        """

        return len(
            self.handlers
        )



    # -------------------------------------------------------------------------
    # Formatter Count
    # -------------------------------------------------------------------------

    @property
    def formatter_count(
        self,
    ) -> int:
        """
        Number of registered formatters.
        """

        return len(
            self.formatters
        )



    # -------------------------------------------------------------------------
    # Filter Count
    # -------------------------------------------------------------------------

    @property
    def filter_count(
        self,
    ) -> int:
        """
        Number of registered filters.
        """

        return len(
            self.filters
        )



    # -------------------------------------------------------------------------
    # Age
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Logger lifetime in seconds.
        """

        now = datetime.now(
            timezone.utc
        )


        return (
            now
            -
            self.created_at
        ).total_seconds()
# =============================================================================
# Part 3. Logging API
# =============================================================================
    # -------------------------------------------------------------------------
    # Log
    # -------------------------------------------------------------------------

    def log(
        self,
        level: str,
        message: str,
        *,
        source: Optional[str] = None,
        context: Optional[Mapping[str, Any]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        """
        Generic logging entry point.

        Flow:

        log()
          |
          ▼
        emit()
          |
          ▼
        Handler Pipeline
        """

        level = level.upper()


        if level not in SUPPORTED_LEVELS:

            raise ValueError(
                f"Unsupported level: {level}"
            )


        return self.emit(
            level=level,
            message=message,
            source=source,
            context=context,
            metadata=metadata,
        )



    # -------------------------------------------------------------------------
    # Trace
    # -------------------------------------------------------------------------

    def trace(
        self,
        message: str,
        **kwargs,
    ):
        """
        Emit TRACE log.
        """

        return self.log(
            "TRACE",
            message,
            **kwargs,
        )



    # -------------------------------------------------------------------------
    # Debug
    # -------------------------------------------------------------------------

    def debug(
        self,
        message: str,
        **kwargs,
    ):
        """
        Emit DEBUG log.
        """

        return self.log(
            "DEBUG",
            message,
            **kwargs,
        )



    # -------------------------------------------------------------------------
    # Info
    # -------------------------------------------------------------------------

    def info(
        self,
        message: str,
        **kwargs,
    ):
        """
        Emit INFO log.
        """

        return self.log(
            "INFO",
            message,
            **kwargs,
        )



    # -------------------------------------------------------------------------
    # Warning
    # -------------------------------------------------------------------------

    def warning(
        self,
        message: str,
        **kwargs,
    ):
        """
        Emit WARNING log.
        """

        return self.log(
            "WARNING",
            message,
            **kwargs,
        )



    # -------------------------------------------------------------------------
    # Error
    # -------------------------------------------------------------------------

    def error(
        self,
        message: str,
        **kwargs,
    ):
        """
        Emit ERROR log.
        """

        return self.log(
            "ERROR",
            message,
            **kwargs,
        )



    # -------------------------------------------------------------------------
    # Critical
    # -------------------------------------------------------------------------

    def critical(
        self,
        message: str,
        **kwargs,
    ):
        """
        Emit CRITICAL log.
        """

        return self.log(
            "CRITICAL",
            message,
            **kwargs,
        )



    # -------------------------------------------------------------------------
    # Exception
    # -------------------------------------------------------------------------

    def exception(
        self,
        message: str,
        exc: Optional[Exception] = None,
        **kwargs,
    ):
        """
        Emit ERROR log with exception information.
        """

        metadata = dict(
            kwargs.pop(
                "metadata",
                {}
            )
            or {}
        )


        if exc is not None:

            metadata.update(
                {
                    "exception_type":
                        type(exc).__name__,

                    "exception_message":
                        str(exc),
                }
            )


        return self.log(
            "ERROR",
            message,
            metadata=metadata,
            **kwargs,
        )



    # -------------------------------------------------------------------------
    # Emit
    # -------------------------------------------------------------------------

    def emit(
        self,
        *,
        level: str,
        message: str,
        source: Optional[str] = None,
        context: Optional[Mapping[str, Any]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        """
        Core log emission engine.

        Pipeline:

        Logger
          |
          ├── Create Record
          |
          ├── Apply Filters
          |
          ├── Format
          |
          ├── Dispatch Handlers
          |
          └── Update Metrics
        """

        if not self.enabled:

            self.statistics["filtered"] += 1

            return None



        if self._closed:

            raise RuntimeError(
                "Logger is closed"
            )



        start = datetime.now(
            timezone.utc
        )



        try:

            record = {

                "id":
                    str(uuid.uuid4()),

                "timestamp":
                    start.isoformat(),

                "level":
                    level,

                "message":
                    message,

                "source":
                    source,

                "context":
                    dict(
                        context or {}
                    ),

                "metadata":
                    dict(
                        metadata or {}
                    ),

            }



            self.statistics["records"] += 1



            # Dispatch handlers

            for name, handler in self.handlers.items():

                try:

                    handler.emit(
                        record
                    )

                    self.statistics["emitted"] += 1


                except Exception:

                    self.statistics["errors"] += 1



            elapsed = (

                datetime.now(
                    timezone.utc
                )

                -

                start

            ).total_seconds()



            self.statistics["latency"] += elapsed



            return record



        except Exception:

            self.statistics["errors"] += 1

            raise
# =============================================================================
# Part 4. Handler Registry API
# =============================================================================
    # -------------------------------------------------------------------------
    # Add Handler
    # -------------------------------------------------------------------------

    def add_handler(
        self,
        name: str,
        handler: Handler,
    ) -> "Logger":
        """
        Register a log handler.

        Handler requirements:
            emit(record)
        """

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen"
            )


        self.handlers[name] = {

            "object": handler,

            "enabled": True,

        }


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Remove Handler
    # -------------------------------------------------------------------------

    def remove_handler(
        self,
        name: str,
    ) -> bool:
        """
        Remove handler from registry.
        """

        if name not in self.handlers:

            return False


        del self.handlers[name]


        self.updated_at = datetime.now(
            timezone.utc
        )


        return True



    # -------------------------------------------------------------------------
    # Handler
    # -------------------------------------------------------------------------

    def handler(
        self,
        name: str,
    ) -> Handler:
        """
        Get handler object.
        """

        if name not in self.handlers:

            raise KeyError(
                f"Handler not found: {name}"
            )


        return self.handlers[name]["object"]



    # -------------------------------------------------------------------------
    # Handlers
    # -------------------------------------------------------------------------

    def handlers(
        self,
    ) -> Dict[str, Handler]:
        """
        Return all registered handlers.
        """

        return {

            name:
                item["object"]

            for name, item
            in self.handlers.items()

        }



    # -------------------------------------------------------------------------
    # Has Handler
    # -------------------------------------------------------------------------

    def has_handler(
        self,
        name: str,
    ) -> bool:
        """
        Check handler existence.
        """

        return (
            name
            in
            self.handlers
        )



    # -------------------------------------------------------------------------
    # Enable Handler
    # -------------------------------------------------------------------------

    def enable_handler(
        self,
        name: str,
    ) -> "Logger":
        """
        Enable specific handler.
        """

        if name not in self.handlers:

            raise KeyError(
                f"Handler not found: {name}"
            )


        self.handlers[name]["enabled"] = True


        return self



    # -------------------------------------------------------------------------
    # Disable Handler
    # -------------------------------------------------------------------------

    def disable_handler(
        self,
        name: str,
    ) -> "Logger":
        """
        Disable specific handler.
        """

        if name not in self.handlers:

            raise KeyError(
                f"Handler not found: {name}"
            )


        self.handlers[name]["enabled"] = False


        return self



    # -------------------------------------------------------------------------
    # Handler Names
    # -------------------------------------------------------------------------

    def handler_names(
        self,
    ) -> List[str]:
        """
        Return registered handler names.
        """

        return list(
            self.handlers.keys()
        )



    # -------------------------------------------------------------------------
    # Handler Count
    # -------------------------------------------------------------------------

    @property
    def handler_count(
        self,
    ) -> int:
        """
        Return number of handlers.
        """

        return len(
            self.handlers
        )



    # -------------------------------------------------------------------------
    # Clear Handlers
    # -------------------------------------------------------------------------

    def clear_handlers(
        self,
    ) -> "Logger":
        """
        Remove all handlers.
        """

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen"
            )


        self.handlers.clear()


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Dispatch
    # -------------------------------------------------------------------------

    def dispatch(
        self,
        record: Mapping[str, Any],
    ) -> int:
        """
        Dispatch record to enabled handlers.

        Returns:
            number of successful dispatches
        """

        dispatched = 0


        for name, entry in self.handlers.items():


            if not entry["enabled"]:

                continue


            handler = entry["object"]


            try:

                handler.emit(
                    record
                )


                dispatched += 1


            except Exception:

                self.statistics["errors"] += 1



        return dispatched
# =============================================================================
# Part 5. Formatter Registry API
# =============================================================================
    # -------------------------------------------------------------------------
    # Add Formatter
    # -------------------------------------------------------------------------

    def add_formatter(
        self,
        name: str,
        formatter: Formatter,
    ) -> "Logger":
        """
        Register a log formatter.

        Formatter requirements:
            format(record) -> str | dict
        """

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen"
            )


        self.formatters[name] = {

            "object": formatter,

            "enabled": True,

        }


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Remove Formatter
    # -------------------------------------------------------------------------

    def remove_formatter(
        self,
        name: str,
    ) -> bool:
        """
        Remove formatter from registry.
        """

        if name not in self.formatters:

            return False


        del self.formatters[name]


        if getattr(
            self,
            "_active_formatter",
            None
        ) == name:

            self._active_formatter = None


        self.updated_at = datetime.now(
            timezone.utc
        )


        return True



    # -------------------------------------------------------------------------
    # Formatter
    # -------------------------------------------------------------------------

    def formatter(
        self,
        name: str,
    ) -> Formatter:
        """
        Get formatter object.
        """

        if name not in self.formatters:

            raise KeyError(
                f"Formatter not found: {name}"
            )


        return self.formatters[name]["object"]



    # -------------------------------------------------------------------------
    # Formatters
    # -------------------------------------------------------------------------

    def formatters(
        self,
    ) -> Dict[str, Formatter]:
        """
        Return all registered formatters.
        """

        return {

            name:
                item["object"]

            for name, item
            in self.formatters.items()

        }



    # -------------------------------------------------------------------------
    # Has Formatter
    # -------------------------------------------------------------------------

    def has_formatter(
        self,
        name: str,
    ) -> bool:
        """
        Check formatter existence.
        """

        return (
            name
            in
            self.formatters
        )



    # -------------------------------------------------------------------------
    # Use Formatter
    # -------------------------------------------------------------------------

    def use_formatter(
        self,
        name: str,
    ) -> "Logger":
        """
        Set active formatter.
        """

        if name not in self.formatters:

            raise KeyError(
                f"Formatter not found: {name}"
            )


        self._active_formatter = name


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Formatter Names
    # -------------------------------------------------------------------------

    def formatter_names(
        self,
    ) -> List[str]:
        """
        Return formatter names.
        """

        return list(
            self.formatters.keys()
        )



    # -------------------------------------------------------------------------
    # Formatter Count
    # -------------------------------------------------------------------------

    @property
    def formatter_count(
        self,
    ) -> int:
        """
        Return formatter count.
        """

        return len(
            self.formatters
        )



    # -------------------------------------------------------------------------
    # Clear Formatters
    # -------------------------------------------------------------------------

    def clear_formatters(
        self,
    ) -> "Logger":
        """
        Remove all formatters.
        """

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen"
            )


        self.formatters.clear()


        self._active_formatter = None


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Format Record
    # -------------------------------------------------------------------------

    def format_record(
        self,
        record: Mapping[str, Any],
        formatter: Optional[str] = None,
    ) -> Any:
        """
        Format log record.

        Priority:

        1. Explicit formatter
        2. Active formatter
        3. Raw record
        """

        target = (

            formatter

            if formatter is not None

            else getattr(
                self,
                "_active_formatter",
                None
            )

        )


        if target is None:

            return dict(
                record
            )


        if target not in self.formatters:

            raise KeyError(
                f"Formatter not found: {target}"
            )


        formatter_obj = self.formatters[target]["object"]


        try:

            if hasattr(
                formatter_obj,
                "format_record"
            ):

                return formatter_obj.format_record(
                    record
                )


            if hasattr(
                formatter_obj,
                "format"
            ):

                return formatter_obj.format(
                    record
                )


            raise TypeError(
                "Invalid formatter object"
            )


        except Exception:

            self.statistics["errors"] += 1

            raise
# =============================================================================
# Part 6. Filter Registry API
# =============================================================================
    # -------------------------------------------------------------------------
    # Add Filter
    # -------------------------------------------------------------------------

    def add_filter(
        self,
        name: str,
        filter_obj: Filter,
    ) -> "Logger":
        """
        Register a log filter.

        Filter requirements:

            filter(record) -> bool

        Return:
            True  : accept record
            False : reject record
        """

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen"
            )


        self.filters[name] = {

            "object": filter_obj,

            "enabled": True,

        }


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Remove Filter
    # -------------------------------------------------------------------------

    def remove_filter(
        self,
        name: str,
    ) -> bool:
        """
        Remove filter from registry.
        """

        if name not in self.filters:

            return False


        del self.filters[name]


        self.updated_at = datetime.now(
            timezone.utc
        )


        return True



    # -------------------------------------------------------------------------
    # Filter
    # -------------------------------------------------------------------------

    def filter(
        self,
        name: str,
    ) -> Filter:
        """
        Get filter object.
        """

        if name not in self.filters:

            raise KeyError(
                f"Filter not found: {name}"
            )


        return self.filters[name]["object"]



    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------

    def filters(
        self,
    ) -> Dict[str, Filter]:
        """
        Return all registered filters.
        """

        return {

            name:
                item["object"]

            for name, item
            in self.filters.items()

        }



    # -------------------------------------------------------------------------
    # Has Filter
    # -------------------------------------------------------------------------

    def has_filter(
        self,
        name: str,
    ) -> bool:
        """
        Check filter existence.
        """

        return (
            name
            in
            self.filters
        )



    # -------------------------------------------------------------------------
    # Enable Filter
    # -------------------------------------------------------------------------

    def enable_filter(
        self,
        name: str,
    ) -> "Logger":
        """
        Enable filter.
        """

        if name not in self.filters:

            raise KeyError(
                f"Filter not found: {name}"
            )


        self.filters[name]["enabled"] = True


        return self



    # -------------------------------------------------------------------------
    # Disable Filter
    # -------------------------------------------------------------------------

    def disable_filter(
        self,
        name: str,
    ) -> "Logger":
        """
        Disable filter.
        """

        if name not in self.filters:

            raise KeyError(
                f"Filter not found: {name}"
            )


        self.filters[name]["enabled"] = False


        return self



    # -------------------------------------------------------------------------
    # Filter Names
    # -------------------------------------------------------------------------

    def filter_names(
        self,
    ) -> List[str]:
        """
        Return registered filter names.
        """

        return list(
            self.filters.keys()
        )



    # -------------------------------------------------------------------------
    # Filter Count
    # -------------------------------------------------------------------------

    @property
    def filter_count(
        self,
    ) -> int:
        """
        Return number of filters.
        """

        return len(
            self.filters
        )



    # -------------------------------------------------------------------------
    # Clear Filters
    # -------------------------------------------------------------------------

    def clear_filters(
        self,
    ) -> "Logger":
        """
        Remove all filters.
        """

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen"
            )


        self.filters.clear()


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Apply Filters
    # -------------------------------------------------------------------------

    def apply_filters(
        self,
        record: Mapping[str, Any],
    ) -> bool:
        """
        Apply all enabled filters.

        Pipeline:

            Record
              |
              ▼
          Filter 1
              |
              ▼
          Filter 2
              |
              ▼
          Accepted / Rejected

        """

        for name, entry in self.filters.items():


            if not entry["enabled"]:

                continue


            filter_obj = entry["object"]


            try:

                result = filter_obj(
                    record
                )


                if result is False:

                    self.statistics["filtered"] += 1

                    return False



            except Exception:

                self.statistics["errors"] += 1

                return False



        return True
# =============================================================================
# Part 7. Lifecycle API
# =============================================================================
    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "Logger":
        """
        Enable logger.

        State transition:

            disabled -> enabled
        """

        if self._closed:

            raise RuntimeError(
                "Cannot enable closed logger"
            )


        self._enabled = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        self.emit(
            level="DEBUG",
            message="Logger enabled"
        )


        return self



    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "Logger":
        """
        Disable logger.

        Log records are ignored while disabled.
        """

        self._enabled = False


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "Logger":
        """
        Freeze configuration.

        Frozen logger:

        - cannot add handlers
        - cannot remove handlers
        - cannot modify formatter
        - cannot modify filters
        """

        self._frozen = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "Logger":
        """
        Unlock logger configuration.
        """

        self._frozen = False


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "Logger":
        """
        Close logger.

        After close:

        - emit disabled
        - handlers remain registered
        - state preserved
        """

        self._closed = True

        self._enabled = False


        self.updated_at = datetime.now(
            timezone.utc
        )


        # close handlers

        for entry in self.handlers.values():

            handler = entry["object"]


            if hasattr(
                handler,
                "close"
            ):

                try:

                    handler.close()


                except Exception:

                    self.statistics["errors"] += 1



        return self



    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "Logger":
        """
        Reopen closed logger.

        State transition:

            closed -> active
        """

        if not self._closed:

            return self


        self._closed = False


        self._enabled = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self
# =============================================================================
# Part 8. Runtime Operations
# =============================================================================

from copy import deepcopy


    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
        *,
        reset_statistics: bool = True,
        keep_configuration: bool = True,
    ) -> "Logger":
        """
        Reset runtime state.

        Parameters
        ----------
        reset_statistics:
            Reset runtime counters.

        keep_configuration:
            Preserve handlers, formatters and filters.
        """

        self._enabled = True
        self._frozen = False
        self._closed = False

        if reset_statistics:

            self._statistics = {

                "records": 0,
                "emitted": 0,
                "filtered": 0,
                "errors": 0,
                "bytes": 0,
                "latency": 0.0,

            }

        if not keep_configuration:

            self.handlers.clear()
            self.formatters.clear()
            self.filters.clear()

            self._active_formatter = None

        self.updated_at = datetime.now(
            timezone.utc
        )

        return self


    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
    ) -> "Logger":
        """
        Clear runtime registries.

        Does not modify logger identity.
        """

        if self._frozen:

            raise RuntimeError(
                "Logger is frozen"
            )

        self.handlers.clear()
        self.formatters.clear()
        self.filters.clear()

        self._active_formatter = None

        self.updated_at = datetime.now(
            timezone.utc
        )

        return self


    # -------------------------------------------------------------------------
    # Snapshot
    # -------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Capture runtime state.
        """

        return {

            "enabled":
                self._enabled,

            "frozen":
                self._frozen,

            "closed":
                self._closed,

            "level":
                self._level,

            "statistics":
                deepcopy(
                    self._statistics
                ),

            "metadata":
                deepcopy(
                    self._metadata
                ),

            "handlers":
                deepcopy(
                    self.handlers
                ),

            "formatters":
                deepcopy(
                    self.formatters
                ),

            "filters":
                deepcopy(
                    self.filters
                ),

            "active_formatter":
                self._active_formatter,

        }


    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "Logger":
        """
        Restore runtime state from snapshot.
        """

        self._enabled = snapshot.get(
            "enabled",
            True
        )

        self._frozen = snapshot.get(
            "frozen",
            False
        )

        self._closed = snapshot.get(
            "closed",
            False
        )

        self._level = snapshot.get(
            "level",
            self._level
        )

        self._statistics = deepcopy(
            snapshot.get(
                "statistics",
                {}
            )
        )

        self._metadata = deepcopy(
            snapshot.get(
                "metadata",
                {}
            )
        )

        self.handlers = deepcopy(
            snapshot.get(
                "handlers",
                {}
            )
        )

        self.formatters = deepcopy(
            snapshot.get(
                "formatters",
                {}
            )
        )

        self.filters = deepcopy(
            snapshot.get(
                "filters",
                {}
            )
        )

        self._active_formatter = snapshot.get(
            "active_formatter"
        )

        self.updated_at = datetime.now(
            timezone.utc
        )

        return self


    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "Logger":
        """
        Create a deep cloned logger.
        """

        cloned = self.__class__(
            name=self.name,
            level=self.level,
            enabled=self.enabled,
            metadata=deepcopy(
                self.metadata
            ),
        )

        cloned.restore(
            self.snapshot()
        )

        return cloned


    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def copy(
        self,
    ) -> "Logger":
        """
        Alias for clone().
        """

        return self.clone()
# =============================================================================
# Part 9. Statistics & Diagnostics
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

            "level": self.level,

            "enabled": self.enabled,

            "active": self.active,

            "records": self.record_count,

            "handlers": self.handler_count,

            "formatters": self.formatter_count,

            "filters": self.filter_count,

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

                "frozen": self.frozen,

                "closed": self.closed,

                "active": self.active,

                "level": self.level,

            },

            "registries": {

                "handlers": self.handler_names(),

                "formatters": self.formatter_names(),

                "filters": self.filter_names(),

            },

            "statistics": dict(self.statistics),

            "metadata": dict(self.metadata),

            "uptime": self.uptime,

        }


    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return logger health information.
        """

        healthy = (

            self.enabled

            and

            not self.closed

        )

        return {

            "healthy": healthy,

            "errors": self.error_count,

            "latency": self.latency,

            "handlers": self.handler_count,

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

        if self.closed:

            return "closed"

        if self.frozen:

            return "frozen"

        if not self.enabled:

            return "disabled"

        return "active"


    # -------------------------------------------------------------------------
    # Record Count
    # -------------------------------------------------------------------------

    @property
    def record_count(
        self,
    ) -> int:

        return self.statistics.get(
            "records",
            0
        )


    # -------------------------------------------------------------------------
    # Handler Count
    # -------------------------------------------------------------------------

    @property
    def handler_count(
        self,
    ) -> int:

        return len(
            self.handlers
        )


    # -------------------------------------------------------------------------
    # Formatter Count
    # -------------------------------------------------------------------------

    @property
    def formatter_count(
        self,
    ) -> int:

        return len(
            self.formatters
        )


    # -------------------------------------------------------------------------
    # Filter Count
    # -------------------------------------------------------------------------

    @property
    def filter_count(
        self,
    ) -> int:

        return len(
            self.filters
        )


    # -------------------------------------------------------------------------
    # Error Count
    # -------------------------------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:

        return self.statistics.get(
            "errors",
            0
        )


    # -------------------------------------------------------------------------
    # Uptime
    # -------------------------------------------------------------------------

    @property
    def uptime(
        self,
    ) -> float:
        """
        Logger uptime in seconds.
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
        Average emit latency.
        """

        emitted = max(
            1,
            self.statistics.get(
                "emitted",
                0
            )
        )

        return (

            self.statistics.get(
                "latency",
                0.0
            )

            /

            emitted

        )
# =============================================================================
# Part 10. Serialization
# =============================================================================

import json


    # -------------------------------------------------------------------------
    # To Dict
    # -------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize logger state to a dictionary.
        """

        return {

            "id": self.id,

            "name": self.name,

            "level": self.level,

            "enabled": self.enabled,

            "frozen": self.frozen,

            "closed": self.closed,

            "metadata": dict(self.metadata),

            "statistics": dict(self.statistics),

            "handler_names": self.handler_names(),

            "formatter_names": self.formatter_names(),

            "filter_names": self.filter_names(),

            "active_formatter": getattr(
                self,
                "_active_formatter",
                None,
            ),

            "created_at": self.created_at.isoformat(),

            "updated_at": self.updated_at.isoformat(),

        }


    # -------------------------------------------------------------------------
    # From Dict
    # -------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "Logger":
        """
        Restore Logger from dictionary.

        Runtime registries (handlers, formatters, filters) are created empty.
        They should be re-registered by the caller.
        """

        logger = cls(

            name=data.get(
                "name",
                DEFAULT_LOGGER_NAME,
            ),

            level=data.get(
                "level",
                DEFAULT_LEVEL,
            ),

            enabled=data.get(
                "enabled",
                True,
            ),

            metadata=data.get(
                "metadata",
                {},
            ),

        )

        logger._statistics.update(

            data.get(
                "statistics",
                {},
            )

        )

        logger._frozen = data.get(
            "frozen",
            False,
        )

        logger._closed = data.get(
            "closed",
            False,
        )

        logger._active_formatter = data.get(
            "active_formatter",
        )

        return logger


    # -------------------------------------------------------------------------
    # To JSON
    # -------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize logger to JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=False,

        )


    # -------------------------------------------------------------------------
    # From JSON
    # -------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "Logger":
        """
        Restore Logger from JSON.
        """

        return cls.from_dict(

            json.loads(text)

        )


    # -------------------------------------------------------------------------
    # Serialize
    # -------------------------------------------------------------------------

    def serialize(
        self,
    ) -> str:
        """
        Default serialization entry point.
        """

        return self.to_json()


    # -------------------------------------------------------------------------
    # Deserialize
    # -------------------------------------------------------------------------

    @classmethod
    def deserialize(
        cls,
        payload: str,
    ) -> "Logger":
        """
        Default deserialization entry point.
        """

        return cls.from_json(
            payload
        )                                                                        