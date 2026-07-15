# UXM Pilot 3 — Greater Amman Municipality E-Services Portal

**Audit ID:** `pilot_ammancity_eservices_20260715`  
**Public catalog URL:** https://www.ammancity.gov.jo/ar/gameservices/eservices.aspx  
**Public routes audited:** catalog browse; safe `ملعب` search → `حجز ملعب`; service-card PDF; user-guide PDF.  
**Scope result:** **50%** across 12 scored public-scope checkpoints; 3 checkpoints not verified.  
**Publishable findings:** **5**

## Executive summary

This revision expands the audit from one catalog state into four real public/no-login information routes and four low-risk journeys. The catalog can return a safe non-personal search, and its public requirements and user-guide links open without authentication. The observed friction now spans discovery (ambiguous filter state, obstructive notification, sparse search result) and information consumption (dense requirements PDF and an instruction guide that starts without task guidance).

This is **not** an evaluation of application, login, lookup, payment or submission flows. Those paths were deliberately not entered because they require personal/request data or could create external side effects.

## Routes and journeys visited

| Journey | Route | Safe action taken | Outcome |
|---|---|---|---|
| Browse services | Public catalog | Browse visible cards | Public card inventory visible |
| Find a service | Public catalog | Entered harmless non-personal term `ملعب` and searched | Returned `حجز ملعب` |
| Read requirements | Service-card PDF | Opened `daleeldepts/7.pdf` | One-page public requirement card opened |
| Read instructions | User-guide PDF | Opened `usermanual/10.pdf` | Six-page public guide opened |

## Evidence-backed findings

### UXM-001 — The sector filter sends contradictory requiredness signals
- **Severity:** Medium · **Journey:** Find a service
- **Evidence:** `evidence/raw/ammancity/eservices-catalog-20260715.png`; `evidence/annotated/ammancity-eservices/UXM-001.png`
- **Observation:** The sector label visibly combines a red asterisk and `اختياري` (optional).
- **Recommendation:** Adopt one unambiguous requiredness state.

### UXM-002 — A fixed notification obscures catalog content and filtering controls
- **Severity:** Medium · **Journey:** Browse the public catalog
- **Evidence:** `evidence/raw/ammancity/eservices-catalog-20260715.png`; `evidence/annotated/ammancity-eservices/UXM-002.png`
- **Observation:** The red SMS notice overlaps public catalog content and the filter/result region.
- **Recommendation:** Move non-critical notifications into page flow or reserved space, with a prominent dismissal control if needed.

### UXM-003 — The safe search result separates service information actions with empty card space
- **Severity:** Medium · **Journey:** Safe `ملعب` search
- **Evidence:** `evidence/raw/ammancity/eservices-search-malaab-20260715.png`; `evidence/annotated/ammancity-eservices/UXM-003.png`
- **Observation:** `حجز ملعب` is returned in a tall sparse card; its service-card and guide links are at the bottom.
- **Recommendation:** Keep title, sector, key actions and a short description together in a compact result.

### UXM-004 — Public service requirements are dense at the default fitted PDF view
- **Severity:** Medium · **Journey:** Open public service requirements
- **Evidence:** `evidence/raw/ammancity/service-card-7-viewer-20260715.png`; `evidence/annotated/ammancity-eservices/UXM-004.png`
- **Observation:** Requirement details are compressed into tightly ruled table rows in the browser’s fitted view.
- **Recommendation:** Provide a responsive HTML summary alongside the formal PDF.

### UXM-005 — The public user guide opens on a branding-only cover before task guidance
- **Severity:** Low · **Journey:** Open public user instructions
- **Evidence:** `evidence/raw/ammancity/user-guide-10-viewer-20260715.png`; `evidence/annotated/ammancity-eservices/UXM-005.png`
- **Observation:** The six-page guide’s first visible page has branding and title but no steps, contents or quick-start link.
- **Recommendation:** Make the first page/screen a concise purpose, prerequisites and linked steps entry point.

## Boundaries and next validation

No personal data, filters other than the harmless keyword, forms, login, payments, requests, status lookup, registration, OTP or service-card primary actions were used. If authorised, next validation should test the full filter behavior, the public service-card links at mobile widths, PDF accessibility/tagging, keyboard paths, and—under separate consent and test data—transactional service flows.