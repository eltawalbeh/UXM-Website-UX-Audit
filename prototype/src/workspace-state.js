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
