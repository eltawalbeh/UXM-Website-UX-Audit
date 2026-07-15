// Generated from ../data/uxm-checkpoints.v1.json (schema 1.0.0) on 2026-07-14.
// This browser-safe, immutable map deliberately contains only real checkpoint IDs.
const range = (prefix, first, last, section) => Array.from(
  { length: last - first + 1 },
  (_, index) => [`${prefix}-${String(first + index).padStart(2, '0')}`, section],
);

export const checkpointSectionById = Object.freeze(Object.fromEntries([
  ...range('HP', 1, 20, 'Homepage & First Impression'),
  ...range('TO', 1, 44, 'Task Completion & Conversion'),
  ...range('NAV', 1, 30, 'Navigation & Information Architecture'),
  ...range('FORM', 1, 25, 'Forms & Data Entry'),
  // FORM-28 and FORM-29 are retained legacy pilot IDs; the current library's
  // consolidated form sequence ends at FORM-25, but existing persisted audits
  // must remain truthfully scoped rather than silently dropping these checks.
  ['FORM-28', 'Forms & Data Entry'],
  ['FORM-29', 'Forms & Data Entry'],
  ...range('TRUST', 1, 14, 'Trust, Credibility & Transparency'),
  ...range('CONTENT', 1, 25, 'Content & Microcopy'),
  ...range('VIS', 1, 40, 'Interface & Visual Design'),
  ...range('SEARCH', 1, 21, 'Search & Discovery'),
  ...range('HELP', 1, 37, 'Feedback, Recovery & Error Tolerance'),
  ...range('A11Y', 1, 5, 'Accessibility'),
  ...range('MOB', 1, 4, 'Mobile & Responsive'),
  ...range('PERF', 1, 3, 'Performance & Perceived Performance'),
  ...range('PRIV', 1, 2, 'Privacy & Consent'),
  ...range('BUG', 1, 2, 'Technical Reliability'),
]));

const points = Object.freeze({ pass: 1, partial: 0.5, issue: 0 });

function assessmentEntries(assessments) {
  if (Array.isArray(assessments)) return assessments;
  return Object.entries(assessments || {}).map(([id, status]) => ({ id, status }));
}

export function deriveSectionScores(assessments) {
  const sections = new Map();

  for (const { id, status } of assessmentEntries(assessments)) {
    const name = checkpointSectionById[id];
    if (!name) continue;
    const section = sections.get(name) || { name, assessedCount: 0, applicableCount: 0, points: 0 };
    section.assessedCount += 1;
    if (Object.hasOwn(points, status)) {
      section.applicableCount += 1;
      section.points += points[status];
    }
    sections.set(name, section);
  }

  return [...sections.values()].map(({ name, assessedCount, applicableCount, points: achieved }) => ({
    name,
    score: applicableCount ? Math.round((achieved / applicableCount) * 100) : null,
    assessedCount,
    applicableCount,
  }));
}
