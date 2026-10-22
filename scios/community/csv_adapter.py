"""Local, bounded CSV upload adapter for the Community trial UI.

No changes to the SciOS runtime, governance, or scientific tool contracts.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from scios.application.csv_analysis import CSVAnalysisApplication
from scios.cognitive_core.planner.goal import Goal

MAX_CSV_BYTES = 10 * 1024 * 1024
GOAL = "Analyze the CSV dataset and explain anomalous values."
LIMITATIONS = (
    "The 1.5×IQR rule flags statistical outliers, not measurement errors or "
    "scientific causes. No independent scientific Proof Gate validation is "
    "claimed. Row indices are zero-based; CSV parsing follows pandas defaults."
)


def analyze_csv(raw_bytes: bytes, *, filename: str, query: str) -> dict[str, Any]:
    """Analyze uploaded bytes through the existing application; return a report."""
    if not isinstance(raw_bytes, bytes):
        raise TypeError("CSV content must be bytes.")
    if not raw_bytes or not raw_bytes.strip():
        raise ValueError("CSV file is empty.")
    if len(raw_bytes) > MAX_CSV_BYTES:
        raise ValueError("CSV exceeds the 10 MiB local trial limit.")
    if not isinstance(filename, str) or not filename.lower().endswith(".csv"):
        raise ValueError("Choose a .csv file.")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Enter a research question.")

    checksum = hashlib.sha256(raw_bytes).hexdigest()
    # The application requires a path. Never use the untrusted upload filename.
    with tempfile.TemporaryDirectory(prefix="scios-community-") as directory:
        path = Path(directory) / "input.csv"
        path.write_bytes(raw_bytes)
        application = CSVAnalysisApplication(file_path=str(path))
        answer = application.analyze(goal=Goal(GOAL), query=query.strip())
        if answer["dataset_hash"] != checksum:
            raise RuntimeError("Dataset checksum mismatch; report not generated.")
        record = application.last_provenance_record
        if record is None or application.last_result is None:
            raise RuntimeError("Missing analysis provenance or tool result.")
        evidence = application.last_result.value
        if not isinstance(evidence, dict):
            raise RuntimeError("Invalid evidence payload.")
        operation = record.metadata["operation"]
        report = {
            "report_format": "scios-community-csv-v0.1",
            "dataset": {"filename": Path(filename).name, "sha256": checksum,
                        "size_bytes": len(raw_bytes)},
            "question": query.strip(),
            "analysis_run_id": answer["analysis_run_id"],
            "operation": operation,
            "method": {
                "name": "Interquartile range (IQR)",
                "factor": 1.5,
                "quartiles": "pandas Series.quantile(0.25/0.75) defaults",
                "bounds": "Q1 - 1.5*IQR; Q3 + 1.5*IQR",
            },
            "result": answer,
            "numeric_summary": evidence.get("numeric_summary", {}),
            "limitations": LIMITATIONS,
            "validation_status": "statistical-rule-only; not scientific proof",
        }
        # Reject nonstandard NaN/Infinity JSON instead of emitting invalid JSON.
        json.dumps(report, ensure_ascii=False, allow_nan=False)
        return report


def report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)


def report_markdown(report: dict[str, Any]) -> str:
    result = report["result"]
    lines = [
        "# SciOS Community — CSV Analysis Report",
        "",
        f"**Dataset:** {report['dataset']['filename']}",
        f"**SHA-256:** `{report['dataset']['sha256']}`",
        f"**Analysis Run ID:** `{report['analysis_run_id']}`",
        f"**Question:** {report['question']}",
        f"**Operation:** {report['operation']['name']} v{report['operation']['version']}",
        "",
        "## Method",
        "IQR with Q1/Q3 computed using pandas defaults; lower = Q1 - 1.5×IQR; "
        "upper = Q3 + 1.5×IQR.",
        "",
        "## Dataset",
        f"Rows: {result['rows']}; columns: {result['columns']}.",
        f"Missing values: {json.dumps(result['missing'], ensure_ascii=False)}",
        "",
        "## Results and evidence",
        result["explanation"],
        "",
    ]
    for column, data in result["outliers"].items():
        lines.append(f"### Column: {column} — {data['count']} outlier(s)")
        for item in data["evidence"]:
            lines.append(
                f"- Row {item['index']} (zero-based): value={item['value']}; "
                f"Q1={item['q1']}; Q3={item['q3']}; IQR={item['iqr']}; "
                f"bounds=[{item['lower_bound']}, {item['upper_bound']}]; "
                f"rule={item['rule']}."
            )
    lines += ["", "## Limitations", report["limitations"], "",
              "**Validation:** Statistical rule only; not scientific proof."]
    return "\n".join(lines) + "\n"
