"""
SciOS Command Line Interface
"""

from __future__ import annotations

import argparse
import json
import sys

from scios.api.scios import SciOS
from scios.shared.constants import (
    EXIT_SUCCESS,
    EXIT_FAILURE,
)
from scios.shared.exceptions import SciOSError
from scios.shared.logger import (
    configure_logging,
    get_logger,
)

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """
    Build CLI parser.
    """

    parser = argparse.ArgumentParser(
        prog="scios",
        description="SciOS AI Operating System",
    )

    parser.add_argument(
        "task",
        nargs="?",
        help="Task description.",
    )

    parser.add_argument(
        "--config",
        help="Configuration file.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )

    return parser


def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    configure_logging()

    try:

        scios = SciOS(
            config=args.config,
        )

        result = scios.run(
            args.task,
        )

        if args.json:

            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

        else:

            print(result)

        return EXIT_SUCCESS

    except SciOSError as exc:

        logger.error(str(exc))

        return EXIT_FAILURE

    except KeyboardInterrupt:

        logger.warning("Interrupted by user.")

        return EXIT_FAILURE


if __name__ == "__main__":

    sys.exit(main())