# UXM Pilot 3 — Greater Amman Municipality E-Services Portal

**Audit ID:** `pilot_ammancity_eservices_20260715`  
**Public URL:** https://www.ammancity.gov.jo/ar/gameservices/eservices.aspx  
**Scope:** Public Arabic e-services catalog, desktop 1440 × 1200; observation only.  
**Result:** **50%** across 6 scored checkpoints; 3 checkpoints not verified.  
**Publishable findings:** **2**

## Executive summary

The captured public catalog provides visible navigation and filter controls, but two basic interaction-quality issues are directly evidenced. The sector filter combines contradictory optional/required cues, and a fixed notification blocks content within the service catalog. Both should be remediated before expanding transactional testing.

## Evidence-backed findings

### UXM-001 — The sector filter sends contradictory requiredness signals

- **Severity:** Medium
- **Journey:** Find a service
- **Evidence:** `evidence/raw/ammancity/eservices-portal.png`; `evidence/annotated/ammancity-eservices/UXM-001.png`
- **Observation:** The sector label visibly contains a red asterisk and “اختياري” (optional).
- **Recommendation:** Adopt one unambiguous requiredness state and apply it consistently.

### UXM-002 — A fixed notification obscures a service card while users browse the catalog

- **Severity:** Medium
- **Journey:** Browse services
- **Evidence:** `evidence/raw/ammancity/eservices-portal.png`; `evidence/annotated/ammancity-eservices/UXM-002.png`
- **Observation:** A red notification overlay covers the visible second-row service-card area.
- **Recommendation:** Move non-critical notices into page flow or reserved layout space; make dismissal clear and return content access immediately.

## Boundaries and next validation

No personal data, filters, forms, login, payments, requests, or other external side-effecting actions were used. The next phase, if authorised, should validate filter behavior, the catalogue’s responsive/mobile experience, keyboard behavior, and the public service-card detail routes.
