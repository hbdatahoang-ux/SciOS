"""
SciOS-NG Runtime Visualization Report Engine

Generate reports from MetricDashboard.

SciOS/scios/runtime/observability/metrics/visualization/report.py
"""


from __future__ import annotations


import json
import uuid
import copy
import threading


from datetime import datetime
from typing import Any, Callable



from .dashboard import MetricDashboard



# ==========================================================
# MetricReport
# ==========================================================


class MetricReport:
    """
    Runtime Metrics Visualization Report Engine.

    Foundation
    ----------
    - Identity
    - Runtime State
    - Report Configuration
    - Dashboard Integration
    - Template Registry
    - Metadata
    - Statistics
    """



    # ======================================================
    # Constructor
    # ======================================================


    def __init__(
        self,
        name: str = "MetricReport",
        description: str = "",
        dashboard=None,
    ) -> None:



        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._id = str(

            uuid.uuid4()

        )


        self._name = name


        self._description = description


        self._version = "0.1.0"



        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._frozen = False

        self._closed = False

        self._running = False



        # --------------------------------------------------
        # Synchronization
        # --------------------------------------------------

        self._lock = threading.RLock()



        # --------------------------------------------------
        # Configuration
        # --------------------------------------------------

        self._config = {

            "format":
                "json",

            "template":
                "default",

            "include_charts":
                True,

            "include_timeline":
                True,

            "include_widgets":
                True,

        }



        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at



        # --------------------------------------------------
        # Dashboard Integration
        # --------------------------------------------------

        self._dashboard = (

            dashboard

            if dashboard

            else

            MetricDashboard()

        )



        # --------------------------------------------------
        # Template Registry
        # --------------------------------------------------

        self._templates = {}



        # --------------------------------------------------
        # Runtime Statistics
        # --------------------------------------------------

        self._report_count = 0

        self._generate_count = 0

        self._error_count = 0

        self._latency = 0.0



        # --------------------------------------------------
        # Runtime Data
        # --------------------------------------------------

        self._history = []

        self._last_report = None

        self._context = {}

        self._snapshot = None



        # --------------------------------------------------
        # Hooks
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
    # Dashboard Access
    # ======================================================


    @property
    def dashboard(
        self,
    ):

        return self._dashboard



    def configure(
        self,
        **kwargs,
    ):

        """
        Update report configuration.
        """

        with self._lock:

            self._config.update(

                kwargs

            )


            self._updated_at = datetime.utcnow()


        return self
    # ======================================================
    # Part 2. Report API
    # ======================================================


    def generate(
        self,
        data=None,
        **kwargs,
    ):
        """
        Generate complete report from dashboard.

        Pipeline:

        Data
          |
          v
        Dashboard
          |
          v
        Report Builder
          |
          v
        Report Output
        """


        if not self.active:

            raise RuntimeError(
                "MetricReport is not active."
            )


        self._running = True


        start = datetime.utcnow()


        try:

            dashboard_result = (

                self._dashboard.render(

                    data,

                    **kwargs,

                )

            )



            report = {

                "id":
                    self._id,

                "name":
                    self._name,

                "template":
                    self._config.get(

                        "template",

                        "default",

                    ),


                "created_at":
                    datetime.utcnow(),


                "dashboard":

                    dashboard_result,



                "summary":

                    self.generate_summary(

                        dashboard_result

                    ),



            }



            if self._config.get(

                "include_charts",

                True,

            ):

                report["charts"] = (

                    dashboard_result.get(

                        "charts",

                        {}

                    )

                )



            if self._config.get(

                "include_timeline",

                True,

            ):

                report["timeline"] = (

                    dashboard_result.get(

                        "timeline",

                        {}

                    )

                )



            if self._config.get(

                "include_widgets",

                True,

            ):

                report["widgets"] = (

                    dashboard_result.get(

                        "widgets",

                        {}

                    )

                )



            self._last_report = report


            self._history.append(

                report

            )


            self._report_count += 1


            self._generate_count += 1


            self._latency = (

                datetime.utcnow()

                -

                start

            ).total_seconds()



            self._updated_at = datetime.utcnow()



            return report



        except Exception:

            self._error_count += 1

            raise



        finally:

            self._running = False





    def generate_summary(
        self,
        report=None,
    ):
        """
        Generate report summary.
        """

        if report is None:

            report = self._last_report



        if report is None:

            return {}



        dashboard = report.get(

            "dashboard",

            {}

        )



        return {

            "name":
                self._name,


            "widgets":

                len(

                    dashboard.get(

                        "widgets",

                        {}

                    )

                ),


            "charts":

                bool(

                    dashboard.get(

                        "charts"

                    )

                ),


            "timeline":

                bool(

                    dashboard.get(

                        "timeline"

                    )

                ),


            "generated_at":
                datetime.utcnow(),

        }





    def generate_dashboard_report(
        self,
        **kwargs,
    ):
        """
        Generate report directly from dashboard state.
        """

        return self.generate(

            self._dashboard,

            **kwargs,

        )





    def export(
        self,
        format: str = "json",
        **kwargs,
    ):
        """
        Export report.

        Supported:
        - json
        - dict
        """

        if self._last_report is None:

            self.generate()



        if format == "dict":

            return self._last_report



        if format == "json":

            return json.dumps(

                self._last_report,

                default=str,

                **kwargs,

            )



        raise ValueError(

            f"Unsupported format: {format}"

        )





    def save(
        self,
        path: str,
        format: str = "json",
        **kwargs,
    ):
        """
        Save report to file.
        """

        content = self.export(

            format=format,

            **kwargs,

        )


        mode = (

            "w"

            if isinstance(content, str)

            else

            "w"

        )


        with open(

            path,

            mode,

            encoding="utf-8",

        ) as file:

            if isinstance(content, str):

                file.write(

                    content

                )

            else:

                json.dump(

                    content,

                    file,

                    default=str,

                )



        return path





    def load(
        self,
        path: str,
    ):
        """
        Load report from file.
        """

        with open(

            path,

            "r",

            encoding="utf-8",

        ) as file:


            self._last_report = json.load(

                file

            )


        return self._last_report
    # ======================================================
    # Part 3. Report Builders
    # ======================================================


    def build(
        self,
        dashboard_result: dict,
        **kwargs,
    ):
        """
        Build complete report structure.

        Combines all builders.
        """

        return {

            "summary":

                self.build_summary(

                    dashboard_result

                ),


            "dashboard":

                self.build_dashboard(

                    dashboard_result

                ),


            "metrics":

                self.build_metrics(

                    dashboard_result

                ),


            "charts":

                self.build_charts(

                    dashboard_result

                ),


            "timeline":

                self.build_timeline(

                    dashboard_result

                ),


            "widgets":

                self.build_widgets(

                    dashboard_result

                ),


            "generated_at":

                datetime.utcnow(),

        }



    def build_summary(
        self,
        dashboard_result: dict,
    ):
        """
        Build report summary section.
        """

        return {

            "dashboard":

                dashboard_result.get(

                    "dashboard",

                    "unknown"

                ),


            "chart_available":

                "charts"

                in

                dashboard_result,


            "timeline_available":

                "timeline"

                in

                dashboard_result,


            "widget_count":

                len(

                    dashboard_result.get(

                        "widgets",

                        {}

                    )

                ),


            "generated":

                datetime.utcnow(),

        }



    def build_dashboard(
        self,
        dashboard_result: dict,
    ):
        """
        Build dashboard section.
        """

        return {

            "name":

                dashboard_result.get(

                    "dashboard"

                ),


            "timestamp":

                dashboard_result.get(

                    "timestamp"

                ),


            "components":

                [

                    "charts",

                    "timeline",

                    "widgets",

                ],

        }



    def build_metrics(
        self,
        dashboard_result: dict,
    ):
        """
        Extract metric information.
        """

        metrics = {}


        widgets = dashboard_result.get(

            "widgets",

            {}

        )


        for name, widget in widgets.items():

            if (

                widget.get(

                    "metadata",

                    {}

                ).get(

                    "component"

                )

                ==

                "metric"

            ):

                metrics[name] = widget



        return metrics



    def build_charts(
        self,
        dashboard_result: dict,
    ):
        """
        Build chart report section.
        """

        return {

            "enabled":

                bool(

                    dashboard_result.get(

                        "charts"

                    )

                ),


            "data":

                dashboard_result.get(

                    "charts",

                    {}

                ),

        }



    def build_timeline(
        self,
        dashboard_result: dict,
    ):
        """
        Build timeline report section.
        """

        return {

            "enabled":

                bool(

                    dashboard_result.get(

                        "timeline"

                    )

                ),


            "data":

                dashboard_result.get(

                    "timeline",

                    {}

                ),

        }



    def build_widgets(
        self,
        dashboard_result: dict,
    ):
        """
        Build widget report section.
        """

        widgets = dashboard_result.get(

            "widgets",

            {}

        )


        result = {}


        for name, widget in widgets.items():


            result[name] = {

                "type":

                    widget.get(

                        "metadata",

                        {}

                    ).get(

                        "component",

                        "unknown"

                    ),


                "enabled":

                    widget.get(

                        "enabled",

                        True

                    ),

            }


        return result



    def custom_builder(
        self,
        name: str,
        builder: Callable,
    ):
        """
        Register custom report builder.
        """

        if not hasattr(

            self,

            "_builders"

        ):

            self._builders = {}



        self._builders[name] = builder


        return self



    def execute_builder(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        """
        Execute custom builder.
        """

        builder = getattr(

            self,

            "_builders",

            {}

        ).get(

            name

        )


        if builder is None:

            raise KeyError(

                f"Unknown builder: {name}"

            )


        return builder(

            *args,

            **kwargs

        )
    # ======================================================
    # Part 4. Report Registry API
    # ======================================================


    def register_template(
        self,
        name: str,
        template: Any,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register report template.
        """

        with self._lock:

            self._templates[name] = {

                "name":
                    name,

                "template":
                    template,

                "enabled":
                    enabled,

                "metadata":
                    metadata or {},

                "created_at":
                    datetime.utcnow(),

            }


            self._updated_at = datetime.utcnow()


        return self



    def remove_template(
        self,
        name: str,
    ):
        """
        Remove report template.
        """

        with self._lock:

            self._templates.pop(

                name,

                None,

            )


            self._updated_at = datetime.utcnow()


        return self



    def template(
        self,
        name: str,
        default=None,
    ):
        """
        Get registered template.
        """

        return self._templates.get(

            name,

            default,

        )



    def templates(
        self,
    ):
        """
        Return all templates.
        """

        return dict(

            self._templates

        )



    def contains_template(
        self,
        name: str,
    ) -> bool:
        """
        Check template existence.
        """

        return (

            name

            in

            self._templates

        )



    def exists_template(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_template().
        """

        return self.contains_template(

            name

        )



    def enable_template(
        self,
        name: str,
    ):
        """
        Enable report template.
        """

        template = self._templates.get(

            name

        )


        if template is not None:

            template["enabled"] = True

            self._updated_at = datetime.utcnow()


        return self



    def disable_template(
        self,
        name: str,
    ):
        """
        Disable report template.
        """

        template = self._templates.get(

            name

        )


        if template is not None:

            template["enabled"] = False

            self._updated_at = datetime.utcnow()


        return self



    def template_names(
        self,
    ):
        """
        Return template names.
        """

        return list(

            self._templates.keys()

        )



    @property
    def template_count(
        self,
    ):
        """
        Number of registered templates.
        """

        return len(

            self._templates

        )



    def clear_templates(
        self,
    ):
        """
        Remove all report templates.
        """

        with self._lock:

            self._templates.clear()

            self._updated_at = datetime.utcnow()


        return self



    def execute_template(
        self,
        name: str,
        report_data: dict,
        *args,
        **kwargs,
    ):
        """
        Execute report template.
        """

        entry = self._templates.get(

            name

        )


        if entry is None:

            raise KeyError(

                f"Unknown report template: {name}"

            )



        if not entry["enabled"]:

            raise RuntimeError(

                f"Template '{name}' is disabled."

            )



        template = entry["template"]



        if callable(template):

            return template(

                report_data,

                *args,

                **kwargs,

            )



        return template



    def register_builtin_templates(
        self,
    ):
        """
        Register default report templates.
        """



        self.register_template(

            "default",

            self.build,

            metadata={

                "type":

                    "standard"

            },

        )



        self.register_template(

            "summary",

            self.build_summary,

            metadata={

                "type":

                    "summary"

            },

        )



        self.register_template(

            "dashboard",

            self.build_dashboard,

            metadata={

                "type":

                    "dashboard"

            },

        )



        self.register_template(

            "metrics",

            self.build_metrics,

            metadata={

                "type":

                    "metrics"

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
        Enable report engine.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()


        return self



    def disable(
        self,
    ):
        """
        Disable report engine.
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
        Freeze report engine.

        Keeps current state but blocks
        report generation.
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
        Unfreeze report engine.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()


        return self



    def close(
        self,
    ):
        """
        Close report engine.

        Runtime is terminated.
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
        Reopen closed report engine.
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
        Reset report runtime state.

        Keeps:
        - configuration
        - templates
        - dashboard reference

        Clears:
        - history
        - counters
        - last report
        """

        with self._lock:

            self._report_count = 0

            self._generate_count = 0

            self._error_count = 0

            self._latency = 0.0


            self._history.clear()


            self._last_report = None


            self._context.clear()


            self._events.clear()


            self._running = False


            self._updated_at = datetime.utcnow()


        return self



    def clear(
        self,
    ):
        """
        Clear generated report data.

        Keeps:
        - templates
        - dashboard
        - configuration
        """

        with self._lock:

            self._history.clear()


            self._last_report = None


            self._context.clear()


            self._updated_at = datetime.utcnow()


        return self



    def snapshot(
        self,
    ):
        """
        Create runtime snapshot.

        Used for:
        - checkpoint
        - recovery
        - migration
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


                "report_count":

                    self._report_count,


                "generate_count":

                    self._generate_count,


                "error_count":

                    self._error_count,


                "latency":

                    self._latency,


                "history":

                    list(

                        self._history

                    ),


                "last_report":

                    self._last_report,


                "context":

                    dict(

                        self._context

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



            self._report_count = snapshot.get(

                "report_count",

                0,

            )


            self._generate_count = snapshot.get(

                "generate_count",

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



            self._last_report = snapshot.get(

                "last_report"

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
        Clone report engine.

        Creates independent runtime copy.
        """

        cloned = self.__class__(

            name=self._name,

            description=self._description,

            dashboard=self._dashboard,

        )


        cloned._config = dict(

            self._config

        )


        cloned._templates = copy.deepcopy(

            self._templates

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
        Return report engine summary.
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


            "frozen":

                self._frozen,


            "closed":

                self._closed,


            "running":

                self._running,


            "template_count":

                self.template_count,


            "report_count":

                self.report_count,


            "generate_count":

                self.generate_count,


            "error_count":

                self.error_count,


            "uptime":

                self.uptime,


            "latency":

                self.latency,

        }



    def report(
        self,
    ) -> dict:
        """
        Generate full diagnostic report
        of MetricReport engine.
        """

        return {

            "summary":

                self.summary(),



            "configuration":

                dict(

                    self._config

                ),



            "templates":

                self.template_names(),



            "dashboard":

                self._dashboard.summary(),



            "statistics":

                {

                    "reports":

                        self._report_count,


                    "generations":

                        self._generate_count,


                    "errors":

                        self._error_count,


                    "latency":

                        self._latency,

                },



            "runtime":

                {

                    "running":

                        self._running,


                    "history_size":

                        len(

                            self._history

                        ),


                    "has_last_report":

                        self._last_report is not None,

                },



            "metadata":

                {

                    "created_at":

                        self._created_at,


                    "updated_at":

                        self._updated_at,

                },

        }



    def health(
        self,
    ) -> dict:
        """
        Runtime health check.
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



        healthy = (

            self._enabled

            and

            not self._closed

            and

            self._error_count == 0

        )



        return {

            "healthy":

                healthy,


            "state":

                state,


            "reports":

                self._report_count,


            "generations":

                self._generate_count,


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
        Alias for health().
        """

        return self.health()



    # ======================================================
    # Statistics Properties
    # ======================================================


    @property
    def report_count(
        self,
    ) -> int:
        """
        Total generated reports.
        """

        return self._report_count



    @property
    def generate_count(
        self,
    ) -> int:
        """
        Total generate operations.
        """

        return self._generate_count



    @property
    def error_count(
        self,
    ) -> int:
        """
        Total runtime errors.
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

            datetime.utcnow()

            -

            self._created_at

        ).total_seconds()



    @property
    def latency(
        self,
    ) -> float:
        """
        Last report generation latency.
        """

        return self._latency
    # ======================================================
    # Part 8. Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict:
        """
        Serialize MetricReport into dictionary.
        """

        return {

            # --------------------------------------------------
            # Identity
            # --------------------------------------------------

            "id":

                self._id,


            "name":

                self._name,


            "description":

                self._description,


            "version":

                self._version,



            # --------------------------------------------------
            # Lifecycle
            # --------------------------------------------------

            "enabled":

                self._enabled,


            "frozen":

                self._frozen,


            "closed":

                self._closed,



            # --------------------------------------------------
            # Configuration
            # --------------------------------------------------

            "config":

                dict(

                    self._config

                ),



            # --------------------------------------------------
            # Statistics
            # --------------------------------------------------

            "statistics":

                {

                    "report_count":

                        self._report_count,


                    "generate_count":

                        self._generate_count,


                    "error_count":

                        self._error_count,


                    "latency":

                        self._latency,

                },



            # --------------------------------------------------
            # Runtime
            # --------------------------------------------------

            "runtime":

                {

                    "history":

                        list(

                            self._history

                        ),


                    "last_report":

                        self._last_report,


                    "context":

                        dict(

                            self._context

                        ),

                },



            # --------------------------------------------------
            # Templates
            # --------------------------------------------------

            "templates":

                {

                    name:

                        {

                            "enabled":

                                template.get(

                                    "enabled",

                                    True,

                                ),


                            "metadata":

                                template.get(

                                    "metadata",

                                    {},

                                ),

                        }


                    for name, template

                    in self._templates.items()

                },



            # --------------------------------------------------
            # Metadata
            # --------------------------------------------------

            "metadata":

                {

                    "created_at":

                        self._created_at.isoformat(),


                    "updated_at":

                        self._updated_at.isoformat(),

                },

        }



    @classmethod
    def from_dict(
        cls,
        data: dict,
        dashboard=None,
    ):
        """
        Restore MetricReport from dictionary.
        """


        report = cls(

            name=data.get(

                "name",

                "MetricReport",

            ),


            description=data.get(

                "description",

                "",

            ),


            dashboard=dashboard,

        )



        # --------------------------------------------------
        # Lifecycle
        # --------------------------------------------------

        report._enabled = data.get(

            "enabled",

            True,

        )


        report._frozen = data.get(

            "frozen",

            False,

        )


        report._closed = data.get(

            "closed",

            False,

        )



        # --------------------------------------------------
        # Configuration
        # --------------------------------------------------

        report._config.update(

            data.get(

                "config",

                {},

            )

        )



        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        stats = data.get(

            "statistics",

            {},

        )


        report._report_count = stats.get(

            "report_count",

            0,

        )


        report._generate_count = stats.get(

            "generate_count",

            0,

        )


        report._error_count = stats.get(

            "error_count",

            0,

        )


        report._latency = stats.get(

            "latency",

            0.0,

        )



        # --------------------------------------------------
        # Runtime
        # --------------------------------------------------

        runtime = data.get(

            "runtime",

            {},

        )


        report._history = list(

            runtime.get(

                "history",

                [],

            )

        )


        report._last_report = runtime.get(

            "last_report"

        )


        report._context = dict(

            runtime.get(

                "context",

                {},

            )

        )



        # --------------------------------------------------
        # Restore template metadata
        # --------------------------------------------------

        templates = data.get(

            "templates",

            {},

        )


        for name, info in templates.items():

            report._templates[name] = {

                "name":

                    name,


                "template":

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



        report._updated_at = datetime.utcnow()


        return report





    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize MetricReport into JSON.
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
        dashboard=None,
    ):
        """
        Restore MetricReport from JSON.
        """

        return cls.from_dict(

            json.loads(

                data

            ),

            dashboard=dashboard,

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
        dashboard=None,
    ):
        """
        Alias of from_json().
        """

        return cls.from_json(

            data,

            dashboard=dashboard,

        )
    # ======================================================
    # Part 9. Events & Hooks
    # ======================================================


    def before_generate(
        self,
        data=None,
        **kwargs,
    ):
        """
        Hook executed before report generation.
        """

        self.emit(

            "before_generate",

            data=data,

            kwargs=kwargs,

        )

        return self



    def after_generate(
        self,
        report,
    ):
        """
        Hook executed after report generation.
        """

        self.emit(

            "after_generate",

            report=report,

        )

        return self



    def before_builder(
        self,
        builder: str,
        data=None,
        **kwargs,
    ):
        """
        Hook executed before builder execution.
        """

        self.emit(

            "before_builder",

            builder=builder,

            data=data,

            kwargs=kwargs,

        )

        return self



    def after_builder(
        self,
        builder: str,
        result=None,
    ):
        """
        Hook executed after builder execution.
        """

        self.emit(

            "after_builder",

            builder=builder,

            result=result,

        )

        return self



    def add_hook(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Register event hook.
        """

        if not callable(callback):

            raise TypeError(

                "Hook callback must be callable"

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
        Remove event hook.

        If callback is None,
        remove all hooks for event.
        """

        with self._lock:

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
        Emit report event.
        """


        event_data = {

            "event":

                event,


            "payload":

                payload,


            "timestamp":

                datetime.utcnow(),

        }



        self._events.append(

            event_data

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
        Alias for add_hook().
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

            f"templates={self.template_count}, "

            f"reports={self._report_count}, "

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

            f"[templates={self.template_count}, "

            f"reports={self._report_count}]"

        )



    def __len__(
        self,
    ) -> int:
        """
        Return number of report templates.
        """

        return self.template_count



    def __iter__(
        self,
    ):
        """
        Iterate over registered templates.
        """

        return iter(

            self._templates.items()

        )



    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check template existence.
        """

        return (

            name

            in

            self._templates

        )



    def __call__(
        self,
        data=None,
        **kwargs,
    ):
        """
        Callable report engine.

        Equivalent to generate().
        """

        return self.generate(

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