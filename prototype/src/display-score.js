export function displayScore(audit, derivedScore, assessedCount = null) {
  const persisted = audit?.assessmentSummary?.score;
  if (audit?.templateId && assessedCount === 0 && !Number.isFinite(persisted)) return null;
  return Number.isFinite(persisted) ? persisted : derivedScore;
}

export function scopeIncludedItems(audit) {
  const included = audit?.scope?.included;
  if (!Array.isArray(included)) return [];
  return included.map((item) => {
    if (typeof item === 'string') return { label: item, reference: '' };
    if (!item || typeof item !== 'object') return { label: String(item || ''), reference: '' };
    const reference = item.url || item.href || item.path || '';
    return { label: item.title || item.label || item.name || item.page || reference || 'Scope item', reference };
  }).filter((item) => item.label);
}

export function scopeSummary(audit) {
  const scope = audit?.scope;
  if (typeof scope === 'string') return scope;
  const included = scopeIncludedItems(audit);
  return included.length ? included.map((item) => item.label).join(' · ') : 'Scope not specified';
}
