# Lightspeed — Vol. 02 · The Six Weeks

A documentary intelligence report covering the six weeks **15 May – 26 June 2026 (NZT)** of
Citadel Capital's "Lightspeed" operating-layer programme, rendered in the established
*Softer Volumes* magazine style (the soft stone-and-ink palette settled on for the Vol. 01
three-month roundup).

## Deliverables
- `2026-06-26_002_report_lightspeed-vol02-six-weeks.pdf` — 33-page A4 report (print-ready).
- `2026-06-26_002_report_lightspeed-vol02-six-weeks.html` — self-contained HTML (CSS + images inlined).

## Source
- `source-report.html` — the authored markup (uses a `__CSS__` token and `plates/` image refs).
- `source-styles.css` — the merged stylesheet (base Softer Volumes system + Vol. 02 data-viz
  additions + page-fit overrides).

## What it covers
Built from a full multi-surface trawl — Dropbox daily briefings + event sidecars, Gmail, Google
Drive, Calendar, Notion, and the Lightspeed brain corpus. Four sections:
- **Projects** — McLeans Mansion, RYU Albany, Babich Rise, 126 Featherston.
- **Fronts** — the Citadel Capital → Hyperion One administration, the IRD/NOPA tax-loss chess,
  ERA 3407924, the new criminal file (Police v Moinfar), and the Castra litigation suite.
- **Field** — the Christchurch theatre, the acquisition pipeline, and the counterparty room.
- **Machine** — Lightspeed in production, the research desk, the gaps identified, and the plan.

The closing Machine section is deliberately candid: every available signal was captured and the
coverage gaps (frozen Notion state, missing control plane, `sheba` down, telemetry masking faults,
runtime EOL) are named rather than papered over.

## Rebuild
Rendered with headless Chromium (Playwright). To regenerate the PDF from the self-contained HTML:
`chromium --headless --print-to-pdf=out.pdf report.html` (or the Playwright `page.pdf({ preferCSSPageSize: true })` path).
