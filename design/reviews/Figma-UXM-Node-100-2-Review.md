# UXM Figma Review — Node 100:2

**Source:** `https://www.figma.com/design/RYgdpeagYxr34nsA8m1Oqe/UXM?node-id=100-2`
**Reviewed directly through:** Figma Desktop MCP
**Review scope:** Visual/product-design fidelity only
**Frames inspected:** 22 top-level frames plus landing/report sections

## Executive verdict

The concept is visually coherent and the overall architecture is now substantially correct. It is a strong direction, but it is **not ready for visual acceptance or implementation handoff** yet.

The strongest parts are the disciplined internal OS shell, the readiness gate, the 60/40 report finding layout, the separate request flow, and the absence of a client portal.

The main problems are not cosmetic. The file violates several explicit content and brand constraints: it replaces the supplied logo, invents client/audit/evidence data throughout the file, makes absolute or unsupported claims, omits the required mobile and Arabic RTL designs, and does not make evidence visible in the AI candidate review screen.

## Architecture check

The file correctly contains:

1. One scrolling landing page
2. Internal login page
3. Login feedback states
4. Standalone Request an Audit page
5. Request success state
6. Internal OS screens
7. Secure shared report
8. PDF direction

The landing page contains section-based content rather than separate public marketing pages.

No client portal frame was found.

### Internal OS frames found

- Portfolio
- Client Detail
- Project Detail
- Create Audit
- Templates
- Audit Overview
- Scope & First Pass
- Candidate Review
- Criteria Review
- Finding Editor
- Findings Queue
- Score & Priority Review
- Delivery Readiness
- Delivery History
- Incoming Requests

## What is strong

### 1. Overall family coherence

The landing, login, request flow, OS, report, and PDF feel like members of one product family. Midnight, white, and blue are used consistently, and the system feels serious rather than playful.

### 2. Correct public scope

The public website is one long landing page with the expected section structure. Login and Request an Audit are standalone. This directly fixes the earlier multi-page public-site misunderstanding.

### 3. Internal OS density

The OS is compact and operational. It avoids oversized mobile-style components on desktop. Portfolio, criteria, findings, readiness, delivery, and request intake all use a consistent shell.

### 4. Readiness design

The Delivery Readiness screen is the strongest OS frame. It:

- Shows passed, warning, blocked, and not-configured gates
- Disables Publish
- Provides direct repair actions
- Separates preview generation from publication

### 5. Evidence-first report layout

The report finding detail uses an effective evidence/prose relationship. Evidence is visually dominant, while observation, impact, recommendation, and metadata remain readable.

### 6. Request success copy

The request success state correctly states that:

- No client account was created
- No automated crawler was started
- The internal team will review the request

### 7. Delivery model

The Delivery History screen supports a secure shared link, PDF, report versioning, and immutable history without introducing a client portal.

---

# Blockers

## B01 — The supplied UX Mosaic logo was replaced

The file repeatedly uses a newly created square `M` brand mark and text lockup instead of the supplied original UX Mosaic artwork.

This violates the brand rule:

> Preserve the original UX Mosaic artwork. Do not redraw, recolor, crop, stretch, or reinterpret it.

### Required correction

Replace every custom `M` mark with the supplied original logo assets:

- Horizontal dark-background lockup
- Horizontal light-background lockup
- Vertical mark only where compact navigation genuinely requires it

The descriptor may remain separate text beneath or beside the logo.

## B02 — Fabricated client, audit, evidence, score, date, and PII-like content

The file contains extensive invented records, including examples such as:

- Acme Corp
- SaaS Rocket
- Fintech Flow
- Global Gov
- Health Labs
- Alex Mercer
- Personal-looking email and phone values
- Specific scores such as `72/100`
- Specific coverage values
- Specific findings and observations
- Specific publication dates
- Specific source URLs
- Specific evidence IDs
- Specific capture dates/devices

The metadata review found more than 100 occurrences of fabricated or production-looking content.

Adding `DESIGN PREVIEW ONLY` to some frames does not make the unlabelled OS records safe, and it does not solve the problem of realistic fake client evidence.

