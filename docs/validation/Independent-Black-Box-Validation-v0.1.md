# Independent Black-Box Validation Report v0.1

## SciOS Public Trial / CSV Analysis

**Validation type:** Independent Black-Box Validation
**System under validation:** SciOS Public Trial — CSV Analysis
**Validation version:** v0.1
**Validation scope:** Public CLI and public HTTP API
**Repository:** SciOS
**Validation principle:** Input → execution → observable output → error behavior → reproducibility
**Implementation inspection:** Excluded from pass/fail determination
**New test artifacts:** None created
**Source modification:** None performed during validation

---

## 1. Purpose

This report records an independent black-box validation of the SciOS Public Trial CSV Analysis interface.

The objective was to determine whether the publicly exposed CSV analysis workflow behaves according to its observable public contract when exercised as an external user would exercise it.

The validation deliberately avoids relying on:

* internal class structure,
* internal execution graphs,
* cognitive-core implementation,
* internal test results,
* private execution objects,
* implementation-specific assumptions,
* newly authored validation fixtures.

The validation therefore evaluates the externally observable behavior of the system rather than its internal implementation.

---

## 2. Validation Scope

The validation covered the following public surfaces.

### 2.1 CLI

Public command:

```text
python -m scios.cli.csv_analysis
```

with:

```text
--file
--query
```

The documented/default analytical goal was:

```text
Analyze the CSV dataset and explain anomalous values.
```

### 2.2 HTTP API

Public endpoint:

```text
POST /csv/analyze
```

The observed request contract used:

```text
{
  "file_path": "...",
  "query": "Analyze the CSV dataset and explain anomalous values."
}
```

The public response was evaluated only through fields observable from the HTTP response.

### 2.3 Reproducibility

The validation examined the documented distinction between:

* `analysis_run_id`
* `dataset_hash`

The validation also independently computed the SHA-256 hash of the raw CSV fixture.

### 2.4 Error behavior

The following documented error classes were exercised:

* missing CSV file,
* empty CSV file,
* malformed CSV file.

Other failure modes were not marked as tested unless directly observed.

---

## 3. Black-Box Protocol

The validation followed this principle:

```text
Known public input
       ↓
Public interface
       ↓
Observed stdout / stderr / HTTP response
       ↓
Observed exit code / HTTP status
       ↓
Evidence record
       ↓
Contract classification
```

No internal test was treated as a substitute for public black-box evidence.

In particular, internal tests referring to implementation contracts were not used to establish public API behavior.

---

## 4. Evidence Ledger

| ID    | Evidence                            | Interface                     | Result       |
| ----- | ----------------------------------- | ----------------------------- | ------------ |
| EV-01 | GS-01 single-outlier CLI execution  | CLI                           | PASS         |
| EV-02 | GS-01 single-outlier HTTP execution | HTTP API                      | PASS         |
| EV-03 | Repeated identical HTTP requests    | HTTP API                      | PASS         |
| EV-04 | Independent SHA-256 verification    | Local file vs API             | PASS         |
| EV-05 | Missing CSV error                   | HTTP API                      | PASS         |
| EV-06 | Empty CSV error                     | HTTP API                      | PASS         |
| EV-07 | Malformed CSV error                 | HTTP API                      | PASS         |
| EV-08 | Search for canonical GS-05 artifact | Repository/public-trial audit | INCONCLUSIVE |

---

# 5. GS-01 — Single Outlier

## 5.1 Test artifact

Canonical repository fixture used:

```text
data/real_workflow/gs01_single_outlier.csv
```

No fixture was created or modified for this validation.

## 5.2 CLI execution

The public CLI was executed against the fixture with the documented analytical query.

Observed result:

```text
Rows: 10
Columns: 4
Columns: id, val_1, val_2, val_3
```

Missing values:

```text
id: 0
val_1: 0
val_2: 0
val_3: 0
```

The observable anomaly was:

```text
column: val_1
row: 9
value: 100.0
rule: IQR
range: [5.5, 23.5]
```

The CLI also produced a reasoning section and an explanation stating that `100.0` was above the upper bound `23.5` under the IQR rule.

Observed exit code:

```text
0
```

### Classification

**GS-01 CLI: PASS**

