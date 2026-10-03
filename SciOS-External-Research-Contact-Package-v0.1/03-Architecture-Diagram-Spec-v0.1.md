# SciOS — Architecture Diagram Specification v0.1

**Scientific AI Architecture for Evidence-Driven Research Workflows**

**Author:** Bùi Đình Hoàng  
**Position:** Independent Researcher  
**Affiliation:** Lab-on-Chip Group  
**Status:** Experimental Research Architecture / Research Prototype

---

## 1. Purpose

This document specifies a conceptual architecture diagram for presenting SciOS to external researchers and technical reviewers.

The diagram is intended to communicate architectural boundaries, information flow, evidence handling, provenance, governance, and validation.

It is not an implementation map and must not be interpreted as evidence that every component shown is implemented, integrated, tested, validated, or authorized.

---

## 2. Primary Diagram

The primary conceptual diagram should use the following structure:

```text
                         ┌───────────────────────┐
                         │   Cognitive Models    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      Cognition        │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       Planning        │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       Reasoning       │
                         └───────────┬───────────┘
                                     │
                         Explicit boundary
                                     │
                                     ▼
                    ┌────────────────────────────┐
                    │    Evidence → Inference    │
                    │        Input Boundary      │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                         ┌───────────────────────┐
                         │    ReasoningEngine     │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    ReasoningResult    │
                         └───────────────────────┘

                                     │
                                     │ separate execution path
                                     ▼

        ┌──────────┐   ┌─────────────┐   ┌──────────────┐
        │ Tool     │ → │ Tool Router │ → │ Tool Executor│
        └──────────┘   └─────────────┘   └──────┬───────┘
                                                 │
                                                 ▼
                                         ┌──────────────┐
                                         │ Tool Sandbox │
                                         └──────┬───────┘
                                                │
                                                ▼
                                           Tool Result

````

---

## 3. Evidence and Provenance Layer

The diagram should show Evidence and Provenance as explicit architectural concerns rather than hidden metadata.

Recommended conceptual flow:

```text
Raw Observation
      │
      ▼
Provenance
      │
      ▼
Evidence Admission
      │
      ▼
Admissible Evidence
      │
      ▼
Inference
      │
      ▼
Validation
      │
      ▼
Claim
```

The visual distinction should make clear that traceability, evidence admission, verification, and scientific correctness are separate concepts.

---

## 4. Governance Boundary

Governance should be represented as a boundary surrounding consequential execution rather than as an informal property of the language model.

The diagram should identify:

- authority and permission boundaries;
- safety constraints;
- execution controls;
- provenance requirements;
- validation state;
- conditions under which consequential action is permitted.

A key runtime principle is:

```text
GovernanceContext ∩ Tool Args/Kwargs = ∅
```

The diagram must not imply that governance context is silently injected into individual tool arguments.

**Adapter trước, Intelligence sau.**

---

## 5. Explicit Boundary Labels

The final visual should label the following distinctions explicitly:

| Boundary | Required interpretation |
|---|---|
| Evidence | Information admitted for possible scientific reasoning |
| Inference | Reasoning derived from admissible inputs |
| Authorization | Permission to perform a consequential action |
| Provenance | Traceability of origin and transformation |
| Ownership | Responsibility for a contract or decision |
| Capability | What a component can technically perform |
| Validation | Evidence supporting a claimed behavior |

These concepts must not be visually collapsed into a single generic AI or intelligence box.

---

## 6. Current Architectural Status

The diagram specification must preserve the current status of the architecture:

```text
P2-G06.3 Evidence → Inference Boundary Contract v0.1
    = DESIGN-SEALED

P2-G06 Evidence → Inference capability
    = NOT ESTABLISHED

P2-G07
    = NOT AUTHORIZED

Current posture
    = PROTOTYPE-1 — ARCHITECTURAL HOLD / PROVENANCE WAIT STATE

Current mode
    = DESIGN-ONLY / READ-ONLY / HOLD
```

The visual must not use implementation-looking styling to imply that a design-sealed boundary is already an established autonomous capability.

---

## 7. Validation Boundary

A validation lane should be shown separately from the architecture itself:

```text
Specification
      ↓
Implementation
      ↓
Tests
      ↓
Independent Validation
      ↓
Evidence
      ↓
Claim
```

The visual should make clear that implementation and testing do not automatically establish scientific correctness.

---

## 8. Required Visual Semantics

The final diagram should use visual distinctions for:

1. conceptual components;
2. explicit interfaces;
3. evidence boundaries;
4. provenance flow;
5. governance boundaries;
6. validation boundaries;
7. current status markers.

Where implementation status is relevant, labels such as `DESIGN`, `IMPLEMENTED`, `TESTED`, `VALIDATED`, or `NOT ESTABLISHED` should be used explicitly rather than inferred from graphical appearance.

---

## 9. Caption for External Distribution

Suggested caption:

> Conceptual SciOS architecture for evidence-driven scientific AI workflows. The diagram separates cognition, planning, reasoning, evidence, provenance, governance, tool execution, and validation. It describes architectural boundaries and intended information flow; it does not imply that every component is implemented, scientifically validated, independently verified, or authorized for consequential use.

---

## 10. Forbidden Interpretations

The diagram must not be presented as evidence of:

- autonomous scientific AGI;
- guaranteed scientific correctness;
- automatic evidence validation;
- automatic authorization of consequential actions;
- complete closed-loop scientific learning;
- automatic resolution of provenance disputes;
- universal reasoning capability.

The diagram is an architectural communication artifact, not a capability certificate.

---

## 11. Design Principle

The diagram should preserve the following research principle:

**Audit first. Establish ownership. Preserve evidence. Then implement.**

This principle describes the intended engineering discipline and does not itself constitute authorization.

---

## 12. Status

This specification is prepared for external technical discussion and independent architectural review.

It should not be interpreted as a declaration that unresolved provenance, ownership, validation, or authorization requirements have been satisfied.

**Artifact status:** External Research Contact Package v0.1 / Architecture Diagram Specification / Design Communication Artifact
