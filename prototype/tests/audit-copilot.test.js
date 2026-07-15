import test from 'node:test';
import assert from 'node:assert/strict';
import { createSeedAudit } from '../src/audit-state.js';
import { applyAiDraft } from '../src/workspace-state.js';

test('applying an AI draft requires an explicit action and preserves the original audit until then', () => {
  const audit = createSeedAudit();
  const draft = {
    observation: 'The submitted note describes an unclear primary label.',
    impact: 'Visitors may not find the intended application path.',
    recommendation: 'Use an application-focused label.',
    suggestedSeverity: 'medium', confidence: 'medium',
    missingEvidenceChecks: ['Confirm this on a narrow viewport.'],
    duplicateRisk: { level: 'none', matches: [] },
  };

  const applied = applyAiDraft(audit, {
    criterionId: 'NAV-02', category: 'navigation', journey: 'Discover', page: 'Home',
    title: 'Primary label does not name the task', notes: 'Analyst note retained.',
    evidence: { alt: 'Header screenshot', capturedAt: '2026-07-15T12:00:00Z' },
  }, draft);

  assert.equal(audit.findings.length, 0);
  assert.equal(applied.findings.length, 1);
  assert.equal(applied.findings[0].severity, 'medium');
  assert.equal(applied.findings[0].observed, draft.observation);
  assert.equal(applied.findings[0].impact, draft.impact);
  assert.equal(applied.findings[0].recommendation, draft.recommendation);
  assert.equal(applied.findings[0].aiDraft.confidence, 'medium');
  assert.equal(applied.findings[0].evidence.alt, 'Header screenshot');
});
