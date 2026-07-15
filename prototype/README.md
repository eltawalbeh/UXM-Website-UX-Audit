# UXM Audit Prototype

A local, evidence-led UX audit workspace and report publisher backed by SQLite.

## What works

1. Select an imported, persisted audit from the workspace picker.
2. View its scope, section health, findings, and client-facing report.
3. Change a checkpoint between Pass, Partial, Issue, Not applicable, and Not verified; changes are explicitly marked **Unsaved changes**.
4. Create an evidence-backed finding with severity, observation, impact, recommendation, and alt text; new findings are also tracked as unsaved.
5. Use **Save changes** to POST the complete active audit to `/api/audits`, or **Discard & reload** to restore the persisted version.
6. Use **Create backup** to call `POST /api/backups` and create a SQLite snapshot in `data/backups`.
7. Attach source and annotated PNG/JPEG evidence to a saved finding. The server validates MIME/signature, size, paths, and persists generated filenames.
8. Use **Check readiness** to see server-enforced publication blockers. **Print / Save PDF** checks `/api/audits/:id/readiness` first and opens the dedicated `report.html` only when `ready` is true.
9. The dedicated report is report-only (no workspace shell), uses A4 landscape print CSS, filters excluded findings, and renders persisted annotated evidence images.

## Run on Windows

Double-click:

```text
START-UXM-AUDIT.bat
```

The prototype opens at:

```text
http://127.0.0.1:4173
```

Or run a release-check server on another port:

```bash
python -m backend.api_server --port 48171
```

## Automated test and acceptance procedure

Run the full suite:

```bash
python -m unittest discover -s tests_py -v
npm test
```

`tests_py/test_release_acceptance.py` is the isolated real-HTTP release path. It uses a temporary SQLite database and verifies:

1. selecting a persisted audit;
2. editing an assessment, saving it, and reloading it;
3. uploading source and annotated evidence;
4. a ready result from the publication gate and the standalone report route;
5. creating a backup; and
6. reading the edited audit back from that backup.

The Node report tests also assert that persisted evidence metadata is rendered as a browser-served image URL and that excluded findings never enter report counts, roadmap, or finding pages.

## Release PDF check (headless Chrome)

Start the server, then generate and inspect the Jordan report:

```bash
REPORT_URL='http://127.0.0.1:48171/report.html?audit=pilot_jordan_gov_onyourservice_20260714&lang=en'
'/c/Program Files/Google/Chrome/Application/chrome.exe' --headless --disable-gpu --no-first-run --run-all-compositor-stages-before-draw --virtual-time-budget=5000 --print-to-pdf='artifacts/jordan-report.pdf' "$REPORT_URL"
pdftotext -layout artifacts/jordan-report.pdf artifacts/jordan-report.txt
```

Release acceptance requires a readiness response with `ready: true`, A4-landscape PDF media boxes (`841.92 × 594.96` points), no workspace-shell strings, all expected finding IDs/counts, and report DOM image URLs for every publishable finding. Capture a cover screenshot with the same URL and Chrome's `--screenshot=...` flag for visual review.

## Publication boundaries

Readiness is a server gate, not an assertion that every user journey has been tested. The Jordan pilot is evidence-ready for its five supported, public-form findings, but its audit scope explicitly excludes form submission/validation, personal-data entry, authenticated/back-office flows, narrow mobile testing, keyboard-only/assistive-technology testing, and English-locale verification. The client report is visibly marked **DRAFT** pending human review/sign-off. Unsupported findings remain excluded from publication and cannot be reintroduced by report rendering.

## Prototype boundary

This Task 9 slice uses a local SQLite database and standard-library Python HTTP server. It serves the static workspace, `/api/audits`, readiness/evidence routes, and `/api/backups`; selecting an audit loads persisted data. Edits stay explicitly in-memory until **Save changes** posts the full audit to `/api/audits`; **Discard & reload** restores the persisted version.