This classification is based solely on the observed public CLI behavior.

The validation does not infer how the result was produced internally.

---

# 6. GS-01 — Public HTTP API

The same canonical fixture was submitted through:

```text
POST /csv/analyze
```

Observed HTTP status:

```text
200 OK
```

The response contained:

```text
goal
rows
columns
column_names
missing
outliers
reasoning
explanation
analysis_run_id
dataset_hash
```

Observed analytical result included:

```text
rows: 10
columns: 4
```

For `val_1`:

```text
index: 9
value: 100.0
q1: 12.25
q3: 16.75
iqr: 4.5
lower_bound: 5.5
upper_bound: 23.5
rule: IQR
```

The response marked the value as an outlier and provided a corresponding explanation.

A server-side HTTP access log recorded:

```text
POST /csv/analyze HTTP/1.1" 200 OK
```

### Classification

**GS-01 Public HTTP Black-Box: PASS**

---

# 7. Reproducibility Contract

Two identical public HTTP requests were executed against the same fixture and query.

### Run 1

```text
analysis_run_id:
32becddc-20b7-4ced-87b8-78596f1e0c80

dataset_hash:
bb3e9a920b0e7891339c795b8b5e9cc642ff3f400591764caf36920ae9004313
```

### Run 2

```text
analysis_run_id:
f8d5fd0d-c70d-4ade-97fd-66dea0ab28f0

dataset_hash:
bb3e9a920b0e7891339c795b8b5e9cc642ff3f400591764caf36920ae9004313
```

Observed comparison:

```text
Same dataset_hash: True
Different run_id: True
```

This directly supports the following observed behavior:

```text
same raw input
    → same dataset_hash

separate analysis executions
    → different analysis_run_id
```

### Classification

**Reproducibility contract: PASS**

---

# 8. Independent Dataset Hash Verification

The SHA-256 hash of the exact local CSV bytes was independently computed using:

```text
Get-FileHash -Algorithm SHA256
```

Observed local hash:

```text
bb3e9a920b0e7891339c795b8b5e9cc642ff3f400591764caf36920ae9004313
```

Observed API hash:

```text
bb3e9a920b0e7891339c795b8b5e9cc642ff3f400591764caf36920ae9004313
```

Observed comparison:

```text
MATCH: True
```

### Classification

**Dataset hash cross-check: PASS**

This is an independently performed consistency check between the public API result and the exact local fixture bytes.

---

# 9. Public HTTP Error Contract

Three documented error cases were exercised.

## 9.1 Missing CSV

Input referenced:

```text
data/real_workflow/does_not_exist.csv
```

Observed:

```text
HTTP 404
```

Server log:

```text
POST /csv/analyze HTTP/1.1" 404 Not Found
```

### Classification

**PASS**

---

## 9.2 Empty CSV

Canonical fixture:

```text
data/real_workflow/empty.csv
```

Observed:

```text
HTTP 400
```

Server log recorded the corresponding `400` response.

### Classification

**PASS**

---

## 9.3 Malformed CSV

Canonical fixture:

```text
data/real_workflow/malformed.csv
```

Observed:

```text
HTTP 400
```

Server log recorded the corresponding `400` response.

### Classification

**PASS**

---

## 9.4 Other CSV analysis failure

The documented `500` behavior for an otherwise unclassified CSV analysis failure was **not exercised**.

Therefore:

```text
Status: NOT TESTED
```

No conclusion is made about this case.

---

# 10. GS-05 — Boundary Case

## 10.1 Intended validation question

The proposed GS-05 validation question was whether the public CSV analysis workflow exposes a canonical boundary case for the outlier threshold, particularly behavior at or around the upper boundary.

The independent validation specifically looked for:

* an explicit `GS-05` / `GS05` reference,
* a documented CSV boundary scenario,
* a canonical boundary fixture,
* public documentation defining the expected boundary behavior.

## 10.2 Artifact audit

A read-only repository audit was performed across:

```text
README.md
docs/
data/
tests/
```

excluding virtual-environment content.

The audit found:

```text
No explicit GS-05 / GS05 reference.
```

No canonical fixture named:

```text
gs05_boundary.csv
```

was present.

