# SciOS Community CSV v0.1.1 — external trial

**Status:** Community pilot; local statistical IQR only, **not scientific proof**.
Python 3.11+ required. No scientific Proof Gate validation is claimed.

## Install from the ZIP

Extract `SciOS-Community-v0.1.1-source.zip`, open a terminal in the extracted
`SciOS-Community-v0.1.1` directory, then run:

```powershell
python -m pip install -e ".[community]"
python -m streamlit run scios/community/app.py
```

Open http://localhost:8501 on the same computer. The default UI and application
limit is 10 MiB per CSV. Do not expose the network URL publicly; this is a local
trial, not a hosted authenticated service.

## Five-step trial

1. Upload a CSV containing numeric data (up to 10 MiB).
2. Ask a research question.
3. Select **Analyze**.
4. Inspect the IQR outlier counts, histogram, value-by-row chart, threshold
   lines (where evidence exists), and selected-column outlier table.
5. Download the JSON and Markdown reports and compare the SHA-256 and
   Analysis Run ID.

Outlier counts are **values**, not necessarily unique rows. For columns with
zero outliers, v0.1 evidence contains no bounds, so the UI does not invent
threshold lines. The histogram labels are rounded for display only; underlying
analysis and exported evidence are unchanged. This app does not interpret
arbitrary natural-language instructions as chart commands.

## Verify and package (maintainers)

```powershell
python -m pip install -e ".[community]"
python -m pip install pytest
python -m pytest tests/community tests/api/test_csv_analyze.py tests/application/test_csv_end_to_end.py tests/runtime/tools/test_csv_analysis.py -q
powershell -ExecutionPolicy Bypass -File scripts/package_community_v0_1_1.ps1
```

The packaging script refuses a dirty working tree or wrong branch, runs the
focused regression tests, archives the exact Git HEAD and writes SHA256.txt.
It does not sign the archive or publish a GitHub release.

## Feedback

Report installation errors, CSV parsing failures, confusing explanations, or
unexpected charts via https://github.com/hbdatahoang-ux/SciOS/issues .
Avoid sharing private or sensitive datasets. When reporting a problem, include
Python/Streamlit versions, OS, error text, and a small **synthetic** CSV that
reproduces it. Do not upload confidential CSVs.

## Limitations

The method uses pandas defaults and the 1.5×IQR rule. Flagged observations
are statistical outliers, not measurement errors or physical discoveries.
Dataset SHA-256 checks bytes, not scientific correctness. Streamlit may have
its own deployment-specific limits and telemetry settings; repository
`.streamlit/config.toml` disables Streamlit usage telemetry for this trial.
