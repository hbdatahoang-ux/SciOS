"""
SciOS-NG Runtime Visualization Dashboard

Dashboard Engine

SciOS/scios/runtime/observability/metrics/visualization/dashboard.py
"""


from __future__ import annotations


import json
import threading
import uuid
import copy


from datetime import datetime
from typing import Any, Callable


from .charts import MetricChartRenderer
from .timeline import MetricTimeline



# ==========================================================
# MetricDashboard
# ==========================================================


class MetricDashboard:
    """
    Runtime Metrics Visualization Dashboard Engine.

    Foundation
    ----------
    - Identity
    - Runtime State
    - Dashboard Configuration
    - Chart Engine Integration
    - Timeline Integration
    - Widget Registry
    - Metadata
    - Statistics
    """



    # ======================================================
    # Constructor
    # ======================================================


    def __init__(
        self,
        name: str = "MetricDashboard",
        description: str = "",
        chart_renderer=None,
        timeline=None,
    ) -> None:



        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

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
        # Dashboard Configuration
        # --------------------------------------------------

        self._config = {

            "theme": "default",

            "layout": "grid",

            "refresh_interval": 5,

            "max_widgets": 100,

        }



        # --------------------------------------------------
        # Synchronization
        # --------------------------------------------------

        self._lock = threading.RLock()



        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._version = "0.1.0"



        # --------------------------------------------------
        # Components
        # --------------------------------------------------

        self._chart_renderer = (

            chart_renderer

            if chart_renderer

            else

            MetricChartRenderer()

        )


        self._timeline = (

            timeline

            if timeline

            else

            MetricTimeline(

                chart_renderer=self._chart_renderer

            )

        )



        # --------------------------------------------------
        # Widget Registry
        # --------------------------------------------------

        self._widgets = {}



        # --------------------------------------------------
        # Runtime Statistics
        # --------------------------------------------------

        self._dashboard_count = 0

        self._render_count = 0

        self._error_count = 0

        self._latency = 0.0



        # --------------------------------------------------
        # Runtime Data
        # --------------------------------------------------

        self._history = []

        self._last_result = None

        self._snapshot = None

        self._context = {}



        # --------------------------------------------------
        # Events & Hooks
        # --------------------------------------------------

        self._hooks: dict[
            str,
            list[Callable]
        ] = {}


        self._events = []



    # ======================================================
    # Identity
    # ======================================================


    @property
    def id(
        self,
    ):

        return self._id



    @property
    def name(
        self,
    ):

        return self._name



    @property
    def description(
        self,
    ):

        return self._description



    @property
    def version(
        self,
    ):

        return self._version



    # ======================================================
    # Runtime State
    # ======================================================


    @property
    def enabled(
        self,
    ):

        return self._enabled



    @property
    def disabled(
        self,
    ):

        return not self._enabled



    @property
    def frozen(
        self,
    ):

        return self._frozen



    @property
    def closed(
        self,
    ):

        return self._closed



    @property
    def running(
        self,
    ):

        return self._running



    @property
    def active(
        self,
    ):

        return (

            self._enabled

            and

            not self._frozen

            and

            not self._closed

        )



    # ======================================================
    # Dashboard Configuration
    # ======================================================


    def config(
        self,
        key=None,
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
    # Component Access
    # ======================================================


    @property
    def charts(
        self,
    ):

        return self._chart_renderer



    @property
    def timeline(
        self,
    ):

        return self._timeline
    # ======================================================
    # Part 2. Dashboard API
    # ======================================================


    def render(
        self,
        data=None,
        **kwargs,
    ):
        """
        Render complete dashboard.

        Combines:
        - charts
        - timelines
        - widgets
        """

        if not self.active:

            raise RuntimeError(
                "MetricDashboard is not active."
            )


        self._running = True


        try:

            result = {

                "dashboard":
                    self._name,

                "charts":
                    self.render_chart(
                        data,
                        **kwargs,
                    ),

                "timeline":
                    self.render_timeline(
                        data,
                        **kwargs,
                    ),

                "widgets":
                    dict(
                        self._widgets
                    ),

                "timestamp":
                    datetime.utcnow(),

            }


            self._render_count += 1

            self._dashboard_count += 1


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



    def render_chart(
        self,
        data,
        chart: str = "line",
        **kwargs,
    ):
        """
        Render dashboard chart.
        """

        return self._chart_renderer.render(

            data,

            chart=chart,

            **kwargs,

        )



    def render_timeline(
        self,
        data,
        renderer: str = "line",
        **kwargs,
    ):
        """
        Render dashboard timeline.
        """

        return self._timeline.render(

            data,

            chart=renderer,

            **kwargs,

        )



    def add_widget(
        self,
        name: str,
        widget: Any,
        *,
        metadata: dict | None = None,
    ):
        """
        Add dashboard widget.
        """

        with self._lock:


            self._widgets[name] = {

                "name":
                    name,

                "widget":
                    widget,

                "metadata":
                    metadata or {},

                "created_at":
                    datetime.utcnow(),

            }


            self._updated_at = datetime.utcnow()



        return self



    def remove_widget(
        self,
        name: str,
    ):
        """
        Remove dashboard widget.
        """

        with self._lock:

            self._widgets.pop(

                name,

                None,

            )


            self._updated_at = datetime.utcnow()



        return self



    def update_widget(
        self,
        name: str,
        widget=None,
        **metadata,
    ):
        """
        Update dashboard widget.
        """

        entry = self._widgets.get(
            name
        )


        if entry is None:

            raise KeyError(
                f"Unknown widget: {name}"
            )


        with self._lock:


            if widget is not None:

                entry["widget"] = widget


            entry["metadata"].update(
                metadata
            )


            self._updated_at = datetime.utcnow()



        return self



    def widget(
        self,
        name: str,
        default=None,
    ):
        """
        Get widget.
        """

        return self._widgets.get(
            name,
            default,
        )



    def widgets(
        self,
    ):
        """
        Return all widgets.
        """

        return dict(
            self._widgets
        )



    def dashboard(
        self,
        data=None,
        **kwargs,
    ):
        """
        Alias of render().
        """

        return self.render(

            data,

            **kwargs,

        )



    # ------------------------------------------------------
    # Aliases
    # ------------------------------------------------------

    show = render

    display = render

    visualize = render
    # ======================================================
    # Part 3. Dashboard Components
    # ======================================================


    def chart_component(
        self,
        name: str,
        data,
        chart: str = "line",
        **kwargs,
    ):
        """
        Create chart component.
        """

        component = {

            "type":
                "chart",

            "name":
                name,

            "renderer":
                chart,

            "data":
                data,

            "result":
                self.render_chart(

                    data,

                    chart=chart,

                    **kwargs,

                ),

            "created_at":
                datetime.utcnow(),

        }


        self.add_widget(

            name,

            component,

            metadata={

                "component":
                    "chart"

            },

        )


        return component



    def timeline_component(
        self,
        name: str,
        data,
        renderer: str = "line",
        **kwargs,
    ):
        """
        Create timeline component.
        """

        component = {

            "type":
                "timeline",

            "name":
                name,

            "renderer":
                renderer,

            "data":
                data,

            "result":
                self.render_timeline(

                    data,

                    renderer=renderer,

                    **kwargs,

                ),

            "created_at":
                datetime.utcnow(),

        }


        self.add_widget(

            name,

            component,

            metadata={

                "component":
                    "timeline"

            },

        )


        return component



    def metric_component(
        self,
        name: str,
        value,
        unit: str | None = None,
        **metadata,
    ):
        """
        Create metric display component.
        """

        component = {

            "type":
                "metric",

            "name":
                name,

            "value":
                value,

            "unit":
                unit,

            "metadata":
                metadata,

            "created_at":
                datetime.utcnow(),

        }


        self.add_widget(

            name,

            component,

            metadata={

                "component":
                    "metric"

            },

        )


        return component



    def table_component(
        self,
        name: str,
        rows,
        columns=None,
        **metadata,
    ):
        """
        Create table component.
        """

        component = {

            "type":
                "table",

            "name":
                name,

            "rows":
                list(rows),

            "columns":
                columns,

            "metadata":
                metadata,

            "created_at":
                datetime.utcnow(),

        }


        self.add_widget(

            name,

            component,

            metadata={

                "component":
                    "table"

            },

        )


        return component



    def text_component(
        self,
        name: str,
        text: str,
        **metadata,
    ):
        """
        Create text component.
        """

        component = {

            "type":
                "text",

            "name":
                name,

            "text":
                text,

            "metadata":
                metadata,

            "created_at":
                datetime.utcnow(),

        }


        self.add_widget(

            name,

            component,

            metadata={

                "component":
                    "text"

            },

        )


        return component



    def image_component(
        self,
        name: str,
        source,
        **metadata,
    ):
        """
        Create image component.
        """

        component = {

            "type":
                "image",

            "name":
                name,

            "source":
                source,

            "metadata":
                metadata,

            "created_at":
                datetime.utcnow(),

        }


        self.add_widget(

            name,

            component,

            metadata={

                "component":
                    "image"

            },

        )


        return component



    def custom_component(
        self,
        name: str,
        component: Any,
        **metadata,
    ):
        """
        Register custom dashboard component.
        """

        entry = {

            "type":
                "custom",

            "name":
                name,

            "component":
                component,

            "metadata":
                metadata,

            "created_at":
                datetime.utcnow(),

        }


        self.add_widget(

            name,

            entry,

            metadata={

                "component":
                    "custom"

            },

        )


        return entry
    # ======================================================
    # Part 4. Widget Registry API
    # ======================================================


    def register_widget(
        self,
        name: str,
        widget: Any,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register dashboard widget.
        """

        with self._lock:

            entry = {

                "name":
                    name,

                "widget":
                    widget,

                "enabled":
                    enabled,

                "metadata":
                    metadata or {},

                "created_at":
                    datetime.utcnow(),

            }


            self._widgets[name] = entry


            self._updated_at = datetime.utcnow()


        return self



    def remove_widget(
        self,
        name: str,
    ):
        """
        Remove dashboard widget.
        """

        with self._lock:

            self._widgets.pop(

                name,

                None,

            )


            self._updated_at = datetime.utcnow()


        return self



    def widget(
        self,
        name: str,
        default=None,
    ):
        """
        Get widget metadata.
        """

        return self._widgets.get(

            name,

            default,

        )



    def widgets(
        self,
    ):
        """
        Return all widgets.
        """

        return dict(
            self._widgets
        )



    def contains_widget(
        self,
        name: str,
    ) -> bool:
        """
        Check widget existence.
        """

        return (

            name

            in

            self._widgets

        )



    def exists_widget(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_widget().
        """

        return self.contains_widget(

            name

        )



    def enable_widget(
        self,
        name: str,
    ):
        """
        Enable widget.
        """

        entry = self._widgets.get(

            name

        )


        if entry is not None:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()


        return self



    def disable_widget(
        self,
        name: str,
    ):
        """
        Disable widget.
        """

        entry = self._widgets.get(

            name

        )


        if entry is not None:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()


        return self



    def widget_names(
        self,
    ):
        """
        Return widget names.
        """

        return list(

            self._widgets.keys()

        )



    @property
    def widget_count(
        self,
    ) -> int:
        """
        Number of registered widgets.
        """

        return len(

            self._widgets

        )



    def clear_widgets(
        self,
    ):
        """
        Remove all widgets.
        """

        with self._lock:

            self._widgets.clear()

            self._updated_at = datetime.utcnow()


        return self



    def execute_widget(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        """
        Execute registered widget.
        """

        entry = self._widgets.get(

            name

        )


        if entry is None:

            raise KeyError(

                f"Unknown dashboard widget: {name}"

            )



        if not entry["enabled"]:

            raise RuntimeError(

                f"Dashboard widget '{name}' is disabled."

            )



        widget = entry["widget"]



        if not callable(widget):

            return widget



        return widget(

            *args,

            **kwargs,

        )



    def register_builtin_widgets(
        self,
    ):
        """
        Register default dashboard widgets.
        """

        self.register_widget(

            "chart",

            self.chart_component,

            metadata={

                "type":
                    "chart"

            },

        )


        self.register_widget(

            "timeline",

            self.timeline_component,

            metadata={

                "type":
                    "timeline"

            },

        )


        self.register_widget(

            "metric",

            self.metric_component,

            metadata={

                "type":
                    "metric"

            },

        )


        self.register_widget(

            "table",

            self.table_component,

            metadata={

                "type":
                    "table"

            },

        )


        self.register_widget(

            "text",

            self.text_component,

            metadata={

                "type":
                    "text"

            },

        )


        return self
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================


    def enable(
        self,
    ):
        """
        Enable dashboard engine.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()


        return self



    def disable(
        self,
    ):
        """
        Disable dashboard engine.
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
        Freeze dashboard runtime.

        Existing state remains,
        but new rendering operations are blocked.
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
        Unfreeze dashboard runtime.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()


        return self



    def close(
        self,
    ):
        """
        Close dashboard engine.

        Releases runtime execution.
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
        Reopen dashboard engine.
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
        Reset dashboard runtime state.

        Keeps:
        - configuration
        - widgets
        - chart renderer
        - timeline engine
        """

        with self._lock:

            self._dashboard_count = 0

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
        Clear dashboard runtime data.

        Does not remove widgets.
        """

        with self._lock:

            self._history.clear()

            self._last_result = None

            self._context.clear()

            self._updated_at = datetime.utcnow()


        return self



    def snapshot(
        self,
    ):
        """
        Create dashboard runtime snapshot.
        """

        with self._lock:

            self._snapshot = {

                "id":
                    self._id,

                "name":
                    self._name,

                "config":
                    dict(
                        self._config
                    ),

                "enabled":
                    self._enabled,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

                "dashboard_count":
                    self._dashboard_count,

                "render_count":
                    self._render_count,

                "error_count":
                    self._error_count,

                "latency":
                    self._latency,

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
        Restore dashboard runtime snapshot.
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


            self._dashboard_count = snapshot.get(
                "dashboard_count",
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
        Clone dashboard engine.
        """

        cloned = self.__class__(

            name=self._name,

            description=self._description,

            chart_renderer=self._chart_renderer,

            timeline=self._timeline,

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
        Return dashboard summary.
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


            "widget_count":
                self.widget_count,


            "dashboard_count":
                self._dashboard_count,


            "render_count":
                self._render_count,


            "error_count":
                self._error_count,


            "uptime":
                self.uptime,


            "latency":
                self._latency,

        }



    def report(
        self,
    ) -> dict:
        """
        Return detailed dashboard diagnostic report.
        """

        return {

            "summary":
                self.summary(),


            "configuration":
                dict(
                    self._config
                ),


            "widgets":
                self.widget_names(),


            "widget_registry":
                self.widgets(),


            "chart_renderer":
                self._chart_renderer.summary(),


            "timeline":
                self._timeline.summary(),


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


            "widgets":
                self.widget_count,


            "dashboards":
                self._dashboard_count,


            "renders":
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
    def dashboard_count(
        self,
    ) -> int:
        """
        Number of dashboard executions.
        """

        return self._dashboard_count



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
    def latency(
        self,
    ) -> float:
        """
        Last rendering latency.
        """

        return self._latency



    @property
    def uptime(
        self,
    ) -> float:
        """
        Dashboard uptime in seconds.
        """

        if self._created_at:

            return (

                datetime.utcnow()

                -

                self._created_at

            ).total_seconds()


        return 0.0
    # ======================================================
    # Part 8. Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict:
        """
        Serialize dashboard engine into dictionary.
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


            # Lifecycle

            "enabled":
                self._enabled,

            "frozen":
                self._frozen,

            "closed":
                self._closed,



            # Configuration

            "config":
                dict(
                    self._config
                ),



            # Runtime Statistics

            "dashboard_count":
                self._dashboard_count,

            "render_count":
                self._render_count,

            "error_count":
                self._error_count,

            "latency":
                self._latency,

            "uptime":
                self.uptime,



            # Widgets

            "widgets":

                {

                    name:
                        {

                            "metadata":
                                widget.get(
                                    "metadata",
                                    {}
                                ),

                            "enabled":
                                widget.get(
                                    "enabled",
                                    True
                                ),

                        }

                    for name, widget

                    in self._widgets.items()

                },



            # Runtime Data

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



            # Metadata

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
        Restore dashboard from dictionary.
        """


        dashboard = cls(

            name=data.get(
                "name",
                "MetricDashboard",
            ),

            description=data.get(
                "description",
                "",
            ),

        )



        # Lifecycle

        dashboard._enabled = data.get(

            "enabled",

            True,

        )


        dashboard._frozen = data.get(

            "frozen",

            False,

        )


        dashboard._closed = data.get(

            "closed",

            False,

        )



        # Configuration

        dashboard._config.update(

            data.get(

                "config",

                {},

            )

        )



        # Statistics

        dashboard._dashboard_count = data.get(

            "dashboard_count",

            0,

        )


        dashboard._render_count = data.get(

            "render_count",

            0,

        )


        dashboard._error_count = data.get(

            "error_count",

            0,

        )


        dashboard._latency = data.get(

            "latency",

            0.0,

        )



        # Runtime

        dashboard._history = list(

            data.get(

                "history",

                [],

            )

        )


        dashboard._last_result = data.get(

            "last_result"

        )


        dashboard._context = dict(

            data.get(

                "context",

                {},

            )

        )



        # Restore widget metadata

        widgets = data.get(

            "widgets",

            {},

        )


        for name, info in widgets.items():


            dashboard._widgets[name] = {

                "name":

                    name,


                "widget":

                    None,


                "enabled":

                    info.get(

                        "enabled",

                        True,

                    ),


                "metadata":

                    info.get(

                        "metadata",

                        {},

                    ),

            }



        dashboard._updated_at = datetime.utcnow()


        return dashboard





    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize dashboard into JSON.
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
        Restore dashboard from JSON.
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
        data=None,
        **kwargs,
    ):
        """
        Hook executed before dashboard rendering.
        """

        self.emit(

            "before_render",

            data=data,

            kwargs=kwargs,

        )

        return self



    def after_render(
        self,
        result,
    ):
        """
        Hook executed after dashboard rendering.
        """

        self.emit(

            "after_render",

            result=result,

        )

        return self



    def before_component(
        self,
        name: str,
        **kwargs,
    ):
        """
        Hook executed before component execution.
        """

        self.emit(

            "before_component",

            component=name,

            kwargs=kwargs,

        )

        return self



    def after_component(
        self,
        name: str,
        result=None,
    ):
        """
        Hook executed after component execution.
        """

        self.emit(

            "after_component",

            component=name,

            result=result,

        )

        return self



    def add_hook(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Register dashboard event hook.
        """

        if not callable(callback):

            raise TypeError(
                "callback must be callable"
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
        Remove dashboard hook.

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
        Emit dashboard event.
        """


        event_record = {

            "event":
                event,

            "payload":
                payload,

            "timestamp":
                datetime.utcnow(),

        }



        self._events.append(

            event_record

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

            f"widgets={self.widget_count}, "

            f"renders={self._render_count}, "

            f"errors={self._error_count}, "

            f"enabled={self._enabled}"

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

            f"(widgets={self.widget_count}, "

            f"renders={self._render_count})"

        )



    def __len__(
        self,
    ) -> int:
        """
        Return number of registered widgets.
        """

        return self.widget_count



    def __iter__(
        self,
    ):
        """
        Iterate over dashboard widgets.
        """

        return iter(

            self._widgets.items()

        )



    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check widget existence.
        """

        return (

            name

            in

            self._widgets

        )



    def __call__(
        self,
        data=None,
        **kwargs,
    ):
        """
        Callable dashboard interface.

        Equivalent to render().
        """

        return self.render(

            data,

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