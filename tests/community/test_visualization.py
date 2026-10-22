"""Chart data regression tests; charts must reflect existing evidence."""
import pytest

from scios.community.csv_adapter import analyze_csv
from scios.community.visualization import chart_data

CSV = b"value,other\n10,1\n11,1\n12,1\n13,1\n14,1\n100,1\n"


def test_histogram_bounds_and_outlier_rows():
    report = analyze_csv(CSV, filename="sample.csv", query="Find outliers")
    histogram, series, outliers = chart_data(CSV, report, "value")
    evidence = report["result"]["outliers"]["value"]["evidence"][0]
    assert histogram["count"].sum() == 6
    assert len(series) == 6
    assert outliers["row_index"].tolist() == [5]
    assert series["upper_bound"].iloc[0] == evidence["upper_bound"]
    assert series["lower_bound"].iloc[0] == evidence["lower_bound"]


def test_zero_outliers_no_invented_thresholds():
    report = analyze_csv(CSV, filename="sample.csv", query="Find outliers")
    histogram, series, outliers = chart_data(CSV, report, "other")
    assert histogram["count"].sum() == 6
    assert outliers.empty
    assert series["upper_bound"].isna().all()


def test_checksum_mismatch_is_rejected():
    report = analyze_csv(CSV, filename="sample.csv", query="Find outliers")
    with pytest.raises(ValueError, match="differs"):
        chart_data(CSV + b"\n", report, "value")


def test_unknown_column_is_rejected():
    report = analyze_csv(CSV, filename="sample.csv", query="Find outliers")
    with pytest.raises(ValueError, match="not part"):
        chart_data(CSV, report, "galaxy")
