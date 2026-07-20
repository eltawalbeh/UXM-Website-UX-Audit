import test from 'node:test';
import assert from 'node:assert/strict';
import { buildAdminDashboard, deriveAuditStage } from '../src/admin-dashboard.js';

const audits = [
  {
    id: 'UXM-401', client: 'Acme Corp', project: 'Checkout Funnel', url: 'https://acme.test/checkout',
    assessments: { 'NAV-01': 'pass', 'NAV-02': 'issue', 'FORM-01': 'not_verified' },
    assessmentSummary: { score: 72 },
    findings: [
      { id: 'UXM-041', title: 'Checkout CTA lacks an accessible label', severity: 'high', evidence: { status: 'draft' } },
    ],
  },
  {
    id: 'UXM-405', client: 'Health Labs', project: 'Booking Journey', url: 'https://health.test/booking',
    assessments: { 'NAV-01': 'pass', 'NAV-02': 'pass' },
    assessmentSummary: { score: 89 }, findings: [],
  },
];

const readiness = {
  'UXM-401': { ready: false, blockers: [{ findingId: 'UXM-041', message: 'Evidence is incomplete.' }] },
  'UXM-405': { ready: true, blockers: [] },
};

test('Main OS derives a truthful operating queue and registry from persisted audit/readiness data', () => {
  const dashboard = buildAdminDashboard(audits, readiness);

  assert.deepEqual(dashboard.summary, {
    needsAttention: 1,
    waitingReview: 1,
    blocked: 1,
    readinessUnavailable: 0,
    ready: 1,
  });
  assert.deepEqual(dashboard.queue[0], {
    auditId: 'UXM-401', findingId: 'UXM-041', tone: 'critical', action: 'Resolve',
    title: 'Evidence is incomplete.', client: 'Acme Corp', project: 'Checkout Funnel',
  });
  assert.deepEqual(dashboard.registry.map((row) => row.id), ['UXM-401', 'UXM-405']);
  assert.equal(dashboard.registry[0].coverage, '2 / 3');
  assert.equal(dashboard.registry[0].score, '72/100');
  assert.equal(dashboard.registry[0].stage, 'Readiness review');
  assert.equal(dashboard.registry[1].stage, 'Ready to deliver');
});

test('Main OS groups publication blockers into one actionable queue item per audit', () => {
  const dashboard = buildAdminDashboard([audits[0]], {
    'UXM-401': { ready: false, blockers: [
      { findingId: 'UXM-041', message: 'Evidence is incomplete.' },
      { findingId: 'UXM-041', message: 'Annotated image is required.' },
      { findingId: 'UXM-041', message: 'Capture timestamp is required.' },
    ] },
  });

  assert.equal(dashboard.summary.needsAttention, 1);
  assert.equal(dashboard.queue.length, 1);
  assert.deepEqual(dashboard.queue[0], {
    auditId: 'UXM-401', findingId: 'UXM-041', blockerCount: 3, tone: 'critical', action: 'Resolve 3 blockers',
    title: '3 publication blockers require resolution.', client: 'Acme Corp', project: 'Checkout Funnel',
  });
});

test('Main OS never invents a score, project, target date, or ready state', () => {
  const dashboard = buildAdminDashboard([{
    id: 'UXM-999', client: 'Unlinked client', url: 'https://example.test', assessments: {}, findings: [],
  }], {});

  assert.deepEqual(dashboard.registry[0], {
    id: 'UXM-999', client: 'Unlinked client', project: 'Not linked', url: 'https://example.test',
    stage: 'Assessment review', coverage: '0 / 0', score: 'Not scored', targetDate: '—', ready: false,
  });
  assert.equal(deriveAuditStage({ assessments: {}, findings: [] }, undefined), 'Assessment review');
});

test('Main OS marks unavailable readiness as unknown work instead of a zero-blocker state', () => {
  const dashboard = buildAdminDashboard([audits[0]], { 'UXM-401': { state: 'unavailable' } });

  assert.equal(dashboard.summary.readinessUnavailable, 1);
  assert.equal(dashboard.summary.needsAttention, 1);
  assert.equal(dashboard.summary.blocked, 0);
  assert.equal(dashboard.registry[0].stage, 'Readiness unavailable');
  assert.deepEqual(dashboard.queue[0], {
    auditId: 'UXM-401', findingId: '', tone: 'warning', action: 'Retry',
    title: 'Readiness status unavailable.', client: 'Acme Corp', project: 'Checkout Funnel',
  });
});
