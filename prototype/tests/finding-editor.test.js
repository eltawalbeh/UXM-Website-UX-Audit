import test from 'node:test';
import assert from 'node:assert/strict';
import { NEW_FINDING_DRAFT, buildAiReviewedFindingDraft, buildEvidenceCompletePayload, buildFindingDraft, datetimeLocalToUtcIso, newFindingStateForCheckpoint, nextFindingId, resolveFindingEditorSelection, utcIsoToDatetimeLocal } from '../src/finding-editor.js';

test('finding draft preserves evidence-first structured metadata without claiming evidence is complete', () => {
  const draft = buildFindingDraft({
    id: 'UXM-101', checkpoint: 'NAV-02', url: 'https://example.test/pricing', page: 'Pricing',
    journey: 'Understand', device: 'Mobile Safari', capturedAt: '2026-07-19T10:30:00Z',
    severity: 'high', effort: 'medium', title: 'Pricing labels hide plan differences',
    observation: 'Plan labels do not explain the included limits.', impact: 'Buyers cannot compare plans confidently.',
    recommendation: 'State limits beside each plan label.', evidenceAlt: 'Mobile pricing comparison.',
  });

  assert.equal(draft.checkpoint, 'NAV-02');
  assert.equal(draft.url, 'https://example.test/pricing');
  assert.equal(draft.evidence.capture.device, 'Mobile Safari');
  assert.equal(draft.evidence.capturedAt, '2026-07-19T10:30:00Z');
  assert.equal(draft.evidence.status, 'draft');
  assert.equal(draft.evidenceComplete, false);
  assert.equal(draft.candidateId, undefined);
});

test('evidence completion sends an explicit truthful completion request only for a saved finding', () => {
  assert.deepEqual(buildEvidenceCompletePayload('UXM-101'), { evidenceComplete: true });
  assert.throws(() => buildEvidenceCompletePayload(''), /saved finding/i);
});

test('evidence completion UI never reports success when the server rejects a stale completion decision', async () => {
  const source = await import('node:fs/promises').then(({ readFile }) => readFile(new URL('../app.js', import.meta.url), 'utf8'));

  assert.match(source, /if \(!response\.ok \|\| body\.completed !== true\) throw new Error\(body\.error \|\| 'Evidence completion failed'\);/);
  assert.match(source, /Evidence remains incomplete\. \$\{error\.message\}/);
  assert.match(source, /Evidence is truthfully marked complete and can now satisfy publication readiness\./);
});

