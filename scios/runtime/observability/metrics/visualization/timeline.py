"""
SciOS-NG Runtime Metrics Visualization

Timeline Visualization Engine

SciOS/scios/runtime/observability/metrics/visualization/timeline.py
"""

from __future__ import annotations

import json
import threading
import uuid

from datetime import datetime
from typing import Any, Callable

from .charts import MetricChartRenderer


# ==========================================================
# MetricTimeline
# ==========================================================

class MetricTimeline:
    """
    Runtime Metrics Timeline Visualization Engine.

    Foundation
    ----------
    - Timeline Registry
    - Timeline Renderer
    - Runtime State
    - Timeline Configuration
    - Chart Renderer Integration
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        name: str = "MetricTimeline",
        description: str = "",
    ) -> None:

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._id = str(uuid.uuid4())

        self._name = name

        self._description = description

        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._frozen = False

        self._closed = False

        self._running = False

        # --------------------------------------------------
        # Timeline Configuration
        # --------------------------------------------------

        self._config = {

            "time_key": "timestamp",

            "timezone": "UTC",

            "sort": True,

            "ascending": True,

            "window": None,

            "group_by": None,

            "show_labels": True,

            "show_grid": True,

        }

        # --------------------------------------------------
        # Timeline Registry
        # --------------------------------------------------

        self._timelines: dict[
            str,
            dict[str, Any],
        ] = {}

        self._renderers: dict[
            str,
            dict[str, Any],
        ] = {}

        # --------------------------------------------------
        # Chart Renderer
        # --------------------------------------------------

        self._chart_renderer = MetricChartRenderer()

        # --------------------------------------------------
        # Synchronization
        # --------------------------------------------------

        self._lock = threading.RLock()

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._version = "0.2.0"

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self._timeline_count = 0

        self._render_count = 0

        self._error_count = 0

        self._latency = 0.0

        self._uptime = 0.0

        # --------------------------------------------------
        # Runtime Data
        # --------------------------------------------------

        self._history: list[dict] = []

        self._last_result = None

        self._snapshot = None

        self._context: dict[
            str,
            Any,
        ] = {}

        # --------------------------------------------------
        # Events
        # --------------------------------------------------

        self._hooks: dict[
            str,
            list[Callable],
        ] = {}

        self._events: list[
            dict[str, Any]
        ] = []

    # ======================================================
    # Identity
    # ======================================================

    @property
    def id(self):

        return self._id

    @property
    def name(self):

        return self._name

    @property
    def description(self):

        return self._description

    # ======================================================
    # Runtime State
    # ======================================================

    @property
    def enabled(self):

        return self._enabled

    @property
    def disabled(self):

        return not self._enabled

    @property
    def frozen(self):

        return self._frozen

    @property
    def closed(self):

        return self._closed

    @property
    def running(self):

        return self._running

    @property
    def active(self):

        return (

            self._enabled

            and

            not self._frozen

            and

            not self._closed

        )

    # ======================================================
    # Timeline Configuration
    # ======================================================

    def config(
        self,
        key: str | None = None,
        default=None,
    ):

        if key is None:

            return dict(
                self._config
            )

        return self._config.get(
            key,
            default,
        )

    def configure(
        self,
        **kwargs,
    ):

        with self._lock:

            self._config.update(
                kwargs
            )

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Chart Renderer
    # ======================================================

    @property
    def chart_renderer(
        self,
    ) -> MetricChartRenderer:
        """
        Underlying chart renderer.
        """

        return self._chart_renderer

    # ======================================================
    # Metadata
    # ======================================================

    @property
    def created_at(self):

        return self._created_at

    @property
    def updated_at(self):

        return self._updated_at

    @property
    def version(self):

        return self._version

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def timeline_count(self):

        return self._timeline_count

    @property
    def render_count(self):

        return self._render_count

    @property
    def error_count(self):

        return self._error_count

    # ======================================================
    # NOTE
    # ======================================================
    # Part 2 : Timeline API
    # Part 3 : Timeline Algorithms
    # Part 4 : Timeline Registry API
    # Part 5 : Lifecycle
    # Part 6 : Runtime Operations
    # Part 7 : Statistics & Diagnostics
    # Part 8 : Serialization
    # Part 9 : Events & Hooks
    # Part 10: Python Protocols
    # ======================================================
    # ======================================================
    # Part 2. Timeline API
    # ======================================================

    def render(
        self,
        events,
        chart: str = "line",
        **kwargs,
    ):
        """
        Render a timeline.
        """

        if not self.active:

            raise RuntimeError(
                "MetricTimeline is not active."
            )

        renderer = self._renderers.get(
            chart
        )

        if renderer is None:

            raise KeyError(
                f"Unknown timeline renderer: {chart}"
            )

        self._running = True

        try:

            result = renderer["callable"](

                events,

                **kwargs,

            )

            self._render_count += 1

            self._timeline_count += 1

            self._last_result = result

            self._history.append(
                result
            )

            self._updated_at = datetime.utcnow()

            return result

        except Exception:

            self._error_count += 1

            raise

        finally:

            self._running = False

    def render_one(
        self,
        events,
        chart: str = "line",
        **kwargs,
    ):
        """
        Render one timeline.
        """

        return self.render(

            events,

            chart=chart,

            **kwargs,

        )

    def render_many(
        self,
        timelines,
        chart: str = "line",
        **kwargs,
    ):
        """
        Render multiple timelines.
        """

        results = []

        for events in timelines:

            results.append(

                self.render(

                    events,

                    chart=chart,

                    **kwargs,

                )

            )

        return results

    def render_batch(
        self,
        batches,
        chart: str = "line",
        **kwargs,
    ):
        """
        Batch timeline rendering.
        """

        return self.render_many(

            batches,

            chart=chart,

            **kwargs,

        )

    # ------------------------------------------------------
    # Aliases
    # ------------------------------------------------------

    draw = render

    plot = render

    visualize = render
    # ======================================================
    # Part 3. Timeline Algorithms
    # ======================================================

    def line(
        self,
        events,
        **kwargs,
    ):
        """
        Render a line timeline.
        """

        return self._chart_renderer.line(

            events,

            **kwargs,

        )

    def area(
        self,
        events,
        **kwargs,
    ):
        """
        Render an area timeline.
        """

        return self._chart_renderer.area(

            events,

            **kwargs,

        )

    def scatter(
        self,
        events,
        **kwargs,
    ):
        """
        Render a scatter timeline.
        """

        return self._chart_renderer.scatter(

            events,

            **kwargs,

        )

    def event(
        self,
        events,
        **kwargs,
    ):
        """
        Render an event timeline.
        """

        return {

            "timeline": "event",

            "events": list(events),

            "chart": self._chart_renderer.scatter(

                events,

                **kwargs,

            ),

        }

    def sequence(
        self,
        events,
        **kwargs,
    ):
        """
        Render a sequence timeline.
        """

        return {

            "timeline": "sequence",

            "events": list(events),

            "chart": self._chart_renderer.line(

                events,

                **kwargs,

            ),

        }

    def gantt(
        self,
        tasks,
        **kwargs,
    ):
        """
        Render a Gantt timeline.
        """

        return {

            "timeline": "gantt",

            "tasks": list(tasks),

            "chart": self._chart_renderer.bar(

                tasks,

                **kwargs,

            ),

        }

    def milestone(
        self,
        milestones,
        **kwargs,
    ):
        """
        Render a milestone timeline.
        """

        return {

            "timeline": "milestone",

            "milestones": list(

                milestones

            ),

            "chart": self._chart_renderer.scatter(

                milestones,

                **kwargs,

            ),

        }

    def waterfall(
        self,
        events,
        **kwargs,
    ):
        """
        Render a waterfall timeline.
        """

        return {

            "timeline": "waterfall",

            "events": list(events),

            "chart": self._chart_renderer.bar(

                events,

                **kwargs,

            ),

        }

    def custom(
        self,
        events,
        renderer,
        **kwargs,
    ):
        """
        Execute a user-defined timeline renderer.
        """

        if not callable(
            renderer
        ):

            raise TypeError(
                "renderer must be callable."
            )

        return renderer(

            events,

            **kwargs,

        )
    # ======================================================
    # Part 4. Timeline Registry API
    # ======================================================

    def register_renderer(
        self,
        name: str,
        renderer: Callable,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register a timeline renderer.
        """

        if not callable(renderer):

            raise TypeError(
                "renderer must be callable."
            )

        with self._lock:

            entry = {

                "name": name,

                "callable": renderer,

                "enabled": enabled,

                "metadata": metadata or {},

                "created_at": datetime.utcnow(),

            }

            self._renderers[name] = entry

            self._timelines[name] = entry

            self._updated_at = datetime.utcnow()

        return self

    def remove_renderer(
        self,
        name: str,
    ):
        """
        Remove a timeline renderer.
        """

        with self._lock:

            self._renderers.pop(
                name,
                None,
            )

            self._timelines.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self

    # ------------------------------------------------------
    # Alias
    # ------------------------------------------------------

    unregister_renderer = remove_renderer

    def renderer(
        self,
        name: str,
        default=None,
    ):
        """
        Return renderer metadata.
        """

        return self._renderers.get(
            name,
            default,
        )

    def renderers(
        self,
    ):
        """
        Return all registered renderers.
        """

        return dict(
            self._renderers
        )

    def contains_renderer(
        self,
        name: str,
    ) -> bool:
        """
        Whether a renderer exists.
        """

        return (

            name

            in

            self._renderers

        )

    def exists_renderer(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_renderer().
        """

        return self.contains_renderer(
            name
        )

    def enable_renderer(
        self,
        name: str,
    ):
        """
        Enable a renderer.
        """

        entry = self._renderers.get(
            name
        )

        if entry is not None:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self

    def disable_renderer(
        self,
        name: str,
    ):
        """
        Disable a renderer.
        """

        entry = self._renderers.get(
            name
        )

        if entry is not None:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self

    def renderer_names(
        self,
    ):
        """
        Return renderer names.
        """

        return list(
            self._renderers.keys()
        )

    @property
    def renderer_count(
        self,
    ) -> int:
        """
        Number of registered renderers.
        """

        return len(
            self._renderers
        )

    def clear_renderers(
        self,
    ):
        """
        Remove all renderers.
        """

        with self._lock:

            self._renderers.clear()

            self._timelines.clear()

            self._updated_at = datetime.utcnow()

        return self

    def execute_renderer(
        self,
        name: str,
        events,
        **kwargs,
    ):
        """
        Execute a registered renderer.
        """

        entry = self._renderers.get(
            name
        )

        if entry is None:

            raise KeyError(
                f"Unknown timeline renderer: {name}"
            )

        if not entry["enabled"]:

            raise RuntimeError(
                f"Timeline renderer '{name}' is disabled."
            )

        return entry["callable"](

            events,

            **kwargs,

        )

    def register_builtin_renderers(
        self,
    ):
        """
        Register built-in timeline renderers.
        """

        self.register_renderer(
            "line",
            self.line,
        )

        self.register_renderer(
            "area",
            self.area,
        )

        self.register_renderer(
            "scatter",
            self.scatter,
        )

        self.register_renderer(
            "event",
            self.event,
        )

        self.register_renderer(
            "sequence",
            self.sequence,
        )

        self.register_renderer(
            "gantt",
            self.gantt,
        )

        self.register_renderer(
            "milestone",
            self.milestone,
        )

        self.register_renderer(
            "waterfall",
            self.waterfall,
        )

        return self
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(
        self,
    ):
        """
        Enable the timeline engine.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ):
        """
        Disable the timeline engine.
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
        Freeze the timeline engine.
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
        Unfreeze the timeline engine.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ):
        """
        Close the timeline engine.
        """

        with self._lock:

            self._closed = True

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    def reopen(
        self,
    ):
        """
        Reopen the timeline engine.
        """

        with self._lock:

            self._closed = False

            self._updated_at = datetime.utcnow()

        return self
    # ======================================================
    # Part 6. Runtime Operations
    # ======================================================

    def reset(
        self,
    ):
        """
        Reset runtime state while preserving
        configuration and registered renderers.
        """

        with self._lock:

            self._timeline_count = 0

            self._render_count = 0

            self._error_count = 0

            self._latency = 0.0

            self._running = False

            self._last_result = None

            self._history.clear()

            self._events.clear()

            self._context.clear()

            self._updated_at = datetime.utcnow()

        return self


    def clear(
        self,
    ):
        """
        Clear timeline runtime history.
        """

        with self._lock:

            self._history.clear()

            self._last_result = None

            self._updated_at = datetime.utcnow()

        return self


    def snapshot(
        self,
    ):
        """
        Create runtime snapshot.
        """

        with self._lock:

            self._snapshot = {

                "config":
                    dict(self._config),

                "timeline_count":
                    self._timeline_count,

                "render_count":
                    self._render_count,

                "error_count":
                    self._error_count,

                "latency":
                    self._latency,

                "enabled":
                    self._enabled,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

                "history":
                    list(self._history),

                "last_result":
                    self._last_result,

                "context":
                    dict(self._context),

                "updated_at":
                    self._updated_at,

            }

            return dict(
                self._snapshot
            )


    def restore(
        self,
        snapshot: dict | None = None,
    ):
        """
        Restore runtime snapshot.
        """

        if snapshot is None:

            snapshot = self._snapshot


        if snapshot is None:

            return self


        with self._lock:

            self._config = dict(

                snapshot.get(
                    "config",
                    {},
                )

            )


            self._timeline_count = snapshot.get(
                "timeline_count",
                0,
            )


            self._render_count = snapshot.get(
                "render_count",
                0,
            )


            self._error_count = snapshot.get(
                "error_count",
                0,
            )


            self._latency = snapshot.get(
                "latency",
                0.0,
            )


            self._enabled = snapshot.get(
                "enabled",
                True,
            )


            self._frozen = snapshot.get(
                "frozen",
                False,
            )


            self._closed = snapshot.get(
                "closed",
                False,
            )


            self._history = list(

                snapshot.get(
                    "history",
                    [],
                )

            )


            self._last_result = snapshot.get(
                "last_result"
            )


            self._context = dict(

                snapshot.get(
                    "context",
                    {},
                )

            )


            self._updated_at = datetime.utcnow()

        return self


    def clone(
        self,
    ):
        """
        Clone timeline engine.
        """

        cloned = self.__class__(

            name=self._name,

            description=self._description,

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
        Return timeline engine summary.
        """

        return {

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

            "timeline_count":
                self._timeline_count,

            "render_count":
                self._render_count,

            "error_count":
                self._error_count,

            "renderer_count":
                self.renderer_count,

            "uptime":
                self.uptime,

            "latency":
                self._latency,

        }


    def report(
        self,
    ) -> dict:
        """
        Return detailed diagnostic report.
        """

        return {

            "summary":
                self.summary(),

            "configuration":
                dict(
                    self._config
                ),

            "renderers":
                self.renderer_names(),

            "history":
                list(
                    self._history
                ),

            "last_result":
                self._last_result,

            "created_at":
                self._created_at,

            "updated_at":
                self._updated_at,

            "chart_renderer":
                self._chart_renderer.summary(),

        }


    def health(
        self,
    ) -> dict:
        """
        Runtime health diagnostics.
        """

        if self._closed:

            state = "closed"

        elif self._frozen:

            state = "frozen"

        elif not self._enabled:

            state = "disabled"

        elif self._running:

            state = "running"

        else:

            state = "idle"


        return {

            "healthy":
                self.active,

            "state":
                state,

            "timeline_count":
                self._timeline_count,

            "render_count":
                self._render_count,

            "errors":
                self._error_count,

            "latency":
                self._latency,

            "uptime":
                self.uptime,

        }


    def status(
        self,
    ) -> dict:
        """
        Alias of health().
        """

        return self.health()


    # ======================================================
    # Statistics Properties
    # ======================================================

    @property
    def uptime(
        self,
    ) -> float:
        """
        Timeline uptime in seconds.
        """

        if self._created_at:

            return (

                datetime.utcnow()

                -

                self._created_at

            ).total_seconds()

        return 0.0


    @property
    def latency(
        self,
    ) -> float:
        """
        Last render latency.
        """

        return self._latency


    @property
    def renderer_count(
        self,
    ) -> int:
        """
        Number of timeline renderers.
        """

        return len(
            self._renderers
        )
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize timeline engine to dictionary.
        """

        return {

            "id":
                self._id,

            "name":
                self._name,

            "description":
                self._description,

            "version":
                self._version,

            "enabled":
                self._enabled,

            "frozen":
                self._frozen,

            "closed":
                self._closed,

            "config":
                dict(
                    self._config
                ),

            "timeline_count":
                self._timeline_count,

            "render_count":
                self._render_count,

            "error_count":
                self._error_count,

            "latency":
                self._latency,

            "uptime":
                self.uptime,

            "renderers":
                self.renderer_names(),

            "history":
                list(
                    self._history
                ),

            "last_result":
                self._last_result,

            "context":
                dict(
                    self._context
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
        Restore timeline engine from dictionary.
        """

        timeline = cls(

            name=data.get(
                "name",
                "MetricTimeline",
            ),

            description=data.get(
                "description",
                "",
            ),

        )


        timeline._enabled = data.get(
            "enabled",
            True,
        )


        timeline._frozen = data.get(
            "frozen",
            False,
        )


        timeline._closed = data.get(
            "closed",
            False,
        )


        timeline._config.update(

            data.get(
                "config",
                {},
            )

        )


        timeline._timeline_count = data.get(
            "timeline_count",
            0,
        )


        timeline._render_count = data.get(
            "render_count",
            0,
        )


        timeline._error_count = data.get(
            "error_count",
            0,
        )


        timeline._latency = data.get(
            "latency",
            0.0,
        )


        timeline._history = list(

            data.get(
                "history",
                [],
            )

        )


        timeline._last_result = data.get(
            "last_result"
        )


        timeline._context = dict(

            data.get(
                "context",
                {},
            )

        )


        return timeline



    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize timeline engine to JSON.
        """

        return json.dumps(

            self.to_dict(),

            default=str,

            **kwargs,

        )



    @classmethod
    def from_json(
        cls,
        data: str,
    ):
        """
        Restore timeline engine from JSON.
        """

        return cls.from_dict(

            json.loads(
                data
            )

        )



    def serialize(
        self,
        **kwargs,
    ) -> str:
        """
        Alias of to_json().
        """

        return self.to_json(
            **kwargs
        )



    @classmethod
    def deserialize(
        cls,
        data: str,
    ):
        """
        Alias of from_json().
        """

        return cls.from_json(
            data
        )
    # ======================================================
    # Part 9. Events & Hooks
    # ======================================================

    def before_render(
        self,
        events,
        renderer: str,
        **kwargs,
    ):
        """
        Hook executed before timeline rendering.
        """

        self.emit(

            "before_render",

            events=events,

            renderer=renderer,

            kwargs=kwargs,

        )

        return self



    def after_render(
        self,
        result,
        renderer: str,
    ):
        """
        Hook executed after timeline rendering.
        """

        self.emit(

            "after_render",

            result=result,

            renderer=renderer,

        )

        return self



    def before_renderer(
        self,
        name: str,
    ):
        """
        Hook executed before renderer execution.
        """

        self.emit(

            "before_renderer",

            renderer=name,

        )

        return self



    def after_renderer(
        self,
        name: str,
        result=None,
    ):
        """
        Hook executed after renderer execution.
        """

        self.emit(

            "after_renderer",

            renderer=name,

            result=result,

        )

        return self



    def add_hook(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Register event callback.
        """

        if not callable(callback):

            raise TypeError(
                "callback must be callable."
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
        callback: Callable | None = None,
    ):
        """
        Remove hook callback.

        If callback is None:
        remove all hooks of event.
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
        Emit timeline event.
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


        return self



    def subscribe(
        self,
        event: str,
        callback: Callable,
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

            f"enabled={self._enabled}, "

            f"renderers={len(self._renderers)}, "

            f"timelines={self._timeline_count}, "

            f"renders={self._render_count}, "

            f"errors={self._error_count}"

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

            f"(renderers={len(self._renderers)}, "

            f"timelines={self._timeline_count}, "

            f"renders={self._render_count})"

        )


    def __len__(
        self,
    ) -> int:
        """
        Return number of registered renderers.
        """

        return len(
            self._renderers
        )


    def __iter__(
        self,
    ):
        """
        Iterate over registered renderers.
        """

        return iter(

            self._renderers.items()

        )


    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check renderer existence.
        """

        return (

            name

            in

            self._renderers

        )


    def __call__(
        self,
        events,
        renderer: str = "line",
        **kwargs,
    ):
        """
        Callable timeline interface.

        Equivalent to render().
        """

        return self.render(

            events,

            chart=renderer,

            **kwargs,

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