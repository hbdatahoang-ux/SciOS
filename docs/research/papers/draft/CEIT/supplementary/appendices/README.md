# CEIT Appendices

This directory contains appendices for the CEIT research project.  
Appendices provide extended background, supporting notes, or additional documentation that complements the main manuscript.

---

# Directory Structure

appendices/
├── README.md
├── registry.csv
├── APP-0001.md
├── APP-0002.md
└── ...

Code

---

# Naming Convention

Every appendix uses the following format:

APP-0001
APP-0002
APP-0003
...

Code

Rules

- Prefix: `APP`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every appendix consists of:

- Markdown file (`.md`) containing the appendix content
- Registry entry in `registry.csv`
- Reference inside the manuscript

Example

registry.csv
↓
APP-0001.md
↓
paper.md

Code

---

# Appendix Lifecycle

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

Each appendix file should:

- Provide structured content (sections, subsections)
- Include references to related tables, figures, or equations
- Use UTF-8 encoding
- Include metadata (author, version, status, created/modified dates)

Example

```markdown
## Appendix: Experimental Setup (APP-0001)

This appendix provides detailed notes on the laboratory setup used in CEIT experiments.

- Microchannel dimensions: 800 µm × 50 µm
- Flow rate: 2.5 mL/min
- Temperature: 25 °C

See Table T-0001 for parameters.
Registry
Every appendix must appear in:

Code
registry.csv
Example

ID	Title	Status
APP-0001	Experimental Setup	Draft


Referencing
Inside the manuscript:

markdown
See Appendix APP-0001.
or

markdown
Appendix A (APP-0001)
Best Practices
One appendix = one Markdown file

Keep appendices atomic

Provide clear context and metadata

Register every appendix before using it

Keep filenames synchronized with IDs

Use consistent formatting

Related Documentation
registry.csv

paper.md

tables/README.md

figures/README.md

equations/README.md

supplementary/README.md

extended_methods/README.md

additional_results/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)