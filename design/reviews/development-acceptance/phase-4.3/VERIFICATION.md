# Phase 4.3 — Frontend Route Separation Acceptance

**Verified:** 2026-07-19
**Status:** Accepted after independent review

## Canonical routes

| Route | Surface | Runtime boundary |
|---|---|---|
| `/` | Public landing | Does not load operator JavaScript |
| `/login.html` | Operator login scaffold | Authentication disabled and explicitly unavailable |
| `/request-audit.html` | Audit request scaffold | Submission disabled; no data collected |
| `/workspace.html` | Operator system | Loads the existing persisted audit workspace and APIs |
| `/report.html` | Secure shared report surface | Dedicated read-only report document |

Legacy operator subroutes (`/operations.html` and `/templates.html`) remain available and link back to the canonical workspace route.

## Automated verification

- Frontend: `npm test` → **45/45 passed**.
- Backend: `python -m unittest discover -s tests_py -v` → **39/39 passed**.
- Route contract: **6/6 passed**.
- Design-system contract: **5/5 passed**.
- `git diff --check` → passed; CRLF conversion notices only.
- Added-line security scan → no hardcoded secrets, shell injection, dangerous eval/exec, unsafe pickle, or formatted SQL matches.
- No tracked `.env`, SQLite database, or generated PDF artifacts.

## Browser and responsive verification

All five canonical routes were loaded through the real Python API/static server at a true 390px CSS viewport using Chrome DevTools Protocol.

For every route:

```text
innerWidth = 390
clientWidth = 390
scrollWidth = 390
bodyScroll = 390
overflow elements = []
console/runtime errors = []
```

The operator mobile header and navigation were corrected so Operations, Templates, Arabic, PDF report, audit selector, Overview, Criteria, Findings, Scorecard, and Client report remain reachable without a horizontal strip.

## Typography and RTL

- Production UI/report family: `Thmanyah Sans`, with Arial only as system fallback.
- Removed active declarations for Cairo, Inter, Manrope, Georgia, IBM Plex Sans Arabic, and Tahoma.
- Arabic shared report verified with `dir="rtl"`.
- Browser-computed report/title font: `"Thmanyah Sans", Arial, sans-serif`.
- Thmanyah regular and bold binaries loaded successfully.
- Dark report cover title computed to `rgb(255, 253, 248)` after contrast correction.

## Visual evidence

- `landing-390.png`
- `login-390.png`
- `request-audit-390.png`
- `workspace-390.png`
- `shared-report-390.png`
- `routes-390-contact-sheet.png`

No route-separation blocker remains in the final contact-sheet review. Later product slices still own full visual/functional implementation of Landing, Authentication, Request Audit, and the redesigned Operator System.
