"""
SciOS-NG Metrics Core Manager

Central orchestration layer for metric objects.

Responsibilities:

- Create metrics
- Register metrics
- Update metrics
- Collect values
- Snapshot state
- Debug inspection

"""


from typing import Any, Dict


from .metric import Metric
from .metric_registry import MetricRegistry
from .metric_collector import MetricCollector



class MetricManager:
    """
    Core metric lifecycle manager.

    Example:

        manager = MetricManager()

        manager.create(
            "cpu_usage",
            50
        )

        manager.update(
            "cpu_usage",
            80
        )

        print(
            manager.collect()
        )

    """


    def __init__(
        self,
        registry=None,
        collector=None,
    ):

        self.registry = (
            registry
            if registry
            else MetricRegistry()
        )


        self.collector = (
            collector
            if collector
            else MetricCollector()
        )



    # -------------------------------------------------
    # Creation API
    # -------------------------------------------------

    def create(
        self,
        name: str,
        value: Any = 0,
        **metadata,
    ) -> Metric:

        metric = Metric(
            name=name,
            value=value,
            **metadata,
        )


        self.registry.register(
            metric
        )


        self.collector.register(
            metric
        )


        return metric



    # -------------------------------------------------
    # Query API
    # -------------------------------------------------

    def get(
        self,
        name: str,
    ):

        return self.registry.get(
            name
        )



    def exists(
        self,
        name: str,
    ):

        return self.registry.exists(
            name
        )



    def list(
        self,
    ):

        return self.registry.list()



    # -------------------------------------------------
    # Update API
    # -------------------------------------------------

    def update(
        self,
        name: str,
        value: Any,
    ):

        metric = self.get(
            name
        )


        if metric is None:

            raise KeyError(
                f"Metric not found: {name}"
            )


        metric.update(
            value
        )


        return metric



    # -------------------------------------------------
    # Collection API
    # -------------------------------------------------

    def collect(
        self,
    ) -> Dict:

        return self.collector.collect()



    # -------------------------------------------------
    # Snapshot API
    # -------------------------------------------------

    def snapshot(
        self,
    ):

        return {
            metric.name:
                metric.snapshot()

            for metric
            in self.registry.list()
        }



    # -------------------------------------------------
    # Lifecycle API
    # -------------------------------------------------

    def remove(
        self,
        name: str,
    ):

        self.registry.remove(
            name
        )


        self.collector.remove(
            name
        )



    def clear(
        self,
    ):

        self.registry.clear()
        self.collector.clear()



    # -------------------------------------------------
    # Debug API
    # -------------------------------------------------

    def to_dict(
        self,
    ):

        return {
            "metrics":
                self.collect(),

            "count":
                len(
                    self.registry.list()
                ),
        }