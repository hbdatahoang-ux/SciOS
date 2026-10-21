# CEIT Extended Methods

This directory contains extended methodological details that support the CEIT research project.  
These methods provide additional experimental protocols, computational workflows, or theoretical procedures that are too detailed to include in the main manuscript.

---

# Directory Structure

extended_methods/
├── README.md
├── registry.csv
├── EM-0001.md
├── EM-0002.md
└── ...

Code

---

# Naming Convention

Every extended method uses the following format:

EM-0001
EM-0002
EM-0003
...

Code

Rules

- Prefix: `EM`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every extended method consists of:

- Markdown file (`.md`) containing the method description
- Registry entry in `registry.csv`
- Reference inside the manuscript

Example

registry.csv
↓
EM-0001.md
↓
paper.md

Code

---

# Method Lifecycle

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

Each method file should:

- Provide step-by-step protocol or workflow
- Include figures/tables references if applicable
- Use UTF-8 encoding
- Include metadata (author, version, status, created/modified dates)

Example

```markdown
## Extended Microfluidic Protocol (EM-0001)

Step 1: Prepare microchannel with width 800 µm.  
Step 2: Inject fluid at flow rate 2.5 mL/min.  
Step 3: Maintain ambient temperature at 25 °C.  

This extended method provides detailed setup instructions for replicating the microfluidic experiment.
Registry
Every extended method must appear in:

Code
registry.csv
Example

ID	Title	Status
EM-0001	Extended Microfluidic Setup	Draft


Referencing
Inside the manuscript:

markdown
See Extended Method EM-0001.
or

markdown
Extended Method (EM-0001)
Best Practices
One method = one Markdown file

Keep methods atomic

Provide clear step-by-step instructions

Register every method before using it

Keep filenames synchronized with IDs

Use consistent formatting

Related Documentation
registry.csv

paper.md

tables/README.md

figures/README.md

equations/README.md

supplementary/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)