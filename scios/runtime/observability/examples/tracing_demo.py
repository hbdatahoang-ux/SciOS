"""
SciOS-NG Observability
Tracing Demo

Demonstrates:

- TraceSchema
- SpanSchema
- Span lifecycle
- Trace hierarchy
- Attributes
- Tags
- Events
- Serialization
- Diagnostics

"""

from __future__ import annotations


import time
import traceback


from scios.runtime.observability.schemas import (
    TraceSchema,
    SpanSchema,
)



# ============================================================
# Helpers
# ============================================================


def print_section(title: str) -> None:
    """
    Pretty section printer.
    """

    print("\n - tracing_demo.py:43" + "=" * 70)

    print(title)

    print("= - tracing_demo.py:47" * 70)



# ============================================================
# Trace Demo
# ============================================================


def create_trace() -> TraceSchema:
    """
    Create root trace.
    """

    trace = TraceSchema(
        name="scios.reasoning.pipeline",
    )


    trace.set_tag(
        "service",
        "SciOS-NG",
    )


    trace.set_attribute(
        "version",
        "0.3.0",
    )


    trace.set_attribute(
        "environment",
        "development",
    )


    return trace



# ============================================================
# Span Demo
# ============================================================


def execute_span(
    trace: TraceSchema,
    name: str,
    parent_id: str | None = None,
) -> SpanSchema:
    """
    Create and execute span.
    """

    span = SpanSchema(

        trace_id=trace.id,

        name=name,

        parent_span_id=parent_id,
    )


    span.start()


    span.set_tag(
        "component",
        name,
    )


    span.set_attribute(
        "worker",
        "main",
    )


    time.sleep(
        0.01
    )


    span.finish()


    return span



# ============================================================
# Error Span Demo
# ============================================================


def execute_failed_span(
    trace: TraceSchema,
) -> SpanSchema:
    """
    Demonstrate failed span.
    """

    span = SpanSchema(

        trace_id=trace.id,

        name="model.inference",
    )


    span.start()


    try:

        raise RuntimeError(
            "Demo inference failure"
        )


    except Exception as exc:

        span.record_exception(
            exc
        )


        span.fail()



    return span



# ============================================================
# Main Demo
# ============================================================


def main() -> None:

    print_section(
        "SciOS-NG TraceSchema Demo"
    )


    # --------------------------------------------------------
    # Create Trace
    # --------------------------------------------------------

    trace = create_trace()


    print(
        "TRACE CREATED"
    )

    print(
        trace
    )


    # --------------------------------------------------------
    # Root Span
    # --------------------------------------------------------

    root_span = execute_span(
        trace,
        "runtime.execute",
    )


    print_section(
        "ROOT SPAN"
    )


    print(
        root_span
    )



    # --------------------------------------------------------
    # Child Spans
    # --------------------------------------------------------

    planner_span = execute_span(
        trace,

        "planner.execute",

        parent_id=root_span.id,
    )


    tool_span = execute_span(
        trace,

        "tool.execution",

        parent_id=planner_span.id,
    )


    print_section(
        "SPAN TREE"
    )


    print(
        "Root:",
        root_span.id
    )


    print(
        "Planner:",
        planner_span.id
    )


    print(
        "Tool:",
        tool_span.id
    )



    # --------------------------------------------------------
    # Failed Span
    # --------------------------------------------------------

    failed = execute_failed_span(
        trace
    )


    print_section(
        "FAILED SPAN"
    )


    print(
        failed
    )



    # --------------------------------------------------------
    # Trace Complete
    # --------------------------------------------------------

    trace.finish()



    print_section(
        "TRACE RESULT"
    )


    print(
        trace.to_dict()
    )



    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    print_section(
        "TRACE JSON"
    )


    print(
        trace.to_json()
    )



    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------

    print_section(
        "TRACE DIAGNOSTICS"
    )


    print(
        trace.diagnostics()
    )



    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print_section(
        "TRACE VALIDATION"
    )


    print(
        "VALID:",
        trace.is_valid()
    )



# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":

    main()