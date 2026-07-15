# Evidence-First PDF Completion Plan

> **For Hermes:** Implement this in order. Do not mark the PDF as delivered until every evidence and print acceptance gate passes.

**Goal:** Replace broad/page-level screenshots with precise, finding-specific evidence crops and in-image callouts, then generate and approve the Monshaat-style UXM PDF.

**Architecture:** Evidence is completed before report rendering is accepted. Each finding has a raw source screenshot, a focused crop, and non-destructive annotation metadata. The dedicated report route renders only the annotated crop for publishable findings. The web workspace remains separate from the PDF surface.

**Sequence decision:** **Finish evidence first → validate evidence → finish PDF output → resume the remaining product tasks.** We do not continue unrelated tasks while the report evidence is untrusted.

---

## Task 1 — Evidence map per finding

**Files:**
- Modify: `scripts/create_evidence_assets.py`
- Modify: `pilots/tawasal-bekhedmetcom/audit.json`
- Modify: `pilots/jordan-gov-onyourservice/audit.json`
- Test: `tests/test_evidence_assets.py`

For each finding, record a specific crop rectangle and a specific focus rectangle based on the actual UI issue. Do not use a generic crop for different issue types.

Examples:
- Phone-field issue: input + its label/help state only.
- Upload-localization issue: upload widget and untranslated labels only.
- Disabled dependency issue: government selector + disabled department selector only.
- Hero/task-focus issue: one wider crop showing the hero and the first task entry point.
- 404 issue: error message + available recovery choices only.

**Acceptance:** Every annotation’s focus rectangle corresponds to the finding’s evidence description. A visual review rejects oversized or unrelated crops.

## Task 2 — Re-capture the two blocked Tawasal findings

**Files:**
- Create: `evidence/raw/tawasal/sendotp-en.png`
- Create: `evidence/raw/tawasal/dashboard-metrics.png`
- Modify: `pilots/tawasal-bekhedmetcom/audit.json`

1. Capture the English SendOTP state before using it for the English-copy finding.
2. Capture the actual dashboard state containing the satisfaction metric. If the dashboard cannot be captured reliably, remove the metric finding from the client report rather than presenting unsupported evidence.

**Acceptance:** `UXM-003` and `UXM-006` are either supported by correct source captures or are excluded from the publishable finding set with a recorded rationale.

## Task 3 — Regenerate and verify all evidence assets

**Files:**
- Modify: `scripts/create_evidence_assets.py`
- Modify: `tests/test_evidence_assets.py`

**Verification:**
```text
python scripts/create_evidence_assets.py
python -m pytest tests/test_evidence_assets.py -v
```

Required test assertions:
- crop is smaller than source image;
- annotation contains exact crop/focus coordinates and marker;
- each evidence file is readable;
- each included finding is supported, or is excluded and cannot enter the report.

## Task 4 — Sync approved data into SQLite and report route

**Files:**
- Modify: `prototype/backend/storage.py` or an explicit import command
- Modify: `prototype/src/report-renderer.js`
- Test: `prototype/tests/report-renderer.test.js`

**Acceptance:** The database audit record contains the approved image paths and annotations. The report shows only the focused annotated image. Evidence-pending findings display publication-blocked state and cannot be exported in a client report.

## Task 5 — PDF visual acceptance

**Files:**
- Modify if needed: `prototype/report-print.css`, `prototype/report.js`

For each pilot and language:
1. Open `report.html?audit=<id>&lang=en|ar`.
2. Review web report evidence crops.
3. Open print preview with A4 landscape.
4. Verify one evidence-led finding page per finding; no workspace shell; no squeezed page; no clipped screenshot; no split finding.
5. Save PDF and review every PDF page.

**Completion condition:** Only after all evidence pages are visual-approved do we call the PDF/report part of Task 9 complete. Then we resume remaining product tasks: editor save controls, evidence upload workflow, full section scoring, and release hardening.
