"""
SciOS-NG Metrics Runtime Integration

scios/runtime/observability/metrics/integration/runtime.py
"""

from __future__ import annotations

import uuid
import time
import copy

from datetime import datetime
from threading import RLock
from typing import Any, Dict, Optional



class MetricRuntimeIntegration:
    """
    Runtime adapter between SciOS Runtime
    and Metrics Observability subsystem.
    """

    # ======================================================
    # Part 1. Foundation
    # ======================================================


    def __init__(
        self,
        name: str = "MetricRuntimeIntegration",
        runtime=None,
        config: Optional[dict] = None,
    ):
        """
        Initialize runtime integration adapter.
        """

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
        # Runtime Reference
        # --------------------------------------------------

        self._runtime = runtime



        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._running = False

        self._frozen = False

        self._closed = False



        # --------------------------------------------------
        # Adapter Configuration
        # --------------------------------------------------

        self._config = config or {

            "auto_collect": True,

            "collect_runtime_state": True,

            "collect_events": True,

            "collect_latency": True,

        }



        # --------------------------------------------------
        # Integration Registry
        # --------------------------------------------------

        self._registry = {}



        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at



        self._metadata = {

            "component":
                "metrics.integration.runtime",

            "engine":
                "SciOS-NG",

            "version":
                self._version,

        }



        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self._collect_count = 0

        self._error_count = 0

        self._last_latency = 0.0

        self._start_time = time.time()



    # ======================================================
    # Identity
    # ======================================================


    @property
    def id(
        self
    ):
        return self._id



    @property
    def name(
        self
    ):
        return self._name



    @property
    def version(
        self
    ):
        return self._version



    # ======================================================
    # Runtime State
    # ======================================================


    @property
    def enabled(
        self
    ):
        return self._enabled



    @property
    def running(
        self
    ):
        return self._running



    @property
    def frozen(
        self
    ):
        return self._frozen



    @property
    def closed(
        self
    ):
        return self._closed



    # ======================================================
    # Adapter Configuration
    # ======================================================


    @property
    def config(
        self
    ):
        return dict(
            self._config
        )



    def configure(
        self,
        **kwargs
    ):
        """
        Update adapter configuration.
        """

        with self._lock:

            self._config.update(
                kwargs
            )

            self._updated_at = datetime.utcnow()


        return self



    # ======================================================
    # Integration Registry
    # ======================================================


    def register(
        self,
        name: str,
        adapter: Any,
    ):
        """
        Register external runtime adapter.
        """

        with self._lock:

            self._registry[name] = adapter


        return self



    def unregister(
        self,
        name: str,
    ):
        """
        Remove adapter.
        """

        with self._lock:

            self._registry.pop(
                name,
                None
            )


        return self



    def adapter(
        self,
        name: str,
        default=None,
    ):
        """
        Get registered adapter.
        """

        return self._registry.get(
            name,
            default
        )



    def adapters(
        self
    ):
        """
        Return all adapters.
        """

        return dict(
            self._registry
        )



    # ======================================================
    # Metadata
    # ======================================================


    def metadata(
        self
    ):
        """
        Return integration metadata.
        """

        return dict(
            self._metadata
        )



    # ======================================================
    # Statistics
    # ======================================================


    @property
    def collect_count(
        self
    ):
        return self._collect_count



    @property
    def error_count(
        self
    ):
        return self._error_count



    @property
    def latency(
        self
    ):
        return self._last_latency



    @property
    def uptime(
        self
    ):
        return (
            time.time()
            -
            self._start_time
        )
    # ======================================================
    # Part 2. Runtime Integration API
    # ======================================================


    def attach(
        self,
        runtime,
    ):
        """
        Attach SciOS Runtime instance.

        Connect integration adapter
        with runtime engine.
        """

        with self._lock:

            self._runtime = runtime

            self._running = True

            self._updated_at = datetime.utcnow()


        return self



    def detach(
        self,
    ):
        """
        Detach runtime instance.
        """

        with self._lock:

            self._runtime = None

            self._running = False

            self._updated_at = datetime.utcnow()


        return self



    def collect(
        self,
        **kwargs,
    ) -> dict:
        """
        Collect complete runtime observability data.

        Combines:
        - state
        - metrics
        - events
        - health
        """

        start = time.perf_counter()


        try:

            result = {

                "runtime":

                    self.collect_state(),


                "metrics":

                    self.collect_metrics(),


                "events":

                    self.collect_events(),


                "health":

                    self.collect_health(),

            }


            self._collect_count += 1



            return result



        except Exception:

            self._error_count += 1

            raise



        finally:

            self._last_latency = (

                time.perf_counter()

                -

                start

            )



    def collect_state(
        self,
    ) -> dict:
        """
        Collect runtime state.

        Returns:
        - lifecycle
        - identity
        - status
        """

        runtime = self._runtime


        if runtime is None:

            return {

                "attached":

                    False,

            }



        state = {

            "attached":

                True,


            "id":

                getattr(

                    runtime,

                    "id",

                    None,

                ),


            "name":

                getattr(

                    runtime,

                    "name",

                    runtime.__class__.__name__,

                ),


            "running":

                getattr(

                    runtime,

                    "running",

                    False,

                ),


            "enabled":

                getattr(

                    runtime,

                    "enabled",

                    True,

                ),


            "created_at":

                getattr(

                    runtime,

                    "created_at",

                    None,

                ),

        }


        return state



    def collect_metrics(
        self,
    ) -> dict:
        """
        Collect runtime metrics.
        """

        runtime = self._runtime


        if runtime is None:

            return {}



        metrics = {}



        candidates = [

            "metrics",

            "statistics",

            "summary",

        ]



        for name in candidates:


            value = getattr(

                runtime,

                name,

                None,

            )


            if callable(value):

                try:

                    metrics[name] = value()


                except Exception:

                    metrics[name] = None



            elif value is not None:

                metrics[name] = value



        return metrics



    def collect_events(
        self,
    ) -> list:
        """
        Collect runtime events.
        """

        runtime = self._runtime


        if runtime is None:

            return []



        events = getattr(

            runtime,

            "events",

            []

        )


        if callable(events):

            events = events()



        return list(

            events

        )



    def collect_health(
        self,
    ) -> dict:
        """
        Collect runtime health status.
        """

        runtime = self._runtime


        if runtime is None:

            return {

                "healthy":

                    False,


                "reason":

                    "runtime_not_attached",

            }



        health = getattr(

            runtime,

            "health",

            None,

        )



        if callable(health):

            return health()



        return {

            "healthy":

                True,


            "state":

                "unknown",

        }



    def sync(
        self,
        **kwargs,
    ):
        """
        Synchronize runtime state into metrics system.
        """

        data = self.collect(
            **kwargs
        )


        self._last_sync = data


        self._updated_at = datetime.utcnow()


        return data
    # ======================================================
    # Part 3. Runtime Adapters
    # ======================================================


    def register_adapter(
        self,
        name: str,
        adapter,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register runtime adapter.

        Adapter can connect:
        - SciOS Runtime
        - Ray
        - Kubernetes
        - GPU Runtime
        - QTC Runtime
        """

        with self._lock:

            self._registry[name] = {

                "name":

                    name,


                "adapter":

                    adapter,


                "enabled":

                    enabled,


                "metadata":

                    metadata or {},


                "created_at":

                    datetime.utcnow(),

            }


            self._updated_at = datetime.utcnow()


        return self



    def remove_adapter(
        self,
        name: str,
    ):
        """
        Remove runtime adapter.
        """

        with self._lock:

            self._registry.pop(

                name,

                None,

            )


            self._updated_at = datetime.utcnow()


        return self



    def adapter(
        self,
        name: str,
        default=None,
    ):
        """
        Get runtime adapter instance.
        """

        entry = self._registry.get(

            name

        )


        if entry is None:

            return default



        return entry["adapter"]



    def adapters(
        self,
    ):
        """
        Return registered adapters.
        """

        return dict(

            self._registry

        )



    def execute_adapter(
        self,
        name: str,
        operation: str,
        *args,
        **kwargs,
    ):
        """
        Execute adapter operation.
        """

        entry = self._registry.get(

            name

        )


        if entry is None:

            raise KeyError(

                f"Unknown adapter: {name}"

            )



        if not entry["enabled"]:

            raise RuntimeError(

                f"Adapter '{name}' is disabled."

            )



        adapter = entry["adapter"]



        method = getattr(

            adapter,

            operation,

            None,

        )



        if method is None:

            raise AttributeError(

                f"Adapter '{name}' has no operation '{operation}'"

            )



        return method(

            *args,

            **kwargs,

        )



    def enable_adapter(
        self,
        name: str,
    ):
        """
        Enable runtime adapter.
        """

        entry = self._registry.get(

            name

        )


        if entry:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()


        return self



    def disable_adapter(
        self,
        name: str,
    ):
        """
        Disable runtime adapter.
        """

        entry = self._registry.get(

            name

        )


        if entry:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()


        return self



    def builtin_adapters(
        self,
    ):
        """
        Register SciOS-NG builtin adapters.
        """


        # ------------------------------------------
        # SciOS Runtime Adapter
        # ------------------------------------------

        self.register_adapter(

            "scios",

            self._runtime,

            metadata={

                "type":

                    "native",

                "engine":

                    "SciOS",

            },

        )



        # ------------------------------------------
        # Metrics Adapter
        # ------------------------------------------

        self.register_adapter(

            "metrics",

            self,

            metadata={

                "type":

                    "internal",

                "engine":

                    "Metrics",

            },

        )



        return self
    # ======================================================
    # Part 4. Runtime Lifecycle
    # ======================================================


    def enable(
        self,
    ):
        """
        Enable runtime integration.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()


        return self



    def disable(
        self,
    ):
        """
        Disable runtime integration.

        Stops collecting runtime data.
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
        Freeze integration state.

        Keeps configuration and registry,
        blocks runtime synchronization.
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
        Unfreeze runtime integration.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()


        return self



    def close(
        self,
    ):
        """
        Close runtime integration.

        Release runtime connection.
        """

        with self._lock:

            self._closed = True

            self._running = False


            self._runtime = None


            self._updated_at = datetime.utcnow()


        return self



    def reopen(
        self,
    ):
        """
        Reopen closed integration.

        Keeps:
        - configuration
        - adapters
        - metadata
        """

        with self._lock:

            self._closed = False

            self._enabled = True

            self._updated_at = datetime.utcnow()


        return self
    # ======================================================
    # Part 5. Runtime Operations
    # ======================================================


    def reset(
        self,
    ):
        """
        Reset runtime integration state.

        Keeps:
        - identity
        - configuration
        - adapters

        Clears:
        - counters
        - cached data
        - runtime snapshot
        """

        with self._lock:

            self._collect_count = 0

            self._error_count = 0

            self._last_latency = 0.0


            self._last_sync = None


            self._snapshot = None


            self._updated_at = datetime.utcnow()


        return self



    def clear(
        self,
    ):
        """
        Clear runtime integration cache.

        Keeps:
        - configuration
        - adapter registry
        - metadata
        """

        with self._lock:

            self._last_sync = None

            self._snapshot = None

            self._updated_at = datetime.utcnow()


        return self



    def snapshot(
        self,
    ) -> dict:
        """
        Create runtime integration snapshot.

        Used for:
        - checkpoint
        - recovery
        - distributed migration
        """

        with self._lock:

            self._snapshot = {

                "id":

                    self._id,


                "name":

                    self._name,


                "version":

                    self._version,


                "enabled":

                    self._enabled,


                "running":

                    self._running,


                "frozen":

                    self._frozen,


                "closed":

                    self._closed,


                "config":

                    copy.deepcopy(

                        self._config

                    ),


                "statistics":

                    {

                        "collect_count":

                            self._collect_count,


                        "error_count":

                            self._error_count,


                        "latency":

                            self._last_latency,

                    },


                "metadata":

                    copy.deepcopy(

                        self._metadata

                    ),


                "updated_at":

                    self._updated_at,

            }



            return copy.deepcopy(

                self._snapshot

            )



    def restore(
        self,
        snapshot: dict | None = None,
    ):
        """
        Restore runtime integration snapshot.
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

            self._enabled = snapshot.get(

                "enabled",

                True,

            )


            self._running = snapshot.get(

                "running",

                False,

            )


            self._frozen = snapshot.get(

                "frozen",

                False,

            )


            self._closed = snapshot.get(

                "closed",

                False,

            )



            self._config = copy.deepcopy(

                snapshot.get(

                    "config",

                    {},

                )

            )



            statistics = snapshot.get(

                "statistics",

                {},

            )


            self._collect_count = statistics.get(

                "collect_count",

                0,

            )


            self._error_count = statistics.get(

                "error_count",

                0,

            )


            self._last_latency = statistics.get(

                "latency",

                0.0,

            )



            self._metadata = copy.deepcopy(

                snapshot.get(

                    "metadata",

                    {},

                )

            )


            self._updated_at = datetime.utcnow()


        return self



    def clone(
        self,
    ):
        """
        Clone runtime integration.

        Creates independent adapter instance.
        """

        cloned = self.__class__(

            name=self._name,

            runtime=self._runtime,

            config=copy.deepcopy(

                self._config

            ),

        )


        cloned._registry = copy.deepcopy(

            self._registry

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
    # Part 6. Statistics & Diagnostics
    # ======================================================


    def summary(
        self,
    ) -> dict:
        """
        Return compact runtime integration summary.
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


            "adapters":

                len(

                    self._registry

                ),


            "collect_count":

                self._collect_count,


            "sync_count":

                getattr(

                    self,

                    "_sync_count",

                    0,

                ),


            "error_count":

                self._error_count,


            "uptime":

                self.uptime,


            "latency":

                self._last_latency,

        }



    def report(
        self,
    ) -> dict:
        """
        Generate detailed diagnostic report.
        """

        return {

            "component":

                "MetricRuntimeIntegration",


            "identity":

                {

                    "id":

                        self._id,


                    "name":

                        self._name,


                    "version":

                        self._version,

                },


            "state":

                {

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


            "adapters":

                list(

                    self._registry.keys()

                ),


            "statistics":

                {

                    "collect_count":

                        self._collect_count,


                    "sync_count":

                        getattr(

                            self,

                            "_sync_count",

                            0,

                        ),


                    "error_count":

                        self._error_count,


                    "uptime":

                        self.uptime,


                    "latency":

                        self._last_latency,

                },


            "metadata":

                self.metadata(),

        }



    def health(
        self,
    ) -> dict:
        """
        Evaluate integration health.
        """

        healthy = (

            self._enabled

            and

            not self._closed

            and

            self._error_count == 0

        )


        status = (

            "healthy"

            if healthy

            else

            "degraded"

        )


        return {

            "healthy":

                healthy,


            "status":

                status,


            "enabled":

                self._enabled,


            "running":

                self._running,


            "frozen":

                self._frozen,


            "closed":

                self._closed,


            "errors":

                self._error_count,

        }



    def status(
        self,
    ) -> str:
        """
        Return current lifecycle status.
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
    def collect_count(
        self,
    ):
        """
        Number of successful collections.
        """

        return self._collect_count



    @property
    def sync_count(
        self,
    ):
        """
        Number of synchronization operations.
        """

        return getattr(

            self,

            "_sync_count",

            0,

        )



    @property
    def error_count(
        self,
    ):
        """
        Number of runtime integration errors.
        """

        return self._error_count



    @property
    def uptime(
        self,
    ):
        """
        Integration uptime seconds.
        """

        return (

            time.time()

            -

            self._start_time

        )



    @property
    def latency(
        self,
    ):
        """
        Last collection latency.
        """

        return self._last_latency
    # ======================================================
    # Part 7. Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict:
        """
        Convert runtime integration
        state into dictionary.
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


            "state": {

                "enabled":

                    self._enabled,


                "running":

                    self._running,


                "frozen":

                    self._frozen,


                "closed":

                    self._closed,

            },


            "config":

                copy.deepcopy(

                    self._config

                ),


            "registry": {

                name: {

                    "enabled":

                        item.get(

                            "enabled",

                            True,

                        ),


                    "metadata":

                        item.get(

                            "metadata",

                            {},

                        ),

                }

                for name, item

                in self._registry.items()

            },


            "metadata":

                copy.deepcopy(

                    self._metadata

                ),


            "statistics": {

                "collect_count":

                    self._collect_count,


                "sync_count":

                    getattr(

                        self,

                        "_sync_count",

                        0,

                    ),


                "error_count":

                    self._error_count,


                "latency":

                    self._last_latency,

            },


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
        Restore MetricRuntimeIntegration
        from dictionary.
        """

        identity = data.get(

            "identity",

            {},

        )


        obj = cls(

            name=identity.get(

                "name",

                "MetricRuntimeIntegration",

            ),

            config=data.get(

                "config",

                {},

            ),

        )


        state = data.get(

            "state",

            {},

        )


        obj._enabled = state.get(

            "enabled",

            True,

        )


        obj._running = state.get(

            "running",

            False,

        )


        obj._frozen = state.get(

            "frozen",

            False,

        )


        obj._closed = state.get(

            "closed",

            False,

        )



        obj._metadata = copy.deepcopy(

            data.get(

                "metadata",

                {},

            )

        )



        statistics = data.get(

            "statistics",

            {},

        )


        obj._collect_count = statistics.get(

            "collect_count",

            0,

        )


        obj._sync_count = statistics.get(

            "sync_count",

            0,

        )


        obj._error_count = statistics.get(

            "error_count",

            0,

        )


        obj._last_latency = statistics.get(

            "latency",

            0.0,

        )


        return obj



    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize runtime integration
        into JSON string.
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


        data = json.loads(

            payload

        )


        return cls.from_dict(

            data

        )



    def serialize(
        self,
    ) -> dict:
        """
        Generic serialization API.

        Alias for to_dict().
        """

        return self.to_dict()



    @classmethod
    def deserialize(
        cls,
        data,
    ):
        """
        Generic deserialization API.
        """

        if isinstance(

            data,

            str,

        ):

            return cls.from_json(

                data

            )


        if isinstance(

            data,

            dict,

        ):

            return cls.from_dict(

                data

            )


        raise TypeError(

            "Unsupported serialization format"

        )
    # ======================================================
    # Part 8. Events & Hooks
    # ======================================================


    def before_collect(
        self,
        **payload,
    ):
        """
        Hook executed before metric collection.
        """

        self.emit(

            "before_collect",

            **payload,

        )

        return self



    def after_collect(
        self,
        result=None,
        **payload,
    ):
        """
        Hook executed after metric collection.
        """

        self.emit(

            "after_collect",

            result=result,

            **payload,

        )

        return self



    def before_sync(
        self,
        **payload,
    ):
        """
        Hook executed before runtime synchronization.
        """

        self.emit(

            "before_sync",

            **payload,

        )

        return self



    def after_sync(
        self,
        result=None,
        **payload,
    ):
        """
        Hook executed after runtime synchronization.
        """

        self.emit(

            "after_sync",

            result=result,

            **payload,

        )

        return self



    def add_hook(
        self,
        event: str,
        callback,
    ):
        """
        Register event callback.
        """

        if not callable(callback):

            raise TypeError(

                "Hook callback must be callable"

            )


        with self._lock:

            if not hasattr(

                self,

                "_hooks",

            ):

                self._hooks = {}



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
        Remove event callback.

        If callback is None:
        remove all hooks for event.
        """

        with self._lock:

            if not hasattr(

                self,

                "_hooks",

            ):

                return self



            if event not in self._hooks:

                return self



            if callback is None:

                self._hooks.pop(

                    event,

                    None,

                )


            else:

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
        Emit integration event.
        """


        event_record = {

            "event":

                event,


            "payload":

                payload,


            "timestamp":

                datetime.utcnow(),

        }



        if not hasattr(

            self,

            "_events",

        ):

            self._events = []



        self._events.append(

            event_record

        )



        hooks = getattr(

            self,

            "_hooks",

            {},

        ).get(

            event,

            [],

        )



        for callback in hooks:

            callback(

                self,

                **payload,

            )


        return self



    def subscribe(
        self,
        event: str,
        callback,
    ):
        """
        Subscribe to integration event.

        Alias for add_hook().
        """

        return self.add_hook(

            event,

            callback,

        )
    # ======================================================
    # Part 9. Python Protocols
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

            f"adapters={len(self._registry)}, "

            f"collects={self._collect_count}, "

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

            f"adapters={len(self._registry)}, "

            f"collections={self._collect_count}]"

        )



    def __len__(
        self,
    ) -> int:
        """
        Return number of registered adapters.
        """

        return len(

            self._registry

        )



    def __iter__(
        self,
    ):
        """
        Iterate registered adapters.
        """

        return iter(

            self._registry.items()

        )



    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check adapter existence.
        """

        return name in self._registry



    def __call__(
        self,
        **kwargs,
    ):
        """
        Callable runtime integration.

        Equivalent to collect().
        """

        return self.collect(

            **kwargs

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
                                                                        