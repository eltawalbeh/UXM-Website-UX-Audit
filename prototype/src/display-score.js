export function displayScore(audit, derivedScore, assessedCount = null) {
  const persisted = audit?.assessmentSummary?.score;
  if (audit?.templateId && assessedCount === 0 && !Number.isFinite(persisted)) return null;
  return Number.isFinite(persisted) ? persisted : derivedScore;
}

export function scopeSummary(audit) {
  const scope = audit?.scope;
  if (typeof scope === 'string') return scope;
  if (Array.isArray(scope?.included)) return scope.included.join(' · ');
  return 'Scope not specified';
}
