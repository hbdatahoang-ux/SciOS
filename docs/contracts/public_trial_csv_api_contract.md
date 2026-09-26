# SciOS Public Trial — CSV Analysis Public API Contract v0.2.1
**Contract ID:** public-trial-csv-api-v0.2.1
**Status:** FROZEN
**Authority:** Canonical Public Contract
**Scope:** SciOS Public Trial / CSV Analysis
**Architectural Layer:** Application / Public API
**Owner:** SciOS Public Trial / CSV Analysis

---

## 1. Purpose and Scope

This contract defines the observable public behavior of the SciOS Public
Trial CSV Analysis interface.

The contract covers:

- the public HTTP endpoint;
- the public request surface;
- the public response surface;
- reproducibility identifiers;
- reproducibility invariants;
- public HTTP error status mapping;
- the public/private response boundary;
- explicitly unresolved CSV boundary semantics.

This contract does not define internal implementation structure.

The following are outside the normative scope of this record:

- internal execution objects;
- execution graphs;
- planners;
- tool chains;
- internal provenance structures;
- implementation classes;
- internal test structure;
- implementation-specific exception types.

---

## 2. Canonical Ownership

This record is the canonical contract authority for the SciOS Public Trial
CSV Analysis public API.

Related artifacts have distinct responsibilities:

| Artifact | Responsibility |
|---|---|
| `docs/contracts/public_trial_csv_api_contract.md` | Canonical public contract |
| `README.md` | Public-facing documentation |
| `scios/api/` | API implementation |
| `scios/application/` | CSV analysis implementation |
| `tests/` | Automated verification |
| `docs/validation/` | Validation evidence |

Implementation, tests, and validation evidence do not acquire contract
authority merely by containing corresponding terminology or behavior.

---

## 3. Public API Contract

### 3.1 Endpoint

The public CSV Analysis endpoint is:

    POST /csv/analyze

### 3.2 Request

The public request contains:

    {
      "file_path": "...",
      "query": "..."
    }

`file_path` identifies the CSV input supplied to the analysis operation.

`query` identifies the analysis request supplied by the caller.

### 3.3 Response

The public response surface contains:

- `goal`
- `rows`
- `columns`
- `column_names`
- `missing`
- `outliers`
- `reasoning`
- `explanation`
- `analysis_run_id`
- `dataset_hash`

The response surface is intentionally defined in terms of observable public
fields rather than internal implementation objects.

---

## 4. Reproducibility Contract

### 4.1 `analysis_run_id`

`analysis_run_id` identifies a particular analysis execution.

Each analysis execution produces a distinct `analysis_run_id`.

### 4.2 `dataset_hash`

`dataset_hash` identifies the analyzed input by the SHA-256 digest of the
exact raw CSV bytes analyzed.

### 4.3 Reproducibility Invariants

The public contract defines the following invariants:

1. The same exact raw CSV bytes produce the same `dataset_hash`.
2. Different raw CSV bytes produce a different `dataset_hash`.
3. Each analysis execution has a unique `analysis_run_id`.
4. Repeating an analysis with the same input produces the same
   `dataset_hash` and a different `analysis_run_id`.

Therefore:

    dataset_hash
        identifies the analyzed input

    analysis_run_id
        identifies a particular execution

These identifiers have different semantic responsibilities.

---

## 5. HTTP Error Contract

The public CSV Analysis interface defines the following status mapping:

| Observable condition | HTTP status |
|---|---:|
| CSV file not found | 404 |
| Empty CSV file | 400 |
| Malformed CSV file | 400 |
| Other CSV analysis failure | 500 |

The HTTP status mapping is part of the public contract.

The exact trigger semantics for the category "Other CSV analysis failure"
remain subject to further contract clarification and are not defined here by
an implementation-specific exception type.

---

## 6. Public Boundary Contract

The public response exposes the scientific analysis result together with the
reproducibility identifiers.

