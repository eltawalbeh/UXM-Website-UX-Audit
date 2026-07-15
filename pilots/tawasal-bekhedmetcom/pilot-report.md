# UXM Pilot Audit — Tawasal / BekhedmetCom

**Status:** Preliminary public-scope pilot  
**Audited URL:** https://www.tawasal.gov.jo/BekhedmetCom/BekhedmetComDashboard  
**Date:** 14 July 2026  
**Scope:** Public dashboard, request start/OTP screen, English locale sample, and public 404 recovery page.

> This is an expert-review pilot, not an authenticated service audit. No phone number, login credentials, OTP, or personal data were entered.

## Executive snapshot

- **Preliminary public-scope score: 57/100** across 14 applicable checkpoints.
- **6 evidence-backed findings:** 1 High, 4 Medium, 1 Low.
- **4 checkpoints not verified:** contrast measurement, keyboard-only use, narrow mobile view, and controlled performance behavior.

## Fix now

### UXM-001 — High — Phone-number field has no persistent visible label or input example

**Where:** SendOTP / start a new request  
**Why it matters:** The public request journey begins with an ambiguous input, creating avoidable friction before an OTP can be sent.  
**Recommendation:** Add a persistent mobile-number label, a Jordanian format example, and an adjacent required indicator.

## Fix next

- **UXM-002 — Medium:** Add contextual privacy/data-use reassurance at the mobile-number collection step.
- **UXM-003 — Medium:** Standardize English naming, capitalization, and public task copy.
- **UXM-004 — Medium:** Replace the oversized repeated hero with a compact task header on the request-start flow.
- **UXM-005 — Medium:** Improve the 404 page with search and top recovery tasks alongside Home.

## Enhance later

- **UXM-006 — Low:** Give the dashboard satisfaction metric a visible unit, scale, and response base.

## Pilot calibration notes

1. The UXM library correctly separated public evidence from authenticated/unverified flows using `Not verified`; this is essential for government-service audits.
2. The OTP start page exposed a useful library calibration need: public identity/OTP collection should automatically pull a compact **form + trust/privacy + error-recovery** checkpoint bundle.
3. The 404 assessment confirmed that recovery needs a distinct public-service pattern: Home alone is not a sufficient recovery path for a deep-linked citizen journey.
4. The bilingual copy finding validates retaining `CONTENT-25` as a conditional multilingual checkpoint; it should be included whenever Arabic and English are both publicly available.

## Evidence record

Every finding, scope limitation, assessment, and public URL is stored in `audit.json` beside this report. Screenshots were reviewed in-browser during the pilot and should be captured as immutable evidence files in the production audit workspace.
