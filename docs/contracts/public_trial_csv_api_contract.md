# SciOS Public Trial — CSV Analysis Public API Contract v0.1

**Contract ID:** public-trial-csv-api-v0.1
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

This section records boundary semantics that require explicit
canonicalization.

### 7.1 Outlier Boundary Rule

The public contract does not freeze the exact inequality used at the
lower or upper outlier boundary in this version.

Implementation behavior is not promoted automatically into normative
contract semantics.

**Status:** OPEN

### 7.2 Equality at Lower or Upper Bound

Whether a value exactly equal to `lower_bound` or `upper_bound` is classified
as an outlier is not frozen by this contract version.

**Status:** OPEN

### 7.3 Row / Index Convention

The public contract does not currently freeze whether reported row/index
positions are zero-based or one-based.

**Status:** OPEN

### 7.4 GS-05

GS-05 represents the CSV boundary-case resolution required to establish
canonical public semantics.

Current status:

    GS-05
    INCONCLUSIVE — missing canonical public test artifact

No implementation behavior, internal test, or validator-authored fixture is
used here to convert GS-05 into a frozen contract result.

**Status:** OPEN

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

In particular, implementation details must not be used retrospectively to
resolve currently OPEN contract semantics.

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

**Version:** v0.1

**Current status:** FROZEN

This record is not yet a fully frozen semantic specification.

The following remain explicitly OPEN:

- GS-05 boundary semantics;
- equality at `lower_bound` / `upper_bound`;
- row/index convention;
- exact trigger semantics for "Other CSV analysis failure".

A subsequent contract-resolution phase is required before those OPEN items
are promoted to frozen normative semantics.

---

## 12. Next Contract Phase

The planned sequence after creation of this record is:

    Contract Record v0.1
            ↓
    review / freeze
            ↓
    GS-05 Boundary Contract Resolution
            ↓
    canonical fixture design
            ↓
    implementation / test
            ↓
    independent black-box revalidation

No validation result is retroactively changed by creation of this contract
record.