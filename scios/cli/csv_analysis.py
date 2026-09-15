"""CLI entry point for CSV anomaly analysis."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from scios.application.csv_analysis import CSVAnalysisApplication
from scios.cognitive_core.planner import Goal


DEFAULT_GOAL = "Analyze the CSV dataset and explain anomalous values."


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a CSV dataset and explain anomalous values."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the CSV file.",
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Question about the CSV dataset.",
    )
    return parser


def _render_answer(answer: dict[str, object]) -> None:
    print("SciOS CSV Analysis")
    print("==================")
    print()
    print("Dataset")
    print(f"  Rows: {answer['rows']}")
    print(f"  Columns: {answer['columns']}")
    print(f"  Columns: {', '.join(answer['column_names'])}")
    print()
    print("Missing values")

    missing = answer["missing"]
    for column, count in missing.items():
        print(f"  {column}: {count}")

    print()
    print("Anomalies")

    outliers = answer["outliers"]
    anomaly_count = 0

    for column, data in outliers.items():
        count = data["count"]
        anomaly_count += count

        if count == 0:
            continue

        print(f"  {column}")

        for evidence in data["evidence"]:
            print(f"    row: {evidence['index']}")
            print(f"    value: {evidence['value']}")
            print(f"    rule: {evidence['rule']}")
            print(
                "    range: "
                f"[{evidence['lower_bound']}, {evidence['upper_bound']}]"
            )

    print()
    print("Reasoning")

    reasoning = answer["reasoning"]
    for index, conclusion in enumerate(reasoning, start=1):
        print(f"  {index}.")
        print(f"     column: {conclusion['column']}")
        print(f"     row: {conclusion['index']}")
        print(f"     value: {conclusion['value']}")
        print(f"     outlier: {conclusion['is_outlier']}")
        print(f"     evidence: {conclusion['evidence']['rule']}")

    print()
    print("Conclusion")
    print(f"  {anomaly_count} anomalous value(s) detected.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    application = CSVAnalysisApplication(file_path=args.file)
    goal = Goal(DEFAULT_GOAL)

    answer = application.analyze(
        goal=goal,
        query=args.query,
    )

    _render_answer(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
