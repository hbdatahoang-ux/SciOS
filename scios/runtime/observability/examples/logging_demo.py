"""
SciOS-NG Observability
Logging Demo

Demonstrates:

- LogSchema creation
- Log levels
- Runtime logging lifecycle
- Tags
- Attributes
- Exception management
- Metadata
- Serialization
- Snapshot / Restore
- Diagnostics

"""

from __future__ import annotations


import time
import traceback


from scios.runtime.observability.schemas import (
    LogSchema,
    LogLevel,
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

    print("\n - logging_demo.py:46" + "=" * 70)

    print(title)

    print("= - logging_demo.py:50" * 70)



# ============================================================
# Logger Factory
# ============================================================


def create_logger() -> LogSchema:
    """
    Create base runtime log object.
    """

    log = LogSchema(

        message="SciOS Runtime initialized",

        logger="SciOS.Runtime",

        module="runtime.engine",

        function="bootstrap",
    )


    log.info()


    log.set_tag(
        "service",
        "SciOS-NG",
    )


    log.set_tag(
        "component",
        "kernel",
    )


    log.set_attribute(
        "environment",
        "development",
    )


    log.set_attribute(
        "version",
        "0.3.0",
    )


    log.update_metadata(
        {
            "node":
                "worker-01",

            "region":
                "local",
        }
    )


    return log



# ============================================================
# Log Levels Demo
# ============================================================


def level_demo(
    log: LogSchema,
) -> None:
    """
    Demonstrate log levels.
    """

    print_section(
        "LOG LEVELS"
    )


    logs = [

        log.debug(
            "Debug information"
        ),

        log.info(
            "Runtime started"
        ),

        log.warning(
            "High memory usage"
        ),

        log.error(
            "Recoverable error"
        ),

        log.critical(
            "Critical system state"
        ),
    ]


    for item in logs:

        print(
            item
        )



# ============================================================
# Exception Demo
# ============================================================


def exception_demo(
    log: LogSchema,
) -> None:
    """
    Demonstrate exception tracking.
    """

    print_section(
        "EXCEPTION MANAGEMENT"
    )


    try:

        raise RuntimeError(
            "Demo runtime failure"
        )


    except Exception as exc:

        log.attach_exception(
            exc
        )


    print(
        "Has exception:",
        log.has_exception()
    )


    print()

    print(
        "Exception type:"
    )


    print(
        log.exception_type()
    )


    print()

    print(
        "Exception message:"
    )


    print(
        log.exception_message()
    )


    print()

    print(
        "Stack trace:"
    )


    print(
        log.stack_trace()
    )



# ============================================================
# Metadata Demo
# ============================================================


def metadata_demo(
    log: LogSchema,
) -> None:
    """
    Demonstrate metadata manipulation.
    """

    print_section(
        "TAGS & ATTRIBUTES"
    )


    print(
        "Tags:"
    )


    print(
        log.tags
    )


    print()


    print(
        "Attributes:"
    )


    print(
        log.attributes
    )



# ============================================================
# Snapshot Demo
# ============================================================


def snapshot_demo(
    log: LogSchema,
) -> None:
    """
    Demonstrate snapshot and restore.
    """

    print_section(
        "SNAPSHOT"
    )


    snapshot = log.snapshot()


    print(
        snapshot
    )


    log.reset()


    print()

    print(
        "After reset:"
    )


    print(
        log
    )


    log.restore(
        snapshot
    )


    print()

    print(
        "After restore:"
    )


    print(
        log
    )



# ============================================================
# Serialization Demo
# ============================================================


def serialization_demo(
    log: LogSchema,
) -> None:
    """
    Demonstrate serialization.
    """

    print_section(
        "SERIALIZATION"
    )


    data = log.to_dict()


    print(
        "DICT:"
    )


    print(
        data
    )


    print()


    json_data = log.to_json()


    print(
        "JSON:"
    )


    print(
        json_data
    )


    restored = LogSchema.from_json(
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
        "SciOS-NG LogSchema Demo"
    )


    # --------------------------------------------------------
    # Create Logger
    # --------------------------------------------------------

    log = create_logger()


    print(
        "Created Log:"
    )


    print(
        log
    )


    # --------------------------------------------------------
    # Levels
    # --------------------------------------------------------

    level_demo(
        log
    )


    # --------------------------------------------------------
    # Exception
    # --------------------------------------------------------

    exception_demo(
        log
    )


    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata_demo(
        log
    )


    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    print_section(
        "UPDATE"
    )


    log.update(
        message="Runtime worker completed",
    )


    log.touch()


    print(
        log
    )


    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    snapshot_demo(
        log
    )


    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    serialization_demo(
        log
    )


    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------

    print_section(
        "DIAGNOSTICS"
    )


    print(
        log.diagnostics()
    )


    print_section(
        "VALIDATION"
    )


    print(
        "Valid:",
        log.validate()
    )



# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":

    main()