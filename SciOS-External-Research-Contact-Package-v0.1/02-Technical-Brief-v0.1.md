# SciOS — Technical Brief v0.1

**Scientific AI Architecture for Evidence-Driven Research Workflows**

**Author:** Bùi Đình Hoàng  
**Position:** Independent Researcher  
**Affiliation:** Lab-on-Chip Group  
**Status:** Experimental Research Architecture / Research Prototype

---

## 1. Technical Scope

SciOS is an experimental architecture for exploring how AI components can participate in scientific research workflows while preserving explicit boundaries between cognition, evidence, inference, execution, provenance, governance, and validation.

The technical scope is architectural rather than product-oriented. SciOS does not assume that every described component is implemented, integrated, independently validated, or authorized for consequential use.

The central architectural concern is the transition from observation and data toward evidence, inference, execution, validation, and subsequent action.

```text
Observation
    ↓
Data
    ↓
Evidence
    ↓
Inference
    ↓
Execution
    ↓
Result
    ↓
Validation
    ↓
Subsequent Action
```

Each transition should have an explicit semantic and architectural boundary.

---

## 2. Architectural Layers

SciOS separates several conceptual layers:

- **Cognition** — interaction with models and cognitive representations.
- **Planning** — construction and decomposition of candidate plans.
- **Reasoning** — transformation of admissible inputs into reasoning results.
- **Tool Use** — controlled selection and invocation of available tools.
- **Execution** — bounded execution of operations.
- **Evidence** — representation and admission of information that may support scientific reasoning.
- **Provenance** — traceability of artifacts, observations, transformations, and decisions.
- **Governance** — explicit control of authority, permissions, safety boundaries, and consequential actions.

These layers are related but are not treated as interchangeable responsibilities.

---

## 3. Agent and Tool Execution Path

A representative SciOS execution path is:

```text
Agent
  → Planner
  → Tool Router
  → Tool Registry
  → Tool Executor
  → Tool Sandbox
  → Tool
  → Tool Result
```

This chain separates planning, routing, registration, execution, sandboxing, and tool behavior.

The existence of an execution path does not by itself establish scientific validity, general autonomy, or authorization for consequential action.

Tool execution should remain bounded by explicit runtime and governance contracts.

---

## 4. Evidence → Inference Boundary

The current design-sealed boundary is intentionally narrow:

```text
Cognitive Evidence
        ↓
Explicit Adapter
        ↓
Evidence → Inference Input
        ↓
ReasoningEngine
        ↓
ReasoningResult
```

Cognitive Evidence and Domain-Science Evidence remain separately owned concepts.

Where information must cross the boundary between these domains, the mapping is required to occur through an explicit adapter rather than an implicit dataclass merge or hidden coupling.

The following are outside the scope of the current P2-G06.3 boundary:

- strategy update
- replanning
- learning
- MUSES integration
- QTC integration
- runtime execution
- autonomous closed-loop scientific operation

The boundary therefore defines an input-to-reasoning contract, not a complete autonomous scientific loop.

---

## 5. Current Contract Status

| Artifact / Capability | Current Status |
|---|---|
| P2-G06.3 Evidence → Inference Boundary Contract v0.1 | DESIGN-SEALED |
| P2-G06 Evidence → Inference capability | NOT ESTABLISHED |
| P2-G07 | NOT AUTHORIZED |
| Evidence Admission Semantics v0.1 | DRAFT / DESIGN-ONLY / RECOVERED CONTEXT |
| Scientific validation | NOT ASSESSED |

These states must not be collapsed into one another.

**DESIGN-SEALED ≠ IMPLEMENTATION AUTHORIZED.**

**NOT ESTABLISHED ≠ FALSE or REJECTED.**

A design can be sufficiently specified for architectural review while the corresponding implementation or capability remains unestablished.

---

## 6. Evidence, Provenance, and Validation

A conceptual evidence chain is:

```text
Observation
    ↓
Provenance
    ↓
Evidence Admission
    ↓
Admissible Evidence
    ↓
Inference
    ↓
Validation
    ↓
Claim
```

Several distinctions are important:

- Traceability is not equivalent to evidence admission.
- Evidence admission is not equivalent to verification.
- Verification is not equivalent to scientific correctness.
- Documentation is not equivalent to independent validation.
- Contextual origin is not equivalent to authoritative provenance.
- Capability existence is not equivalent to permission to exercise that capability.

Evidence should therefore carry sufficient provenance and admission information for downstream reasoning and later audit.

---

## 7. Governance Boundary

SciOS treats governance as infrastructure separate from domain-specific scientific capabilities.

