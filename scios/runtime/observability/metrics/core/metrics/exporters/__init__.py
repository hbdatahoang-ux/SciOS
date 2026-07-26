"""
SciOS-NG Metrics Exporters

Supported exporters:

- JSONExporter
- PrometheusExporter
- OpenTelemetryExporter
"""


from .json_exporter import JSONExporter


try:
    from .prometheus import PrometheusExporter
except ImportError:
    PrometheusExporter = None



try:
    from .opentelemetry import OpenTelemetryExporter
except ImportError:
    OpenTelemetryExporter = None



__version__ = "0.1.0"



class ExporterRegistry:
    """
    Registry for metric exporters.
    """


    def __init__(self):

        self._exporters = {}



    def register(
        self,
        name: str,
        exporter,
    ):

        self._exporters[name] = exporter



    def unregister(
        self,
        name: str,
    ):

        self._exporters.pop(
            name,
            None
        )



    def get(
        self,
        name: str,
    ):

        return self._exporters.get(
            name
        )



    def available(
        self,
    ):

        return list(
            self._exporters.keys()
        )



    def clear(
        self,
    ):

        self._exporters.clear()



default_registry = ExporterRegistry()



default_registry.register(
    "json",
    JSONExporter
)



if PrometheusExporter:

    default_registry.register(
        "prometheus",
        PrometheusExporter
    )



if OpenTelemetryExporter:

    default_registry.register(
        "opentelemetry",
        OpenTelemetryExporter
    )



def create_exporter(
    name: str,
    **kwargs,
):
    """
    Create exporter instance.
    """

    exporter_cls = (
        default_registry.get(
            name
        )
    )


    if exporter_cls is None:

        raise ValueError(
            f"Unknown exporter: {name}"
        )


    return exporter_cls(
        **kwargs
    )



__all__ = [

    "JSONExporter",

    "PrometheusExporter",

    "OpenTelemetryExporter",

    "ExporterRegistry",

    "default_registry",

    "create_exporter",

]