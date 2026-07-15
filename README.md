# UXM Audit

A local, evidence-led UX audit workspace. The repository contains the committed pilot JSON and evidence fixtures; local SQLite state, backups, exports, and virtual environments are created on each machine and are not committed.

## Fresh clone → setup → run

**Prerequisites:** Python 3.11+ and Node.js 18+ (for the browser-facing test suite).

On Windows, double-click [`prototype/START-UXM-AUDIT.bat`](prototype/START-UXM-AUDIT.bat). It creates `prototype/.venv`, installs `prototype/requirements.txt`, creates or updates `prototype/data/uxm-audit.db` from the two committed pilot JSON files, opens the browser, then starts the local server.

The Python requirements file is intentionally standard-library-only. To bootstrap without starting the server:

```bash
python scripts/bootstrap_prototype.py
```

Then serve manually:

```bash
cd prototype
python -m backend.api_server
```

Open <http://127.0.0.1:4173>.

## Tests

Run the Python suite from `prototype`:

```bash
python -m unittest discover -s tests_py -v
```

Run the browser/application tests:

```bash
npm test
```

## Direct PDF export

Start the server and use the workspace **Export PDF** control after the audit passes its readiness gate. It calls `POST /api/audits/:auditId/export-pdf?locale=en` (or `ar`) and writes a timestamped PDF to `prototype/artifacts/exports/`.

The export uses installed Google Chrome in headless mode. For a direct API check after starting the server, replace the audit id and run:

```bash
curl -X POST "http://127.0.0.1:4173/api/audits/pilot_jordan_gov_onyourservice_20260714/export-pdf?locale=en"
```

The response supplies a browser-downloadable URL. Generated PDFs are intentionally ignored by Git.