The following internal structures are not part of the public CSV Analysis
response contract:

- plans;
- execution graphs;
- tool results;
- internal execution objects;
- internal provenance records.

The existence of an internal object does not by itself make that object part
of the public contract.

---

## 7. CSV Boundary Semantics

This section defines the normative public semantics proposed by the
GS-05 contract decision.

### 7.1 Normative Outlier Boundary Rule

The public CSV analysis contract uses a strict IQR boundary rule.

A numeric value is classified as an outlier when:

    value < lower_bound
    OR
    value > upper_bound

A value within the inclusive interval

    lower_bound <= value <= upper_bound

is not classified as an outlier under this boundary rule.

**Status:** FROZEN

### 7.2 Normative Equality at Lower or Upper Bound

A value exactly equal to `lower_bound` is **not** an outlier.

A value exactly equal to `upper_bound` is **not** an outlier.

Therefore both boundary values belong to the accepted interval:

    lower_bound <= value <= upper_bound

Only values strictly outside that interval are classified as statistical
outliers.

**Status:** FROZEN

### 7.3 Normative Row / Index Convention

The public `index` field is **zero-based**.

It identifies the zero-based position of the data row within the analyzed
CSV dataset.

The CSV header row is not counted as a data-row index.

For example:

    first data row  -> index 0
    second data row -> index 1
    tenth data row  -> index 9

`index` is a data-row position, not a one-based spreadsheet row number and
not a physical CSV line number.

**Status:** FROZEN

### 7.4 GS-05

GS-05 represents the canonical boundary-case validation required to
independently verify the normative semantics proposed in Sections 7.1
through 7.3.

Semantic resolution:

    lower boundary equality  -> NOT OUTLIER
    upper boundary equality  -> NOT OUTLIER
    below lower_bound        -> OUTLIER
    above upper_bound        -> OUTLIER
    index convention         -> ZERO-BASED DATA-ROW POSITION

The canonical GS-05 public test fixture has not yet been created.

Therefore the semantic decision is resolved at the contract-decision level,
but independent black-box validation remains pending.

**Status:** FROZEN — VALIDATION ARTIFACT PENDING

---

## 8. Evidence and Validation Relationship

The relationship between contract, implementation, and validation is:

    Contract
        defines expected public behavior

    Implementation
        realizes the public behavior

    Validation
        observes whether the public behavior is satisfied

The independent black-box validation report is evidence for this contract;
it is not the canonical contract authority.

Internal tests are verification artifacts and are not substituted for
independent public evidence.

---

## 9. Implementation Relationship

The existing implementation may contain behavior corresponding to this
contract.

Such behavior is treated as implementation evidence unless explicitly
adopted into the canonical contract.

Implementation evidence does not retrospectively establish or override
canonical contract semantics.

---

## 10. Change Control

Changes to the public contract must be explicit and versioned.

A contract change should assess its impact on:

- implementation;
- automated tests;
- public artifacts;
- validation evidence;
- reproducibility behavior.

Breaking changes must not be silently introduced into an already frozen
contract version.

---

## 11. Version and Freeze Status

**Version:** v0.2.1
**Current status:** FROZEN

The boundary semantics resolved in Sections 7.1 through 7.3 are frozen
normative contract semantics.

GS-05 remains pending independent black-box validation because the canonical
public test fixture has not yet been created.

The following item remains explicitly OPEN:

- exact trigger semantics for "Other CSV analysis failure".

No validation result is retroactively changed by this contract update.

---

## 12. Contract Lifecycle

The normative lifecycle for this contract is:

    Contract Record v0.2
            ↓
    semantic review
            ↓
    boundary semantics freeze
            ↓
    canonical fixture design
            ↓
    implementation / test
            ↓
    independent black-box revalidation

The v0.2.1 record preserves the distinction between frozen contract
semantics and pending independent validation.

No validation result is retroactively changed by this contract update.
