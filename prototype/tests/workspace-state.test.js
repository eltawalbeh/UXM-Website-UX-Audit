import test from 'node:test';
import assert from 'node:assert/strict';
import { createSeedAudit, createFinding, updateAssessment } from '../src/audit-state.js';
import { beginWorkspace, changeAudit, discardChanges, isDirty, markSaved } from '../src/workspace-state.js';

test('an assessment change marks the workspace dirty and saving establishes the new baseline', () => {
  const initial = createSeedAudit();
  let workspace = beginWorkspace(initial);

  workspace = changeAudit(workspace, updateAssessment(workspace.audit, 'NAV-01', 'issue'));

  assert.equal(isDirty(workspace), true);
  assert.equal(workspace.audit.assessments['NAV-01'], 'issue');

  workspace = markSaved(workspace);
  assert.equal(isDirty(workspace), false);
  assert.equal(workspace.savedAudit.assessments['NAV-01'], 'issue');
});

test('adding a finding marks the workspace dirty and discard restores the persisted audit', () => {
  const initial = createSeedAudit();
  let workspace = beginWorkspace(initial);
  workspace = changeAudit(workspace, createFinding(workspace.audit, {
    criterionId: 'NAV-02', severity: 'high', category: 'information_architecture',
    page: 'Home', journey: 'Discover', title: 'Navigation labels are unclear',
    observed: 'Labels do not match visitors’ goals.', impact: 'Visitors may miss key services.',
    recommendation: 'Use task-focused labels.', evidence: { alt: 'Navigation labels in the header.' },
  }));

  assert.equal(isDirty(workspace), true);
  assert.equal(workspace.audit.findings.length, 1);

  workspace = discardChanges(workspace);
  assert.equal(isDirty(workspace), false);
  assert.equal(workspace.audit.findings.length, 0);
  assert.deepEqual(workspace.audit, initial);
});
