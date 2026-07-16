# UXM Audit

A local, evidence-led UX audit workspace. The repository contains the committed pilot JSON and evidence fixtures; local SQLite state, backups, exports, and virtual environments are created on each machine and are not committed.

## Fresh clone → setup → run

**Prerequisites:** Python 3.11+ and Node.js 18+ (for the browser-facing test suite).

On Windows, double-click [`prototype/START-UXM-AUDIT.bat`](prototype/START-UXM-AUDIT.bat). It creates `prototype/.venv`, installs `prototype/requirements.txt`, creates or updates `prototype/data/uxm-audit.db` from the committed pilot JSON files, opens the browser, then starts the local server.

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

## Client and project operations

Open <http://127.0.0.1:4173/operations.html> or use **Operations** in the audit workspace header.

The operations workspace persists this hierarchy in local SQLite:

```text
Client → Project → Linked audits
```

It supports client and project creation, project search, product type and owner metadata, audit linking, and the project lifecycle states `Draft`, `In review`, `Evidence complete`, `Ready for client`, and `Delivered`. Existing unlinked pilot audits are migrated into client/project records idempotently when the server starts.

The current browser surfaces are functional workflow prototypes. A separate final UX-polish phase will replace the visual and interaction design before final acceptance.

## Audit templates

Open <http://127.0.0.1:4173/templates.html> or use **Templates** from the workspace or operations header.

The versioned catalog in `data/audit-templates.v1.json` contains five reusable baselines: Government / Civic Service, Corporate / Marketing, E-commerce, SaaS / Digital Product, and Content / Publisher. Each template defines a product type, default scope bundle, journeys, official UXM checkpoint IDs, evidence requirements, and report sections.

Creating from a template persists a new audit under the selected project. Every selected checkpoint begins as `not_verified`; findings, scores, evidence, and AI output are never fabricated. A new template audit remains **Not scored** until at least one applicable checkpoint is assessed.

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
