"""
SciOS CLI Commands
"""

from __future__ import annotations

from typing import Any

from scios.api.scios import SciOS


def run_command(args) -> Any:
    """
    Execute a reasoning task.
    """
    system = SciOS(config=args.config)

    return system.run(args.task)


def kernel_status(args) -> dict:
    """
    Show kernel status.
    """
    system = SciOS(config=args.config)

    return system.kernel.status()


def kernel_boot(args) -> dict:
    """
    Boot the SciOS kernel.
    """
    system = SciOS(config=args.config)

    system.kernel.boot()

    return {
        "status": "booted",
    }


def kernel_shutdown(args) -> dict:
    """
    Shutdown the SciOS kernel.
    """
    system = SciOS(config=args.config)

    system.kernel.shutdown()

    return {
        "status": "stopped",
    }


def version_command(args) -> dict:
    """
    Show SciOS version.
    """
    system = SciOS(config=args.config)

    return {
        "name": system.config.app_name,
        "version": system.config.version,
    }


#
# Command Registry
#

COMMANDS = {
    "run": run_command,
    "kernel-status": kernel_status,
    "kernel-boot": kernel_boot,
    "kernel-shutdown": kernel_shutdown,
    "version": version_command,
}