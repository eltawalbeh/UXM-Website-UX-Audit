import test from 'node:test';
import assert from 'node:assert/strict';
import { renderReport } from '../src/report-renderer.js';

const audit = {
  id: 'pilot_demo', client: 'Example Authority', url: 'https://example.gov/service',
  scope: { included: ['Public service form'], excluded: ['Authenticated journeys'], limitation: 'Mobile testing remains pending.' },
  assessmentSummary: { score: 62, scoredCheckpoints: 10, notVerified: 2 },
  assessments: [{ id: 'NAV-01', status: 'pass' }, { id: 'FORM-01', status: 'issue' }, { id: 'A11Y-01', status: 'not_verified' }],
  findings: [{
    id: 'UXM-001', severity: 'high', category: 'forms_data_entry', page: 'Service form', journey: 'Complete',
    title: 'Required fields are unclear before submission', observed: 'The form does not identify required fields until an error appears.',
    impact: 'People may abandon the request after a failed submission.', recommendation: 'Mark required fields before data entry.',
    evidence: { url: 'https://example.gov/service', capture: 'Desktop Chrome, 14 Jul 2026', description: 'Required inputs shown without visible required markers.' },
  }],
};

test('renderReport creates a complete English report with one dedicated finding print page', () => {
  const html = renderReport(audit, 'en');

  for (const section of ['Cover', 'Executive snapshot', 'Scope & methodology', 'Severity & category legend', 'Scorecard', 'Priority roadmap', 'Conclusion', 'Thank you']) {
    assert.match(html, new RegExp(section));
  }
  assert.match(html, /class="finding-page print-page"/);
  assert.match(html, /What we observed/);
  assert.match(html, /Why it matters/);
  assert.match(html, /Recommendation/);
  assert.match(html, /publication-blocked/);
  assert.doesNotMatch(html, /workspace|sidebar|Internal workspace/i);
});

test('renderReport omits excluded findings from the publishable roadmap, count, and finding pages', () => {
  const auditWithExcludedFinding = {
    ...audit,
    findings: [
      ...audit.findings,
      {
        id: 'UXM-002', severity: 'medium', category: 'content_microcopy', page: 'English page', journey: 'Understand',
        title: 'Unsupported English observation', observed: 'No valid source capture supports this.',
        impact: 'This must not be published.', recommendation: 'Capture valid evidence first.',
        excludedFromPublication: true, exclusionReason: 'No matching source capture exists.',
        evidence: { description: 'Unsupported capture.', evidencePending: true },
      },
    ],
  };

  const html = renderReport(auditWithExcludedFinding, 'en');

  assert.doesNotMatch(html, /UXM-002/);
  assert.doesNotMatch(html, /Unsupported English observation/);
  assert.match(html, /1 \/ 1/);
});

test('renderReport uses persisted annotated evidence metadata as a browser-served image', () => {
  const html = renderReport({
    ...audit,
    findings: [{
      ...audit.findings[0],
      evidence: {
        ...audit.findings[0].evidence,
        annotatedImage: { path: 'evidence/annotated-proof.png', filename: 'annotated-proof.png' },
      },
    }],
  }, 'en');

  assert.match(html, /<img src="evidence\/annotated-proof\.png"/);
  assert.doesNotMatch(html, /\[object Object\]/);
});

test('renderReport normalizes JSON-string evidence metadata and only blocks when no image exists', () => {
  const withStringMetadata = renderReport({
    ...audit,
    findings: [{
      ...audit.findings[0],
      evidence: { ...audit.findings[0].evidence, annotatedImage: JSON.stringify({ path: 'evidence/annotated-string.png' }) },
    }],
  }, 'en');
  const missingImage = renderReport(audit, 'en');

  assert.match(withStringMetadata, /<img src="evidence\/annotated-string\.png"/);
  assert.doesNotMatch(withStringMetadata, /publication-blocked/);
  assert.match(missingImage, /publication-blocked/);
});

test('renderReport keeps the client report CTA and finding markup inside the bounded layout contract', () => {
  const html = renderReport({
    ...audit,
    findings: [{
      ...audit.findings[0],
      evidence: { ...audit.findings[0].evidence, annotatedImage: { path: 'evidence/annotated-proof.png' } },
    }],
  }, 'en');

  assert.match(html, /data-export-pdf[^>]*>PDF report</);
  assert.match(html, /class="finding-layout"/);
  assert.match(html, /class="evidence-canvas finding-evidence"><img src="evidence\/annotated-proof\.png"/);
  assert.doesNotMatch(html, /Preview report|Create backup/);
});

test('template audit report supports object assessments and remains not scored before review', () => {
  const html = renderReport({
    id: 'audit_template', client: 'Template Client', url: 'https://example.com', templateId: 'corporate-marketing-v1',
    scope: { included: ['Template baseline'] },
    assessments: { 'HP-01': 'not_verified', 'NAV-01': 'not_verified', 'A11Y-01': 'not_verified' },
    findings: [],
  }, 'en');

  assert.match(html, /Not scored/);
  assert.match(html, /0 \/ 3/);
  assert.doesNotMatch(html, />0<small>\/100<\/small>/);
});

test('renderReport creates a native RTL Arabic report and isolates technical tokens LTR', () => {
  const html = renderReport(audit, 'ar');

  assert.match(html, /lang="ar" dir="rtl"/);
  for (const section of ['الملخص التنفيذي', 'النطاق والمنهجية', 'مقياس الأولوية وتصنيفات الملاحظات', 'بطاقة تقييم التجربة', 'خارطة أولويات التحسين', 'الخلاصة', 'شكراً لكم']) {
    assert.match(html, new RegExp(section));
  }
  assert.match(html, /class="technical-token" dir="ltr">UXM-001/);
  assert.match(html, /class="technical-token" dir="ltr">https:\/\/example.gov\/service/);
  assert.match(html, /الترجمة العربية مطلوبة قبل النشر/);
  assert.doesNotMatch(html, /Required fields are unclear before submission/);
});