test('evidence uploads send the persisted operator-selected capture timestamp rather than upload time', async () => {
  const source = await import('node:fs/promises').then(({ readFile }) => readFile(new URL('../app.js', import.meta.url), 'utf8'));

  assert.match(source, /const capturedAt = finding\?\.evidence\?\.capturedAt;/);
  assert.match(source, /\.\.\.\(capturedAt \? \{ 'X-Captured-At': capturedAt \} : \{\}\)/);
  assert.doesNotMatch(source, /X-Captured-At': new Date\(\)\.toISOString\(\)/);
});

test('accepted AI review becomes an unsaved operator draft rather than a local official finding', () => {
  const operatorDraft = buildAiReviewedFindingDraft({
    criterionId: 'NAV-02', category: 'navigation', journey: 'Discover', page: 'Home',
    title: 'Navigation labels obscure tasks', notes: 'Reviewed operator notes',
    evidence: { alt: 'Validate this observation with a screenshot before saving.' },
  }, {
    observation: 'Navigation labels use internal terminology.',
    impact: 'Visitors cannot predict where links lead.',
    recommendation: 'Use task-oriented labels.',
    suggestedSeverity: 'high', confidence: 'medium', missingEvidenceChecks: ['Capture source evidence'],
  });

  assert.deepEqual(operatorDraft, {
    checkpoint: 'NAV-02', category: 'navigation', journey: 'Discover', page: 'Home',
    title: 'Navigation labels obscure tasks', notes: 'Reviewed operator notes', severity: 'high',
    observed: 'Navigation labels use internal terminology.', impact: 'Visitors cannot predict where links lead.',
    recommendation: 'Use task-oriented labels.',
    evidence: { alt: 'Validate this observation with a screenshot before saving.' },
  });
  assert.equal(operatorDraft.candidateId, undefined);
  assert.equal(operatorDraft.aiDraft, undefined);
});

test('generic save reloads server-authoritative findings and AI review only opens an operator draft', async () => {
  const source = await import('node:fs/promises').then(({ readFile }) => readFile(new URL('../app.js', import.meta.url), 'utf8'));

  assert.doesNotMatch(source, /replaceAudit\(applyAiDraft\(/);
  assert.match(source, /const updated = await fetch\(`\/api\/audits\/\$\{encodeURIComponent\(audit\.id\)\}`\);\s*if \(!updated\.ok\) throw new Error\('Could not reload saved workspace'\);\s*establishSavedAudit\(normalizeAudit\(await updated\.json\(\)\)\);/s);
  assert.match(source, /pendingFindingDraft = buildAiReviewedFindingDraft\(context, reviewed\);/);
  assert.match(source, /message:'Reviewed draft is ready for the operator editor\. Save draft to persist it\.'/);
});

test('New finding selects a blank draft instead of falling back to the first persisted finding', () => {
  const persisted = [{ id: 'UXM-001', title: 'First saved finding' }, { id: 'UXM-002', title: 'Second saved finding' }];

  assert.equal(resolveFindingEditorSelection(undefined, persisted).finding.id, 'UXM-001');
  assert.deepEqual(resolveFindingEditorSelection(NEW_FINDING_DRAFT, persisted), { mode: 'new', finding: null });
  assert.equal(resolveFindingEditorSelection('UXM-002', persisted).finding.id, 'UXM-002');
});

test('creating a linked finding starts a new editor draft at the selected checkpoint', () => {
  const state = newFindingStateForCheckpoint('FORM-02');

  assert.equal(state.selection, NEW_FINDING_DRAFT);
  assert.deepEqual(state.pendingFindingDraft, { checkpoint: 'FORM-02' });
});

test('new finding ID advances past the highest non-sequential persisted UXM ID', () => {
  const persisted = [{ id: 'UXM-002' }, { id: 'UXM-019' }, { id: 'UXM-007' }, { id: 'external-100' }];

  assert.equal(nextFindingId(persisted), 'UXM-020');
});

test('finding draft converts persisted UTC capture timestamps for datetime-local editing and back to UTC for saving', () => {
  const persistedUtc = '2026-07-19T10:30:00.000Z';
  const localInput = utcIsoToDatetimeLocal(persistedUtc);
  const draft = buildFindingDraft({ capturedAt: localInput });

  assert.match(localInput, /^2026-07-19T\d{2}:30$/);
  assert.equal(draft.evidence.capturedAt, persistedUtc);
  assert.equal(datetimeLocalToUtcIso(localInput), persistedUtc);
});

test('operator finding editor is evidence-first, bilingual, keyboard-addressable, and keeps AI candidates separate', async () => {
  const source = await import('node:fs/promises').then(({ readFile }) => readFile(new URL('../app.js', import.meta.url), 'utf8'));
  const css = await import('node:fs/promises').then(({ readFile }) => readFile(new URL('../workspace-polish.css', import.meta.url), 'utf8'));

  assert.match(source, /evidence-first-editor/);
  assert.match(source, /Save draft/);
  assert.match(source, /Mark evidence complete/);
  assert.match(source, /data-action="save-finding-draft"/);
  assert.match(source, /data-action="complete-finding-evidence"/);
  assert.match(source, /الدليل أولاً/);
  assert.match(source, /dir="ltr"/);
  assert.match(source, /AI candidates are not official findings/);
  assert.match(css, /\.evidence-first-editor\s*\{[^}]*grid-template-columns:/s);
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.evidence-first-editor\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/s);
});

test('finding editor offers an explicit new-finding action, a persisted-finding selector, and escapes persisted prose in workspace markup', async () => {
  const source = await import('node:fs/promises').then(({ readFile }) => readFile(new URL('../app.js', import.meta.url), 'utf8'));

  assert.match(source, /data-action="new-finding"/);
  assert.match(source, /data-finding-selector/);
  assert.match(source, /escapeHtml\(reportText\(f,'title'\)\)/);
  assert.match(source, /escapeHtml\(reportText\(f,'observed'\)\)/);
  assert.match(source, /escapeHtml\(reportText\(f,'impact'\)\)/);
  assert.match(source, /escapeHtml\(reportText\(f,'recommendation'\)\)/);
});
