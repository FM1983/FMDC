# 3370 Great North Road — Mixed Residential Scheme (output 008)

Citadel-branded concept-development pack for the 809 m² THAB site at 3370 Great North
Road, Glen Eden. Built from the self-contained handoff brief (CLAUDE.md / specs / locked
data) for output **008**, dated **2026-06-25**.

## Deliverables (four-file set)
- `3370 Great North Road - Mixed Residential Scheme.pdf` — primary pack (A4, 11 pages)
- `2026-06-25_008_feasibility_mixed-residential-scheme.md` — full markdown twin
- `2026-06-25_008_summary_mixed-residential-scheme.md` — condensed summary

(The PDF lives in `_outputs/` and is mirrored to `04 Design/` and/or
`09 Investment Committee/` in the Citadel vault; the twin → `_llm/outputs/`, summary →
`_llm/summaries/`. Filenames use hyphens only — no em/en dashes.)

## Build
```bash
pip install reportlab matplotlib numpy
cd scripts
python3 model_logic.py     # verifies the locked base case (margin 24.7%, land $1,761/m², total $9,144,378)
python3 build_visuals.py   # regenerates the six schematic figures -> ../figures/
python3 build_pack.py      # assembles the PDF
```

## Contents
- `scripts/build_pack.py` — the PDF builder (brand helpers + 11-page layout)
- `scripts/build_visuals.py` — the six schematic diagram generators
- `scripts/model_logic.py` — self-contained feasibility recompute (sensitivity rows)
- `scripts/mixed_scheme.json` — the LOCKED figures (source of every number)
- `figures/` — generated schematic PNGs (site plan, axonometric, stacking, two unit
  plates, elevation)

## The one rule that matters most
Every visual is an **indicative schematic diagram** only — flat blocks, labelled zones,
never photoreal or to-scale architecture — and every figure carries the caption:
*"Indicative schematic only — not to scale, not for construction or resource consent.
Architectural design to be prepared by a registered architect."* Interiors are credited
to Studio 11:11; the building architect is "to be appointed".

## Status note
This pack is the recommended **development concept** and the value story underpinning the
consented envelope. The current live transaction thesis is a capital-light,
vendor-financed flip; this development case is the fallback / buyer-facing concept, not
the base transaction plan.
