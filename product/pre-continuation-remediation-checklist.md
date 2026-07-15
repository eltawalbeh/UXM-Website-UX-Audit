# UXM Audit — Pre-Continuation Remediation Checklist

This checklist must be completed and verified before building the client PDF/report renderer or advancing Task 9.

## A. Audit truth and scoring
- [ ] Keep the persisted `assessmentSummary.score` authoritative for every imported audit.
- [ ] Replace prototype-only section buckets (navigation/forms/accessibility) with section scores calculated from the actual applicable checkpoint IDs in the stored audit.
- [ ] Show assessed/applicable denominator, `Not applicable`, and `Not verified` counts beside every client-facing score.
- [ ] Verify switching Tawasal ↔ Jordan.gov updates title, score, scope, finding count, severity distribution, and section data together.
- [ ] Remove every demo/prototype label from client-facing views.

## B. Evidence capture is mandatory
- [ ] Create a local evidence directory per audit and finding.
- [ ] Capture a real source screenshot for each existing finding (11 total), without entering personal data or submitting public-service forms.
- [ ] Create a non-destructive annotated copy for every finding.
- [ ] Store screenshot path, original URL, device/browser, capture time, alt text, and annotation metadata in SQLite.
- [ ] Block client report publication/PDF rendering if any included finding has no evidence image.

## C. Workspace UI quality
- [x] Reserve a dedicated chevron area in the Workspace audit selector; truncate long audit names instead of overlapping the arrow.
- [x] Render object-based scopes as readable included-scope text; never expose `[object Object]`.
- [ ] Add responsive selector checks for desktop and narrow widths.
- [ ] Ensure loading, empty, API-error, and long-name states are intentional and readable.
- [ ] Do not display prototype-derived 0% section rows for sections outside the current audit mapping.

## D. Print/PDF safety
- [ ] Remove the temporary workspace-print behavior from the delivery path.
- [ ] Build a dedicated report-only route; workspace controls, navigation, inputs, and status labels must never print.
- [ ] Add A4 landscape print CSS with controlled page breaks and one finding per evidence-led page.
- [ ] Implement the Monshaat-derived page sequence defined in `design/screens/client-report-en.md` and `design/screens/client-report-ar.md`.
- [ ] Open print preview and inspect every generated page before accepting either pilot as export-ready.

## E. Verification contract
- [ ] Test score/coverage calculations against both stored pilot records.
- [ ] Test audit switching, evidence readiness blocking, report-route data loading, and backup.
- [ ] Browser smoke test desktop and narrow viewport.
- [ ] Run the complete Python and Node test suites.
- [ ] Review the generated English and Arabic PDF page-by-page against the report design specifications.

## Completion rule
No client report, PDF, or Task 9 delivery is described as complete until every checkbox above is verified with real artifacts and test/browser evidence.
