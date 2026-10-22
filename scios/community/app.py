"""Streamlit entry point: streamlit run scios/community/app.py"""
from __future__ import annotations

import hashlib

import streamlit as st

from scios.community.visualization import chart_data

from scios.community.csv_adapter import (
    MAX_CSV_BYTES, analyze_csv, report_json, report_markdown,
)

st.set_page_config(page_title="SciOS Community", page_icon="🔬")
st.title("SciOS Community — CSV Analysis")
st.caption("Local deterministic IQR analysis; not scientific proof.")

uploaded = st.file_uploader("1. Choose a CSV file", type=["csv"], max_upload_size=10)
query = st.text_area(
    "2. Ask a research question",
    value="Which numeric values are anomalous, and what evidence supports them?",
)
if "community_report" not in st.session_state:
    st.session_state.community_report = None

if st.button("3. Analyze", type="primary"):
    st.session_state.community_report = None
    if uploaded is None:
        st.warning("Choose a CSV file first.")
    elif uploaded.size > MAX_CSV_BYTES:
        st.error("CSV exceeds the 10 MiB local trial limit.")
    else:
        try:
            with st.spinner("Analyzing locally…"):
                st.session_state.community_report = analyze_csv(
                    uploaded.getvalue(), filename=uploaded.name, query=query
                )
        except (ValueError, RuntimeError, OSError, UnicodeError) as exc:
            st.error(f"Analysis could not be completed: {exc}")
        except Exception:
            st.error("Analysis failed unexpectedly. No report was generated.")

report = st.session_state.community_report
if report is not None:
    answer = report["result"]
    st.subheader("4. Results and evidence")
    a, b = st.columns(2)
    a.metric("Rows", answer["rows"])
    b.metric("Columns", answer["columns"])
    counts = {name: info["count"] for name, info in answer["outliers"].items()}
    distinct_rows = set()
    for info in answer["outliers"].values():
        distinct_rows.update(info["indices"])
    st.success(
        f"{sum(counts.values())} outlier values across "
        f"{len(distinct_rows)} distinct rows (IQR rule)."
    )
    st.bar_chart(
        {"column": list(counts), "outliers": list(counts.values())},
        x="column", y="outliers",
    )
    with st.expander("Full deterministic explanation"):
        st.write(answer["explanation"])

    st.markdown("#### Distribution and IQR thresholds")
    numeric_columns = list(answer["outliers"])
    if numeric_columns and uploaded is not None and (
        hashlib.sha256(uploaded.getvalue()).hexdigest()
        == report["dataset"]["sha256"]
    ):
        chosen = st.selectbox("Numeric column", numeric_columns)
        try:
            histogram, series, outlier_table = chart_data(
                uploaded.getvalue(), report, chosen
            )
            if histogram.empty:
                st.info("No finite numeric observations to chart.")
            else:
                st.caption("Histogram of numeric values (counts by bin center).")
                st.bar_chart(histogram.set_index("bin_center"))
                if outlier_table.empty:
                    st.info(
                        "No outliers in this column. IQR thresholds are not "
                        "stored in the v0.1 evidence for zero-outlier columns."
                    )
                    st.line_chart(series[["value"]])
                else:
                    st.caption(
                        "Value by zero-based CSV row; horizontal lines are "
                        "the IQR bounds from SciOS evidence."
                    )
                    st.line_chart(series[["value", "lower_bound", "upper_bound"]])
                    st.dataframe(outlier_table, use_container_width=True)
        except (ValueError, TypeError) as exc:
            st.warning(f"Visualization unavailable: {exc}")
    else:
        st.info("Select and analyze the same CSV to view its distribution.")

    st.write("Missing values", answer["missing"])
    st.write("IQR outlier evidence (zero-based row indices)")
    for column, data in answer["outliers"].items():
        with st.expander(f"{column}: {data['count']} outlier(s)", expanded=bool(data["count"])):
            if data["evidence"]:
                st.dataframe(data["evidence"], use_container_width=True)
            else:
                st.write("No outliers detected by this rule.")
    st.caption(f"SHA-256: {report['dataset']['sha256']}")
    st.caption(f"Analysis Run ID: {report['analysis_run_id']}")
    st.warning(report["limitations"])
    st.subheader("5. Export a verifiable report")
    st.download_button(
        "Download JSON", report_json(report), "scios_csv_report.json",
        mime="application/json",
    )
    st.download_button(
        "Download Markdown", report_markdown(report), "scios_csv_report.md",
        mime="text/markdown",
    )
