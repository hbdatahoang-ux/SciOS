# SciOS — Research Brief v0.1

**Scientific AI Architecture for Evidence-Driven Research Workflows**

**Author:** Bùi Đình Hoàng  
**Position:** Independent Researcher  
**Affiliation:** Lab-on-Chip Group  
**Status:** Experimental Research Architecture / Research Prototype

---

## 1. Research Question

AI systems are increasingly capable of answering questions, writing programs, analyzing data, using tools, and assisting scientific work.

However, producing a technically plausible answer is not equivalent to operating a scientific research workflow whose actions, evidence, provenance, and conclusions can be inspected and reproduced.

SciOS studies the following systems question:

> **How can an AI system participate in scientific research while preserving evidence, execution provenance, reproducibility, explicit ownership, and controlled authority?**

The research focus is therefore not primarily on producing a more capable language model.

It is on the architecture surrounding AI models.

---

## 2. The Core Problem

A scientific workflow may contain:

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
Subsequent research action
```

A conventional AI interface may primarily expose the final answer.

SciOS investigates whether the surrounding system can preserve the intermediate structure required to answer questions such as:

- What data were used?
- What execution produced the result?
- Which tool was used?
- Which method or model was applied?
- Which evidence supports the inference?
- What is established, uncertain, or unresolved?
- Can the result be inspected or reproduced?
- What action is authorized next?
- What happens when the evidence is insufficient?

---

## 3. Architectural Hypothesis

SciOS treats scientific AI as a systems problem.

The architecture therefore investigates separate concerns including:

- cognition;
- planning;
- reasoning;
- tool use;
- execution;
- evidence;
- provenance;
- governance.

The central hypothesis is that these components should not silently inherit authority from one another.

For example:

```text
Evidence ≠ Inference
Inference ≠ Authorization
Context ≠ Provenance
Provenance ≠ Ownership
Capability ≠ Permission
```

Explicit boundaries are therefore treated as architectural objects rather than merely documentation.

---

## 4. Why Provenance Matters

A scientific result is more useful when the system can expose the chain that produced it.

Conceptually:

```text
Input Data
    │
    ▼
Execution
    │
    ├── Tool
    ├── Method
    ├── Parameters
    └── Environment
    │
    ▼
Result
    │
    ▼
Evidence / Inference
    │
    ▼
Validation State
```

SciOS investigates how such relationships can remain inspectable across a research workflow.

The objective is not to claim that provenance automatically guarantees scientific validity.

Rather, provenance provides information required for later inspection, validation, reproduction, and governance.

---

## 5. Evidence Discipline

A central design principle is:

> **Do not upgrade an unresolved claim into an established capability without evidence.**

Accordingly, SciOS distinguishes states such as:

```text
ESTABLISHED
    │
    └── supported by explicit evidence

NOT ESTABLISHED
    │
    └── insufficient evidence

PLANNED
    │
    └── intended future work
```

`NOT ESTABLISHED` is not automatically equivalent to `FALSE`.

Likewise, contextual origin is not automatically authoritative provenance.

This distinction is particularly important when architectural documents, prior discussions, prototypes, and formal contracts coexist.

---

## 6. Current Research Position

SciOS is currently an:

> **Experimental Research Architecture / Research Prototype**

It is not presented here as:

- an autonomous scientific AGI;
- a completed closed-loop research system;
- a universal scientific reasoning engine;
- a solved hallucination-prevention system;
- or a completed autonomous learning architecture.

Capabilities that have not been sufficiently demonstrated remain explicitly unestablished or planned.

The architecture also preserves a deliberate hold when ownership, provenance, or contract authority has not been established.

---

## 7. Research Principle

The current development principle is:

> **Audit first. Establish ownership. Preserve evidence. Then implement.**

This principle is intended to reduce the risk of architectural assumptions silently becoming implementation authority.

---

## 8. Questions for External Review

SciOS is being presented for technical and scientific criticism, not for validation by reputation.

The following questions are particularly valuable:

1. Are the proposed boundaries between evidence, inference, execution, and authorization meaningful?
2. Which provenance information is actually necessary for reproducible scientific workflows?
3. Where should authority reside in a scientific AI system?
4. Which parts of the architecture require formal methods or machine-checkable contracts?
5. Which claims require empirical validation rather than architectural argument?
6. Where could the proposed architecture introduce unnecessary complexity?
7. Which existing research areas provide stronger or simpler solutions to the same problems?

External criticism may result in architectural revision.

---

## 9. Position Relative to Foundation Models

SciOS does not attempt to replace foundation models.

A foundation model may serve as one cognitive component inside a larger scientific workflow.

Conceptually:

```text
Foundation Model
       │
       ▼
Cognitive Component
       │
       ▼
SciOS Architecture
       │
 ┌─────┼─────────────┐
 ▼     ▼             ▼
Tools Execution   Evidence
       │             │
       └──────┬──────┘
              ▼
          Provenance
              │
              ▼
          Governance
```

The research question is therefore concerned with the system surrounding AI models.

---

## 10. Closing Statement

SciOS is an ongoing research effort.

Its present value should be evaluated through its architecture, explicit assumptions, implementation evidence, tests, provenance, and limitations — not through claims about future autonomous capability.

The project is made available for independent inspection and constructive criticism.

**Audit first. Establish ownership. Preserve evidence. Then implement.**
