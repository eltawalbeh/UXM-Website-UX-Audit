# UXM Stage 1 — Design QA Record

**Artifact:** `design/previews/UXM-Stage1-Visual-Direction.html`
**Viewport coverage:** Desktop 1440×1000 and true CSS mobile viewport 390×844
**Language coverage:** Complete English and Arabic RTL preview copy across every surface
**Status:** Internal design direction ready for Abdullah’s visual review

## Automated/static checks

- HTML parsed successfully with Python `html.parser`.
- All five product surfaces are present: public website, login, operator system, client portal, and client report. A sixth tab exposes the design-system specimen.
- Four supplied logo assets and seven total brand source images resolve locally.
- Four Thmanyah Sans webfont weights resolve locally: 400, 500, 700, 900.
- Browser console: zero JavaScript errors and zero console warnings.
- `git diff --check`: passed (line-ending notice only for Windows working copy).
- `@google/design.md` CLI download/lint attempt timed out in this environment after five minutes. Fallback validation parsed YAML frontmatter with PyYAML, resolved every token reference, and computed component contrast directly.

## DESIGN.md fallback validation

```text
name: UXM Audit
colors: 28
typography styles: 8
components: 8
broken references: 0
```

### Component contrast

| Component | Ratio | Result |
|---|---:|---|
| Primary button | 16.75:1 | Pass |
| Primary hover | 11.77:1 | Pass |
| Accessible blue action | 6.38:1 | Pass |
| Secondary button | 16.75:1 | Pass |
| Critical chip | 6.50:1 | Pass |
| High chip | 5.01:1 | Pass |
| Medium chip | 5.27:1 | Pass |
| Low chip | 5.50:1 | Pass |

## Responsive verification

CDP device emulation forced a true `390px` CSS viewport. Chrome’s ordinary `--window-size=390` mode was rejected as evidence because headless Chrome internally produced a wider viewport and cropped it.

Verified after correction:

```text
Desktop 1440px: marketing, login, operator, portal, report, system — 0 page overflow
Mobile 390px:   marketing, login, operator, portal, report, system — 0 page overflow
Arabic 390px:   operator, portal, report — 0 page overflow
```

The clipped horizontal tab strip was replaced by an explicit surface selector on narrow screens.

## Visual corrections made during QA

1. Added a real mobile Menu control to the public header after narrow review showed that Login remained reachable but navigation did not.
2. Added a mobile workspace navigation control after the operator rail collapsed.
3. Rebuilt the mobile report header into a two-row composition after the report title was forced into an unreadably narrow column.
4. Flipped the client-row forward arrow in RTL while preserving the supplied logo and evidence images unmirrored.
5. Expanded the Arabic client-portal specimen for primary navigation, delivery, and action labels.
6. Removed invalid cropped screenshots produced by headless Chrome’s minimum window width and replaced them with CDP-emulated evidence.
7. Replaced all client/pilot names, dates, scores, URLs, findings and delivery states with unmistakable placeholders.
8. Added the missing Login surface and documented that production auth still requires backend role and tenant enforcement.
9. Completed Arabic copy across all six preview tabs instead of applying RTL to untranslated English.
10. Added portal and report mobile navigation controls.
11. Replaced the undersized real evidence image with a dominant, explicitly labelled evidence placeholder.
12. Replaced the tablet-cropped horizontal operator logo with the supplied complete vertical lockup.
13. Changed Blue and Slate swatch labels to AA-compliant black text.
14. Replaced mixed Unicode navigation glyphs with one outline SVG family.
15. Added report version, official score and readiness context.
16. Implemented tab/panel relationships, roving tabindex, arrow/Home/End keyboard control, focus-visible styling and disabled-action states.

## Surface-by-surface result

### Public website — Decide / Learn

- Strong UX Mosaic logo, midnight, mint, blue and mosaic-pattern connection.
- Asymmetric proposition/report-preview composition with a flat, explicitly labelled sample rather than a floating proof claim.
- One continuous four-step proof line, not a generic feature-card grid.
- No fabricated client names, testimonials, or impact metrics.
- Mobile Menu, Login and both CTAs remain reachable at 390px.

### Login — Configure

- Secure split composition demonstrates the UX Mosaic brand without inventing authentication capability.
- Production auth, authorization, role enforcement and client isolation are called out explicitly.
- Mobile form and brand narrative stack without overflow.

### Operator system — Operate

- Next-action queue dominates the composition.
- Official score/readiness is secondary, contextual, and deliberately unpopulated in the design preview.
- AI candidates are explicitly excluded from score/report.
- Narrow navigation control is visible; queue and state stack without page overflow.

### Client portal — Monitor

- Published delivery and reports are primary once approved content exists; the current specimen is explicitly empty.
- No internal candidates, drafts, rejected findings, evidence-editing controls, or operational completion data.
- Arabic RTL reorders composition without mirroring the logo, with a reachable mobile menu.

### Client report — Decide / Learn

- The large evidence region is the visual hero and is unmistakably labelled as a placeholder.
- Observation, impact, recommendation, and evidence metadata remain distinct.
- Narrow source order is identity → evidence → observation → impact → recommendation → metadata.
- Mobile report header is repaired, localized, readable, and exposes navigation.

### Design system

- Supplied source palette is displayed exactly.
- Accessible derived blue is used for normal text/action contrast rather than silently modifying the source palette.
- Thmanyah Sans renders both English and Arabic specimens.

## Anti-slop diagnostic

| Tell | Public | Login | Operator | Portal | Report |
|---|---:|---:|---:|---:|---:|
| Tech gradient | 0 | 0 | 0 | 0 | 0 |
| Generic unbranded hue | 0 | 0 | 0 | 0 | 0 |
| Generic feature-tile grid | 0 | 0 | 0 | 0 | 0 |
| Accent rail decoration | 0 | 0 | 0 | 0 | 0 |
| Unearned blur/glass | 0 | 0 | 0 | 0 | 0 |
| Monument/fake stat | 0 | 0 | 0 | 0 | 0 |
| Icon topper repetition | 0 | 0 | 0 | 0 | 0 |
| Center-stack default | 0 | 0 | 0 | 0 | 0 |
| Default typography | 0 | 0 | 0 | 0 | 0 |
| Wrong surface archetype | 0 | 0 | 0 | 0 | 0 |
| **Total / 10** | **0** | **0** | **0** | **0** | **0** |

The four-step public proof strip is a process narrative, not a feature-card grid. No score, delivery state or client finding is populated in the design specimen.

## Visual review files

```text
design/previews/UXM-Stage1-marketing-desktop.png
design/previews/UXM-Stage1-login-desktop.png
design/previews/UXM-Stage1-operator-desktop.png
design/previews/UXM-Stage1-portal-desktop.png
design/previews/UXM-Stage1-report-desktop.png
design/previews/UXM-Stage1-system-desktop.png
design/previews/UXM-Stage1-marketing-mobile.png
design/previews/UXM-Stage1-login-mobile.png
design/previews/UXM-Stage1-operator-mobile.png
design/previews/UXM-Stage1-portal-mobile.png
design/previews/UXM-Stage1-report-mobile.png
design/previews/UXM-Stage1-system-mobile.png
design/previews/UXM-Stage1-operator-mobile-ar.png
design/previews/UXM-Stage1-portal-mobile-ar.png
design/previews/UXM-Stage1-report-mobile-ar.png
```

## Remaining gate

Stage 1 is not considered visually approved until Abdullah reviews the supplied direction. Production replacement of existing prototype surfaces begins only after that review.