### Required correction

Use one of these two patterns consistently:

1. Explicit schema placeholders:
   - `[Approved client name]`
   - `[Approved project name]`
   - `[Approved client URL]`
   - `UXM-[###]`
   - `[N] findings`
   - `Not scored`
   - `[Report version]`

2. A clearly bounded demo workspace labelled on every relevant surface:
   - `DEMO WORKSPACE — FICTIONAL DATA`

Do not use personal-looking emails or phone numbers.

## B03 — Fake evidence and fake metrics appear in the public hero and report

The hero includes:

- `Checkpoint 4.1: Conversion Tunnel`
- `Evidence #104A`
- A specific checkout observation
- `Critical Action`
- `Conviction Rate`
- `100% Evidence Match`

The report includes:

- Score `72/100`
- `100% Proven`
- Specific counts
- Specific findings
- Specific business impact claims
- Specific source paths and capture dates

These are visually persuasive enough to be interpreted as real work.

### Required correction

Replace the hero/report preview data with visibly structural placeholders until approved pilot evidence exists.

Do not use:

- `Conviction Rate`
- `100% Evidence Match`
- `100% Proven`

Use:

- Evidence status
- Human review status
- Report version state
- `Not scored`
- `[Evidence preview placeholder]`
- `[Approved finding title]`

## B04 — No mobile, tablet, or Arabic RTL design frames

All principal product frames are desktop-sized. References to mobile devices and Arabic inside the copy do not constitute mobile or RTL design coverage.

No dedicated mobile landing, mobile request, mobile report, mobile OS, or Arabic RTL frames were found.

### Required correction

Add acceptance frames for at least:

- Landing: 390px English and 390px Arabic RTL
- Request an Audit: 390px English and Arabic RTL
- Login: 390px English and Arabic RTL
- OS: representative 390px/narrow patterns for Portfolio, Candidate Review, Finding Editor, and Readiness
- Shared report: 390px English and Arabic RTL
- At least one tablet/narrow desktop OS frame

Arabic must include complete translated content, bidi-safe technical values, unmirrored evidence images, and unmirrored logo artwork.

## B05 — Unsupported absolute claims

The file contains claims such as:

- `100% Verified Facts`
- `No AI Hallucinations`
- `100% Evidence Match`
- `A scientific approach to your user interface`
- `deterministic categorization`
- `mathematically clean`
- `typically responds in 1 business day`

These are either absolute, unprovable, overly technical, or unsupported by approved evidence/SLA.

### Required correction

Use defensible language:

- `Evidence-backed findings`
- `AI candidates require human review`
- `Measured where reproducible`
- `Human-validated before publication`
- `We will review your request and contact you`

Do not promise response times unless an SLA is approved.

## B06 — Candidate Review lacks a visible evidence canvas

The AI Candidate Registry shows candidate list and candidate details, but the operator cannot directly inspect the source page or evidence alongside the AI suggestion.

This weakens the core operating principle that a human must compare the AI candidate against the actual observed interface before promotion.

### Required correction

Candidate Review must provide direct access to:

- Source page/screenshot
- Relevant crop or page region
- Checkpoint context
- Candidate observation
- Evidence gaps
- Duplicate risk
- Human decision actions

The evidence surface should be central and visible without leaving the review task.

---

# High-priority corrections

## H01 — Services copy contradicts the no-portal model

The service description says:

> Secure online dashboard...

This can be interpreted as a client portal or client dashboard.

Replace it with:

> Secure read-only shared report, annotated evidence, priority roadmap, and optional PDF.

Remove unconfirmed promises such as direct Jira/backlog export and day-zero executive PDFs unless these are approved product capabilities.

## H02 — Testimonials section claims real validation while showing placeholders

The heading says:

> Real validation from industry leaders

The cards contain `[Approved testimonial]` placeholders.

This creates an integrity contradiction.

Until approved testimonials exist, either:

- Remove the section from the release design, or
- Rename it to `Client perspectives — approved testimonials will appear here`, or
- Replace it with `Selected work available on request`.

