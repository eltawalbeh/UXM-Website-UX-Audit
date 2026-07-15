export function displayScore(audit, derivedScore) {
  const persisted = audit?.assessmentSummary?.score;
  return Number.isFinite(persisted) ? persisted : derivedScore;
}

export function scopeSummary(audit) {
  const scope = audit?.scope;
  if (typeof scope === 'string') return scope;
  if (Array.isArray(scope?.included)) return scope.included.join(' · ');
  return 'Scope not specified';
}
