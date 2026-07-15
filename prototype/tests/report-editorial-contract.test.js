import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { renderReport } from '../src/report-renderer.js';

const audit = {
  id: 'tawasal_contract', client: 'Tawasal / BekhedmetCom', url: 'https://www.tawasal.gov.jo/BekhedmetCom/BekhedmetComDashboard',
  scope: { included: ['Public BekhedmetCom service journeys', 'Desktop and mobile-visible interface review'], excluded: ['Authenticated administration', 'Back-office integrations'], limitation: 'Assessment is based on visible public journeys and supplied evidence.' },
  assessmentSummary: { score: 57, scoredCheckpoints: 11, notVerified: 0, method: 'Pass = 1, Partial = 0.5, Issue = 0.' },
  assessments: Array.from({ length: 11 }, (_, index) => ({ id: `CHK-${index + 1}`, status: 'issue' })),
  findings: [
    { id: 'UXM-001', severity: 'high', category: 'forms_data_entry', page: 'Phone verification', journey: 'Complete request', title: 'Phone number field has no persistent visible label or input example', observed: 'The field relies on a placeholder that disappears as people enter their phone number.', impact: 'People can make an avoidable formatting error and fail to complete the request.', recommendation: 'Use a persistent visible label and a regional input example before data entry.', evidence: { annotatedImage: { path: 'evidence/phone-field.png' }, description: 'Phone field captured in the public service journey.', capture: 'Desktop Chrome', url: 'https://www.tawasal.gov.jo/' } },
    { id: 'UXM-002', severity: 'high', category: 'trust_credibility', page: 'Phone verification', journey: 'Understand data use', title: 'Phone collection step lacks contextual privacy/data-use reassurance', observed: 'The service requests a phone number without explaining why it is required at that moment.', impact: 'Unexplained data collection can reduce trust and prompt abandonment.', recommendation: 'Add concise purpose and privacy reassurance beside the field.', evidence: { annotatedImage: { path: 'evidence/privacy.png' }, description: 'Phone collection step.', capture: 'Desktop Chrome', url: 'https://www.tawasal.gov.jo/' } },
    { id: 'UXM-003', severity: 'medium', category: 'usability', page: 'Phone verification', journey: 'Begin request', title: 'A large repeated hero delays the start of the phone-verification task', observed: 'A large visual banner pushes the phone-verification control below the immediate attention area.', impact: 'The delay weakens task focus and makes the next action less discoverable.', recommendation: 'Reduce the banner footprint or move the phone-verification action into the first scan line.', evidence: { annotatedImage: { path: 'evidence/hero.png' }, description: 'Hero preceding the task.', capture: 'Desktop Chrome', url: 'https://www.tawasal.gov.jo/' } },
    { id: 'UXM-004', severity: 'medium', category: 'technical_bug', page: '404 recovery', journey: 'Recover', title: 'The 404 recovery path offers only a generic Home-page route', observed: 'The recovery state gives people a generic route rather than returning them to a relevant service destination.', impact: 'People lose context and may abandon the original task.', recommendation: 'Offer a contextual return route and service search from the recovery page.', evidence: { annotatedImage: { path: 'evidence/404.png' }, description: '404 recovery state.', capture: 'Desktop Chrome', url: 'https://www.tawasal.gov.jo/' } },
  ],
};

const count = (value, needle) => (value.match(new RegExp(needle, 'g')) || []).length;

test('editorial page-template contract uses intentional cover, snapshot, methodology, scorecard-roadmap, finding and closing pages', () => {
  const html = renderReport(audit, 'en');

  for (const template of ['cover-page', 'snapshot-page', 'methodology-page', 'scorecard-roadmap-page', 'finding-page', 'closing-page']) {
    assert.match(html, new RegExp(`class="[^\"]*${template}`));
  }
  assert.equal(count(html, 'finding-page print-page'), audit.findings.length);
  assert.match(html, /class="[^\"]*methodology-grid/);
  assert.match(html, /class="[^\"]*scorecard-roadmap-grid/);
  assert.match(html, /class="[^\"]*finding-evidence/);
  assert.match(html, /class="[^\"]*finding-story/);
});

test('print stylesheet locks the editorial contracts to full A4-landscape composition without browser headers or web preview geometry', () => {
  const css = readFileSync(new URL('../report-print.css', import.meta.url), 'utf8');

  assert.match(css, /@page\s*\{\s*size:\s*A4 landscape;\s*margin:\s*0;/);
  for (const selector of ['.cover-page', '.snapshot-page', '.methodology-page', '.scorecard-roadmap-page', '.finding-page', '.closing-page']) {
    assert.match(css, new RegExp(selector.replace('.', '\\.') + '\\s*\\{'));
  }
  assert.match(css, /@media print[\s\S]*\.print-page\s*\{[\s\S]*width:\s*297mm;[\s\S]*height:\s*210mm;/);
  assert.match(css, /\.finding-evidence\s*\{[\s\S]*min-height:\s*310px/);
  assert.match(css, /\.finding-story\s*\{[\s\S]*font-size:\s*15px/);
  assert.doesNotMatch(css, /min-height:\s*650px/);
  assert.doesNotMatch(css, /width:\s*min\(100%,\s*1240px\)/);
});
