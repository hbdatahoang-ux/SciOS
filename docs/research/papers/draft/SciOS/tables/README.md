# Tables for Paper

Version: 1.0  
Status: Draft  
Authors: Paper Research Team

---

## Overview
This directory contains **Table artifacts** used in this paper.  
Tables represent structured data, results, or comparisons that support experiments, models, and benchmarks.

---

## Structure
Each table is stored as a CSV file (`T-XXXX.csv`) with metadata registered in `registry.csv`.

---

## Registry
All tables must be listed in [registry.csv](registry.csv).  
Registry entries must match metadata fields and follow [naming_convention.md](ca://s?q=Explain_Artifact_Naming_Convention).

---

## Lifecycle
Tables follow the standard lifecycle ([lifecycle.md](ca://s?q=Explain_Artifact_Lifecycle)):

Draft → Internal Review → Approved → Published → Archived  

---

## Validation
Tables must pass checks defined in [validation_rules.md](ca://s?q=Explain_Validation_Rules):

- Metadata completeness  
- Naming consistency  
- Registry entry validation  
- File existence (`T-XXXX.csv`)  
- Dependency graph integrity  

---

## Notes
- Tables are immutable once **Published**.  
- Updates require version increment following [versioning.md](ca://s?q=Explain_Artifact_Versioning).  
