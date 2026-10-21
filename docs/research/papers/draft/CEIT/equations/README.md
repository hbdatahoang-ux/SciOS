# CEIT Equations

This directory contains all analytical, symbolic, and computational equations used in the CEIT research project.

Every equation must have a unique identifier and be registered in `registry.csv`.

---

# Directory Structure

equations/
├── README.md
├── registry.csv
├── EQ-0001.md
├── EQ-0002.md
└── ...

Code

---

# Naming Convention

Every equation uses the following format:

EQ-0001
EQ-0002
EQ-0003
...

Code

Rules

- Prefix: `EQ`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every equation consists of:

- Markdown file (`.md`) containing the equation and explanation
- Registry entry in `registry.csv`
- Reference inside the manuscript

Example

registry.csv
↓
EQ-0001.md
↓
paper.md

Code

---

# Equation Lifecycle

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

Each equation file should:

- Include LaTeX-formatted equation(s)
- Provide a textual explanation
- Reference related figures/tables if applicable
- Use UTF-8 encoding

Example

```markdown
## Effective Elasticity Equation (EQ-0001)



\[
E_{\text{eff}} = \frac{\sigma}{\varepsilon}
\]



This equation defines the effective elasticity under constrained conditions.
Registry
Every equation must appear in:

Code
registry.csv
Example

ID	Title	Status
EQ-0001	Effective Elasticity Equation	Approved


Referencing
Inside the manuscript:

markdown
See Equation EQ-0001.
or

markdown
Equation (1) [EQ-0001]
Versioning
Equations may evolve.

Example

Code
v0.1
v0.2
v1.0
IDs remain unchanged.

Best Practices
One equation = one Markdown file

Keep equations atomic

Provide clear explanations

Register every equation before using it

Keep filenames synchronized with IDs

Use consistent LaTeX formatting

Related Documentation
registry.csv

paper.md

references.bib

tables/README.md

figures/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)