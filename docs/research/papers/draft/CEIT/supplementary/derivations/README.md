# CEIT Supplementary Derivations

This directory contains extended mathematical derivations and proofs that support the CEIT research project.  
These derivations provide detailed steps that are too long or technical to include in the main manuscript.

---

# Directory Structure

supplementary/derivations/
├── README.md
├── registry.csv
├── SUP-DER-0001.md
├── SUP-DER-0002.md
└── ...

Code

---

# Naming Convention

Every derivation uses the following format:

SUP-DER-0001
SUP-DER-0002
SUP-DER-0003
...

Code

Rules

- Prefix: `SUP-DER`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every derivation consists of:

- Markdown file (`.md`) containing the derivation
- Registry entry in `registry.csv`
- Reference inside the manuscript

Example

registry.csv
↓
SUP-DER-0001.md
↓
paper.md

Code

---

# Derivation Lifecycle

Draft
↓
Reviewed
↓
Approved
↓
Published

Code

Status is recorded in `registry.csv`.

---

# Markdown Requirements

Each derivation file should:

- Include LaTeX-formatted equations
- Provide step-by-step reasoning
- Reference related equations/tables if applicable
- Use UTF-8 encoding

Example

```markdown
## Extended Derivation of Effective Elasticity (SUP-DER-0001)

Starting from Hooke's law:



\[
\sigma = E \cdot \varepsilon
\]



Under constrained conditions, we derive:



\[
E_{\text{eff}} = \frac{\sigma}{\varepsilon}
\]



This derivation shows how effective elasticity emerges from constraint-induced modifications.
Registry
Every derivation must appear in:

Code
registry.csv
Example

ID	Title	Status
SUP-DER-0001	Extended Elasticity Derivation	Draft


Referencing
Inside the manuscript:

markdown
See Supplementary Derivation SUP-DER-0001.
or

markdown
Supplementary Derivation (SUP-DER-0001)
Best Practices
One derivation = one Markdown file

Keep derivations atomic

Provide clear step-by-step explanations

Register every derivation before using it

Keep filenames synchronized with IDs

Use consistent LaTeX formatting

Related Documentation
registry.csv

paper.md

equations/README.md

tables/README.md

figures/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)