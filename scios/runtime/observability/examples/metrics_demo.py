"""
SciOS-NG Observability
Metrics Demo

Demonstrates:

- MetricSchema creation
- Metric updates
- Aggregation
- Tags
- Attributes
- Snapshot / Restore
- Serialization
- Diagnostics

"""

from __future__ import annotations


import random
import time


from scios.runtime.observability.schemas import (
    MetricSchema,
)



# ============================================================
# Helpers
# ============================================================


def print_section(
    title: str,
) -> None:
    """
    Pretty console section.
    """

    print("\n - metrics_demo.py:43" + "=" * 70)

    print(title)

    print("= - metrics_demo.py:47" * 70)



# ============================================================
# Metric Factory
# ============================================================


def create_metric() -> MetricSchema:
    """
    Create runtime metric.
    """

    metric = MetricSchema(

        name="runtime.execution.latency",

        value=0.0,

        unit="ms",
    )


    metric.set_tag(
        "service",
        "SciOS-NG",
    )


    metric.set_tag(
        "component",
        "runtime-engine",
    )


    metric.set_attribute(
        "environment",
        "development",
    )


    metric.set_attribute(
        "version",
        "0.3.0",
    )


    return metric



# ============================================================
# Update Simulation
# ============================================================


def simulate_runtime(
    metric: MetricSchema,
    samples: int = 10,
) -> None:
    """
    Simulate runtime measurements.
    """

    for index in range(samples):

        latency = random.uniform(
            10.0,
            100.0,
        )


        metric.update(
            latency
        )


        print(
            f"sample={index + 1:02d}",
            f"value={latency:.2f} ms",
        )


        time.sleep(
            0.01
        )



# ============================================================
# Aggregation Demo
# ============================================================


def show_statistics(
    metric: MetricSchema,
) -> None:
    """
    Display metric statistics.
    """

    print_section(
        "METRIC STATISTICS"
    )


    print(
        "Diagnostics:"
    )


    print(
        metric.diagnostics()
    )


    print()


    print(
        "Summary:"
    )


    print(
        metric.summary()
    )



# ============================================================
# Snapshot Demo
# ============================================================


def snapshot_demo(
    metric: MetricSchema,
) -> None:
    """
    Demonstrate snapshot and restore.
    """

    print_section(
        "SNAPSHOT"
    )


    snapshot = metric.snapshot()


    print(
        snapshot
    )


    metric.reset()


    print()

    print(
        "After reset:"
    )


    print(
        metric
    )


    metric.restore(
        snapshot
    )


    print()

    print(
        "After restore:"
    )


    print(
        metric
    )



# ============================================================
# Serialization Demo
# ============================================================


def serialization_demo(
    metric: MetricSchema,
) -> None:
    """
    Demonstrate serialization.
    """

    print_section(
        "SERIALIZATION"
    )


    data = metric.to_dict()


    print(
        "DICT:"
    )


    print(
        data
    )


    print()


    json_data = metric.to_json()


    print(
        "JSON:"
    )


    print(
        json_data
    )


    restored = MetricSchema.from_json(
        json_data
    )


    print()


    print(
        "RESTORED:"
    )


    print(
        restored
    )



# ============================================================
# Main Demo
# ============================================================


def main() -> None:

    print_section(
        "SciOS-NG MetricSchema Demo"
    )


    # --------------------------------------------------------
    # Create Metric
    # --------------------------------------------------------

    metric = create_metric()


    print(
        "Created Metric:"
    )


    print(
        metric
    )


    # --------------------------------------------------------
    # Runtime Update
    # --------------------------------------------------------

    print_section(
        "RUNTIME SAMPLING"
    )


    simulate_runtime(
        metric,
        samples=10,
    )


    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    show_statistics(
        metric
    )


    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    snapshot_demo(
        metric
    )


    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    serialization_demo(
        metric
    )


    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print_section(
        "VALIDATION"
    )


    print(
        "Valid:",
        metric.is_valid()
    )


    # --------------------------------------------------------
    # Runtime statistics
    # --------------------------------------------------------

    print_section(
        "RUNTIME STATISTICS"
    )


    print(
        metric.runtime_statistics()
    )



# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":

    main()