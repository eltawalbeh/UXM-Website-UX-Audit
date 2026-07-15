# UXM Pilot Audit — Jordan.gov / بخدمتكم

**Status:** Preliminary public-form pilot  
**Audited URL:** https://jordan.gov.jo/ar/custompages/onyourservice  
**Date:** 14 July 2026

> No form was submitted and no personal information, attachment, OTP, or credentials were entered.

## Executive snapshot

- **Preliminary public-scope score: 50/100** across 10 applicable checkpoints.
- **5 evidence-backed findings:** 1 High, 3 Medium, 1 Low.
- **5 checks not verified:** submission validation, contrast measurement, keyboard-only use, mobile viewport, and English locale verification.
- **Environment note:** The language switch triggered a Cloudflare block in the audit browser. This is recorded as a test limitation, not a product finding.

## Fix now

### UXM-001 — High — Sensitive request data lacks contextual privacy/data-use reassurance

**Recommendation:** Add concise data-use/retention reassurance directly above Send, with a contextual privacy-policy link.

## Fix next

- **UXM-002:** Localize the entire Arabic attachment flow; remove English widget text.
- **UXM-003:** Prioritize the service-request task over large banner and peripheral support modules.
- **UXM-004:** Explain the government-to-department field dependency before users reach a disabled control.

## Enhance later

- **UXM-005:** Add practical prompts/examples for subject and details.

## Cross-pilot comparison

Both pilots involve public government-service submission flows. The repeated signals are:

1. **Privacy context at point of collection** is consistently more important than a footer-only policy link.
2. **Bilingual/RTL parity** needs formal verification of all third-party widgets—not only static page copy.
3. **Task focus** is vulnerable when branded hero/support content remains on transactional pages.
4. **Field dependencies and input guidance** are recurring public-service risk areas.

These patterns support the previously added `public_otp_identity` and `multilingual_public_content` bundles. A fourth bundle, `public_service_submission`, has now been added to formalize checkpoint selection for public forms that collect personal details and/or attachments.
