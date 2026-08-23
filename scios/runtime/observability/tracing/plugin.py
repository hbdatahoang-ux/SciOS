# ==============================================================================
# SciOS Runtime Observability
# Trace Plugin
# ==============================================================================

from __future__ import annotations


# ==============================================================================
# Part 1. Module Header
# ==============================================================================

"""
SciOS Runtime Observability
===========================

Tracing plugin integration layer.

This module provides the plugin-level abstraction for the SciOS tracing
subsystem and is designed to integrate with TraceProvider, TraceManager,
processors, samplers, and exporters.

Python 3.11+
"""


# ==============================================================================
# Part 2. Imports
# ==============================================================================

import platform
import socket
import copy

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
)


# ------------------------------------------------------------------------------
# Tracing modules
# ------------------------------------------------------------------------------

from .context import TraceContext
from .exporter import Exporter
from .manager import TraceManager
from .processor import TraceProcessor
from .provider import TraceProvider
from .sampler import TraceSampler
from .span import Span
from .trace import Trace


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

PluginConfig: TypeAlias = Mapping[str, Any]

PluginMetadata: TypeAlias = MutableMapping[str, Any]

PluginAttributes: TypeAlias = Mapping[str, Any]

PluginFactory: TypeAlias = Callable[..., "TracePlugin"]

ProviderFactory: TypeAlias = Callable[..., TraceProvider]

ManagerFactory: TypeAlias = Callable[..., TraceManager]

ProcessorFactory: TypeAlias = Callable[..., TraceProcessor]

SamplerFactory: TypeAlias = Callable[..., TraceSampler]

ExporterFactory: TypeAlias = Callable[..., Exporter]

TraceItem: TypeAlias = Trace | Span

PluginResult: TypeAlias = Any

PluginCallback: TypeAlias = Callable[..., Any]


# ==============================================================================
# Part 4. Constants
# ==============================================================================

PLUGIN_NAME: str = "tracing"

PLUGIN_VERSION: str = "1.0.0"

PLUGIN_API_VERSION: str = "1.0"

PLUGIN_TYPE: str = "observability.tracing"

DEFAULT_PLUGIN_ENABLED: bool = True

DEFAULT_SERVICE_NAME: str = "scios"

DEFAULT_PLUGIN_PRIORITY: int = 100

DEFAULT_PLUGIN_ORDER: int = 0

EMPTY_PLUGIN_NAME: str = ""

PLUGIN_STATUS_CREATED: str = "created"
PLUGIN_STATUS_INITIALIZED: str = "initialized"
PLUGIN_STATUS_RUNNING: str = "running"
PLUGIN_STATUS_STOPPED: str = "stopped"
PLUGIN_STATUS_FAILED: str = "failed"

SUPPORTED_PLUGIN_STATUSES: Tuple[str, ...] = (
    PLUGIN_STATUS_CREATED,
    PLUGIN_STATUS_INITIALIZED,
    PLUGIN_STATUS_RUNNING,
    PLUGIN_STATUS_STOPPED,
    PLUGIN_STATUS_FAILED,
)


# ==============================================================================
# Part 5. Exceptions
# ==============================================================================

class TracePluginError(Exception):
    """Base exception for tracing plugin errors."""


class TracePluginConfigurationError(TracePluginError):
    """Raised when plugin configuration is invalid."""


class TracePluginStateError(TracePluginError):
    """Raised when an operation is invalid for the current plugin state."""


class TracePluginRegistrationError(TracePluginError):
    """Raised when plugin registration fails."""


class TracePluginInitializationError(TracePluginError):
    """Raised when plugin initialization fails."""


class TracePluginLifecycleError(TracePluginError):
    """Raised when plugin lifecycle handling fails."""


class TracePluginValidationError(TracePluginError):
    """Raised when plugin validation fails."""


# ==============================================================================
# Part 6. Enums
# ==============================================================================

class PluginState(Enum):
    """Lifecycle state of a tracing plugin."""

    CREATED = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    STOPPED = auto()
    FAILED = auto()


class PluginType(Enum):
    """Supported SciOS plugin categories."""

    OBSERVABILITY = "observability"
    TRACING = "observability.tracing"


class PluginEvent(Enum):
    """Lifecycle and tracing plugin events."""

    CREATED = "created"
    INITIALIZED = "initialized"
    STARTED = "started"
    STOPPED = "stopped"
    FAILED = "failed"
    TRACE_STARTED = "trace_started"
    TRACE_FINISHED = "trace_finished"
    SPAN_STARTED = "span_started"
    SPAN_FINISHED = "span_finished"


# ==============================================================================
# Part 7. Dataclasses
# ==============================================================================

@dataclass
class PluginConfigData:
    """
    Runtime configuration for TracePlugin.
    """

    name: str = PLUGIN_NAME
    version: str = PLUGIN_VERSION
    api_version: str = PLUGIN_API_VERSION
    service_name: str = DEFAULT_SERVICE_NAME
    enabled: bool = DEFAULT_PLUGIN_ENABLED
    priority: int = DEFAULT_PLUGIN_PRIORITY
    order: int = DEFAULT_PLUGIN_ORDER

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    attributes: Dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass
class PluginStatistics:
    """
    Runtime statistics maintained by TracePlugin.
    """

    trace_count: int = 0
    span_count: int = 0
    processed_count: int = 0
    sampled_count: int = 0
    exported_count: int = 0
    error_count: int = 0
    start_count: int = 0
    stop_count: int = 0

    def reset(self) -> None:
        """Reset all runtime counters."""

        self.trace_count = 0
        self.span_count = 0
        self.processed_count = 0
        self.sampled_count = 0
        self.exported_count = 0
        self.error_count = 0
        self.start_count = 0
        self.stop_count = 0


@dataclass
class PluginSnapshot:
    """
    Serializable runtime snapshot of TracePlugin state.
    """

    name: str
    version: str
    state: PluginState
    enabled: bool
    active: bool

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    attributes: Dict[str, Any] = field(
        default_factory=dict,
    )

    statistics: PluginStatistics = field(
        default_factory=PluginStatistics,
    )

    trace: Optional[Trace] = None
    current_span: Optional[Span] = None
    context: Optional[TraceContext] = None


@dataclass
class PluginRegistration:
    """
    Registration descriptor for a tracing plugin.
    """

    name: str
    plugin_type: PluginType = PluginType.TRACING
    version: str = PLUGIN_VERSION
    priority: int = DEFAULT_PLUGIN_PRIORITY
    enabled: bool = DEFAULT_PLUGIN_ENABLED

    factory: Optional[PluginFactory] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )


# ==========================================================================
# Part 8. TracePlugin
# ==========================================================================


