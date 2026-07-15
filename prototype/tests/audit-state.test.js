import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import {
  createSeedAudit,
  updateAssessment,
  createFinding,
  deriveReport,
} from '../src/audit-state.js';

test('an issue assessment changes the applicable section score', () => {
  const audit = createSeedAudit();
  const before = deriveReport(audit).sectionScores.find((section) => section.name === 'Navigation & Information Architecture').score;
  const updated = updateAssessment(audit, 'NAV-01', 'issue');
  const after = deriveReport(updated).sectionScores.find((section) => section.name === 'Navigation & Information Architecture').score;

  assert.equal(updated.assessments['NAV-01'], 'issue');
  assert.ok(after < before);
});

test('a high-severity finding appears in Fix now with evidence and a recommendation', () => {
  const audit = createSeedAudit();
  const updated = createFinding(audit, {
    criterionId: 'NAV-02',
    severity: 'high',
    category: 'information_architecture',
    page: 'Home',
    journey: 'Discover',
    title: 'Primary navigation has insufficient contrast',
    observed: 'Header labels have weak contrast against the hero image.',
    impact: 'Visitors may miss core destinations during first exploration.',
    recommendation: 'Increase contrast for every header state and verify WCAG AA.',
    evidence: { alt: 'Home page header with navigation labels outlined in red.' },
  });
  const report = deriveReport(updated);

  assert.equal(updated.findings.length, 1);
  assert.equal(updated.findings[0].id, 'UXM-001');
  assert.equal(report.roadmap.fixNow.length, 1);
  assert.equal(report.roadmap.fixNow[0].id, 'UXM-001');
});

test('Arabic report output uses RTL labels while preserving the stable issue ID', () => {
  const audit = createFinding(createSeedAudit(), {
    criterionId: 'FORM-01', severity: 'medium', category: 'forms_data_entry',
    page: 'Apply', journey: 'Complete', title: 'Required fields are unclear',
    observed: 'Required fields are only identified after submission.',
    impact: 'Applicants may need to correct avoidable errors.',
    recommendation: 'Mark required fields before submission.',
    evidence: { alt: 'Application form with an error state.' },
  });
  const report = deriveReport(audit, 'ar');

  assert.equal(report.direction, 'rtl');
  assert.equal(report.labels.roadmap, 'خارطة أولويات التحسين');
  assert.equal(report.findings[0].id, 'UXM-001');
});

test('a pilot report exposes only its library-mapped section rows', async () => {
  const pilot = JSON.parse(await readFile(new URL('../../pilots/tawasal-bekhedmetcom/audit.json', import.meta.url), 'utf8'));
  const report = deriveReport(pilot);

  assert.deepEqual(report.sectionScores.map((section) => section.name), [
    'Homepage & First Impression',
    'Navigation & Information Architecture',
    'Forms & Data Entry',
    'Privacy & Consent',
    'Content & Microcopy',
    'Interface & Visual Design',
    'Feedback, Recovery & Error Tolerance',
    'Accessibility',
    'Mobile & Responsive',
    'Performance & Perceived Performance',
  ]);
  assert.equal(report.sectionScores.some((section) => section.name === 'navigation'), false);
  assert.equal(report.sectionScores.find((section) => section.name === 'Accessibility').score, null);
});
