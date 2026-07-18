# UXM Figma Third Recheck — Node 100:2

**Source re-opened live through Figma Desktop MCP.**
**Current metadata hash:** `ffc55384d3b3687d`
**Decision:** Another meaningful correction pass landed. Four substantive issues remain.

## Newly resolved since the second review

1. **Arabic RTL internal OS frames added**
   - Portfolio
   - Candidate Review
   - Finding Editor
   - Delivery Readiness

2. **How UXM Works simplified**
   - The five-stage public story is now dominant.
   - The 12-step detail was reduced from 12 cards to a compact secondary list.

3. **Hero status label corrected**
   - `CONVICTION RATE` replaced with `HUMAN REVIEW STATUS`.

4. **RTL shell behavior demonstrated**
   - Navigation rail moves to the right.
   - Main reading order is RTL.
   - Evidence is not visually mirrored.
   - IDs, scores, URLs, and dates remain LTR-style tokens.

## Still unresolved

### 1. Fabricated OS/report data remains unbounded

Desktop Portfolio still uses production-looking records with no persistent demo banner:

- Acme Corp
- SaaS Rocket
- Fintech Flow
- Global Gov
- Health Labs
- Alex Mercer
- Realistic URLs
- Realistic dates
- `72/100`, `89/100`, and coverage values

The shared report still carries realistic sample client, score, finding, evidence, and impact content.

**Required:** replace with schema placeholders or add a persistent `DEMO WORKSPACE — FICTIONAL DATA` banner on every affected OS/report frame. Remove personal-looking PII.

### 2. Desktop Candidate Review layout remains unchanged and still collides

The current Candidate Review screenshot is byte-identical to the previous review. Remaining defects:

- Inspector header/status collision
- Evidence gaps and duplicate warnings overlap
- Human Notes label is crowded
- Bottom action row is clipped at the right edge

The tablet candidate frame remains cleaner and can guide the desktop correction.

### 3. Contact copy remains unchanged

Still present:

- `immediate security boundaries`
- `We typically respond within 1 business day.`

**Required:** remove both. Use only General Inquiry versus Request an Audit, with no unapproved response-time SLA.

### 4. Arabic OS is structurally RTL but not fully localized

The new RTL OS frames are a strong structural proof, but several interface labels remain English:

- `Target URL`
- `SOURCE URL`
- `DEVICE / VIEWPORT`
- `Source Page Screenshot`
- Page/product context copy

Technical values such as URLs, IDs, dates, and scores should remain LTR. Their labels and explanatory copy should be translated into Arabic.

## Updated status

| Area | Status |
|---|---|
| Product architecture | Pass |
| Public/mobile/RTL coverage | Pass direction |
| Arabic internal OS structure | Pass direction |
| Arabic OS localization | Partial |
| How UXM Works | Pass |
| Hero status terminology | Pass |
| Candidate evidence model | Pass concept |
| Candidate desktop layout | Fail |
| Contact copy | Fail |
| Demo data integrity | Fail |
| Final acceptance | Not approved yet |

## Remaining correction pass

1. Bound or replace every fictional OS/report record.
2. Repair desktop Candidate Review inspector layout.
3. Remove contact security/SLA copy.
4. Translate Arabic OS labels while preserving technical values as LTR tokens.