class TracePlugin:
    """
    SciOS tracing plugin integration layer.

    Coordinates provider, manager, processor, sampler,
    exporter, context, lifecycle and runtime state.
    """

    def __init__(
        self,
        config: Optional[PluginConfig] = None,
        *,
        name: str = PLUGIN_NAME,
        service_name: str = DEFAULT_SERVICE_NAME,
        enabled: bool = DEFAULT_PLUGIN_ENABLED,
        priority: int = DEFAULT_PLUGIN_PRIORITY,
        order: int = DEFAULT_PLUGIN_ORDER,
        metadata: Optional[Mapping[str, Any]] = None,
        attributes: Optional[Mapping[str, Any]] = None,
        manager: Optional[TraceManager] = None,
        processors: Optional[Iterable[TraceProcessor]] = None,
        exporters: Optional[Iterable[Exporter]] = None,
    ) -> None:

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        normalized = self._normalize_config(
            config,
            name=name,
            service_name=service_name,
            enabled=enabled,
            priority=priority,
            order=order,
            metadata=metadata,
            attributes=attributes,
        )

        self._config = normalized

        self._name = normalized.name
        self._service_name = normalized.service_name
        self._enabled = bool(normalized.enabled)
        self._priority = int(normalized.priority)
        self._order = int(normalized.order)

        self._metadata: Dict[str, Any] = dict(
            normalized.metadata or {}
        )

        self._attributes: Dict[str, Any] = dict(
            normalized.attributes or {}
        )

        # ------------------------------------------------------------------
        # Lifecycle
        # ------------------------------------------------------------------

        self._state = PluginState.CREATED
        self._initialized = False
        self._started = False
        self._stopped = False
        self._failed = False
        self._last_error: Optional[BaseException] = None

        # ------------------------------------------------------------------
        # Current tracing state
        # ------------------------------------------------------------------

        self._trace: Optional[Trace] = None
        self._current_span: Optional[Span] = None
        self._context: Optional[TraceContext] = None

        self._context_explicit = False

        self._span_stack: list[Span] = []

        # ------------------------------------------------------------------
        # Runtime component factories
        # ------------------------------------------------------------------

        self._provider_factory: Optional[
            Callable[..., Any]
        ] = None

        # ------------------------------------------------------------------
        # Runtime components
        # ------------------------------------------------------------------

        self._manager: Optional[TraceManager] = manager
        self._provider: Optional[TraceProvider] = None

        self._processor: Optional[TraceProcessor] = None
        self._sampler: Optional[TraceSampler] = None
        self._exporter: Optional[Exporter] = None

        # ------------------------------------------------------------------
        # Registered processors / exporters
        #
        # IMPORTANT:
        # Keep the complete collections as the authoritative plugin state.
        # `_processor` and `_exporter` are only compatibility aliases for
        # the first registered component.
        # ------------------------------------------------------------------

        self._processors: list[TraceProcessor] = list(
            processors or ()
        )

        self._exporters: list[Exporter] = list(
            exporters or ()
        )

        # ------------------------------------------------------------------
        # Callbacks
        # ------------------------------------------------------------------

        self._callbacks: Dict[
            str,
            list[PluginCallback],
        ] = {}

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        self._statistics = PluginStatistics()

        # ------------------------------------------------------------------
        # Registration
        # ------------------------------------------------------------------

        self._registration: Optional[PluginRegistration] = None

        # ------------------------------------------------------------------
        # Resolve manager
        # ------------------------------------------------------------------

        if self._manager is None:
            try:
                self._manager = TraceManager()
            except Exception:
                self._manager = None

        # ------------------------------------------------------------------
        # Resolve provider
        # ------------------------------------------------------------------

        if self._manager is not None:
            try:
                self._provider = TraceProvider(
                    manager=self._manager,
                )
            except TypeError:
                try:
                    self._provider = TraceProvider()
                except Exception:
                    self._provider = None
            except Exception:
                self._provider = None

        # ------------------------------------------------------------------
        # Resolve processors
        # ------------------------------------------------------------------

        if self._processors:
            # First registered processor remains the singular compatibility
            # processor exposed through `.processor`.
            self._processor = self._processors[0]

        else:
            try:
                self._processor = TraceProcessor()
            except Exception:
                self._processor = None

            if self._processor is not None:
                self._processors.append(
                    self._processor,
                )

        # ------------------------------------------------------------------
        # Inject primary processor into manager
        #
        # Manager supports one primary processor while the plugin itself
        # supports an arbitrary processor collection.
        # ------------------------------------------------------------------

        if self._manager is not None:
            set_processor = getattr(
                self._manager,
                "set_processor",
                None,
            )

            if callable(set_processor):
                try:
                    set_processor(
                        self._processor,
                    )
                except Exception:
                    pass

        # ------------------------------------------------------------------
        # Resolve sampler
        # ------------------------------------------------------------------

        try:
            self._sampler = TraceSampler()
        except Exception:
            self._sampler = None

        # ------------------------------------------------------------------
        # Resolve exporters
        # ------------------------------------------------------------------

        if self._exporters:
            self._exporter = self._exporters[0]

        else:
            self._exporter = None

        # ------------------------------------------------------------------
        # Runtime metadata
        # ------------------------------------------------------------------

        self._metadata.setdefault(
            "plugin_type",
            PLUGIN_TYPE,
        )

        self._metadata.setdefault(
            "plugin_version",
            PLUGIN_VERSION,
        )

        self._metadata.setdefault(
            "service_name",
            self._service_name,
        )

        # ------------------------------------------------------------------
        # Runtime attributes
        # ------------------------------------------------------------------

        self._attributes.setdefault(
            "service.name",
            self._service_name,
        )

        # ------------------------------------------------------------------
        # Bind manager event processing
        # ------------------------------------------------------------------

        self._bind_event_processor()
    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_config(
        config: Optional[PluginConfig],
        *,
        name: str,
        service_name: str,
        enabled: bool,
        priority: int,
        order: int,
        metadata: Optional[Mapping[str, Any]],
        attributes: Optional[Mapping[str, Any]],
    ) -> PluginConfigData:

        values: Dict[str, Any] = {}

        if isinstance(config, PluginConfigData):
            values = {
                "name": config.name,
                "version": config.version,
                "api_version": config.api_version,
                "service_name": config.service_name,
                "enabled": config.enabled,
                "priority": config.priority,
                "order": config.order,
                "metadata": dict(config.metadata),
                "attributes": dict(config.attributes),
            }

        elif config is not None:
            values.update(dict(config))

        resolved_metadata = dict(
            values.pop("metadata", {}) or {},
        )

        if metadata is not None:
            resolved_metadata.update(dict(metadata))

        resolved_attributes = dict(
            values.pop("attributes", {}) or {},
        )

        if attributes is not None:
            resolved_attributes.update(dict(attributes))

        return PluginConfigData(
            name=str(values.pop("name", name)),
            version=str(
                values.pop(
                    "version",
                    PLUGIN_VERSION,
                ),
            ),
            api_version=str(
                values.pop(
                    "api_version",
                    PLUGIN_API_VERSION,
                ),
            ),
            service_name=str(
                values.pop(
                    "service_name",
                    service_name,
                ),
            ),
            enabled=bool(
                values.pop(
                    "enabled",
                    enabled,
                ),
            ),
            priority=int(
                values.pop(
                    "priority",
                    priority,
                ),
            ),
            order=int(
                values.pop(
                    "order",
                    order,
                ),
            ),
            metadata=resolved_metadata,
            attributes=resolved_attributes,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._config.version

    @property
    def api_version(self) -> str:
        return self._config.api_version

    @property
    def service_name(self) -> str:
        return self._service_name

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = bool(value)

    @property
    def state(self) -> PluginState:
        return self._state

    @property
    def active(self) -> bool:
        return self._state == PluginState.RUNNING

    @property
    def ready(self) -> bool:
        return self._state in (
            PluginState.INITIALIZED,
            PluginState.RUNNING,
        )

    @property
    def provider(self) -> Optional[TraceProvider]:
        return self._provider

    @property
    def manager(self) -> Optional[TraceManager]:
        return self._manager

    @property
    def processor(self) -> Optional[TraceProcessor]:
        return self._processor

    @property
    def sampler(self) -> Optional[TraceSampler]:
        return self._sampler

    @property
    def exporter(self) -> Optional[Exporter]:
        return self._exporter

    @property
    def trace(self) -> Optional[Trace]:
        return self._trace

    @property
    def current_trace(self) -> Optional[Trace]:
        return self._trace

    @property
    def current_span(self) -> Optional[Span]:
        return self._current_span

    @property
    def current_context(self) -> Optional[TraceContext]:
        return self._context

    @property
    def context(self) -> Optional[TraceContext]:
        return self._context

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def attributes(self) -> Dict[str, Any]:
        return dict(self._attributes)

    @property
    def statistics(self) -> PluginStatistics:
        return self._statistics

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def order(self) -> int:
        return self._order

    @property
    def config(self) -> PluginConfigData:
        return self._config

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.TRACING

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _invoke(
        target: Any,
        method_names: Sequence[str],
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        if target is None:
            return None

        for method_name in method_names:
            method = getattr(
                target,
                method_name,
                None,
            )

            if not callable(method):
                continue

            # First attempt: exact invocation.
            try:
                return method(
                    *args,
                    **kwargs,
                )
            except TypeError:
                pass

            # Second attempt: keyword-free invocation only when arguments
            # were actually supplied.
            if args or kwargs:
                try:
                    return method()
                except TypeError:
                    continue

        return None

    def _notify_processors(
        self,
        method_name: str,
        item: TraceItem,
        **kwargs: Any,
    ) -> None:
        """
        Notify all registered trace processors.

        Processor callbacks are best-effort. A failure in one processor
        must not break the tracing lifecycle.
        """

        for processor in tuple(self._processors):
            callback = getattr(
                processor,
                method_name,
                None,
            )

            if not callable(callback):
                continue

            try:
                callback(
                    item,
                    **kwargs,
                )
            except (
                AttributeError,
                RuntimeError,
                TypeError,
                ValueError,
            ):
                continue

    def _emit(
        self,
        event: PluginEvent,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        callbacks = self._callbacks.get(
            event.value,
            (),
        )

        for callback in tuple(callbacks):
            try:
                callback(*args, **kwargs)
            except Exception:
                self._statistics.error_count += 1

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> "TracePlugin":

        if self._state == PluginState.FAILED:
            raise TracePluginLifecycleError(
                "Cannot initialize a failed TracePlugin.",
            )

        if self._state in (
            PluginState.INITIALIZED,
            PluginState.RUNNING,
        ):
            return self

        self._state = PluginState.INITIALIZED

        self._emit(
            PluginEvent.INITIALIZED,
            self,
        )

        return self

    def start(self) -> "TracePlugin":

        if not self._enabled:
            return self

        if self._state == PluginState.RUNNING:
            return self

        if self._state == PluginState.CREATED:
            self.initialize()

        self._state = PluginState.RUNNING
        self._statistics.start_count += 1

        self._invoke(
            self._provider,
            (
                "start",
                "initialize",
            ),
        )

        self._emit(
            PluginEvent.STARTED,
            self,
        )

        return self

    def stop(self) -> "TracePlugin":

        if self._state == PluginState.STOPPED:
            return self

        if self._state == PluginState.RUNNING:
            self._invoke(
                self._provider,
                (
                    "stop",
                    "shutdown",
                ),
            )

        self._state = PluginState.STOPPED
        self._statistics.stop_count += 1

        self._emit(
            PluginEvent.STOPPED,
            self,
        )

        return self

    def flush(self) -> "TracePlugin":
        """Flush all configured exporters."""

        if not self._enabled:
            return self

        for exporter in list(self._exporters):
            if exporter is None:
                continue

            callback = getattr(exporter, "flush", None)

            if callable(callback):
                try:
                    callback()
                except Exception:
                    continue

        return self


    def shutdown(self) -> "TracePlugin":
        """
        Permanently shut down the tracing plugin.

        Shutdown is a terminal lifecycle operation:

        1. Finish any active runtime trace.
        2. Flush exporters.
        3. Shutdown processors.
        4. Shutdown exporters.
        5. Reset manager state.
        6. Stop the provider.
        7. Clear plugin-local runtime state.

        Individual processor/exporter failures are isolated so that one
        failing component cannot prevent the remaining components from
        being cleaned up.
        """
        if self._state == PluginState.STOPPED:
            return self

        manager = self._manager

        # ------------------------------------------------------------------
        # 1. Finish active runtime trace
        # ------------------------------------------------------------------

        if self._trace is not None:
            try:
                self.after_runtime(
                    success=False,
                )
            except Exception:
                # Shutdown must remain best-effort.
                self._trace = None
                self._span = None
                self._context = None

        # ------------------------------------------------------------------
        # 2. Flush exporters before shutdown
        # ------------------------------------------------------------------

        for exporter in list(self._exporters):
            if exporter is None:
                continue

            callback = getattr(
                exporter,
                "flush",
                None,
            )

            if callable(callback):
                try:
                    callback()
                except Exception:
                    # Isolation: one exporter must not prevent the
                    # remaining exporters from being flushed.
                    continue

        # ------------------------------------------------------------------
        # 3. Shutdown processors
        # ------------------------------------------------------------------

        for processor in list(self._processors):
            if processor is None:
                continue

            callback = getattr(
                processor,
                "shutdown",
                None,
            )

            if callable(callback):
                try:
                    callback()
                except Exception:
                    # Isolation: one processor must not prevent
                    # remaining processors/exporters from shutting down.
                    continue

        # ------------------------------------------------------------------
        # 4. Shutdown exporters
        # ------------------------------------------------------------------

        for exporter in list(self._exporters):
            if exporter is None:
                continue

            callback = getattr(
                exporter,
                "shutdown",
                None,
            )

            if callable(callback):
                try:
                    callback()
                except Exception:
                    # Isolation: one exporter must not prevent
                    # remaining exporters from shutting down.
                    continue

        # ------------------------------------------------------------------
        # 5. Reset manager state
        # ------------------------------------------------------------------

        if manager is not None:
            reset = getattr(
                manager,
                "reset",
                None,
            )

            if callable(reset):
                try:
                    reset()
                except Exception:
                    # Plugin shutdown remains best-effort even when a
                    # manager implementation does not fully support reset.
                    pass

        # ------------------------------------------------------------------
        # 6. Stop provider
        # ------------------------------------------------------------------

        try:
            self._invoke(
                self._provider,
                (
                    "stop",
                    "shutdown",
                ),
            )
        except Exception:
            # Provider failure must not leave the plugin in RUNNING state.
            pass

        # ------------------------------------------------------------------
        # 7. Terminal plugin state
        # ------------------------------------------------------------------

        self._state = PluginState.STOPPED

        self._trace = None
        self._span = None
        self._context = None

        return self



    # ------------------------------------------------------------------
    # Components
    # ------------------------------------------------------------------

    def set_provider_factory(
        self,
        factory: Optional[Callable[..., Any]],
    ) -> "TracePlugin":

        self._provider_factory = factory
        return self

    def create_provider(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        if self._provider_factory is None:
            return self._provider

        self._provider = self._provider_factory(
            *args,
            **kwargs,
        )

        return self._provider

    def set_provider(
        self,
        provider: Optional[Any],
    ) -> "TracePlugin":

        self._provider = provider

        if provider is not None:
            manager = getattr(
                provider,
                "manager",
                None,
            )

            if manager is not None:
                self._manager = manager

        return self

    def _bind_event_processor(self) -> None:
        manager = self._manager
        processor = self._processor

        if manager is None or processor is None:
            return

        register = getattr(
            manager,
            "add_event_callback",
            None,
        )

        if not callable(register):
            return

        def on_event(event: Any) -> None:
            span = getattr(
                manager,
                "current_span",
                None,
            )

            self._invoke(
                processor,
                (
                    "on_event",
                ),
                span,
                event,
            )

        register(on_event)

    def set_manager(
        self,
        manager: Optional[TraceManager],
    ) -> "TracePlugin":

        self._manager = manager
        self._bind_event_processor()

        return self

    def set_processor(
        self,
        processor: Optional[TraceProcessor],
    ) -> "TracePlugin":

        self._processor = processor
        self._bind_event_processor()

        return self

    def set_sampler(
        self,
        sampler: Optional[TraceSampler],
    ) -> "TracePlugin":

        self._sampler = sampler
        return self

    def set_exporter(
        self,
        exporter: Optional[Exporter],
    ) -> "TracePlugin":

        self._exporter = exporter
        return self

    # ------------------------------------------------------------------
    # Trace operations
    # ------------------------------------------------------------------

    def start_trace(
        self,
        name: str = "trace",
        *args: Any,
        **kwargs: Any,
    ) -> Optional[Trace]:

        if not self._enabled:
            return None

        result = self._invoke(
            self._provider,
            (
                "start_trace",
                "create_trace",
                "trace",
            ),
            name,
            *args,
            **kwargs,
        )

        if result is None:
            result = self._invoke(
                self._manager,
                (
                    "start_trace",
                    "create_trace",
                    "trace",
                ),
                name,
                *args,
                **kwargs,
            )

        # --------------------------------------------------------------
        # Final local fallback
        # --------------------------------------------------------------

        if result is None:
            try:
                result = Trace(
                    name=name,
                    *args,
                    **kwargs,
                )
            except TypeError:
                try:
                    result = Trace(
                        name=name,
                    )
                except TypeError:
                    result = Trace(name)

        # --------------------------------------------------------------
        # Synchronize plugin state
        # --------------------------------------------------------------

        self._trace = result
        self._current_span = None

        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------

        self._statistics.trace_count += 1

        # --------------------------------------------------------------
        # Lifecycle event
        # --------------------------------------------------------------

        self._emit(
            PluginEvent.TRACE_STARTED,
            result,
        )

        return result



    def finish_trace(
        self,
        trace: Optional[Trace] = None,
    ) -> Any:

        target = trace or self._trace

        if target is None:
            return self

        result = self._invoke(
            self._provider,
            (
                "finish_trace",
                "end_trace",
            ),
            target,
        )

        if result is None:
            result = self._invoke(
                self._manager,
                (
                    "finish_trace",
                    "end_trace",
                ),
                target,
            )

        self._emit(
            PluginEvent.TRACE_FINISHED,
            target,
        )

        if target is self._trace:
            self._trace = None
            self._current_span = None

        return target if result is None else result

    def cancel_trace(
        self,
        trace: Optional[Trace] = None,
    ) -> "TracePlugin":

        target = trace or self._trace

        if target is None:
            return self

        try:
            # Let the manager/provider own the lifecycle transition.
            # Do NOT call target.cancel() before manager.cancel_trace(),
            # because the manager may cancel the same trace again.
            self._invoke(
                self._provider,
                (
                    "cancel_trace",
                    "abort_trace",
                ),
            )

            self._invoke(
                self._manager,
                (
                    "cancel_trace",
                    "abort_trace",
                ),
            )

        except Exception:
            # Fallback for explicit traces or managers that do not own
            # the supplied trace.
            try:
                if not getattr(target, "cancelled", False):
                    target.cancel()
            except Exception:
                self._statistics.error_count += 1

        finally:
            if target is self._trace:
                self._trace = None
                self._current_span = None
                self._context = None
                self._span_stack.clear()

            self._emit(
                PluginEvent.STOPPED,
                target,
            )

        return self

    # ------------------------------------------------------------------
    # Span operations
    # ------------------------------------------------------------------

    def start_span(
        self,
        name: str = "span",
        *args: Any,
        **kwargs: Any,
    ) -> Optional[Span]:

        if not self._enabled:
            return None

        parent = kwargs.pop(
            "parent",
            self._current_span,
        )

        # Provider may delegate to TraceManager, which requires its own
        # active trace. The plugin may nevertheless own a local trace.
        result = None

        try:
            result = self._invoke(
                self._provider,
                (
                    "start_span",
                    "create_span",
                ),
                name,
                parent=parent,
                *args,
                **kwargs,
            )
        except Exception:
            result = None

        if result is None:
            try:
                result = self._invoke(
                    self._manager,
                    (
                        "start_span",
                        "create_span",
                    ),
                    name,
                    parent=parent,
                    *args,
                    **kwargs,
                )
            except Exception:
                result = None

        # Plugin-local fallback.
        if result is None:
            trace = self._trace

            if trace is None:
                trace = self.start_trace("trace")

            if trace is None:
                return None

            try:
                result = Span(
                    name=name,
                    trace=trace,
                    parent=parent,
                    *args,
                    **kwargs,
                )
            except TypeError:
                try:
                    result = Span(
                        name=name,
                        trace=trace,
                        parent=parent,
                    )
                except TypeError:
                    try:
                        result = Span(
                            name=name,
                            trace=trace,
                        )
                    except TypeError:
                        try:
                            result = Span(name=name)
                        except TypeError:
                            result = Span(name)

        if result is None:
            return None

        self._current_span = result
        self._statistics.span_count += 1

        self._emit(
            PluginEvent.SPAN_STARTED,
            result,
        )

        return result

    def finish_span(
        self,
        span: Optional[Span] = None,
    ) -> Any:

        target = span or self.current_span

        if target is None:
            return self

        result = self._invoke(
            self._provider,
            (
                "finish_span",
                "end_span",
            ),
            target,
        )

        if result is None:
            result = self._invoke(
                self._manager,
                (
                    "finish_span",
                    "end_span",
                ),
                target,
            )

        self._emit(
            PluginEvent.SPAN_FINISHED,
            target,
        )

        if target is self._current_span:
            self._current_span = None

        return target if result is None else result

    def cancel_span(
        self,
        span: Optional[Span] = None,
    ) -> "TracePlugin":

        target = span or self.current_span

        if target is None:
            return self

        try:
            self._invoke(
                self._provider,
                (
                    "cancel_span",
                    "abort_span",
                ),
                target,
            )
        except Exception:
            pass

        try:
            self._invoke(
                self._manager,
                (
                    "cancel_span",
                    "abort_span",
                ),
                target,
            )
        except Exception:
            pass

        # Lightweight/FakeSpan objects may not implement cancel().
        cancel = getattr(target, "cancel", None)

        if callable(cancel):
            try:
                cancel()
            except Exception:
                pass

        if target is self._current_span:
            self._current_span = None

        return self

    def enter_span(
        self,
        name: str = "span",
        *args: Any,
        **kwargs: Any,
    ) -> Optional[Span]:

        return self.start_span(
            name,
            *args,
            **kwargs,
        )

    def exit_span(
        self,
        span: Optional[Span] = None,
    ) -> Any:
        """
        Finish the current span.

        Alias used by the tracing plugin public API and tests.
        """

        target = span or self._current_span

        if target is None:
            return self

        return self.finish_span(target)


    # ------------------------------------------------------------------
    # Part 8.5. Runtime / Task Integration
    # ------------------------------------------------------------------

    def before_runtime(
        self,
        runtime_name: str = "Runtime",
        **attributes: Any,
    ) -> Any:
        """
        Start a runtime trace and attach normalized runtime metadata.

        The TraceManager is the authoritative owner of trace lifecycle.

        Runtime/system metadata is stored directly in
        ``trace.attributes``.

        Precedence:

            system/runtime metadata
                >
            explicit runtime arguments
                >
            user metadata

        User metadata is copied so the caller's original mapping is never
        mutated.
        """

        if not self._enabled:
            return None

        manager = self._manager

        # ------------------------------------------------------------------
        # 1. Copy user input
        # ------------------------------------------------------------------

        user_attributes = dict(attributes)

        # ------------------------------------------------------------------
        # 2. Normalize trace attributes
        # ------------------------------------------------------------------

        trace_attributes: dict[str, Any] = {}

        # ------------------------------------------------------------------
        # 2.1 User metadata
        #
        # ``metadata={...}`` is flattened directly into trace.attributes.
        # ------------------------------------------------------------------

        metadata = user_attributes.pop(
            "metadata",
            None,
        )

        if metadata is not None:
            if not isinstance(
                metadata,
                Mapping,
            ):
                raise TypeError(
                    "metadata must be a mapping"
                )

            trace_attributes.update(
                dict(metadata)
            )

        # ------------------------------------------------------------------
        # 2.2 Preserve ordinary custom attributes
        #
        # Example:
        #
        #     before_runtime(
        #         "Runtime",
        #         dataset="ImageNet",
        #     )
        #
        # becomes:
        #
        #     trace.attributes["dataset"] == "ImageNet"
        # ------------------------------------------------------------------

        trace_attributes.update(
            user_attributes
        )

        # ------------------------------------------------------------------
        # 3. Normalize runtime/system metadata
        # ------------------------------------------------------------------

        hostname = socket.gethostname()
        platform_name = platform.system()

        # System metadata always has highest precedence.
        trace_attributes["system.hostname"] = hostname
        trace_attributes["system.platform"] = platform_name
        trace_attributes["system.python"] = platform.python_version()

        # Runtime identity always has highest precedence.
        trace_attributes["runtime.name"] = runtime_name

        # ------------------------------------------------------------------
        # 3.1 Explicit runtime version
        # ------------------------------------------------------------------

        runtime_version = attributes.get(
            "runtime_version"
        )

        if runtime_version is not None:
            trace_attributes["runtime.version"] = runtime_version

        # ------------------------------------------------------------------
        # 3.2 Explicit runtime id
        # ------------------------------------------------------------------

        runtime_id = attributes.get(
            "runtime_id"
        )

        if runtime_id is not None:
            trace_attributes["runtime.id"] = runtime_id

        # ------------------------------------------------------------------
        # 4. Remove transport-only keys
        #
        # These are API arguments, not desired trace attribute names.
        # ------------------------------------------------------------------

        trace_attributes.pop(
            "runtime_version",
            None,
        )

        trace_attributes.pop(
            "runtime_id",
            None,
        )

        trace_attributes.pop(
            "metadata",
            None,
        )

        # ------------------------------------------------------------------
        # 5. Manager is authoritative
        # ------------------------------------------------------------------

        trace = None

        if manager is not None:
            trace = self._invoke(
                manager,
                (
                    "start_trace",
                    "create_trace",
                    "trace",
                ),
                runtime_name,
                attributes=trace_attributes,
            )

        # ------------------------------------------------------------------
        # 6. Provider fallback
        # ------------------------------------------------------------------

        if trace is None:
            trace = self._invoke(
                self._provider,
                (
                    "start_trace",
                    "create_trace",
                    "trace",
                ),
                runtime_name,
                attributes=trace_attributes,
            )

        # ------------------------------------------------------------------
        # 7. Final local fallback
        # ------------------------------------------------------------------

        if trace is None:
            try:
                trace = Trace(
                    name=runtime_name,
                    attributes=dict(trace_attributes),
                )
            except TypeError:
                trace = Trace(
                    name=runtime_name,
                )

        if trace is None:
            return None

        # ------------------------------------------------------------------
        # 8. Synchronize plugin mirror state
        # ------------------------------------------------------------------

        self._trace = trace

        if manager is not None:
            self._current_span = getattr(
                manager,
                "current_span",
                None,
            )

            manager_context = getattr(
                manager,
                "current_context",
                None,
            )

            if manager_context is not None:
                self._context = manager_context

        # ------------------------------------------------------------------
        # 9. Defensive synchronization
        #
        # The manager/provider should already have attached the attributes.
        # This second synchronization guarantees the plugin contract even
        # when a lightweight provider or fake manager returns a Trace whose
        # attributes were not populated.
        # ------------------------------------------------------------------

        trace_attributes_obj = getattr(
            trace,
            "attributes",
            None,
        )

        if isinstance(
            trace_attributes_obj,
            MutableMapping,
        ):
            trace_attributes_obj.update(
                trace_attributes
            )

        elif trace_attributes_obj is None:
            try:
                trace.attributes = dict(
                    trace_attributes
                )
            except (
                AttributeError,
                TypeError,
            ):
                pass

        # ------------------------------------------------------------------
        # 10. Processor lifecycle
        # ------------------------------------------------------------------

        self._notify_processors(
            "on_trace_start",
            trace,
        )

        # ------------------------------------------------------------------
        # 11. Plugin lifecycle event
        # ------------------------------------------------------------------

        self._emit(
            PluginEvent.TRACE_STARTED,
            trace,
        )

        return trace


    def after_runtime(
        self,
        *,
        success: bool = True,
        error: Optional[BaseException] = None,
    ) -> Any:
        """
        Finish the active runtime trace.

        Lifecycle contract
        ------------------
        1. Resolve the active trace.
        2. Finalize it exactly once with the requested outcome.
        3. Notify processors in registration order.
        4. Export the finished trace in exporter registration order.
        5. Clear runtime lifecycle state.

        When ``success=False``, the failure state must be preserved by the
        trace manager and must not be overwritten by a default-success finish.
        """

        if not self._enabled:
            return None

        manager = self._manager

        # ------------------------------------------------------------------
        # 1. Resolve active trace
        # ------------------------------------------------------------------

        trace = None

        if manager is not None:
            trace = getattr(
                manager,
                "current_trace",
                None,
            )

        if trace is None:
            trace = self._trace

        if trace is None:
            return None

        # ------------------------------------------------------------------
        # 2. Finalize trace
        # ------------------------------------------------------------------

        finished_trace = trace

        if manager is not None:
            finish_kwargs = {
                "success": success,
                "error": error,
            }

            # Preserve the requested runtime outcome explicitly.
            #
            # ``FakeTraceManager.finish_trace()`` accepts ``status`` while
            # the plugin lifecycle API exposes ``success``. Passing the
            # resolved status prevents its default SUCCESS value from
            # overwriting a failed runtime.
            if not success:
                finish_kwargs["status"] = "error"

            result = self._invoke(
                manager,
                (
                    "finish_trace",
                    "end_trace",
                ),
                trace,
                **finish_kwargs,
            )

            if result is not None:
                finished_trace = result

        # ------------------------------------------------------------------
        # 3. Notify processors
        # ------------------------------------------------------------------

        processors = list(self._processors)

        if (
            self._processor is not None
            and self._processor not in processors
        ):
            processors.insert(
                0,
                self._processor,
            )

        for processor in processors:
            if processor is None:
                continue

            callback = getattr(
                processor,
                "on_trace_finish",
                None,
            )

            if callable(callback):
                callback(
                    finished_trace,
                    success=success,
                )

        # ------------------------------------------------------------------
        # 4. Export finished trace
        # ------------------------------------------------------------------

        for exporter in list(self._exporters):
            if exporter is None:
                continue

            callback = getattr(
                exporter,
                "export_trace",
                None,
            )

            if callable(callback):
                callback(finished_trace)
                continue

            # Generic compatibility fallback.
            callback = getattr(
                exporter,
                "export",
                None,
            )

            if callable(callback):
                callback(finished_trace)

        # ------------------------------------------------------------------
        # 5. Clear lifecycle state
        # ------------------------------------------------------------------

        self._trace = None
        self._span = None
        self._context = None

        return finished_trace



    def before_task(
        self,
        task_name: str = "task",
        *,
        component: Optional[str] = None,
        task_id: Optional[str] = None,
        **attributes: Any,
    ) -> Any:
        """
        Start a task span.

        Manager owns span construction. Task metadata is attached after
        construction for compatibility with lightweight manager fakes.
        """

        if not self._enabled:
            return None

        manager = self._manager

        task_attributes: Dict[str, Any] = dict(
            attributes,
        )

        if component is not None:
            task_attributes["component"] = component

        if task_id is not None:
            task_attributes["task_id"] = task_id

        parent = getattr(
            manager,
            "current_span",
            None,
        )

        # --------------------------------------------------------------
        # No manager
        # --------------------------------------------------------------

        if manager is None:
            span = self.start_span(
                task_name,
                parent=parent,
            )

            if span is not None:
                self._apply_span_attributes(
                    span,
                    task_attributes,
                )

            return span

        # --------------------------------------------------------------
        # Manager construction
        # --------------------------------------------------------------

        span = self._invoke(
            manager,
            (
                "start_span",
                "create_span",
                "enter_span",
            ),
            task_name,
            parent=parent,
        )

        # --------------------------------------------------------------
        # Minimal manager compatibility
        # --------------------------------------------------------------

        if span is None:
            span = self._invoke(
                manager,
                (
                    "start_span",
                    "create_span",
                    "enter_span",
                ),
                task_name,
            )

        if span is None:
            return None

        # --------------------------------------------------------------
        # Attach metadata after construction
        # --------------------------------------------------------------

        self._apply_span_attributes(
            span,
            task_attributes,
        )

        self._current_span = getattr(
            manager,
            "current_span",
            span,
        )

        # --------------------------------------------------------------
        # Notify all processors
        # --------------------------------------------------------------

        self._notify_processors(
            "before_task",
            span,
        )

        return span

    def before_stage(
        self,
        stage_name: str = "stage",
        **attributes: Any,
    ) -> Any:
        """
        Start a stage span.

        Stage lifecycle delegates to task lifecycle.
        """

        return self.before_task(
            task_name=stage_name,
            **attributes,
        )

    def after_task(
        self,
        *,
        success: Optional[bool] = None,
        error: Optional[BaseException] = None,
        exception: Optional[BaseException] = None,
        **attributes: Any,
    ) -> Any:
        """
        Finish the current task span.

        Processor callbacks run before finalization.
        Exporters run after span completion.
        """

        manager = self._manager

        # --------------------------------------------------------------
        # Resolve current span
        # --------------------------------------------------------------

        span = None

        if manager is not None:
            span = getattr(
                manager,
                "current_span",
                None,
            )

        if span is None:
            span = self._current_span

        if span is None:
            return self

        # --------------------------------------------------------------
        # Attach completion metadata
        # --------------------------------------------------------------

        self._finish_task_metadata(
            span,
            success=success,
            error=error,
            exception=exception,
            attributes=attributes,
        )

        # --------------------------------------------------------------
        # Processor notification
        # --------------------------------------------------------------

        self._notify_processors(
            "after_task",
            span,
            success=(
                success
                if success is not None
                else True
            ),
            error=error or exception,
        )

        # --------------------------------------------------------------
        # No manager
        # --------------------------------------------------------------

        if manager is None:
            result = self.finish_span(
                span,
            )

            self._current_span = None

            return result

        # --------------------------------------------------------------
        # Manager finalization
        # --------------------------------------------------------------

        result = self._invoke(
            manager,
            (
                "finish_span",
                "exit_span",
                "end_span",
            ),
            span,
        )

        # --------------------------------------------------------------
        # Export completed span
        # --------------------------------------------------------------

        exporter = self._exporter

        if exporter is not None:
            self._invoke(
                exporter,
                (
                    "export_span",
                    "export",
                    "send",
                    "write",
                ),
                span,
            )

            self._statistics.exported_count += 1

        # --------------------------------------------------------------
        # Synchronize current span
        # --------------------------------------------------------------

        self._current_span = getattr(
            manager,
            "current_span",
            None,
        )

        return span if result is None else result

    def after_stage(
        self,
        *,
        success: Optional[bool] = None,
        error: Optional[BaseException] = None,
        exception: Optional[BaseException] = None,
        **attributes: Any,
    ) -> Any:
        """
        Finish the current stage span.

        Delegates to task lifecycle.
        """

        return self.after_task(
            success=success,
            error=error,
            exception=exception,
            **attributes,
        )

    @staticmethod
    def _apply_span_attributes(
        span: Any,
        attributes: Mapping[str, Any],
    ) -> None:
        """
        Attach compatible attributes to a span.
        """

        if span is None or not attributes:
            return

        span_attributes = getattr(
            span,
            "attributes",
            None,
        )

        if isinstance(
            span_attributes,
            dict,
        ):
            span_attributes.update(
                attributes,
            )

        setter = getattr(
            span,
            "set_attribute",
            None,
        )

        if callable(setter):
            for key, value in attributes.items():
                try:
                    setter(
                        key,
                        value,
                    )
                except Exception:
                    pass

        for key, value in attributes.items():
            try:
                setattr(
                    span,
                    key,
                    value,
                )
            except Exception:
                pass

    @staticmethod
    def _finish_task_metadata(
        span: Any,
        *,
        success: Optional[bool],
        error: Optional[BaseException],
        exception: Optional[BaseException],
        attributes: Mapping[str, Any],
    ) -> None:
        """
        Attach task completion state and exception information.
        """

        values: Dict[str, Any] = dict(
            attributes,
        )

        if success is not None:
            values["success"] = success

        if error is not None:
            values["error"] = error

        if exception is not None:
            values["exception"] = exception

        TracePlugin._apply_span_attributes(
            span,
            values,
        )

        exc = exception or error

        if exc is not None:
            recorder = getattr(
                span,
                "record_exception",
                None,
            )

            if callable(recorder):
                try:
                    recorder(exc)
                except Exception:
                    pass

    def cleanup(self) -> "TracePlugin":
        """
        Clear plugin-local task state and delegate manager cleanup.
        """

        manager = self._manager

        if manager is not None:
            self._invoke(
                manager,
                (
                    "clear",
                    "reset",
                    "cleanup",
                ),
            )

        self._current_span = (
            getattr(
                manager,
                "current_span",
                None,
            )
            if manager is not None
            else None
        )

        self._trace = (
            getattr(
                manager,
                "current_trace",
                None,
            )
            if manager is not None
            else None
        )

        self._context = None
        self._span_stack.clear()

        return self



    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def set_context(
        self,
        context: Optional[TraceContext],
    ) -> "TracePlugin":

        self._context = context
        self._context_explicit = True

        self._invoke(
            self._provider,
            (
                "set_context",
                "update_context",
            ),
            context,
        )

        self._invoke(
            self._manager,
            (
                "set_context",
                "update_context",
            ),
            context,
        )

        return self

    def update_context(
        self,
        context: Optional[TraceContext] = None,
        **attributes: Any,
    ) -> "TracePlugin":

        if context is not None:
            self._context = context
            self._context_explicit = True

        target = self._context

        if target is not None and attributes:
            for key, value in attributes.items():
                try:
                    setattr(target, key, value)
                except Exception:
                    pass

        self._invoke(
            self._provider,
            (
                "update_context",
                "set_context",
            ),
            target,
            **attributes,
        )

        self._invoke(
            self._manager,
            (
                "update_context",
                "set_context",
            ),
            target,
            **attributes,
        )

        return self

    def clear_context(self) -> "TracePlugin":

        self._context = None
        self._context_explicit = True

        self._invoke(
            self._provider,
            (
                "clear_context",
                "reset_context",
            ),
        )

        self._invoke(
            self._manager,
            (
                "clear_context",
                "reset_context",
            ),
        )

        return self

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def process(
        self,
        value: Any = None,
    ) -> Any:

        if value is None:
            self._statistics.processed_count += 1
            return self

        if isinstance(value, Trace):
            return self.process_trace(value)

        if isinstance(value, Span):
            return self.process_span(value)

        result = self._invoke(
            self._processor,
            (
                "process",
                "process_item",
                "handle",
            ),
            value,
        )

        self._statistics.processed_count += 1

        return value if result is None else result

    def process_trace(
        self,
        trace: Trace,
    ) -> Trace:

        if trace is None:
            return trace

        result = self._invoke(
            self._processor,
            (
                "process_trace",
                "process",
                "handle",
            ),
            trace,
        )

        if result is not None:
            trace = result

        # Normalize compatible trace-like objects.
        if not isinstance(trace, Trace):
            try:
                trace = Trace(
                    name=getattr(trace, "name", "trace"),
                )
            except TypeError:
                try:
                    trace = Trace(
                        getattr(trace, "name", "trace"),
                    )
                except Exception:
                    pass

        self._statistics.processed_count += 1

        return trace

    def process_span(
        self,
        span: Span,
    ) -> Span:

        if span is None:
            return span

        result = self._invoke(
            self._processor,
            (
                "process_span",
                "process",
                "handle",
            ),
            span,
        )

        if result is not None:
            span = result

        # Normalize compatible span-like objects.
        if not isinstance(span, Span):
            try:
                span = Span(
                    name=getattr(span, "name", "span"),
                )
            except TypeError:
                try:
                    span = Span(
                        getattr(span, "name", "span"),
                    )
                except Exception:
                    pass

        self._statistics.processed_count += 1

        return span

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    def should_sample(
        self,
        value: Any = None,
    ) -> bool:

        if self._sampler is None:
            return True

        result = self._invoke(
            self._sampler,
            (
                "should_sample",
                "sample",
                "decide",
            ),
            value,
        )

        if result is None:
            return True

        decision = bool(result)

        if decision:
            self._statistics.sampled_count += 1

        return decision

    def sampling_decision(
        self,
        value: Any = None,
    ) -> bool:

        return self.should_sample(value)

    # ------------------------------------------------------------------
    # Exporting
    # ------------------------------------------------------------------

    def export(
        self,
        value: Any = None,
    ) -> Any:

        if value is None:
            if self._trace is not None:
                return self.export_trace()

            if self._current_span is not None:
                return self.export_span()

            return self

        if isinstance(value, Trace):
            return self.export_trace(value)

        if isinstance(value, Span):
            return self.export_span(value)

        if self._exporter is None:
            return value

        result = self._invoke(
            self._exporter,
            (
                "export",
                "send",
                "write",
            ),
            value,
        )

        self._statistics.exported_count += 1

        return value if result is None else result

    def export_trace(
        self,
        trace: Optional[Trace] = None,
    ) -> Any:

        target = trace or self._trace

        if target is None:
            return self

        if self._exporter is None:
            return target

        result = self._invoke(
            self._exporter,
            (
                "export_trace",
                "export",
                "send",
                "write",
            ),
            target,
        )

        self._statistics.exported_count += 1

        return target if result is None else result

    def export_span(
        self,
        span: Optional[Span] = None,
    ) -> Any:

        target = span or self.current_span

        if target is None:
            return self

        if self._exporter is None:
            return target

        result = self._invoke(
            self._exporter,
            (
                "export_span",
                "export",
                "send",
                "write",
            ),
            target,
        )

        self._statistics.exported_count += 1

        return target if result is None else result

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def registration(self) -> PluginRegistration:

        if self._registration is None:
            self._registration = PluginRegistration(
                name=self._name,
                plugin_type=PluginType.TRACING,
                version=self.version,
                priority=self._priority,
                enabled=self._enabled,
                factory=type(self),
                metadata=dict(self._metadata),
            )

        return self._registration

    # ------------------------------------------------------------------
    # Snapshot / restore
    # ------------------------------------------------------------------

    def snapshot(self) -> PluginSnapshot:

        statistics = PluginStatistics(
            trace_count=self._statistics.trace_count,
            span_count=self._statistics.span_count,
            processed_count=self._statistics.processed_count,
            sampled_count=self._statistics.sampled_count,
            exported_count=self._statistics.exported_count,
            error_count=self._statistics.error_count,
            start_count=self._statistics.start_count,
            stop_count=self._statistics.stop_count,
        )

        return PluginSnapshot(
            name=self._name,
            version=self.version,
            state=self._state,
            enabled=self._enabled,
            active=self.active,
            metadata=dict(self._metadata),
            attributes=dict(self._attributes),
            statistics=statistics,
            trace=self._trace,
            current_span=self._current_span,
            context=self._context,
        )

    def restore(
        self,
        snapshot: Optional[PluginSnapshot],
    ) -> "TracePlugin":

        if snapshot is None:
            return self

        self._name = snapshot.name
        self._enabled = bool(snapshot.enabled)
        self._state = snapshot.state

        self._metadata = dict(snapshot.metadata)
        self._attributes = dict(snapshot.attributes)

        statistics = snapshot.statistics

        self._statistics = PluginStatistics(
            trace_count=statistics.trace_count,
            span_count=statistics.span_count,
            processed_count=statistics.processed_count,
            sampled_count=statistics.sampled_count,
            exported_count=statistics.exported_count,
            error_count=statistics.error_count,
            start_count=statistics.start_count,
            stop_count=statistics.stop_count,
        )

        self._trace = snapshot.trace
        self._current_span = snapshot.current_span
        self._context = snapshot.context
        self._context_explicit = (
            snapshot.context is not None
        )

        return self

    # ------------------------------------------------------------------
    # Health / state
    # ------------------------------------------------------------------

    def health(self) -> bool:

        if not self._enabled:
            return False

        if self._state == PluginState.FAILED:
            return False

        return True

    def status(self) -> str:
        return self._state.name.lower()

    def disable(self) -> "TracePlugin":
        self._enabled = False
        return self

    def enable(self) -> "TracePlugin":
        self._enabled = True
        return self

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:

        if not self._name:
            return False

        if not self._service_name:
            return False

        if self._priority < 0:
            return False

        if self._order < 0:
            return False

        return True

    def validate_trace(
        self,
        trace: Optional[Trace],
    ) -> bool:

        return trace is not None

    def validate_span(
        self,
        span: Optional[Span],
    ) -> bool:

        return span is not None

    def validate_state(self) -> bool:

        return self._state in (
            PluginState.CREATED,
            PluginState.INITIALIZED,
            PluginState.RUNNING,
            PluginState.STOPPED,
            PluginState.FAILED,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> Dict[str, Any]:

        return {
            "name": self._name,
            "version": self.version,
            "api_version": self.api_version,
            "service_name": self._service_name,
            "state": self.status(),
            "enabled": self._enabled,
            "active": self.active,
            "ready": self.ready,
            "healthy": self.health(),
            "trace_active": self._trace is not None,
            "span_active": self._current_span is not None,
            "context_active": self._context is not None,
            "statistics": {
                "trace_count": self._statistics.trace_count,
                "span_count": self._statistics.span_count,
                "processed_count": self._statistics.processed_count,
                "sampled_count": self._statistics.sampled_count,
                "exported_count": self._statistics.exported_count,
                "error_count": self._statistics.error_count,
                "start_count": self._statistics.start_count,
                "stop_count": self._statistics.stop_count,
            },
        }

    def summary(self) -> Dict[str, Any]:

        return {
            "name": self._name,
            "version": self.version,
            "state": self.status(),
            "enabled": self._enabled,
            "active": self.active,
            "trace_count": self._statistics.trace_count,
            "span_count": self._statistics.span_count,
            "processed_count": self._statistics.processed_count,
            "sampled_count": self._statistics.sampled_count,
            "exported_count": self._statistics.exported_count,
            "error_count": self._statistics.error_count,
        }



# ==============================================================================
# Part 9. Plugin Registry / Integration
# ==============================================================================

class TracePluginRegistry:
    """
    Registry for tracing plugins.
    """

    _plugins: Dict[str, TracePlugin] = {}
    _registrations: Dict[str, PluginRegistration] = {}

    @classmethod
    def register(
        cls,
        plugin: TracePlugin,
        *,
        replace: bool = False,
    ) -> TracePlugin:
        if not isinstance(plugin, TracePlugin):
            raise TracePluginRegistrationError(
                "Only TracePlugin instances can be registered.",
            )

        name = plugin.name

        if name in cls._plugins and not replace:
            raise TracePluginRegistrationError(
                f"Plugin already registered: {name}",
            )

        cls._plugins[name] = plugin

        cls._registrations[name] = PluginRegistration(
            name=name,
            version=plugin.version,
            enabled=plugin.enabled,
        )

        return plugin

    @classmethod
    def unregister(
        cls,
        name: str,
    ) -> Optional[TracePlugin]:
        cls._registrations.pop(name, None)

        return cls._plugins.pop(name, None)

    @classmethod
    def get(
        cls,
        name: str,
    ) -> Optional[TracePlugin]:
        return cls._plugins.get(name)

    @classmethod
    def require(
        cls,
        name: str,
    ) -> TracePlugin:
        plugin = cls.get(name)

        if plugin is None:
            raise TracePluginRegistrationError(
                f"Tracing plugin is not registered: {name}",
            )

        return plugin

    @classmethod
    def contains(
        cls,
        name: str,
    ) -> bool:
        return name in cls._plugins

    @classmethod
    def all(
        cls,
    ) -> Tuple[TracePlugin, ...]:
        return tuple(cls._plugins.values())

    @classmethod
    def names(
        cls,
    ) -> Tuple[str, ...]:
        return tuple(cls._plugins.keys())

    @classmethod
    def clear(cls) -> None:
        cls._plugins.clear()
        cls._registrations.clear()


# ==============================================================================
# Part 10. Utility Methods
# ==============================================================================

def create_trace_plugin(
    name: str = PLUGIN_NAME,
    *,
    service_name: str = DEFAULT_SERVICE_NAME,
    enabled: bool = DEFAULT_PLUGIN_ENABLED,
    **kwargs: Any,
) -> TracePlugin:
    """
    Create a TracePlugin instance.
    """

    return TracePlugin(
        name=name,
        service_name=service_name,
        enabled=enabled,
        **kwargs,
    )


def register_trace_plugin(
    plugin: TracePlugin,
    *,
    replace: bool = False,
) -> TracePlugin:
    """
    Register a TracePlugin globally.
    """

    return TracePluginRegistry.register(
        plugin,
        replace=replace,
    )


def get_trace_plugin(
    name: str = PLUGIN_NAME,
) -> Optional[TracePlugin]:
    """
    Retrieve a registered TracePlugin.
    """

    return TracePluginRegistry.get(name)


def unregister_trace_plugin(
    name: str = PLUGIN_NAME,
) -> Optional[TracePlugin]:
    """
    Remove a registered TracePlugin.
    """

    return TracePluginRegistry.unregister(name)


def default_trace_plugin() -> TracePlugin:
    """
    Return the default SciOS tracing plugin.

    Creates and registers it lazily.
    """

    plugin = get_trace_plugin(PLUGIN_NAME)

    if plugin is None:
        plugin = create_trace_plugin(
            name=PLUGIN_NAME,
        )

        register_trace_plugin(plugin)

    return plugin


# ==============================================================================
# Compatibility Alias
# ==============================================================================

# Canonical public class:
#     TracePlugin
#
# Backward/test compatibility:
#     TracingPlugin
#
# Keep TracePlugin as the canonical API name.
TracingPlugin = TracePlugin


# ==============================================================================
# Part 11. Public API
# ==============================================================================

__all__ = [
    # Type aliases
    "PluginConfig",
    "PluginMetadata",
    "PluginAttributes",
    "PluginFactory",
    "ProviderFactory",
    "ManagerFactory",
    "ProcessorFactory",
    "SamplerFactory",
    "ExporterFactory",
    "TraceItem",
    "PluginResult",
    "PluginCallback",

    # Constants
    "PLUGIN_NAME",
    "PLUGIN_VERSION",
    "PLUGIN_API_VERSION",
    "PLUGIN_TYPE",
    "DEFAULT_PLUGIN_ENABLED",
    "DEFAULT_SERVICE_NAME",
    "DEFAULT_PLUGIN_PRIORITY",
    "DEFAULT_PLUGIN_ORDER",
    "EMPTY_PLUGIN_NAME",
    "PLUGIN_STATUS_CREATED",
    "PLUGIN_STATUS_INITIALIZED",
    "PLUGIN_STATUS_RUNNING",
    "PLUGIN_STATUS_STOPPED",
    "PLUGIN_STATUS_FAILED",
    "SUPPORTED_PLUGIN_STATUSES",

    # Exceptions
    "TracePluginError",
    "TracePluginConfigurationError",
    "TracePluginStateError",
    "TracePluginRegistrationError",
    "TracePluginInitializationError",
    "TracePluginLifecycleError",
    "TracePluginValidationError",

    # Enums
    "PluginState",
    "PluginType",
    "PluginEvent",

    # Dataclasses
    "PluginConfigData",
    "PluginStatistics",
    "PluginSnapshot",
    "PluginRegistration",

    # Plugin
    "TracePlugin",
    "TracingPlugin",

    # Registry
    "TracePluginRegistry",

    # Utilities
    "create_trace_plugin",
    "register_trace_plugin",
    "get_trace_plugin",
    "unregister_trace_plugin",
    "default_trace_plugin",
]
