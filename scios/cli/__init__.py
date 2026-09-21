"""SciOS command-line entry points."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from scios import SciOS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scios",
        description="Scientific Cognitive Operating System.",
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task to execute.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    cli_args = list(sys.argv[1:] if argv is None else argv)

    if cli_args and cli_args[0] == "csv-analysis":
        from scios.cli.csv_analysis import main as csv_analysis_main

        return csv_analysis_main(cli_args[1:])

    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if args.task is None:
        parser.print_help()
        return 0

    os = SciOS()

    try:
        if not os.boot():
            return 1

        result = os.run(args.task)
        print(result)

        return 0 if getattr(result, "status", None) == "success" else 1

    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    finally:
        try:
            os.shutdown()
        except Exception:
            pass


__all__ = ["main"]
