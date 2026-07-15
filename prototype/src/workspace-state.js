import { createFinding } from './audit-state.js';

function snapshot(audit) {
  return structuredClone(audit);
}

export function beginWorkspace(audit) {
  const savedAudit = snapshot(audit);
  return { audit: snapshot(savedAudit), savedAudit };
}

export function changeAudit(workspace, audit) {
  return { ...workspace, audit };
}

export function isDirty(workspace) {
  return JSON.stringify(workspace.audit) !== JSON.stringify(workspace.savedAudit);
}

export function markSaved(workspace, audit = workspace.audit) {
  const savedAudit = snapshot(audit);
  return { audit: snapshot(savedAudit), savedAudit };
}

export function discardChanges(workspace) {
  return { ...workspace, audit: snapshot(workspace.savedAudit) };
}

// This is intentionally local-only. The caller must explicitly save the workspace
// afterwards; drafting or applying never changes persisted audit data by itself.
export function applyAiDraft(audit, findingContext, draft) {
  return createFinding(audit, {
    criterionId: findingContext.criterionId,
    category: findingContext.category,
    journey: findingContext.journey,
    page: findingContext.page,
    title: findingContext.title,
    severity: draft.suggestedSeverity,
    observed: draft.observation,
    impact: draft.impact,
    recommendation: draft.recommendation,
    url: audit.url,
    notes: findingContext.notes,
    evidence: findingContext.evidence || {},
    aiDraft: {
      confidence: draft.confidence,
      missingEvidenceChecks: draft.missingEvidenceChecks,
      duplicateRisk: draft.duplicateRisk,
    },
  });
}
