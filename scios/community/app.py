"""Streamlit entry point: streamlit run scios/community/app.py"""
from __future__ import annotations

import streamlit as st

from scios.community.csv_adapter import (
    MAX_CSV_BYTES, analyze_csv, report_json, report_markdown,
)

st.set_page_config(page_title="SciOS Community", page_icon="🔬")
st.title("SciOS Community — CSV Analysis")
st.caption("Local deterministic IQR analysis; not scientific proof.")

uploaded = st.file_uploader("1. Choose a CSV file", type=["csv"])
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
    st.write(answer["explanation"])
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