The governance boundary is intended to support deterministic enforcement rather than relying exclusively on natural-language instructions or an informal model-level constitution.

A frozen runtime governance principle is zero-code propagation of governance context into tool arguments:

```text
GovernanceContext ∩ Tool Args/Kwargs = ∅
```

In particular, governance context is not expected to be injected through ad-hoc keys such as:

- `governance`
- `_policy`
- `permissions`

The architectural principle is:

**Adapter trước, Intelligence sau.**

This keeps governance semantics at an explicit boundary instead of making them an implicit responsibility of individual tools.

---

## 8. Validation Philosophy

SciOS separates several stages of technical and scientific evidence:

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

The following distinctions are intentional:

- **IMPLEMENTED** means code or architecture exists.
- **TESTED** means specified tests have been executed with recorded results.
- **VALIDATED** means behavior has received an appropriate independent validation process.
- **ESTABLISHED** means the capability has sufficient evidence to support the corresponding architectural status.

Implementation does not automatically prove correctness.

Tests do not automatically establish scientific validity.

Independent validation addresses whether the behavior is supported outside the implementation author's immediate assumptions.

---

## 9. Provenance Recovery and Authority

During provenance recovery, a prior-work design context was identified for the Evidence Admission Semantics v0.1 draft.

This establishes a **contextual origin**, but not an authoritative contract repository or formal approval record.

The following remain unestablished:

- exact authoritative repository path
- exact Git commit associated with the artifact
- physical artifact SHA-256
- formally assigned Contract Owner
- formally assigned Seal Authority
- authority or delegation chain
- formal decision record
- Q1–Q6 semantic decisions

Accordingly, the provenance endpoint is:

**P2-G06.4 — NO AUTHORITATIVE PROVENANCE IDENTIFIED**

This is a provenance closure point, not a claim that the design itself is false or rejected.

Likewise, contextual prior-work origin must not be represented as formal authorization.

---

## 10. Research and Domain Separation

SciOS is intended to provide architectural infrastructure in which domain-specific scientific capabilities can be integrated under explicit boundaries.

Domain models and scientific theories should therefore remain distinguishable from the operating-system architecture that hosts or orchestrates them.

MUSES and QTC are treated as research-domain components rather than evidence that the complete SciOS autonomous scientific architecture has already been established.

This separation is important for preventing scientific-domain assumptions from silently becoming system-level authority.

---

## 11. What the Architecture Does Not Claim

This technical brief does not claim that SciOS currently provides:

- autonomous scientific AGI
- a universal reasoning engine
- guaranteed scientific correctness
- automatic scientific validation
- automatic authorization of consequential actions
- complete closed-loop scientific learning
- automatic resolution of provenance disputes
- immunity from model errors or hallucinations

These are research directions or questions rather than established capabilities.

---

## 12. External Technical Review

The purpose of external technical contact is independent inspection and constructive criticism.

Reviewers are invited to examine:

1. whether the architectural boundaries are sufficiently explicit;
2. whether evidence and provenance semantics are operationally testable;
3. whether ownership and authority are represented at the correct boundaries;
4. whether implementation claims are appropriately separated from validation claims;
5. whether the proposed architecture introduces hidden coupling or ambiguous authority;
6. what evidence would be required before additional capabilities could be considered established.

External feedback is evidence for research development and critique. It is not automatically contract ownership, formal approval, seal authority, or deployment authorization.

---

## 13. Current Development Posture

Current architectural posture:

```text
PROTOTYPE-1
    — ARCHITECTURAL HOLD / PROVENANCE WAIT STATE
```

Current operating mode:

```text
DESIGN-ONLY / READ-ONLY / HOLD
```

Current mutation policy:

```text
ZERO CODE
ZERO TEST
ZERO WIRING
ZERO COMMIT
ZERO PUSH
```

The future target `PROTOTYPE-2 — REAL SCIENTIFIC CLOSED-LOOP & TARGETED LEARNING STRATEGY` is non-authorizing and does not activate implementation.

Design completeness does not itself grant implementation authorization.

---

## 14. Summary

SciOS explores an architecture in which scientific AI workflows can preserve explicit distinctions among evidence, inference, execution, provenance, governance, and validation.

The current architecture intentionally stops short of claiming a completed autonomous scientific system.

The most important technical principle is that each transition toward stronger capability should be accompanied by explicit evidence, provenance, ownership, validation, and authorization boundaries.

SciOS therefore treats architectural restraint as part of the technical design rather than as an afterthought.

**Audit first. Establish ownership. Preserve evidence. Then implement.**
