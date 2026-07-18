# UXM Final Polish — Product IA & Screen Blueprint

**Stage:** 1 — Brand + Design System
**Source of truth:** `design/UXM-Audit-DESIGN.md`
**Purpose:** Lock the product’s visible architecture before production UI replacement.

## 1. Complete product map

```text
PUBLIC
├─ M01 Home
├─ M02 How UXM Works
├─ M03 Services
├─ M04 Methodology & Evidence Standard
├─ M05 Selected Work (placeholder until approved)
├─ M06 Request a Demo / Contact
└─ A01 Login

AUTHENTICATED — UXM OPERATOR
├─ O01 Portfolio
├─ O02 Client Detail
├─ O03 Project Detail
├─ O04 Create Audit
├─ O05 Templates
├─ O06 Audit Overview
├─ O07 Scope & First Pass
├─ O08 Candidate Review
├─ O09 Criteria Review
├─ O10 Finding Editor + Evidence
├─ O11 Findings Queue
├─ O12 Score & Priority Review
├─ O13 Delivery Readiness
└─ O14 Delivery History

AUTHENTICATED — CLIENT
├─ P01 Client Home
├─ P02 Project Detail
├─ P03 Published Reports
├─ P04 Delivery Detail
└─ P05 Account

CLIENT DOCUMENT
├─ R01 Cover
├─ R02 Executive Snapshot
├─ R03 Scope & Methodology
├─ R04 Priority Roadmap
├─ R05 Section Health
├─ R06 Finding Detail
├─ R07 Readiness Decision
└─ R08 Closing / Next Steps
```

## 2. Navigation model

### Public

```text
UX MOSAIC / UXM Audit  |  How it works  Services  Methodology  Selected work  |  Request a demo  Login
```

- `Request a demo` is the only primary conversion action.
- `Login` is distinct and lower-emphasis.
- At narrow widths, use a standard menu button; keep both Demo and Login reachable without horizontal overflow.

### Operator

Primary rail:

```text
Portfolio
Audits
Templates
Deliveries
```

Context header:

```text
Client / Project / Audit ID · audit status · official score state · readiness · contextual actions
```

- Do not expose every feature in the rail.
- `Save/Discard` appears only while dirty.
- Share/PDF/Deliver appear only when relevant and explain readiness blocks.

### Client

```text
Home
Projects
Reports
Deliveries
Account
```

- No editing or internal review actions.
- Only assigned projects and published deliveries.

### Report

```text
Overview
Priorities
Findings
Readiness
Methodology
```

- Five anchors maximum.
- Compact context panel holds client, project, audited URL, scope, official score state, and delivery version.

## 3. Key surface compositions

## M01 — Public Home

**Surface:** Decide / Learn
**Job:** Make a prospect understand the product difference within one viewport, then provide evidence and a demo path.

### Composition

1. **Header:** supplied horizontal light logo on midnight; small live descriptor `Evidence-led UX Audit System`.
2. **Opening statement:** asymmetric two-column hero, not a centered SaaS stack.
   - Left: direct proposition and CTA.
   - Right: a real product/report composition when available; until then, a clearly marked interface preview—not fabricated metrics.
3. **Proof strip:** four stages, not four feature cards:
   ```text
   Discover with AI → Validate with experts → Prove with evidence → Deliver with confidence
   ```
4. **Product journey:** one continuous horizontal/stacked narrative showing the audit lifecycle.
5. **Services:** editorial list with CX/UX Audit as the featured service; avoid equal icon tiles.
6. **Methodology:** measured / human-approved / AI candidate / not verified.
7. **Selected work:** empty-safe module; use `Selected work available on request` until approval.
8. **Final CTA:** Request a demo.

### Brand intensity

High. Use midnight chapter fields, mosaic transition bands, blue for actions, mint for verified outcomes.

## A01 — Login

**Surface:** Configure
**Job:** Fast, trustworthy access with clear role-aware destination.

### Composition

- Left/top brand field: vertical light logo + one cropped mosaic composition + short evidence standard.
- Right/main form: email, password, forgot password, sign in.
- No testimonials, pricing, feature grid, or decorative stats.
- Error and loading states do not clear entered email.
- Production acceptance requires backend authentication and client isolation; Stage 1 preview remains explicitly non-authenticated.

## O01 — Operator Portfolio

**Surface:** Operate
**Job:** Find the client/project/audit requiring attention and act.

### Composition

- Stable rail + compact header.
- Primary work area begins with search and one `New client / project` action.
- Hierarchical client/project rows, not a grid of identical account cards.
- Each project exposes audit count, current delivery state, owner, last update, and next blocked action only when real.
- Secondary right panel appears on selection and shows project context/history.
- Empty state explains the first action without fake portfolio data.

## O06 — Audit Overview

