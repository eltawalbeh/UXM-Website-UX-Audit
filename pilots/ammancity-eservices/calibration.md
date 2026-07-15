# Pilot 3 calibration — Greater Amman Municipality E-Services Portal

- **Audit date:** 2026-07-15
- **Public scope:** Arabic catalog browsing, a safe non-personal keyword search (`ملعب`), the resulting public service information card, and its public user-guide PDF.
- **Routes visited:** catalog; safe search result for **حجز ملعب**; public service card **طلب إصدار مخطط موقع تنظيمي**; public user guide **مخطط موقع تنظيمي والاستعلام عنها**.
- **No-side-effect boundary:** No login, personal/request data, registration, payment, service request, status lookup, OTP or submission was opened or entered. The catalog search used the harmless non-personal term `ملعب` only.
- **Evidence standard:** Every published finding has a source capture, a distinct annotated crop, capture timestamp, direct URL, page and journey metadata. PDF findings use a viewer capture to record the first public view actually presented to a citizen.
- **Excluded verification:** Transaction and lookup flows that request personal/request data, authenticated/back-office workflows, completion/validation, full mobile, keyboard-only, screen-reader, automated contrast/PDF tagging and performance testing.

## Score calibration

Twelve public-scope checkpoints were scored: 5 pass, 2 partial and 5 issue. Using Pass = 1, Partial = 0.5 and Issue = 0, the scoped score is `(5 + 2×0.5) / 12 = 50%`. Three additional checkpoints remain **not verified** and are excluded from the denominator. The score describes the observed public information journeys only; it does not generalize to service completion.

## Publication decision

Publish **5** findings. Two concern catalog discovery/filtering, one comes from the completed harmless search journey, one from the public requirements card, and one from the public instructions route. No finding relies on personal data, a transaction, or a claim about untested service functionality.