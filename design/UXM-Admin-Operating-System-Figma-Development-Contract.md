# UXM Admin Operating System — Figma-to-Development Contract

**Status:** Approved Figma mapping for Slice 4.9
**Live Figma source:** `UXM` → master node `100:2`
**Implementation principle:** Figma defines navigation, page anatomy, visual states, and interaction sequence. The existing protected backend remains authoritative for product data and delivery rules.

## 1. Approved Figma frame inventory

### Desktop (1440 × 900)
| Product surface | Figma frame |
|---|---:|
| Main Operating System | `185:93` |
| Client Details | `185:309` |
| Portfolio | `185:517` |
| Templates Overview | `185:715` |
| Start Here — URL entry | `185:1018` |
| Preliminary detection | `185:1136` |
| Bundle selection | `185:1385` |
| AI First Pass confirmation | `185:1516` |
| Manual First Pass confirmation | `185:1666` |
| Audit Overview | `185:1819` |
| Candidates | `185:1974` |
| Criteria Review | `185:2154` |
| Finding Editor | `185:2457` |
| Finding Queue | `185:2634` |
| Score Priority | `185:2833` |

### Required annotation states (desktop)
| Evidence interaction state | Figma frame |
|---|---:|
| Empty evidence | `191:364` |
| Annotation tools | `191:521` |
| Crop state | `191:692` |
| Annotation editing | `191:879` |
| Save annotated evidence | `191:1070` |
| Completion states | `191:1241` |

### Responsive and RTL reference frames
- Mobile Main OS: `185:3008` (`390 × 844`)
- Mobile URL entry: `185:3298`
- Mobile detection: `185:3365`
- Mobile bundle selection: `185:3492`
- Mobile Audit Overview: `185:3926`
- Mobile Candidates: `185:4022`
- Mobile Criteria Review: `185:4105`
- Mobile Finding Editor: `185:4202`
- Mobile Finding Queue: `185:4277`
- Mobile Score Priority: `185:4388`
- RTL Main OS: `185:4565`
- RTL Start Here: `185:4745`
- RTL detection: `185:4868`
- RTL bundle selection: `185:4999`
- RTL Audit Overview: `185:5342`
- RTL Criteria Review: `185:5494`
- RTL Finding Editor: `185:5650`

## 2. Navigation contract

The desktop shell is a labelled 260px sidebar. It has two semantic groups.

### Global Administration
1. Main OS
2. Client Details
3. Portfolio
4. Templates Overview

### Selected Audit Workflow
1. Audit Overview
2. Candidates
3. Criteria Review
4. Finding Editor
5. Finding Queue
6. Score Priority

`Start Here` is the primary dashboard action; it is not a permanent sidebar item. `Create Audit` is not a standalone page or permanent navigation item.

Selected-audit workflow rules:
- No selected draft/audit: all workflow items are visibly locked.
- Current required step: enabled and marked current.
- Future steps: locked with a reason and required next action.
- Completed earlier steps: may be revisited when it is safe to edit them.
- URL entry, detection, bundle confirmation, and starting mode cannot be skipped.

## 3. Existing-function mapping

| Figma surface | Existing product capability | Required slice work |
|---|---|---|
| Main OS | Authenticated audit listing, client/project records, request intake, readiness checks | Add one truthful aggregate dashboard view; do not fabricate metrics. (`4.10`) |
| Client Details | `/api/clients`, `/api/projects`, project status | Recompose existing data in Figma frame. (`4.10`) |
| Portfolio | `/api/audits`, persisted audit score and project links | Recompose existing data in Figma frame. (`4.10`) |
| Templates Overview | `/api/audit-templates`, project-linked template audit creation | Recompose existing catalog and selection. (`4.10`) |
| Start Here | Public-URL safety validation exists | Add URL-first unassigned draft lifecycle. (`4.11`) |
| Preliminary detection | `/api/audits/:id/detect-product-type` and manual fallback | Allow detection before client/project/audit link. (`4.11`) |
| Bundle selection | Current AI First Pass supports full, selected pages, health check, contact bundles; templates catalog exists | Bind confirmed category/product and bundle to unassigned draft. (`4.11`) |
| AI First Pass | `/api/audits/:id/ai-first-pass`; candidates are transient review-only output | Run against linked/unassigned flow without automatic persistence. (`4.11`, `4.12`) |
| Manual First Pass | Criteria assessment and human finding creation are functional | Add honest entry/continuation state; never fabricate candidates. (`4.11`, `4.12`) |
| Audit Overview | Persisted audit read, scope, assessment summary, readiness | Compose selected audit context and step state. (`4.12`) |
| Candidates | Candidate review, reject/promote-to-unsaved-draft boundary | Persist only workflow context, never candidate-as-finding. (`4.12`) |
| Criteria Review | Persisted human assessment and selected-checkpoint linked draft | Apply stage gating and Figma layout. (`4.12`) |
| Finding Editor | Protected finding draft/update endpoint, explicit evidence completion | Recompose Figma editor and preserve existing safeguards. (`4.13`) |
| Annotation Canvas | Source/annotated asset storage exists | Add in-app crop/annotation tool and generate annotated asset. (`4.13`) |
| Finding Queue | Persisted findings, evidence state, readiness blockers | Recompose as a selected-audit queue. (`4.14`) |
| Score Priority | Authoritative assessment score, readiness endpoint, PDF export | Recompose score/priority/readiness/delivery state. (`4.14`) |

## 4. Existing protected contracts that must survive

```text
AI candidate
≠ official finding
≠ score change
≠ readiness change
≠ report/PDF inclusion

Save draft
≠ evidence complete

Source + annotated asset + descriptive alt text + capture metadata
+ explicit human completion
= evidence complete
```

The existing backend already enforces:
- local authenticated Admin session and protected audit/evidence routes;
- SQLite audit, client, project, template, request, finding, and evidence persistence;
- URL safety checks before a First Pass;
- category/product detection fallback when confidence is insufficient;
- bundle-specific First Pass checkpoint subsets;
- no fabricated candidates if explorer/provider is unavailable;
- human-only candidate promotion;
- finding draft/update persistence with duplicate protection;
- source/annotated evidence ownership, timestamp validation, and race-safe replacement;
- readiness blockers and readiness-gated PDF export.

## 5. New data and UI responsibilities

### Slice 4.11 introduces an unassigned audit draft
It must hold only what is needed before a client/project link:

```text
public URL
product/category detection result and confirmation
bundle
AI or manual starting mode
scope/first-pass context
workflow stage
created/updated timestamps
```

It must not automatically create a client, project, official finding, score, readiness state, or PDF.

### Slice 4.12 introduces a workflow state machine
The state is authoritative and guards direct navigation/refresh as well as visible UI locks.

### Slice 4.13 adds annotation output
The original source screenshot remains immutable. Crop bounds, annotations, marker metadata, and generated annotated asset are finding-specific evidence. Replacing an asset resets evidence completion until the Admin reconfirms it.

## 6. Acceptance contract for all implementation slices

Every visual slice must pass:
- frame-specific Figma comparison;
- live localhost behavior using persisted data;
- frontend and relevant backend regression suites;
- Desktop and true CSS `390px` checks;
- English and Arabic RTL when the Figma frame provides RTL;
- keyboard/focus and browser-console checks;
- `git diff --check` and secret scan;
- independent review before the slice commit/push.

## 7. Explicit non-goals for Slice 4.9

- No frontend shell rewrite yet.
- No unassigned-draft schema/API change yet.
- No workflow gate implementation yet.
- No annotation-canvas implementation yet.
- No report/PDF behavior change yet.

Those changes begin only in the approved subsequent slices.
