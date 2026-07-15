# AI First Pass — Scope Bundles

## Product intent
The user starts by entering a public URL. Before any AI crawl or audit analysis begins, UXM asks them to choose a clearly priced, bounded scope bundle. The selected bundle determines page discovery, applicable checkpoint selection, evidence capture, candidate findings, score denominator, and report scope.

This is a commercial scoping system, not a generic crawler setting.

## Required selection flow

1. **Enter public website URL**
2. **Choose one audit bundle**
3. **Confirm included pages / journeys**
4. **Run AI First Pass**
5. **Review candidate findings**
6. **Human double check and promote only valid findings**
7. **Generate report from approved findings only**

## Bundle options

### 1. Full Website Audit
**Label:** `Full website`

- Discover public URLs through the XML sitemap when available.
- Fall back to public internal navigation only when no sitemap is available.
- Show the discovered URL count and allow the reviewer to exclude pages before run.
- Group analysis by page type and primary public journey so duplicate templates are not needlessly audited as separate unique experiences.
- Apply the relevant subset of the UXM 272 checkpoint library page-by-page and journey-by-journey.
- Explicitly exclude login-only, payment, submission, private account, and personal-data flows unless access is formally provided.

### 2. Selected Pages Audit
**Label:** `Selected pages`

- User supplies one or more page URLs, paths, or page identifiers.
- Validate every URL is within the original public domain before analysis.
- Present the resolved page list for confirmation.
- Apply only checkpoints relevant to those page types and the named user journey.

### 3. General / Quick Health Check
**Label:** `General health check`

- Audit the homepage plus a small, explicit public sample of top navigation and primary discovery paths.
- Never imply whole-site coverage.
- Report scope prominently as a quick public health check.
- Use a focused cross-section of the 272 checkpoints, marking all other checks out of scope / not verified.

### 4. Contact Experience Audit
**Label:** `Contact experience`

- Audit contact entry points, contact page(s), branch/location/contact details, help channels, support discovery, public form clarity, privacy messaging, and public error/recovery states.
- Do not submit a form or enter personal information.
- Use the contact/support bundle of applicable checkpoints from the 272-library.

## Required scope contract
Every First Pass run must show before execution:

- Bundle name.
- Included URLs/pages/journeys.
- Public-only safety boundary.
- Applicable checkpoint count from the 272 library.
- Excluded / not-verifiable areas.
- Candidate-finding-only rule: no score, report, or published finding changes until human review.

## Candidate finding contract
Each AI candidate must include:

- Stable candidate ID.
- Page URL and page name.
- Journey and applicable UXM checkpoint ID.
- Evidence capture/reference.
- Observation, impact, recommendation.
- Suggested severity and confidence.
- Evidence gaps and duplicate risk.
- Review state: `Awaiting review`, `Approved`, `Edited`, `Rejected`, or `Evidence insufficient`.

Only `Approved` or explicitly `Edited` candidates with valid evidence become report findings.

## Site-type bundles and commercial rule
Bundles are productized audit packages. The same scope label must not imply the same workload across different digital products. Before scope selection, UXM identifies or lets the operator select the product type; this determines the checkpoint subset, journeys, evidence requirements, operational risk, and price.

### Required product types

- **Government / civic service:** public service discovery, eligibility/instructions, public forms, bilingual/RTL, accessibility, privacy, help and recovery. Authenticated submission, OTP, and citizen data remain out of scope unless access is provided.
- **E-commerce:** discovery, search/filter, product detail, availability, cart, checkout, delivery/returns, payment handoff, trust and support. Any real payment or order submission stays out of scope unless a safe test environment is supplied.
- **SaaS / digital product:** marketing-to-trial, pricing, onboarding, workspace/task flows, permissions, empty/error/recovery states, help and account management. Authenticated application flows require authorised access or a demo account.
- **Corporate / marketing website:** information architecture, credibility, services, conversion, content, contact/support, accessibility and performance.
- **Content / publisher:** navigation, search, reading experience, subscription prompts, ad/distraction load, related content, author/date credibility, and accessibility.
- **Custom:** operator explicitly selects the journeys and commercial scope.

### Pricing model

Pricing belongs to a commercial catalogue, not to an AI judgment. Each saleable package is defined by:

- product type;
- selected scope bundle (`Full website`, `Selected pages`, `General health check`, `Contact experience`);
- page count / sitemap coverage;
- journey count and complexity;
- applicable checkpoint bundle from the 272-library;
- language and RTL coverage;
- authenticated-flow access, if supplied;
- evidence depth, client workshop, report language(s), and delivery format.

Examples: a government contact bundle, e-commerce checkout bundle, and SaaS onboarding bundle are distinct sellable products even if each covers a similar number of pages. Their scope, risk, evidence expectation, and price are not interchangeable.

The report must always state the actual selected product type, package, pages, journeys, inclusions, and exclusions so the deliverable never implies a broader engagement than what was sold.
