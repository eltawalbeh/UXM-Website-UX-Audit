# UXM Print Report & Delivery Readiness Implementation Plan

> **For Hermes:** Use strict TDD and complete each acceptance gate before declaring a feature complete.

**Goal:** Deliver a client-ready, print/PDF report that follows the Monshaat report rhythm and UXM visual language, while keeping the web workspace as a separate operational surface.

**Architecture:** One audit record in SQLite remains the sole source of truth. The web workspace is optimized for auditing and editing; the print renderer is a dedicated, paginated report route with its own A4 landscape stylesheet and report-only components. The two surfaces deliberately do not share a visual layout, but both consume the same persisted audit data.

**Tech stack:** Existing stdlib Python HTTP server, SQLite, static HTML/CSS/JS, native browser Save as PDF initially; no third-party PDF renderer until browser output passes visual acceptance.

---

## Non-negotiable completion gates

A task is **not complete** because a button, route, or placeholder exists. It is complete only when all gates below pass with recorded evidence.

1. **Source-of-truth gate:** selected pilot score, applicable count, findings count, severity distribution, and report data match SQLite exactly.
2. **Web audit gate:** workspace shows the correct audit and can load a different persisted audit without stale data.
3. **Print-report gate:** printing opens a report-only document—not the dashboard—with no workspace nav, controls, edit fields, or prototype labels.
4. **Monshaat-structure gate:** PDF contains the required report sequence: Cover → Executive Snapshot → Scope/Methodology → Severity & Category Legend → Scorecard → Priority Roadmap → Section divider(s) → one Finding per page → Conclusion/validation → Closing.
5. **Finding-evidence gate:** every published finding has screenshot/annotated evidence, issue ID, severity, category, page/journey, URL, capture metadata, observed/impact/recommendation.
6. **Arabic gate:** Arabic document is native RTL; no English temporary labels; URLs, IDs, browser strings, and screenshots remain correctly isolated/not mirrored.
7. **Visual gate:** A4 landscape page breaks are intentional; no clipped content, split finding pages, orphan headings, tiny body text, dashboard KPI-card grids, or missing severity text labels.
8. **Export gate:** a user can choose Print or Save as PDF and obtain a complete report file. The exported PDF is visually reviewed page-by-page against the gates above.
9. **Regression gate:** automated data/API tests plus browser smoke tests run for both pilots before delivery.

---

## Task 1: Correct score and coverage presentation

**Files:**
- Modify: `prototype/app.js`
- Test: `prototype/tests/display-score.test.js`

**Acceptance:** The UI shows 57 for Tawasal and 50 for Jordan.gov because those persisted audit summaries are authoritative. The score label says `Preliminary` whenever scope exclusions or `Not verified` checks exist. Coverage states assessed/applicable counts; no prototype-only score is presented as a client score.

## Task 2: Model report metadata and publication readiness

**Files:**
- Modify: `prototype/backend/storage.py`
- Modify: `prototype/backend/api_server.py`
- Create: `prototype/backend/report_readiness.py`
- Test: `prototype/tests_py/test_report_readiness.py`

**Acceptance:** A report cannot be marked publishable if a finding lacks evidence file/description, page/journey, URL, capture date/device, impact, recommendation, or required translation. The API returns a human-readable readiness checklist.

## Task 3: Add evidence-file storage and annotations

**Files:**
- Modify: `prototype/backend/storage.py`
- Modify: `prototype/backend/api_server.py`
- Modify: `prototype/app.js`
- Create: `prototype/data/evidence/.gitkeep`
- Test: `prototype/tests_py/test_evidence_api.py`

**Acceptance:** An auditor can attach a local screenshot to a finding. The system records immutable filename, MIME type, capture metadata, alt text, and annotation coordinates. The report renders the actual evidence image, not an alt-text placeholder.

## Task 4: Build dedicated print-report route and A4 layout

**Files:**
- Create: `prototype/report.html`
- Create: `prototype/report.js`
- Create: `prototype/report-print.css`
- Modify: `prototype/app.js`
- Test: `prototype/tests/report-model.test.js`

**Acceptance:** `Print / Save PDF` opens `report.html?audit=<id>&lang=en|ar`. This route has a report shell only; it does not render workspace navigation. CSS uses `@page { size: A4 landscape; }`, deliberate breaks, and a `finding-page` rule to keep each finding together.

## Task 5: Implement the Monshaat-inspired UXM report sequence

**Files:**
- Modify: `prototype/report.js`
- Modify: `prototype/report-print.css`
- Test: `prototype/tests/report-model.test.js`

**Required pages:**
1. Cover
2. Executive Snapshot
3. Scope & Methodology
4. Severity & Category Legend
5. Scorecard
6. Priority Roadmap
7. Section Summary/Divider
8. One Finding Detail page per finding
9. Conclusion & Validation
10. Closing

**Acceptance:** The report uses evidence-led editorial pages, never a dashboard export. Each finding page has large evidence canvas and concise metadata rail, as defined in `design/screens/client-report-en.md` and `design/screens/client-report-ar.md`.

## Task 6: Create Arabic report as an independent RTL render

**Files:**
- Modify: `prototype/report.js`
- Modify: `prototype/report-print.css`
- Test: `prototype/tests/report-model.test.js`

**Acceptance:** Arabic output follows `design/screens/client-report-ar.md`: RTL shell and Arabic labels; stable IDs/URLs remain LTR; screenshots are not flipped; all translated finding content is required before publication.

## Task 7: Add print and PDF acceptance automation

**Files:**
- Create: `prototype/tests_py/test_report_routes.py`
- Modify: `prototype/README.md`

**Acceptance:** Tests validate report data and readiness. Browser smoke tests open both pilots’ report route, verify the selected audit’s title/score/finding count, invoke native print preview, and capture the produced PDF for manual page-by-page visual review.

## Task 8: Final verification matrix

Run for both Tawasal and Jordan.gov:

```text
python -m unittest discover -s tests_py -v
npm test
```

Then verify manually:
- switch audit → title, score, coverage, and findings match the stored audit JSON
- English report pages 1–N satisfy the Monshaat-derived sequence
- Arabic RTL report pages 1–N satisfy the RTL rules
- print preview has clean A4 landscape pagination
- Save as PDF produces a readable report containing every finding exactly once
- evidence screenshot/annotations match the linked finding

Only after this matrix is complete may Task 9 be labelled delivered.
