const labels = {
  en: {
    roadmap: 'Priority roadmap',
    fixNow: 'Fix now',
    fixNext: 'Fix next',
    enhanceLater: 'Enhance later',
  },
  ar: {
    roadmap: 'خارطة أولويات التحسين',
    fixNow: 'معالجة فورية',
    fixNext: 'التحسينات التالية',
    enhanceLater: 'تحسينات لاحقة',
  },
};

const checkpointSeeds = [
  { id: 'NAV-01', section: 'navigation', score: 'pass' },
  { id: 'NAV-02', section: 'navigation', score: 'pass' },
  { id: 'NAV-03', section: 'navigation', score: 'partial' },
  { id: 'FORM-01', section: 'forms', score: 'pass' },
  { id: 'FORM-02', section: 'forms', score: 'partial' },
  { id: 'A11Y-01', section: 'accessibility', score: 'pass' },
];

const point = (status) => ({ pass: 1, partial: 0.5, issue: 0 }[status] ?? null);

export function createSeedAudit() {
  return {
    id: 'audit_demo_001',
    client: 'Northstar Services',
    website: 'northstar.example',
    url: 'https://northstar.example/',
    scope: 'Home · Apply · Contact · Desktop Chrome + Mobile Safari',
    assessments: Object.fromEntries(checkpointSeeds.map((item) => [item.id, item.score])),
    findings: [],
  };
}

export function updateAssessment(audit, criterionId, status) {
  return {
    ...audit,
    assessments: { ...audit.assessments, [criterionId]: status },
  };
}

export function createFinding(audit, data) {
  const id = `UXM-${String(audit.findings.length + 1).padStart(3, '0')}`;
  return {
    ...audit,
    findings: [...audit.findings, { id, ...data }],
  };
}

function sectionScore(audit, section) {
  const scoped = checkpointSeeds.filter((item) => item.section === section);
  const points = scoped.map((item) => point(audit.assessments[item.id])).filter((value) => value !== null);
  if (!points.length) return 0;
  return Math.round((points.reduce((sum, value) => sum + value, 0) / points.length) * 100);
}

export function deriveReport(audit, locale = 'en') {
  const roadmap = { fixNow: [], fixNext: [], enhanceLater: [] };
  for (const finding of audit.findings) {
    if (finding.severity === 'critical' || finding.severity === 'high') roadmap.fixNow.push(finding);
    else if (finding.severity === 'medium') roadmap.fixNext.push(finding);
    else roadmap.enhanceLater.push(finding);
  }
  return {
    direction: locale === 'ar' ? 'rtl' : 'ltr',
    labels: labels[locale],
    findings: audit.findings,
    roadmap,
    sectionScores: {
      navigation: sectionScore(audit, 'navigation'),
      forms: sectionScore(audit, 'forms'),
      accessibility: sectionScore(audit, 'accessibility'),
    },
  };
}
