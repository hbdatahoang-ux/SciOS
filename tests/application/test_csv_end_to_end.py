from __future__ import annotations

import pandas as pd

from scios.application.csv_analysis import CSVAnalysisApplication
from scios.cognitive_core.planner.goal import Goal


def test_csv_product_vertical_slice_end_to_end(tmp_path) -> None:
    csv_path = tmp_path / "dataset.csv"

    dataframe = pd.DataFrame(
        {
            "value": [10, 11, 12, 13, 14, 100],
        }
    )
    dataframe.to_csv(csv_path, index=False)

    application = CSVAnalysisApplication(
        file_path=str(csv_path),
    )

    goal = Goal(
        "Analyze the CSV dataset and explain anomalous values.",
    )

    answer = application.analyze(
        goal=goal,
        query="Why is value 100 an anomaly?",
    )

    assert answer["goal"] == goal.description

    assert answer["rows"] == 6
    assert answer["columns"] == 1
    assert answer["column_names"] == ["value"]

    outlier = answer["outliers"]["value"]

    assert outlier["count"] == 1
    assert outlier["indices"] == [5]

    assert len(answer["reasoning"]) == 1

    conclusion = answer["reasoning"][0]

    assert conclusion["column"] == "value"
    assert conclusion["index"] == 5
    assert conclusion["value"] == 100.0
    assert conclusion["is_outlier"] is True

    assert conclusion["evidence"]["rule"] == "IQR"

def test_analysis_creates_analysis_run_id(tmp_path):
    from scios.application.csv_analysis import CSVAnalysisApplication
    from scios.cognitive_core.planner.goal import Goal

    path = tmp_path / "data.csv"
    path.write_text(
        "value\n10\n20\n30\n",
        encoding="utf-8",
    )

    application = CSVAnalysisApplication(
        file_path=str(path),
    )

    assert application.last_analysis_run_id is None

    application.analyze(
        goal=Goal("Analyze CSV dataset"),
        query="Analyze the dataset for anomalies.",
    )

    first_run_id = application.last_analysis_run_id

    assert isinstance(first_run_id, str)
    assert len(first_run_id) == 36

    application.analyze(
        goal=Goal("Analyze CSV dataset"),
        query="Analyze the dataset for anomalies.",
    )

    second_run_id = application.last_analysis_run_id

    assert isinstance(second_run_id, str)
    assert len(second_run_id) == 36
    assert second_run_id != first_run_id

def test_csv_analysis_exposes_provenance_contract(tmp_path):
    import hashlib

    path = tmp_path / "data.csv"
    path.write_bytes(
        b"value\n10\n20\n30\n100\n",
    )

    application = CSVAnalysisApplication(
        file_path=str(path),
    )

    goal = Goal("Analyze CSV dataset")
    query = "Analyze the dataset for anomalies."

    answer = application.analyze(
        goal=goal,
        query=query,
    )

    record = application.last_provenance_record
    lineage = application.last_provenance_lineage

    assert record is not None
    assert lineage is not None

    assert application.last_analysis_run_id == record.id
    assert record.entity_type == "csv_analysis"
    assert record.parent_ids == ()

    expected_hash = hashlib.sha256(path.read_bytes()).hexdigest()

    assert record.metadata["analysis_run_id"] == record.id
    assert record.metadata["dataset_hash"] == expected_hash
    assert record.metadata["question"] == query

    assert record.metadata["operation"] == {
        "name": "csv_analysis",
        "version": "0.1.0",
    }

    assert record.metadata["parameters"] == {
        "file_path": str(path),
    }

    assert record.metadata["evidence"] == application.last_result.value
    assert record.metadata["reasoning"] == answer["reasoning"]
    assert record.metadata["answer"] == answer

    assert lineage.get(record.id) is record



def test_csv_analysis_is_reproducible_for_same_inputs(tmp_path) -> None:
    csv_path = tmp_path / "dataset.csv"

    csv_path.write_text(
        "value\n10\n11\n12\n13\n14\n100\n",
        encoding="utf-8",
    )

    goal = Goal(
        "Analyze the CSV dataset and explain anomalous values.",
    )
    query = "Why is value 100 an anomaly?"

    application = CSVAnalysisApplication(
        file_path=str(csv_path),
    )

    first_answer = application.analyze(
        goal=goal,
        query=query,
    )
    first_record = application.last_provenance_record

    second_answer = application.analyze(
        goal=goal,
        query=query,
    )
    second_record = application.last_provenance_record

    assert first_record is not None
    assert second_record is not None

    # Analytical output is reproducible.
    assert second_answer == first_answer

    # Dataset identity is reproducible.
    assert (
        second_record.metadata["dataset_hash"]
        == first_record.metadata["dataset_hash"]
    )

    # The recorded execution contract is reproducible.
    assert (
        second_record.metadata["question"]
        == first_record.metadata["question"]
        == query
    )
    assert (
        second_record.metadata["operation"]
        == first_record.metadata["operation"]
    )
    assert (
        second_record.metadata["parameters"]
        == first_record.metadata["parameters"]
    )
    assert second_record.metadata["plan"] == first_record.metadata["plan"]
    assert second_record.metadata["evidence"] == first_record.metadata["evidence"]
    assert second_record.metadata["reasoning"] == first_record.metadata["reasoning"]
    assert second_record.metadata["answer"] == first_record.metadata["answer"]

    # Run identity is intentionally unique per invocation.
    assert second_record.id != first_record.id
    assert (
        second_record.metadata["analysis_run_id"]
        != first_record.metadata["analysis_run_id"]
    )

    # Timestamps are execution metadata, not analytical output.
    assert second_record.created_at != first_record.created_at
