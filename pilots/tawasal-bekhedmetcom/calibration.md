# UXM Library Calibration — Pilot 001

**Pilot:** Tawasal / BekhedmetCom public-scope audit  
**Date:** 14 July 2026

## Adopted calibration

Three auditable bundles were added to `data/uxm-checkpoints.v1.json`:

1. `public_otp_identity` — automatically suggests form clarity, privacy/data-use, accessibility, and perceived-performance checks when a public service asks for an OTP, mobile number, or equivalent identifier.
2. `public_404_recovery` — suggests contextual recovery checks when public deep links can fail.
3. `multilingual_public_content` — groups bilingual copy parity, visual consistency, titles, and heading clarity whenever multiple locales are public.

## Why this matters

The 272-checkpoint library is broad by design. These bundles prevent an auditor from overlooking high-risk public-service contexts while preserving the conditional, scoped approach. They do not change the score formula or create a new severity system.
