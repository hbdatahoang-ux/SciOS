# SciOS Artifact Lifecycle v1.0

Version: 1.0  
Status: Draft  
Authors: SciOS Research Team

---

## Overview
This document defines the lifecycle states and transitions for all artifacts in SciOS.  
Every artifact SHALL follow the same standardized lifecycle to ensure consistency, traceability, and reproducibility.

---

## Lifecycle States

1. **Draft**
   - Artifact created but incomplete.
   - Metadata present but may be partial.
   - Files may be preliminary or placeholders.
   - Not yet validated.

2. **Internal Review**
   - Artifact submitted for team review.
   - Metadata must be complete.
   - Dependencies declared.
   - Reviewer assigned.

3. **Approved**
   - Artifact validated and approved by reviewer.
   - Metadata and files pass validation rules.
   - Registry entry confirmed.
   - Dependencies resolved.

4. **Published**
   - Artifact included in official paper or release.
   - DOI assigned if applicable.
   - Immutable ID enforced.
   - Artifact is considered authoritative.

5. **Archived**
   - Artifact retired or superseded.
   - Preserved for historical traceability.
   - Registry entry marked as archived.
   - No further modifications allowed.

---

## Transition Rules

- **Draft → Internal Review**
  - Requires complete metadata.
  - Requires initial files (PNG, CSV, equation.md, etc.).
  - Reviewer assigned.

- **Internal Review → Approved**
  - Reviewer validation complete.
  - Dependencies checked.
  - Registry updated.

- **Approved → Published**
  - Artifact referenced in paper or supplementary material.
  - DOI assigned (optional).
  - CI/CD validation passed.

- **Published → Archived**
  - Artifact superseded by newer version.
  - Archived for provenance.
  - Registry updated with archival status.

---

## Compliance Checklist

- Metadata complete and valid.
- Registry entry exists and matches metadata.
- Dependencies declared and resolved.
- Files present and accessible.
- Lifecycle state updated consistently.

---

## Example Lifecycle

