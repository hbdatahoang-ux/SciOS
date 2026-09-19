"""
SciOS-NG Runtime Metrics Visualization

Chart Rendering Engine

SciOS/scios/runtime/observability/metrics/visualization/charts.py
"""

from __future__ import annotations

import threading
import uuid

from datetime import datetime
from typing import Any, Callable


# ==========================================================
# MetricChartRenderer
# ==========================================================

class MetricChartRenderer:
    """
    Runtime Metrics Chart Rendering Engine.

    Foundation
    ----------
    - Chart Registry
    - Renderer Registry
    - Runtime State
    - Chart Configuration
    - Visualization Engine
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        name: str = "MetricChartRenderer",
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
        # Chart Configuration
        # --------------------------------------------------

        self._config = {

            "theme": "light",

            "width": 800,

            "height": 600,

            "dpi": 100,

            "format": "png",

            "title": True,

            "legend": True,

            "grid": True,

            "animation": False,

        }

        # --------------------------------------------------
        # Chart Registry
        # --------------------------------------------------

        self._charts: dict[
            str,
            dict[str, Any],
        ] = {}

        self._renderers: dict[
            str,
            dict[str, Any],
        ] = {}

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

        self._chart_count = 0

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
    # Chart Configuration
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
    def chart_count(self):

        return self._chart_count

    @property
    def render_count(self):

        return self._render_count

    @property
    def error_count(self):

        return self._error_count

    # ======================================================
    # NOTE
    # ======================================================
    # Part 2 : Chart API
    # Part 3 : Chart Types
    # Part 4 : Chart Registry API
    # Part 5 : Lifecycle
    # Part 6 : Runtime Operations
    # Part 7 : Statistics & Diagnostics
    # Part 8 : Serialization
    # Part 9 : Events & Hooks
    # Part 10: Python Protocols
    # ======================================================
    # ======================================================
    # Part 2. Chart API
    # ======================================================

    def render(
        self,
        data,
        chart: str = "line",
        **kwargs,
    ):
        """
        Render a chart.
        """

        if not self.active:

            raise RuntimeError(
                "MetricChartRenderer is not active."
            )

        renderer = self._renderers.get(
            chart
        )

        if renderer is None:

            raise KeyError(
                f"Unknown chart renderer: {chart}"
            )

        self._running = True

        try:

            result = renderer["callable"](

                data,

                **kwargs,

            )

            self._render_count += 1

            if isinstance(
                result,
                dict,
            ):

                self._chart_count += 1

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
        data,
        chart: str = "line",
        **kwargs,
    ):
        """
        Render one chart.
        """

        return self.render(

            data,

            chart=chart,

            **kwargs,

        )

    def render_many(
        self,
        datasets,
        chart: str = "line",
        **kwargs,
    ):
        """
        Render multiple charts.
        """

        results = []

        for data in datasets:

            results.append(

                self.render(

                    data,

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
        Batch rendering.
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
    # Part 3. Chart Types
    # ======================================================

    def line(
        self,
        data,
        **kwargs,
    ):
        """
        Render a line chart.
        """

        return {

            "chart": "line",

            "data": data,

            "options": kwargs,

        }

    def bar(
        self,
        data,
        **kwargs,
    ):
        """
        Render a bar chart.
        """

        return {

            "chart": "bar",

            "data": data,

            "options": kwargs,

        }

    def scatter(
        self,
        data,
        **kwargs,
    ):
        """
        Render a scatter chart.
        """

        return {

            "chart": "scatter",

            "data": data,

            "options": kwargs,

        }

    def histogram(
        self,
        data,
        **kwargs,
    ):
        """
        Render a histogram.
        """

        return {

            "chart": "histogram",

            "data": data,

            "options": kwargs,

        }

    def pie(
        self,
        data,
        **kwargs,
    ):
        """
        Render a pie chart.
        """

        return {

            "chart": "pie",

            "data": data,

            "options": kwargs,

        }

    def heatmap(
        self,
        data,
        **kwargs,
    ):
        """
        Render a heatmap.
        """

        return {

            "chart": "heatmap",

            "data": data,

            "options": kwargs,

        }

    def area(
        self,
        data,
        **kwargs,
    ):
        """
        Render an area chart.
        """

        return {

            "chart": "area",

            "data": data,

            "options": kwargs,

        }

    def gauge(
        self,
        value,
        *,
        minimum: float = 0.0,
        maximum: float = 100.0,
        **kwargs,
    ):
        """
        Render a gauge chart.
        """

        return {

            "chart": "gauge",

            "value": value,

            "minimum": minimum,

            "maximum": maximum,

            "options": kwargs,

        }

    def radar(
        self,
        data,
        labels=None,
        **kwargs,
    ):
        """
        Render a radar chart.
        """

        return {

            "chart": "radar",

            "data": data,

            "labels": labels,

            "options": kwargs,

        }

    def custom(
        self,
        data,
        renderer,
        **kwargs,
    ):
        """
        Execute a user-defined renderer.
        """

        if not callable(
            renderer
        ):

            raise TypeError(
                "renderer must be callable."
            )

        return renderer(

            data,

            **kwargs,

        )
    # ======================================================
    # Part 4. Chart Registry API
    # ======================================================

    def register_chart(
        self,
        name: str,
        renderer: Callable,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register a chart renderer.
        """

        if not callable(
            renderer
        ):

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

            self._charts[name] = entry

            self._updated_at = datetime.utcnow()

        return self

    def remove_chart(
        self,
        name: str,
    ):
        """
        Remove a chart renderer.
        """

        with self._lock:

            self._renderers.pop(
                name,
                None,
            )

            self._charts.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self

    # ------------------------------------------------------
    # Alias
    # ------------------------------------------------------

    unregister_chart = remove_chart

    def chart(
        self,
        name: str,
        default=None,
    ):
        """
        Return chart metadata.
        """

        return self._renderers.get(
            name,
            default,
        )

    def charts(
        self,
    ):
        """
        Return all registered charts.
        """

        return dict(
            self._renderers
        )

    def contains_chart(
        self,
        name: str,
    ) -> bool:
        """
        Whether a chart exists.
        """

        return (

            name

            in

            self._renderers

        )

    def exists_chart(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_chart().
        """

        return self.contains_chart(
            name
        )

    def enable_chart(
        self,
        name: str,
    ):
        """
        Enable a chart renderer.
        """

        entry = self._renderers.get(
            name
        )

        if entry is not None:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self

    def disable_chart(
        self,
        name: str,
    ):
        """
        Disable a chart renderer.
        """

        entry = self._renderers.get(
            name
        )

        if entry is not None:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self

    def chart_names(
        self,
    ):
        """
        Return registered chart names.
        """

        return list(
            self._renderers.keys()
        )

    @property
    def chart_registry_count(
        self,
    ) -> int:
        """
        Number of registered charts.
        """

        return len(
            self._renderers
        )

    def clear_charts(
        self,
    ):
        """
        Remove all registered charts.
        """

        with self._lock:

            self._renderers.clear()

            self._charts.clear()

            self._updated_at = datetime.utcnow()

        return self

    def execute_chart(
        self,
        name: str,
        data,
        **kwargs,
    ):
        """
        Execute a registered chart renderer.
        """

        entry = self._renderers.get(
            name
        )

        if entry is None:

            raise KeyError(
                f"Unknown chart renderer: {name}"
            )

        if not entry["enabled"]:

            raise RuntimeError(
                f"Chart '{name}' is disabled."
            )

        return entry["callable"](

            data,

            **kwargs,

        )

    def register_builtin_charts(
        self,
    ):
        """
        Register built-in chart renderers.
        """

        self.register_chart(
            "line",
            self.line,
        )

        self.register_chart(
            "bar",
            self.bar,
        )

        self.register_chart(
            "scatter",
            self.scatter,
        )

        self.register_chart(
            "histogram",
            self.histogram,
        )

        self.register_chart(
            "pie",
            self.pie,
        )

        self.register_chart(
            "heatmap",
            self.heatmap,
        )

        self.register_chart(
            "area",
            self.area,
        )

        self.register_chart(
            "gauge",
            self.gauge,
        )

        self.register_chart(
            "radar",
            self.radar,
        )

        return self
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(
        self,
    ):
        """
        Enable the chart renderer.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ):
        """
        Disable the chart renderer.
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
        Freeze the chart renderer.
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
        Unfreeze the chart renderer.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ):
        """
        Close the chart renderer.
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
        Reopen the chart renderer.
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
        Reset the runtime state while preserving
        configuration and registered chart renderers.
        """

        with self._lock:

            self._chart_count = 0

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
        Clear runtime history.
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
        Create a runtime snapshot.
        """

        with self._lock:

            self._snapshot = {

                "config":
                    dict(self._config),

                "history":
                    list(self._history),

                "last_result":
                    self._last_result,

                "chart_count":
                    self._chart_count,

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
        Restore runtime state from a snapshot.
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

            self._history = list(

                snapshot.get(
                    "history",
                    [],
                )

            )

            self._last_result = snapshot.get(
                "last_result"
            )

            self._chart_count = snapshot.get(
                "chart_count",
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

            self._updated_at = datetime.utcnow()

        return self

    def clone(
        self,
    ):
        """
        Create a cloned renderer.
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
        Return renderer summary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "version": self._version,

            "enabled": self._enabled,

            "running": self._running,

            "chart_count":
                self._chart_count,

            "render_count":
                self._render_count,

            "error_count":
                self._error_count,

            "uptime":
                self.uptime,

            "latency":
                self._latency,

            "charts":
                self.chart_names(),

        }

    def report(
        self,
    ) -> dict:
        """
        Return a detailed renderer report.
        """

        return {

            "summary":
                self.summary(),

            "configuration":
                dict(self._config),

            "history":
                list(self._history),

            "last_result":
                self._last_result,

            "created_at":
                self._created_at,

            "updated_at":
                self._updated_at,

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

            "errors":
                self._error_count,

            "uptime":
                self.uptime,

            "latency":
                self._latency,

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
    def chart_count(
        self,
    ) -> int:
        """
        Number of rendered charts.
        """

        return self._chart_count

    @property
    def render_count(
        self,
    ) -> int:
        """
        Number of render operations.
        """

        return self._render_count

    @property
    def error_count(
        self,
    ) -> int:
        """
        Number of runtime errors.
        """

        return self._error_count

    @property
    def uptime(
        self,
    ) -> float:
        """
        Renderer uptime (seconds).
        """

        return self._uptime

    @property
    def latency(
        self,
    ) -> float:
        """
        Last rendering latency (seconds).
        """

        return self._latency
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize renderer to a dictionary.
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
                dict(self._config),

            "chart_count":
                self._chart_count,

            "render_count":
                self._render_count,

            "error_count":
                self._error_count,

            "latency":
                self._latency,

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
        Create a renderer from a dictionary.
        """

        renderer = cls(

            name=data.get(
                "name",
                "MetricChartRenderer",
            ),

            description=data.get(
                "description",
                "",
            ),

        )

        renderer._enabled = data.get(
            "enabled",
            True,
        )

        renderer._frozen = data.get(
            "frozen",
            False,
        )

        renderer._closed = data.get(
            "closed",
            False,
        )

        renderer._config.update(

            data.get(
                "config",
                {},
            )

        )

        renderer._chart_count = data.get(
            "chart_count",
            0,
        )

        renderer._render_count = data.get(
            "render_count",
            0,
        )

        renderer._error_count = data.get(
            "error_count",
            0,
        )

        renderer._latency = data.get(
            "latency",
            0.0,
        )

        return renderer

    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize renderer to JSON.
        """

        import json

        return json.dumps(

            self.to_dict(),

            **kwargs,

        )

    @classmethod
    def from_json(
        cls,
        data: str,
    ):
        """
        Create a renderer from JSON.
        """

        import json

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
        data,
        chart: str,
        **kwargs,
    ):
        """
        Hook executed before rendering.
        """

        self.emit(

            "before_render",

            data=data,

            chart=chart,

            kwargs=kwargs,

        )

        return self

    def after_render(
        self,
        result,
        chart: str,
    ):
        """
        Hook executed after rendering.
        """

        self.emit(

            "after_render",

            result=result,

            chart=chart,

        )

        return self

    def before_chart(
        self,
        name: str,
    ):
        """
        Hook executed before chart execution.
        """

        self.emit(

            "before_chart",

            chart=name,

        )

        return self

    def after_chart(
        self,
        name: str,
        result=None,
    ):
        """
        Hook executed after chart execution.
        """

        self.emit(

            "after_chart",

            chart=name,

            result=result,

        )

        return self

    def add_hook(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Register an event hook.
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
        Remove one hook or all hooks for an event.
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
        Emit an event.
        """

        record = {

            "timestamp":
                datetime.utcnow(),

            "event":
                event,

            "payload":
                payload,

        }

        self._events.append(
            record
        )

        for callback in self._hooks.get(
            event,
            [],
        ):

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

            f"charts={len(self._renderers)}, "

            f"renders={self._render_count}, "

            f"errors={self._error_count}"

            f")"

        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self._name} "

            f"(charts={len(self._renderers)}, "

            f"renders={self._render_count}, "

            f"errors={self._error_count})"

        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered chart renderers.
        """

        return len(
            self._renderers
        )

    def __iter__(
        self,
    ):
        """
        Iterate over registered chart renderers.
        """

        return iter(
            self._renderers.items()
        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a chart renderer exists.
        """

        return (

            name

            in

            self._renderers

        )

    def __call__(
        self,
        data,
        chart: str = "line",
        **kwargs,
    ):
        """
        Callable interface.

        Equivalent to render().
        """

        return self.render(

            data,

            chart=chart,

            **kwargs,

        )

    def __copy__(
        self,
    ):
        """
        Create a shallow copy.
        """

        return self.clone()

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Create a deep copy.
        """

        clone = self.clone()

        memo[id(self)] = clone

        return clone
                                                                        