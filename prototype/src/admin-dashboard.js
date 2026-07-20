const statuses = (audit) => Object.values(audit?.assessments || {});

export function deriveAuditStage(audit, readiness) {
  if (readiness?.state === 'unavailable') return 'Readiness unavailable';
  if (readiness?.ready) return 'Ready to deliver';
  if (readiness && readiness.ready === false) return 'Readiness review';
  if ((audit?.findings || []).some((finding) => finding?.evidence?.status !== 'complete')) return 'Evidence review';
  return 'Assessment review';
}

function scoreLabel(audit) {
  const score = audit?.assessmentSummary?.score;
  return Number.isFinite(score) ? `${score}/100` : 'Not scored';
}

function coverageLabel(audit) {
  const values = statuses(audit);
  const assessed = values.filter((status) => status !== 'not_verified' && status !== 'not_applicable').length;
  return `${assessed} / ${values.length}`;
}

function queueForAudit(audit, readiness) {
  if (readiness?.state === 'unavailable') {
    return [{
      auditId: audit.id, findingId: '', tone: 'warning', action: 'Retry',
      title: 'Readiness status unavailable.', client: audit.client || 'Unlinked client', project: audit.project || 'Not linked',
    }];
  }
  if (!readiness || readiness.ready !== false) return [];
  const blockers = readiness.blockers || [];
  if (!blockers.length) return [];
  const firstBlocker = blockers[0];
  const blockerCount = blockers.length;
  const findingId = firstBlocker.findingId || '';
  if (blockerCount === 1) return [{
    auditId: audit.id, findingId, tone: findingId ? 'critical' : 'warning', action: 'Resolve',
    title: firstBlocker.message || 'Resolve a publication blocker.', client: audit.client || 'Unlinked client', project: audit.project || 'Not linked',
  }];
  return [{
    auditId: audit.id, findingId, blockerCount, tone: findingId ? 'critical' : 'warning', action: `Resolve ${blockerCount} blockers`,
    title: `${blockerCount} publication blockers require resolution.`, client: audit.client || 'Unlinked client', project: audit.project || 'Not linked',
  }];
}

export function buildAdminDashboard(audits = [], readinessByAudit = {}) {
  const registry = audits.map((audit) => {
    const readiness = readinessByAudit[audit.id];
    return {
      id: audit.id,
      client: audit.client || 'Unlinked client',
      project: audit.project || 'Not linked',
      url: audit.url || '—',
      stage: deriveAuditStage(audit, readiness),
      coverage: coverageLabel(audit),
      score: scoreLabel(audit),
      targetDate: audit.targetDate || '—',
      ready: readiness?.ready === true,
    };
  });
  const queue = audits.flatMap((audit) => queueForAudit(audit, readinessByAudit[audit.id]));
  const readinessUnavailable = registry.filter((row) => row.stage === 'Readiness unavailable').length;
  const needsAttention = queue.length;
  const waitingReview = audits.filter((audit) => {
    const stage = deriveAuditStage(audit, readinessByAudit[audit.id]);
    return stage === 'Assessment review'
      || stage === 'Evidence review'
      || (audit.findings || []).some((finding) => finding?.evidence?.status !== 'complete');
  }).length;
  const blocked = registry.filter((row) => row.stage === 'Readiness review').length;
  const ready = registry.filter((row) => row.ready).length;

  return { summary: { needsAttention, waitingReview, blocked, readinessUnavailable, ready }, queue, registry };
}