The available `data/real_workflow` fixtures included:

```text
categorical_only.csv
empty.csv
gs01_single_outlier.csv
header_only.csv
malformed.csv
missing_values.csv
multiple_numeric.csv
normal_outlier.csv
no_outlier.csv
```

as well as dataset-quality and time-series fixtures.

None was identified by the public trial artifacts as the canonical GS-05 boundary fixture.

## 10.3 Important distinction

The repository does contain references to:

```text
SG-05 — Consequential Action Boundary
```

within safety/governance testing.

That artifact was **not** treated as GS-05 CSV evidence.

The two identifiers represent different validation subjects.

Similarly, internal tests containing IQR, `upper_bound`, `lower_bound`, or boundary-related assertions were not treated as independent public black-box evidence.

## 10.4 Validation consequence

Because no canonical public GS-05 fixture or explicit public GS-05 boundary contract was found, a boundary test cannot be completed without creating a new test artifact.

Creating such an artifact during independent validation would introduce a validator-authored test case and would therefore change the nature of the validation.

No such artifact was created.

### Classification

**GS-05: INCONCLUSIVE — missing canonical public test artifact**

This classification means:

```text
Boundary behavior was not independently established.
```

It does **not** mean:

```text
The implementation failed the boundary test.
```

It also does **not** mean:

```text
The implementation passed the boundary test.
```

No implementation conclusion is made.

---

# 11. Self-Authored Testing Boundary

To preserve the independence of this validation, the following actions were deliberately not performed:

* no `gs05_boundary.csv` was created;
* no new boundary fixture was added to the repository;
* no expected-result file was authored for GS-05;
* no internal test was modified;
* no implementation code was modified;
* no internal test result was substituted for public black-box evidence.

The previously attempted execution against a nonexistent `gs05_boundary.csv` produced:

```text
Error: CSV file not found.
```

with exit code:

```text
1
```

That observation establishes only that the requested file was unavailable at that path.

It is **not** evidence about CSV boundary semantics and is therefore not classified as a GS-05 implementation failure.

---

# 12. Usability / Friction Observations

## 12.1 Row/index convention

The public output identifies the observed outlier as:

```text
row: 9
```

and the HTTP response exposes:

```text
index: 9
```

The black-box output does not itself make the indexing convention explicit.

This is recorded as a **clarification question**, not as a functional defect.

Suggested public documentation clarification:

```text
Specify whether reported row/index positions are zero-based or one-based.
```

No source change was made as part of this validation.

## 12.2 API availability

Before the Uvicorn server was started, the local API endpoint was unavailable.

This was classified as an environment state rather than a SciOS CSV-analysis failure.

After Uvicorn was started, the application reported:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

A request to `/` returned:

```text
404 Not Found
```

This was not treated as an API failure because `/` was not the documented CSV analysis endpoint.

The documented endpoint:

```text
POST /csv/analyze
```

was subsequently exercised successfully.

---

# 13. Validation Matrix

| Area                   | Artifact / Input             | Observable Result                                   | Status           |
| ---------------------- | ---------------------------- | --------------------------------------------------- | ---------------- |
| GS-01 CLI              | `gs01_single_outlier.csv`    | Outlier detected; exit code 0                       | **PASS**         |
| GS-01 HTTP             | `gs01_single_outlier.csv`    | HTTP 200; expected public result fields             | **PASS**         |
| Reproducibility        | Same fixture/query twice     | Same hash, different run IDs                        | **PASS**         |
| Dataset hash           | Exact raw CSV bytes          | API hash matched local SHA-256                      | **PASS**         |
| Missing CSV            | nonexistent path             | HTTP 404                                            | **PASS**         |
| Empty CSV              | `empty.csv`                  | HTTP 400                                            | **PASS**         |
| Malformed CSV          | `malformed.csv`              | HTTP 400                                            | **PASS**         |
| Other analysis failure | No canonical test performed  | Not observed                                        | **NOT TESTED**   |
| GS-05 boundary         | No canonical public artifact | Boundary semantics unavailable for independent test | **INCONCLUSIVE** |

---

# 14. Evidence Quality Assessment

The strongest evidence in this validation consists of direct observations from the public interfaces:

