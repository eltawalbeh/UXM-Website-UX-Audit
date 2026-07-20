export const NEW_FINDING_DRAFT = Symbol('new-finding-draft');

const pad = (value) => String(value).padStart(2, '0');

export function nextFindingId(findings) {
  const highest = findings.reduce((maximum, finding) => {
    const match = /^UXM-(\d+)$/i.exec(String(finding?.id || ''));
    return match ? Math.max(maximum, Number(match[1])) : maximum;
  }, 0);
  return `UXM-${String(highest + 1).padStart(3, '0')}`;
}

export function utcIsoToDatetimeLocal(value) {
  const instant = new Date(value);
  if (!value || Number.isNaN(instant.getTime())) return '';
  return `${instant.getFullYear()}-${pad(instant.getMonth() + 1)}-${pad(instant.getDate())}T${pad(instant.getHours())}:${pad(instant.getMinutes())}`;
}

export function datetimeLocalToUtcIso(value) {
  if (!value) return '';
  const instant = new Date(value);
  return Number.isNaN(instant.getTime()) ? '' : instant.toISOString();
}

export function newFindingStateForCheckpoint(checkpoint) {
  return {
    selection: NEW_FINDING_DRAFT,
    pendingFindingDraft: { checkpoint: String(checkpoint || '').trim() },
  };
}

export function resolveFindingEditorSelection(selection, findings) {
  if (selection === NEW_FINDING_DRAFT) return { mode: 'new', finding: null };
  const finding = selection === undefined
    ? findings[0]
    : findings.find((item) => item.id === selection);
  return { mode: 'existing', finding: finding || null };
}

export function buildFindingDraft(values, existingFindingId = '') {
  const text = (value) => String(value || '').trim();
  const capturedAt = text(values.capturedAt);
  return {
    id: text(values.id),
    checkpoint: text(values.checkpoint),
    url: text(values.url),
    page: text(values.page),
    journey: text(values.journey),
    severity: text(values.severity),
    effort: text(values.effort),
    title: text(values.title),
    observed: text(values.observation),
    impact: text(values.impact),
    recommendation: text(values.recommendation),
    evidence: {
      alt: text(values.evidenceAlt),
      capturedAt: /(?:Z|[+-]\d{2}:\d{2})$/i.test(capturedAt) ? capturedAt : datetimeLocalToUtcIso(capturedAt),
      capture: { device: text(values.device) },
      status: 'draft',
    },
    evidenceComplete: false,
    ...(existingFindingId ? { editingFindingId: existingFindingId } : {}),
  };
}

export function buildAiReviewedFindingDraft(findingContext, draft) {
  return {
    checkpoint: String(findingContext.criterionId || '').trim(),
    category: String(findingContext.category || '').trim(),
    journey: String(findingContext.journey || '').trim(),
    page: String(findingContext.page || '').trim(),
    title: String(findingContext.title || '').trim(),
    notes: String(findingContext.notes || '').trim(),
    severity: String(draft.suggestedSeverity || '').trim(),
    observed: String(draft.observation || '').trim(),
    impact: String(draft.impact || '').trim(),
    recommendation: String(draft.recommendation || '').trim(),
    evidence: { ...findingContext.evidence },
  };
}

export function buildEvidenceCompletePayload(findingId) {
  if (!String(findingId || '').trim()) throw new Error('A saved finding is required before completing evidence');
  return { evidenceComplete: true };
}
