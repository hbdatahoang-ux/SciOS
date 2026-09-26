# Figures – SciOS Paper

This directory contains all figures used in the SciOS paper.  
Each figure must be registered in `registry.csv` with a unique ID (e.g., F‑0001, F‑0002).

---

## Structure

- **registry.csv** → Master list of all figures (ID, title, description, file path, status).
- **F‑0001.png** → Kernel Architecture schematic.
- **F‑0002.png** → Runtime Workflow diagram.
- Additional figures follow the same naming convention.

---

## Guidelines

1. **Naming Convention**
   - Use IDs: `F-XXXX` (e.g., F‑0001, F‑0002).
   - File format: `.png` or `.svg` for vector graphics.

2. **Registry**
   - Every figure must be listed in `registry.csv`.
   - Include metadata: ID, caption, source, related section.

3. **Captions**
   - Captions are stored in `paper.md` and cross‑referenced with registry.

4. **Versioning**
   - Update `registry.csv` when figures are revised.
   - Keep old versions in `archive/` if necessary.

---

## Example Registry Entry

```csv
ID,Title,Description,File,Section,Status
F-0001,Kernel Architecture,Schematic of SciOS kernel modules,F-0001.png,Architecture,Final
F-0002,Runtime Workflow,Diagram of reproducible runtime workflow,F-0002.png,Methods,Draft