```text
CLI stdout/stderr
CLI exit code
HTTP status
HTTP response body
HTTP server access log
independent SHA-256 calculation
repository artifact inventory
```

The following were intentionally excluded from the basis of public pass/fail conclusions:

```text
internal implementation structure
internal cognitive-core behavior
internal execution graphs
internal governance architecture
internal unit tests
internal integration tests
developer-authored expected outputs
```

This separation prevents internal correctness claims from being mistaken for independent black-box evidence.

---

# 15. Limitations

This validation does not establish:

1. correctness of internal architecture;
2. correctness of internal cognitive reasoning mechanisms;
3. correctness of governance propagation;
4. correctness of private execution objects;
5. complete statistical correctness of the IQR implementation;
6. behavior for every possible CSV format or failure mode;
7. GS-05 boundary semantics;
8. the untested documented `500` error path.

The validation establishes only the externally observed behaviors recorded in this report.

---

# 16. Findings

### Finding F-01 — Public CSV analysis workflow is externally executable

The canonical GS-01 fixture was successfully processed through both the public CLI and HTTP API.

**Evidence:** EV-01, EV-02.

### Finding F-02 — Public reproducibility identifiers are externally observable

Repeated identical inputs produced the same `dataset_hash` and distinct `analysis_run_id` values.

**Evidence:** EV-03.

### Finding F-03 — Dataset hash is independently reproducible

The API-provided SHA-256 matched an independently calculated hash of the exact CSV bytes.

**Evidence:** EV-04.

### Finding F-04 — Documented HTTP error cases were externally observed

Missing, empty, and malformed CSV cases produced the documented HTTP status classes observed during validation.

**Evidence:** EV-05, EV-06, EV-07.

### Finding F-05 — Canonical GS-05 public validation artifact is absent

The read-only artifact audit found no explicit GS-05 CSV scenario or canonical boundary fixture.

**Evidence:** EV-08.

Therefore GS-05 remains:

```text
INCONCLUSIVE — missing canonical public test artifact
```

---

# 17. Independent Validation Conclusion

The SciOS Public Trial CSV Analysis interface produced observable successful behavior for the canonical GS-01 workflow, reproducibility behavior, dataset hash verification, and the three exercised public HTTP error cases.

The validation did not establish the untested `500` failure path.

Most importantly, the proposed GS-05 boundary case could not be independently executed because no canonical public GS-05 test artifact or explicit public boundary fixture was found in the audited repository.

Accordingly:

```text
GS-05
INCONCLUSIVE — missing canonical public test artifact
```

No new fixture was created to resolve this condition.

This preserves the distinction between:

```text
independent black-box evidence
```

and

```text
validator-authored testing
```

The absence of a GS-05 artifact is therefore recorded as a **validation limitation / public-trial artifact gap**, not as an implementation failure.

---

# 18. Recommended Follow-Up

The independent validation phase should be considered complete for the currently available public artifacts.

If SciOS maintainers later wish to validate the boundary semantics, that should be performed as a **separate, explicitly authored test artifact** with:

* a named public scenario,
* a canonical fixture,
* documented expected behavior,
* explicit boundary semantics,
* reproducibility identifiers where applicable.

Such an artifact should be introduced by the system/project maintainers rather than retroactively inserted into this independent validation evidence.

Until then, this report preserves GS-05 as:

```text
INCONCLUSIVE — missing canonical public test artifact
```

and does not infer behavior that was not independently observed.

---

## 19. Final Status

```text
============================================================
SciOS Independent Black-Box Validation v0.1
Public Trial / CSV Analysis
============================================================

GS-01 CLI                  PASS
GS-01 HTTP                 PASS
Reproducibility            PASS
Dataset SHA-256            PASS
Missing CSV / 404          PASS
Empty CSV / 400            PASS
Malformed CSV / 400        PASS
Other failure / 500        NOT TESTED

GS-05 CSV Boundary         INCONCLUSIVE
                           missing canonical public test artifact

New fixtures created       NO
Source modified            NO
Internal tests used as
public evidence            NO

Validation status          COMPLETE FOR AVAILABLE
                           PUBLIC ARTIFACTS
============================================================
```

**End of Independent Black-Box Validation Report v0.1**
