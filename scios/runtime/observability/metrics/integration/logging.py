"""
SciOS-NG Metrics Logging Integration

scios/runtime/observability/metrics/integration/logging.py
"""

from __future__ import annotations

import uuid
import time
import copy

from datetime import datetime
from threading import RLock
from typing import Any, Optional



class MetricLoggingIntegration:
    """
    Logging bridge for SciOS-NG Metrics.

    Converts runtime/application logs
    into observable metrics.
    """


    # ======================================================
    # Part 1. Foundation
    # ======================================================


    def __init__(
        self,
        name: str = "MetricLoggingIntegration",
        config: Optional[dict] = None,
    ):

        self._lock = RLock()


        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name

        self._version = "0.1.0"



        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._running = False

        self._frozen = False

        self._closed = False



        # --------------------------------------------------
        # Logging Configuration
        # --------------------------------------------------

        self._config = config or {

            "level":
                "INFO",

            "capture_errors":
                True,

            "capture_warnings":
                True,

            "capture_debug":
                False,

        }



        # --------------------------------------------------
        # Logger Registry
        # --------------------------------------------------

        self._registry = {}



        # --------------------------------------------------
        # Log Storage
        # --------------------------------------------------

        self._logs = []



        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at


        self._metadata = {

            "component":
                "metrics.integration.logging",

            "engine":
                "SciOS-NG",

            "version":
                self._version,

        }



        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self._log_count = 0

        self._error_count = 0

        self._warning_count = 0

        self._debug_count = 0

        self._last_latency = 0.0

        self._start_time = time.time()



        # --------------------------------------------------
        # Events
        # --------------------------------------------------

        self._hooks = {}

        self._events = []
    # ======================================================
    # Part 2. Logging API
    # ======================================================


    def log(
        self,
        level: str,
        message: str,
        **context,
    ) -> dict:
        """
        Generic logging API.

        Levels:
        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL
        """

        start = time.perf_counter()


        if not self._enabled:

            return {

                "status":

                    "disabled",

            }



        record = {

            "id":

                str(uuid.uuid4()),


            "level":

                level.upper(),


            "message":

                message,


            "context":

                context,


            "timestamp":

                datetime.utcnow(),

        }



        try:

            with self._lock:

                self._logs.append(

                    record

                )


                self._log_count += 1



                if level.upper() == "ERROR":

                    self._error_count += 1



                elif level.upper() == "WARNING":

                    self._warning_count += 1



                elif level.upper() == "DEBUG":

                    self._debug_count += 1



                self._updated_at = datetime.utcnow()



            self.emit(

                "log",

                record=record,

            )



            return record



        except Exception as exc:

            self._error_count += 1


            self.emit(

                "logging_error",

                error=str(exc),

            )


            raise



        finally:

            self._last_latency = (

                time.perf_counter()

                -

                start

            )



    def debug(
        self,
        message: str,
        **context,
    ):
        """
        Write DEBUG log.
        """

        if not self._config.get(

            "capture_debug",

            False,

        ):

            return None



        return self.log(

            "DEBUG",

            message,

            **context,

        )



    def info(
        self,
        message: str,
        **context,
    ):
        """
        Write INFO log.
        """

        return self.log(

            "INFO",

            message,

            **context,

        )



    def warning(
        self,
        message: str,
        **context,
    ):
        """
        Write WARNING log.
        """

        if not self._config.get(

            "capture_warnings",

            True,

        ):

            return None



        return self.log(

            "WARNING",

            message,

            **context,

        )



    def error(
        self,
        message: str,
        **context,
    ):
        """
        Write ERROR log.
        """

        if not self._config.get(

            "capture_errors",

            True,

        ):

            return None



        return self.log(

            "ERROR",

            message,

            **context,

        )



    def critical(
        self,
        message: str,
        **context,
    ):
        """
        Write CRITICAL log.
        """

        return self.log(

            "CRITICAL",

            message,

            **context,

        )



    def exception(
        self,
        message: str,
        exc: Exception | None = None,
        **context,
    ):
        """
        Write exception log.
        """

        if exc is not None:

            context["exception"] = {

                "type":

                    exc.__class__.__name__,


                "message":

                    str(exc),

            }



        return self.log(

            "ERROR",

            message,

            **context,

        )



    def capture(
        self,
        level: str,
        message: str,
        source: str | None = None,
        **context,
    ):
        """
        Capture external log event.

        Used by:
        - Python logging
        - Runtime logs
        - Application logs
        """

        if source:

            context["source"] = source



        return self.log(

            level,

            message,

            **context,

        )
    # ======================================================
    # Part 3. Log Handlers
    # ======================================================


    def add_handler(
        self,
        name: str,
        handler,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register log handler.

        Handler examples:
        - ConsoleHandler
        - FileHandler
        - RuntimeHandler
        - QTCHandler
        - DistributedHandler
        """

        if not callable(handler):

            raise TypeError(
                "Handler must be callable"
            )


        with self._lock:

            self._registry[name] = {

                "name":

                    name,


                "handler":

                    handler,


                "enabled":

                    enabled,


                "metadata":

                    metadata or {},


                "created_at":

                    datetime.utcnow(),

            }


            self._updated_at = datetime.utcnow()


        return self



    def remove_handler(
        self,
        name: str,
    ):
        """
        Remove log handler.
        """

        with self._lock:

            self._registry.pop(

                name,

                None,

            )


            self._updated_at = datetime.utcnow()


        return self



    def handler(
        self,
        name: str,
        default=None,
    ):
        """
        Get registered handler.
        """

        entry = self._registry.get(

            name

        )


        if entry is None:

            return default



        return entry["handler"]



    def handlers(
        self,
    ):
        """
        Return all registered handlers.
        """

        return dict(

            self._registry

        )



    def emit_handler(
        self,
        name: str,
        record: dict,
    ):
        """
        Send log record to handler.
        """

        entry = self._registry.get(

            name

        )


        if entry is None:

            raise KeyError(

                f"Unknown handler: {name}"

            )



        if not entry["enabled"]:

            return None



        handler = entry["handler"]



        return handler(

            record

        )



    def enable_handler(
        self,
        name: str,
    ):
        """
        Enable log handler.
        """

        entry = self._registry.get(

            name

        )


        if entry:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()


        return self



    def disable_handler(
        self,
        name: str,
    ):
        """
        Disable log handler.
        """

        entry = self._registry.get(

            name

        )


        if entry:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()


        return self



    def builtin_handlers(
        self,
    ):
        """
        Register SciOS-NG builtin handlers.
        """


        # --------------------------------------------------
        # Console Handler
        # --------------------------------------------------

        def console_handler(
            record
        ):

            print(

                f"[{record['level']}] "

                f"{record['message']}"

            )


        self.add_handler(

            "console",

            console_handler,

            metadata={

                "type":

                    "stdout",

                "engine":

                    "SciOS",

            }

        )



        # --------------------------------------------------
        # Internal Metrics Handler
        # --------------------------------------------------

        def metrics_handler(
            record
        ):

            return {

                "metric":

                    "log_event",


                "level":

                    record["level"],

            }



        self.add_handler(

            "metrics",

            metrics_handler,

            metadata={

                "type":

                    "internal",

                "engine":

                    "Metrics",

            }

        )


        return self
    # ======================================================
    # Part 4. Logger Registry API
    # ======================================================

    def register_logger(
        self,
        name: str,
        logger,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register logger backend.

        Examples
        --------
        - Application Logger
        - Kernel Logger
        - Runtime Logger
        - QTC Logger
        - Edge Logger
        """

        with self._lock:

            if not hasattr(self, "_logger_registry"):
                self._logger_registry = {}

            self._logger_registry[name] = {

                "name": name,

                "logger": logger,

                "enabled": enabled,

                "metadata": metadata or {},

                "created_at": datetime.utcnow(),

            }

            self._updated_at = datetime.utcnow()

        return self



    def remove_logger(
        self,
        name: str,
    ):
        """
        Remove logger backend.
        """

        with self._lock:

            if hasattr(self, "_logger_registry"):

                self._logger_registry.pop(
                    name,
                    None,
                )

            self._updated_at = datetime.utcnow()

        return self



    def logger(
        self,
        name: str,
        default=None,
    ):
        """
        Return logger backend.
        """

        registry = getattr(
            self,
            "_logger_registry",
            {},
        )

        entry = registry.get(name)

        if entry is None:
            return default

        return entry["logger"]



    def loggers(
        self,
    ):
        """
        Return all registered loggers.
        """

        return dict(
            getattr(
                self,
                "_logger_registry",
                {},
            )
        )



    def contains_logger(
        self,
        name: str,
    ) -> bool:
        """
        Check whether logger exists.
        """

        return name in getattr(
            self,
            "_logger_registry",
            {},
        )



    def exists_logger(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_logger().
        """

        return self.contains_logger(
            name
        )



    def enable_logger(
        self,
        name: str,
    ):
        """
        Enable logger backend.
        """

        registry = getattr(
            self,
            "_logger_registry",
            {},
        )

        if name in registry:

            registry[name]["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self



    def disable_logger(
        self,
        name: str,
    ):
        """
        Disable logger backend.
        """

        registry = getattr(
            self,
            "_logger_registry",
            {},
        )

        if name in registry:

            registry[name]["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self



    def logger_names(
        self,
    ) -> list[str]:
        """
        Return registered logger names.
        """

        return list(
            getattr(
                self,
                "_logger_registry",
                {},
            ).keys()
        )



    def logger_count(
        self,
    ) -> int:
        """
        Return logger count.
        """

        return len(
            getattr(
                self,
                "_logger_registry",
                {},
            )
        )



    def clear_loggers(
        self,
    ):
        """
        Remove all logger backends.
        """

        with self._lock:

            if hasattr(
                self,
                "_logger_registry",
            ):

                self._logger_registry.clear()

            self._updated_at = datetime.utcnow()

        return self



    def execute_logger(
        self,
        name: str,
        level: str,
        message: str,
        **context,
    ):
        """
        Execute specific logger backend.
        """

        registry = getattr(
            self,
            "_logger_registry",
            {},
        )

        entry = registry.get(name)

        if entry is None:

            raise KeyError(
                f"Unknown logger: {name}"
            )

        if not entry["enabled"]:

            return None

        logger = entry["logger"]


        # Python logging.Logger style
        if hasattr(logger, "log"):

            return logger.log(
                level,
                message,
                **context,
            )


        # Callable backend
        if callable(logger):

            return logger(
                level,
                message,
                **context,
            )


        raise TypeError(
            f"Logger '{name}' is not executable."
        )
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(
        self,
    ):
        """
        Enable logging integration.
        """

        with self._lock:

            self._enabled = True

            self._running = True

            self._updated_at = datetime.utcnow()

        return self



    def disable(
        self,
    ):
        """
        Disable logging integration.

        Logging requests will be ignored
        until enable() is called.
        """

        with self._lock:

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self



    def freeze(
        self,
    ):
        """
        Freeze logging engine.

        Registry and configuration are kept,
        but new log records are not accepted.
        """

        with self._lock:

            self._frozen = True

            self._running = False

            self._updated_at = datetime.utcnow()

        return self



    def unfreeze(
        self,
    ):
        """
        Resume logging engine.
        """

        with self._lock:

            self._frozen = False

            self._running = self._enabled

            self._updated_at = datetime.utcnow()

        return self



    def close(
        self,
    ):
        """
        Close logging integration.

        Clears active execution state while
        preserving object identity.
        """

        with self._lock:

            self._closed = True

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self



    def reopen(
        self,
    ):
        """
        Reopen previously closed logging
        integration.
        """

        with self._lock:

            self._closed = False

            self._enabled = True

            self._running = True

            self._updated_at = datetime.utcnow()

        return self



    @property
    def active(
        self,
    ) -> bool:
        """
        Return True when the logging
        integration can accept log events.
        """

        return (

            self._enabled

            and

            self._running

            and

            not self._frozen

            and

            not self._closed

        )
    # ======================================================
    # Part 6. Runtime Operations
    # ======================================================

    def reset(
        self,
    ):
        """
        Reset runtime statistics while
        preserving configuration,
        handlers and logger registry.
        """

        with self._lock:

            self._logs.clear()

            self._events.clear()

            self._log_count = 0

            self._error_count = 0

            self._warning_count = 0

            self._debug_count = 0

            self._last_latency = 0.0

            self._updated_at = datetime.utcnow()

        return self



    def clear(
        self,
    ):
        """
        Clear collected logs only.
        """

        with self._lock:

            self._logs.clear()

            self._updated_at = datetime.utcnow()

        return self



    def flush(
        self,
    ):
        """
        Flush all enabled handlers.

        Handlers exposing a ``flush()``
        method will be invoked.
        """

        with self._lock:

            for entry in self._registry.values():

                if not entry["enabled"]:
                    continue

                handler = entry["handler"]

                flush = getattr(
                    handler,
                    "flush",
                    None,
                )

                if callable(flush):
                    flush()

        return self



    def snapshot(
        self,
    ) -> dict:
        """
        Create runtime checkpoint.
        """

        with self._lock:

            snapshot = {

                "state": {

                    "enabled": self._enabled,

                    "running": self._running,

                    "frozen": self._frozen,

                    "closed": self._closed,

                },

                "statistics": {

                    "log_count": self._log_count,

                    "error_count": self._error_count,

                    "warning_count": self._warning_count,

                    "debug_count": self._debug_count,

                    "latency": self._last_latency,

                },

                "logs": copy.deepcopy(
                    self._logs
                ),

                "metadata": copy.deepcopy(
                    self._metadata
                ),

                "config": copy.deepcopy(
                    self._config
                ),

            }

            self._snapshot = snapshot

            return copy.deepcopy(snapshot)



    def restore(
        self,
        snapshot: dict | None = None,
    ):
        """
        Restore checkpoint.
        """

        if snapshot is None:
            snapshot = getattr(
                self,
                "_snapshot",
                None,
            )

        if snapshot is None:
            return self

        with self._lock:

            state = snapshot.get(
                "state",
                {},
            )

            self._enabled = state.get(
                "enabled",
                True,
            )

            self._running = state.get(
                "running",
                False,
            )

            self._frozen = state.get(
                "frozen",
                False,
            )

            self._closed = state.get(
                "closed",
                False,
            )

            stats = snapshot.get(
                "statistics",
                {},
            )

            self._log_count = stats.get(
                "log_count",
                0,
            )

            self._error_count = stats.get(
                "error_count",
                0,
            )

            self._warning_count = stats.get(
                "warning_count",
                0,
            )

            self._debug_count = stats.get(
                "debug_count",
                0,
            )

            self._last_latency = stats.get(
                "latency",
                0.0,
            )

            self._logs = copy.deepcopy(
                snapshot.get(
                    "logs",
                    [],
                )
            )

            self._metadata = copy.deepcopy(
                snapshot.get(
                    "metadata",
                    {},
                )
            )

            self._config = copy.deepcopy(
                snapshot.get(
                    "config",
                    {},
                )
            )

            self._updated_at = datetime.utcnow()

        return self



    def clone(
        self,
    ):
        """
        Clone integration.
        """

        cloned = self.__class__(

            name=self._name,

            config=copy.deepcopy(
                self._config
            ),

        )

        cloned._registry = copy.deepcopy(
            self._registry
        )

        cloned._logger_registry = copy.deepcopy(
            self._logger_registry
        )

        cloned.restore(
            self.snapshot()
        )

        return cloned



    def copy(
        self,
    ):
        """
        Alias of clone().
        """

        return self.clone()
    # ======================================================
    # Part 7. Statistics & Diagnostics
    # ======================================================

    def summary(
        self,
    ) -> dict:
        """
        Return compact logging summary.
        """

        return {

            "id":
                self._id,

            "name":
                self._name,

            "enabled":
                self._enabled,

            "running":
                self._running,

            "frozen":
                self._frozen,

            "closed":
                self._closed,

            "handlers":
                len(self._registry),

            "loggers":
                len(self._logger_registry),

            "logs":
                self._log_count,

            "errors":
                self._error_count,

            "warnings":
                self._warning_count,

            "debug":
                self._debug_count,

            "uptime":
                self.uptime,

            "latency":
                self.latency,

        }



    def report(
        self,
    ) -> dict:
        """
        Return detailed diagnostic report.
        """

        return {

            "identity": {

                "id":
                    self._id,

                "name":
                    self._name,

                "version":
                    self._version,

            },

            "runtime": {

                "enabled":
                    self._enabled,

                "running":
                    self._running,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

            },

            "configuration":

                copy.deepcopy(
                    self._config
                ),

            "statistics": {

                "log_count":
                    self._log_count,

                "error_count":
                    self._error_count,

                "warning_count":
                    self._warning_count,

                "debug_count":
                    self._debug_count,

                "handler_count":
                    len(self._registry),

                "logger_count":
                    len(self._logger_registry),

                "uptime":
                    self.uptime,

                "latency":
                    self.latency,

            },

            "handlers":

                list(
                    self._registry.keys()
                ),

            "loggers":

                list(
                    self._logger_registry.keys()
                ),

            "metadata":

                copy.deepcopy(
                    self._metadata
                ),

        }



    def health(
        self,
    ) -> dict:
        """
        Evaluate logging engine health.
        """

        healthy = (

            self.active

            and

            self._error_count == 0

        )


        return {

            "healthy":
                healthy,

            "status":

                "healthy"

                if healthy

                else

                "degraded",

            "errors":
                self._error_count,

            "warnings":
                self._warning_count,

            "handlers":
                len(self._registry),

            "loggers":
                len(self._logger_registry),

        }



    def status(
        self,
    ) -> str:
        """
        Return runtime lifecycle status.
        """

        if self._closed:

            return "closed"

        if self._frozen:

            return "frozen"

        if not self._enabled:

            return "disabled"

        if self._running:

            return "running"

        return "ready"



    # ======================================================
    # Statistics Properties
    # ======================================================

    @property
    def log_count(
        self,
    ) -> int:
        """
        Number of processed logs.
        """

        return self._log_count



    @property
    def warning_count(
        self,
    ) -> int:
        """
        Number of warning logs.
        """

        return self._warning_count



    @property
    def debug_count(
        self,
    ) -> int:
        """
        Number of debug logs.
        """

        return self._debug_count



    @property
    def error_count(
        self,
    ) -> int:
        """
        Number of error logs.
        """

        return self._error_count



    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime uptime in seconds.
        """

        return (

            time.time()

            -

            self._start_time

        )



    @property
    def latency(
        self,
    ) -> float:
        """
        Last logging latency.
        """

        return self._last_latency
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize integration into dictionary.
        """

        return {

            "identity": {

                "id":
                    self._id,

                "name":
                    self._name,

                "version":
                    self._version,

            },

            "runtime": {

                "enabled":
                    self._enabled,

                "running":
                    self._running,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

            },

            "configuration":

                copy.deepcopy(
                    self._config
                ),

            "statistics": {

                "log_count":
                    self._log_count,

                "warning_count":
                    self._warning_count,

                "debug_count":
                    self._debug_count,

                "error_count":
                    self._error_count,

                "latency":
                    self._last_latency,

            },

            "handlers":

                list(
                    self._registry.keys()
                ),

            "loggers":

                list(
                    self._logger_registry.keys()
                ),

            "metadata":

                copy.deepcopy(
                    self._metadata
                ),

            "created_at":

                self._created_at.isoformat(),

            "updated_at":

                self._updated_at.isoformat(),

        }



    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):
        """
        Restore MetricLoggingIntegration
        from dictionary.
        """

        obj = cls(

            name=data.get(
                "identity",
                {},
            ).get(
                "name",
                "MetricLoggingIntegration",
            ),

            config=copy.deepcopy(

                data.get(
                    "configuration",
                    {},
                )

            ),

        )


        runtime = data.get(
            "runtime",
            {},
        )

        obj._enabled = runtime.get(
            "enabled",
            True,
        )

        obj._running = runtime.get(
            "running",
            False,
        )

        obj._frozen = runtime.get(
            "frozen",
            False,
        )

        obj._closed = runtime.get(
            "closed",
            False,
        )


        stats = data.get(
            "statistics",
            {},
        )

        obj._log_count = stats.get(
            "log_count",
            0,
        )

        obj._warning_count = stats.get(
            "warning_count",
            0,
        )

        obj._debug_count = stats.get(
            "debug_count",
            0,
        )

        obj._error_count = stats.get(
            "error_count",
            0,
        )

        obj._last_latency = stats.get(
            "latency",
            0.0,
        )


        obj._metadata = copy.deepcopy(

            data.get(
                "metadata",
                {},
            )

        )

        return obj



    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize into JSON.
        """

        import json

        return json.dumps(

            self.to_dict(),

            indent=indent,

            default=str,

        )



    @classmethod
    def from_json(
        cls,
        payload: str,
    ):
        """
        Restore object from JSON.
        """

        import json

        return cls.from_dict(

            json.loads(
                payload
            )

        )



    def serialize(
        self,
    ):
        """
        Generic serialization API.

        Alias for to_dict().
        """

        return self.to_dict()



    @classmethod
    def deserialize(
        cls,
        payload,
    ):
        """
        Generic deserialization API.
        """

        if isinstance(
            payload,
            dict,
        ):

            return cls.from_dict(
                payload
            )

        if isinstance(
            payload,
            str,
        ):

            return cls.from_json(
                payload
            )

        raise TypeError(
            "Unsupported serialization payload."
        )
    # ======================================================
    # Part 9. Events & Hooks
    # ======================================================

    def before_log(
        self,
        level: str,
        message: str,
        **context,
    ):
        """
        Called before a log record
        is processed.
        """

        self.emit(

            "before_log",

            level=level,

            message=message,

            context=context,

        )

        return self



    def after_log(
        self,
        record: dict,
    ):
        """
        Called after a log record
        has been processed.
        """

        self.emit(

            "after_log",

            record=record,

        )

        return self



    def before_handler(
        self,
        handler_name: str,
        record: dict,
    ):
        """
        Called before a handler
        executes.
        """

        self.emit(

            "before_handler",

            handler=handler_name,

            record=record,

        )

        return self



    def after_handler(
        self,
        handler_name: str,
        record: dict,
        result=None,
    ):
        """
        Called after handler execution.
        """

        self.emit(

            "after_handler",

            handler=handler_name,

            record=record,

            result=result,

        )

        return self



    def add_hook(
        self,
        event: str,
        callback,
    ):
        """
        Register event hook.
        """

        if not callable(callback):

            raise TypeError(

                "Hook must be callable."

            )


        with self._lock:

            self._hooks.setdefault(

                event,

                []

            ).append(

                callback

            )


        return self



    def remove_hook(
        self,
        event: str,
        callback=None,
    ):
        """
        Remove event hook.
        """

        with self._lock:

            if event not in self._hooks:

                return self


            if callback is None:

                self._hooks.pop(

                    event,

                    None,

                )

                return self


            try:

                self._hooks[event].remove(

                    callback

                )

            except ValueError:

                pass


            if not self._hooks[event]:

                self._hooks.pop(

                    event,

                    None,

                )


        return self



    def emit(
        self,
        event: str,
        **payload,
    ):
        """
        Emit runtime event.
        """

        record = {

            "event":

                event,

            "payload":

                payload,

            "timestamp":

                datetime.utcnow(),

        }


        self._events.append(

            record

        )


        callbacks = self._hooks.get(

            event,

            [],

        )


        for callback in callbacks:

            callback(

                self,

                **payload,

            )


        return record



    def subscribe(
        self,
        event: str,
        callback,
    ):
        """
        Alias of add_hook().
        """

        return self.add_hook(

            event,

            callback,

        )
    # ======================================================
    # Part 10. Python Protocols
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"name={self._name!r}, "

            f"handlers={len(self._registry)}, "

            f"loggers={len(self._logger_registry)}, "

            f"logs={self._log_count}, "

            f"errors={self._error_count}, "

            f"status={self.status()}"

            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (

            f"{self._name} "

            f"[status={self.status()}, "

            f"handlers={len(self._registry)}, "

            f"loggers={len(self._logger_registry)}, "

            f"logs={self._log_count}]"

        )



    def __len__(
        self,
    ) -> int:
        """
        Number of collected log records.
        """

        return len(

            self._logs

        )



    def __iter__(
        self,
    ):
        """
        Iterate over collected log records.
        """

        return iter(

            self._logs

        )



    def __contains__(
        self,
        level: str,
    ) -> bool:
        """
        Check whether at least one log
        exists with the given level.
        """

        level = level.upper()

        return any(

            record.get(
                "level"
            ) == level

            for record

            in self._logs

        )



    def __call__(
        self,
        level: str,
        message: str,
        **context,
    ):
        """
        Callable logging interface.

        Equivalent to log().
        """

        return self.log(

            level,

            message,

            **context,

        )



    def __copy__(
        self,
    ):
        """
        Shallow copy protocol.
        """

        return self.clone()



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