## H03 — “How UXM Works” became a 12-card process wall

The 12 equal cards are visually orderly but create exactly the repeated-card pattern the brief asked to avoid. It is too detailed for a public landing page and weakens the main story.

The headline `From raw digital touchpoints to bulletproof backlogs` is also too aggressive and jargon-heavy.

### Required correction

Show the public process as five memorable stages:

Discover with AI
→ Validate with experts
→ Prove with evidence
→ Prioritize action
→ Deliver with confidence

The detailed 12-step process can be secondary disclosure or methodology detail, not the dominant landing composition.

## H04 — AI and methodology language is too technical or misleading

Examples:

- `deterministic categorization`
- `mathematically clean`
- `scale diagnostic check across thousands of nodes`
- `synthesize quantitative severity and UX impact`
- `encrypt platform workspace link and data structures`

These phrases either overstate capability or are inappropriate for the public decision journey.

Use language a business decision-maker can understand and verify.

## H05 — Request form contains unapproved demo identities and omits key intake choices

The request form uses Acme-related values and personal-looking email addresses.

The visible form also needs clear capture of:

- Organization
- Preferred report language: English / Arabic / Both
- `Not sure` options where product type or audit scope is unknown

Do not ask the requester to behave like a UX specialist.

## H06 — Contact section contains an unapproved SLA and off-message wording

Remove:

- `Typically responds in 1 business day` unless formally approved
- `Immediate security boundaries` language, which makes the service sound like security testing

Clarify the two paths:

- General inquiry
- Request an Audit

## H07 — Shared report terminology is not client-ready

`Audit Discovery Logs` sounds internal and technical.

Use a client-facing heading such as:

- Findings and Evidence
- Detailed Findings
- Evidence-backed Findings

## H08 — Rail navigation relies on unexplained compact icons

The internal OS rail is visually clean, but unlabeled icons make orientation dependent on memory.

Required design states:

- Tooltip on hover/focus
- Accessible label
- Clear active state
- Optional expanded rail at onboarding or wider desktop

---

# Medium-priority polish

## M01 — Public identity is clean but not distinctively UX Mosaic

Beyond Midnight/Blue and the incorrect `M` mark, the landing could belong to many SaaS or consulting brands.

Use the actual logo and the approved mosaic pattern in controlled moments to create stronger ownability.

## M02 — Hero composition is strong, but the evidence panel needs an honest placeholder contract

The asymmetric hero is effective and should be retained. Replace only the fake evidence content, not the overall composition.

## M03 — Methodology card row is visually generic

The four equal methodology cards are understandable, but a stronger state-system presentation could make the difference between measured, human-approved, AI candidate, and Not Verified more memorable.

Avoid purple for the AI state; use the approved interaction blue/slate system.

## M04 — OS text density needs narrow-width validation

Desktop density is appropriate, but filters, tables, long URLs, action columns, and the icon rail need actual narrow/mobile frames before acceptance.

## M05 — Report score presentation needs a visible scoring contract

If a score is shown, place coverage and limitations immediately beside it. The score must never appear trustworthy when coverage is incomplete.

For unapproved samples, show `Not scored` rather than a realistic number.

---

# Acceptance decision

## Current status

**Direction:** Strong
**Architecture:** Mostly correct
**Brand fidelity:** Blocked by incorrect logo
**Content integrity:** Blocked by fabricated records and absolute claims
**Responsive:** Not demonstrated
**Arabic RTL:** Not demonstrated
**Final visual acceptance:** Not approved

## Required before acceptance

1. Restore the real UX Mosaic logo everywhere.
2. Remove or explicitly bound all fabricated data.
3. Replace fake evidence, scores, PII-like records, and absolute claims.
4. Add mobile, tablet/narrow, and Arabic RTL frames.
5. Add evidence context to Candidate Review.
6. Remove the service-copy implication of a client dashboard.
7. Simplify the public process section.
8. Correct testimonials, contact SLA, and client-facing report terminology.
9. Re-review landing, Request an Audit, Candidate Review, Readiness, shared report, PDF, and Arabic/mobile variants.
