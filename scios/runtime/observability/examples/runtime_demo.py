"""
SciOS-NG Observability
Runtime Event Demo

Demonstrates:

- EventSchema
- Event lifecycle
- Runtime context
- Payload handling
- Tags / Attributes
- Dispatch
- Snapshot / Restore
- Serialization
- Diagnostics

"""

from __future__ import annotations


import time
import uuid


from scios.runtime.observability.schemas import (
    EventSchema,
    EventContext,
    EventMetadata,
    EventType,
    EventLevel,
    EventStatus,
    EventSource,
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

    print("\n - runtime_demo.py:50" + "=" * 70)

    print(title)

    print("= - runtime_demo.py:54" * 70)



# ============================================================
# Mock Runtime Dispatcher
# ============================================================


class RuntimeDispatcher:
    """
    Minimal dispatcher simulation.

    Real implementation:
        scios.shared.event_bus.EventBus
    """

    def dispatch(
        self,
        event: EventSchema,
    ) -> None:

        print(
            "DISPATCH EVENT:"
        )

        print(
            event
        )



# ============================================================
# Event Factory
# ============================================================


def create_runtime_event() -> EventSchema:
    """
    Create runtime execution event.
    """

    context = EventContext(

        trace_id=str(
            uuid.uuid4()
        ),

        span_id=str(
            uuid.uuid4()
        ),

        runtime_id="runtime-demo-001",

        component="execution-engine",

        service="scios-runtime",

        environment="development",
    )


    metadata = EventMetadata(

        source="runtime",

        version="0.3.0",
    )


    event = EventSchema(

        type=EventType.EXECUTION,

        level=EventLevel.INFO,

        name="runtime.pipeline.start",

        message="Execution pipeline started",

        source=EventSource.RUNTIME,

        context=context,

        metadata=metadata,
    )


    return event



# ============================================================
# Payload Demo
# ============================================================


def payload_demo(
    event: EventSchema,
) -> None:
    """
    Demonstrate event payload.
    """

    print_section(
        "PAYLOAD"
    )


    event.set_payload(
        "pipeline",
        "reasoning",
    )


    event.set_payload(
        "stage",
        "planner",
    )


    event.update_payload(
        {
            "input_tokens": 512,

            "model": "SciOS-Agent",

            "latency_ms": 25.6,
        }
    )


    print(
        event.payload
    )



# ============================================================
# Tags & Attributes Demo
# ============================================================


def metadata_demo(
    event: EventSchema,
) -> None:
    """
    Demonstrate tags and attributes.
    """

    print_section(
        "TAGS & ATTRIBUTES"
    )


    event.set_tag(
        "component",
        "kernel",
    )


    event.set_tag(
        "priority",
        "high",
    )


    event.set_attribute(
        "worker",
        "main-thread",
    )


    event.set_attribute(
        "memory_mb",
        128,
    )


    print(
        "Tags:"
    )

    print(
        event.tags
    )


    print()


    print(
        "Attributes:"
    )


    print(
        event.attributes
    )



# ============================================================
# Lifecycle Demo
# ============================================================


def lifecycle_demo(
    event: EventSchema,
) -> None:
    """
    Demonstrate lifecycle state changes.
    """

    print_section(
        "LIFECYCLE"
    )


    print(
        "Initial:",
        event.status
    )


    event.activate()


    print(
        "Activated:",
        event.status
    )


    time.sleep(
        0.01
    )


    event.complete()


    print(
        "Completed:",
        event.status
    )



# ============================================================
# Dispatch Demo
# ============================================================


def dispatch_demo(
    event: EventSchema,
) -> None:
    """
    Demonstrate dispatch.
    """

    print_section(
        "DISPATCH"
    )


    dispatcher = RuntimeDispatcher()


    event.dispatch(
        dispatcher
    )



# ============================================================
# Snapshot Demo
# ============================================================


def snapshot_demo(
    event: EventSchema,
) -> None:
    """
    Demonstrate checkpoint.
    """

    print_section(
        "SNAPSHOT"
    )


    snapshot = event.snapshot()


    print(
        "Snapshot:"
    )


    print(
        snapshot
    )


    clone = event.clone()


    print()

    print(
        "Clone:"
    )


    print(
        clone
    )


    event.reset()


    print()

    print(
        "After reset:"
    )


    print(
        event
    )


    event.restore(
        snapshot
    )


    print()

    print(
        "After restore:"
    )


    print(
        event
    )



# ============================================================
# Serialization Demo
# ============================================================


def serialization_demo(
    event: EventSchema,
) -> None:
    """
    Demonstrate serialization.
    """

    print_section(
        "SERIALIZATION"
    )


    data = event.to_dict()


    print(
        "DICT:"
    )


    print(
        data
    )


    print()


    json_data = event.to_json()


    print(
        "JSON:"
    )


    print(
        json_data
    )


    restored = EventSchema.from_json(
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
        "SciOS-NG Runtime Event Demo"
    )


    # --------------------------------------------------------
    # Create Event
    # --------------------------------------------------------

    event = create_runtime_event()


    print(
        "Created Event:"
    )


    print(
        event
    )


    # --------------------------------------------------------
    # Payload
    # --------------------------------------------------------

    payload_demo(
        event
    )


    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata_demo(
        event
    )


    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------

    lifecycle_demo(
        event
    )


    # --------------------------------------------------------
    # Dispatch
    # --------------------------------------------------------

    dispatch_demo(
        event
    )


    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    snapshot_demo(
        event
    )


    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    serialization_demo(
        event
    )


    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------

    print_section(
        "DIAGNOSTICS"
    )


    print(
        event.diagnostics()
    )


    print_section(
        "VALIDATION"
    )


    print(
        "Valid:",
        event.is_valid()
    )



# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":

    main()