**Surface:** Operate
**Job:** Answer: what is in scope, what remains, what is blocked, what should I do next?

### Composition

- Audit identity/context strip.
- Main column: next action queue in workflow order.
- Secondary column: scope coverage, official score state, readiness blockers, Critical/High count.
- AI candidates are visibly separate from approved findings.
- No decorative charts above the working queue.

## O08 — Candidate Review

**Surface:** Command / Inspect
**Job:** Review one AI candidate against checkpoint, source page, and evidence gap.

### Composition

- Left queue: candidate IDs, checkpoint, page, confidence label.
- Center: page/source evidence and observed region.
- Right inspector: observation, rationale, gaps, duplicate risk, proposed severity.
- Fixed decision bar: Reject · Edit draft · Promote for evidence review.
- No candidate changes official score/readiness/report.

## O10 — Finding Editor + Evidence

**Surface:** Command / Inspect
**Job:** Turn observed evidence into a defensible finding.

### Composition

- Evidence canvas first, with crop/annotation controls.
- Structured prose inspector: observation → impact → recommendation.
- Metadata: checkpoint, URL, page, journey, device, capture, severity, effort.
- Publishability checklist is contextual and explicit.
- `Save draft` differs from `Mark evidence complete`.

## P01 — Client Home

**Surface:** Monitor
**Job:** Show current projects, published outputs, and next client action without internal audit complexity.

### Composition

- Client identity and concise welcome.
- Published/active project list with delivery state.
- Latest delivered report is the primary content, with Report and PDF actions.
- Next actions use real delivery metadata.
- No AI candidate count, internal completion, rejected items, or evidence-editing controls.

## R02 — Executive Snapshot

**Surface:** Decide / Learn
**Job:** Explain the business conclusion in under two minutes.

### Composition

- Left: conclusion and official score state.
- Right: top actions / blockers and scope coverage.
- Strengths remain secondary to decisions.
- Critical/High issues remain visible regardless of score.
- Charts only when they answer a decision; no radar by default.

## R06 — Finding Detail

**Surface:** Decide / Learn
**Job:** Let a stakeholder verify the problem and act on it.

### Composition

```text
Issue identity + severity/category
Annotated evidence (60%) | Observation / impact / recommendation (40%)
Source/capture metadata
```

- One finding per PDF page where possible.
- Finding-specific crop, not a generic page image.
- Evidence before prose on narrow/RTL reading flow.

## 4. Responsive rules

| Width | Public | Operator | Client portal | Report |
|---|---|---|---|---|
| ≥1200 | Full editorial grid | Rail + canvas + optional inspector | Two-column overview | Content + persistent context rail |
| 768–1199 | 8-column chapters | Compact rail/drawer + canvas | Main + stacked secondary | Context summary above content |
| <768 | Single narrative | Top bar + navigation drawer; inspector becomes sheet/stack | Single column | Summary → evidence → details → recommendation |

- Minimum hit target: 44px.
- Long labels truncate only where full value is available via title/tooltip/details.
- Actions must remain reachable at 390px.
- No horizontal page scrolling.

## 5. Arabic RTL contract

- Translate information architecture, not only labels.
- Operator rail moves to the right; inspector placement follows reading task but screenshot/evidence itself stays unchanged.
- Arabic finding order: identity → evidence → observation → impact → recommendation → metadata.
- IDs/URLs/dates/file names use isolated LTR spans.
- The supplied logo is never mirrored.
- Pattern crops may be recomposed, not mechanically mirrored, to maintain visual balance.
- Test real Arabic paragraphs, English checkpoint IDs, URLs, and numbers in one viewport.

## 6. Required states

Every production surface must define:

```text
Loading
Empty
No search results
Validation error
Network/API error
Permission denied
AI unavailable
Not scored
Not verified
Evidence pending
Readiness blocked
Ready for client
Delivered
```

- Errors preserve user-entered content.
- Blocked actions explain the exact missing requirement.
- Empty states never use fake clients, findings, scores, or logos.

## 7. Stage 1 visual acceptance checklist

- [ ] Supplied logo used in correct dark/light orientation without recoloring.
- [ ] Thmanyah Sans renders real English and Arabic specimen text.
- [ ] Public, operator, client, and report surfaces feel related but not identical.
- [ ] Operator preview is an Operate surface—no hero or feature-card grid.
- [ ] Evidence is visually dominant in finding/report preview.
- [ ] Client portal excludes internal workflow data.
- [ ] Source brand palette is respected with accessible derived text/action colors.
- [ ] Pattern is structural, not wallpaper.
- [ ] Placeholder clients/case studies are clearly empty and not fabricated.
- [ ] Desktop and 390px layouts have no horizontal overflow.
- [ ] RTL preview preserves unmirrored evidence and isolated LTR technical values.
