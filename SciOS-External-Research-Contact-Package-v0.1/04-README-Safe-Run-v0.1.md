# SciOS — How to Run Safely v0.1

**Safe Evaluation Guide for External Researchers and Technical Reviewers**

**Project:** SciOS — Scientific Cognitive Operating System  
**Author:** Bùi Đình Hoàng  
**Position:** Independent Researcher  
**Affiliation:** Lab-on-Chip Group  
**Status:** Experimental Research Architecture / Research Prototype

---

## 1. Purpose

This README describes a conservative procedure for externally inspecting and running SciOS.

The procedure is designed for research review, architectural inspection, reproducibility checks, and bounded experimentation.

It is not a deployment guide for production, medical, energy, financial, industrial, or other safety-critical systems.

The central principle is:

**Inspect first. Run in isolation. Preserve evidence. Do not infer more capability than the evidence supports.**

---

## 2. Current Architectural Posture

At the time of this package, SciOS is maintained under the following architectural posture:

```text
PROTOTYPE-1
— ARCHITECTURAL HOLD / PROVENANCE WAIT STATE

DESIGN-ONLY / READ-ONLY / HOLD

ZERO CODE
ZERO TEST
ZERO WIRING
ZERO COMMIT
ZERO PUSH
```

The future target `PROTOTYPE-2 — REAL SCIENTIFIC CLOSED-LOOP & TARGETED LEARNING STRATEGY` is non-authorizing.

The current package therefore supports external inspection and bounded evaluation rather than deployment authorization.

---

## 3. Safety Principles

Before running anything, apply these principles:

1. Use an isolated working environment.
2. Do not provide production credentials.
3. Do not connect the evaluation environment to private databases unless explicitly required and independently controlled.
4. Do not provide sensitive personal, medical, financial, or confidential research data.
5. Prefer synthetic, public, or non-sensitive datasets.
6. Review tool definitions and execution boundaries before enabling external actions.
7. Treat generated model output as untrusted until independently checked.
8. Preserve logs, inputs, outputs, hashes, and test results when reproducibility matters.
9. Do not treat successful execution as proof of scientific correctness.
10. Stop when an experiment reaches an authorization, provenance, or safety boundary that has not been established.

---

## 4. Recommended Evaluation Environment

For external review, use a disposable or otherwise isolated environment.

Recommended controls include:

- dedicated virtual environment or container;
- no production secrets;
- no unrestricted network access unless the experiment explicitly requires it;
- no access to private datasets by default;
- bounded filesystem permissions;
- recorded package and interpreter versions;
- captured command lines and test results.

The external reviewer should be able to discard the environment without affecting any production system.

---

## 5. Initial Inspection

Before executing a workflow, inspect:

- repository state;
- current branch and commit;
- Python/interpreter version;
- dependency declarations;
- test configuration;
- tool registry and available tools;
- runtime execution boundaries;
- governance and safety adapters;
- evidence and provenance artifacts;
- known limitations and unresolved items.

Do not assume that a README description is sufficient evidence of implementation.

---

## 6. Run Tests Before Experiments

A conservative evaluation sequence begins with tests.

Example:

```text
python -m pytest
```

Record:

- command used;
- interpreter version;
- dependency environment;
- number of tests collected;
- pass/fail/error results;
- relevant warnings;
- commit identifier.

If the baseline test suite does not pass, record that condition rather than silently treating the package as validated.

---

## 7. Bounded Workflow Evaluation

After initial inspection, evaluate only bounded workflows whose inputs and expected behavior are understandable and reversible.

Suitable examples may include:

- public CSV analysis;
- deterministic tool invocation;
- architecture-level contract checks;
- reproducibility checks;
- evidence and provenance tracing.

Avoid experiments that silently introduce uncontrolled external side effects.

For each experiment record:

```text
Input
  ↓
Execution
  ↓
Output
  ↓
Evidence
  ↓
Independent Check
```

---

## 8. Evidence and Provenance

When evaluating a scientific workflow, distinguish:

- observation;
- provenance;
- evidence admission;
- inference;
- verification;
- scientific correctness;
- authorization.

These are separate semantic states.

In particular:

**Contextual origin ≠ authoritative provenance.**

**Implementation ≠ validation.**

**Capability ≠ authorization.**

If the provenance of an artifact cannot be established, record the limitation explicitly rather than reconstructing authority from assumption.

---

## 9. Tool and Execution Safety

Review every tool before allowing it to participate in an external evaluation.

Questions to ask include:

1. What inputs can the tool receive?
2. What resources can it access?
3. Can it modify files or external systems?
4. Can it make network requests?
5. Can it create irreversible side effects?
6. What provenance is recorded for its output?
7. What governance boundary controls consequential execution?

A tool being registered or technically executable does not by itself establish permission for consequential use.

---

## 10. What a Successful Run Does Not Prove

A successful command, passing test, or plausible model response does not by itself prove:

- scientific correctness;
- generalization to unseen scientific problems;
- autonomous research capability;
- reliable evidence admission;
- complete provenance;
- independent scientific validation;
- authorization for consequential action.

Claims should remain proportional to the evidence actually recorded.

---

## 11. External Review Record

For reproducible external review, record at minimum:

| Field | Record |
|---|---|
| Date/time | Evaluation timestamp |
| Environment | OS, interpreter, container/venv |
| Repository | Repository identifier |
| Commit | Exact commit tested |
| Dataset | Dataset identity and provenance |
| Command | Exact command executed |
| Result | Raw result or exit status |
| Evidence | Supporting artifacts |
| Independent check | Verification performed |
| Limitations | Known unresolved conditions |

Do not remove failed runs merely because a later run succeeds.

---

## 12. Reporting Template

A concise external report can follow this structure:

```text
Experiment:

Environment:

Commit:

Input:

Command:

Observed result:

Evidence retained:

Independent check:

Limitations / unresolved items:

Conclusion supported by evidence:
```

The final field should describe only what the recorded evidence supports.

---

## 13. Responsible Use

Do not connect an experimental SciOS evaluation directly to systems where an incorrect action could cause material harm.

This includes, without limitation:

- clinical or medical decision systems;
- energy infrastructure;
- industrial control systems;
- financial transaction systems;
- systems controlling physical equipment;
- confidential production environments.

For such environments, independent safety, security, domain, and regulatory controls are required outside this research package.

---

## 14. Current Limitations

The current research architecture should be evaluated with the following limitations in mind:

- P2-G06.3 is DESIGN-SEALED, not an authorization to implement P2-G06.
- P2-G06 remains NOT ESTABLISHED.
- P2-G07 remains NOT AUTHORIZED.
- Evidence Admission Semantics v0.1 remains DRAFT / DESIGN-ONLY / RECOVERED CONTEXT.
- Authoritative provenance for the Evidence Admission draft has not been identified.
- Scientific validation of the complete architecture has not been established.

These limitations are part of the current research record and should remain visible during external review.

---

## 15. Safe-Run Principle

The recommended external evaluation posture is:

```text
Inspect
  ↓
Isolate
  ↓
Test
  ↓
Run bounded experiment
  ↓
Preserve evidence
  ↓
Independently check
  ↓
Report only supported claims
```

**Audit first. Establish ownership. Preserve evidence. Then implement.**

This principle is an engineering discipline, not an authorization mechanism.

---

## 16. Package Status

This README is part of the SciOS External Research Contact Package v0.1.

It is intended to help external researchers inspect and evaluate the project conservatively, reproducibly, and without confusing architectural design with established capability.

**Artifact status:** External Research Contact Package v0.1 / Safe-Run README / Research Evaluation Guide
