# Client Report Layout & Export Remediation

**Goal:** Repair the workspace Client Report layout and direct PDF export before any further product expansion.

## Confirmed defects from user evidence
1. Finding page grid has unbounded/min-content columns, producing horizontal overflow and variable evidence/text widths.
2. Evidence image areas have unstable sizing; the text column becomes extremely narrow.
3. Scorecard uses an oversized intro-to-card gap and the report cover has excess title-to-summary whitespace.
4. Header actions are noisy: Preview report redundant, Create backup premature, save/discard lack contextual presentation, and UXM Audit is not a logo treatment.
5. Direct PDF export is not functioning in the user runtime and must be verified end-to-end through the UI.

## Execution order
1. Reproduce export failure and write a failing end-to-end test for the exact API/UI path.
2. Replace finding layout with bounded grid: `minmax(0, 1fr)` evidence column plus fixed/clamped prose column; `max-width:100%`, overflow containment, image `object-fit:contain`, and mobile single-column fallback.
3. Define a single finding evidence frame ratio and minimum/maximum dimensions so each crop is readable but never expands the page.
4. Tighten report cover and scorecard spacing tokens; validate desktop and narrow widths.
5. Simplify header: image logo mark, remove Preview report, hide/defer backup, contextual dirty/save controls; rename CTA to `PDF report`.
6. Repair direct export to return an actual downloadable PDF with deterministic errors when Chrome is unavailable; verify no browser header/footer.
7. Perform screenshot, DOM-overflow, PDF text/page, and visual acceptance tests for Jordan and Tawasal.

## Gate
No return to new product work until no horizontal overflow exists, every finding has consistent evidence/prose geometry, and PDF export is exercised successfully through the visible user CTA.