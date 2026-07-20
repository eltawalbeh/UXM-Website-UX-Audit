import { createSeedAudit, updateAssessment, createFinding, deriveReport } from './src/audit-state.js';
import { checkpointSectionById } from './src/section-scoring.js';
import { displayScore, scopeIncludedItems, scopeSummary } from './src/display-score.js';
import { beginWorkspace, changeAudit, discardChanges, isDirty, markSaved } from './src/workspace-state.js';
import { removeReviewedCandidate } from './src/ai-first-pass-state.js';
import { NEW_FINDING_DRAFT, buildAiReviewedFindingDraft, buildEvidenceCompletePayload, buildFindingDraft, newFindingStateForCheckpoint, nextFindingId, resolveFindingEditorSelection, utcIsoToDatetimeLocal } from './src/finding-editor.js';

let workspace = beginWorkspace(createSeedAudit());
let audit = workspace.audit;
let audits = [];
let apiStatus = 'Loading persisted audits…';
let publicationReadiness = null;
let aiDraftState = { context: null, draft: null, message: '' };
let aiFirstPassState = { url: '', productType: '', productTypeMessage: '', bundle: '', selectedPages: '', scope: null, candidates: [], message: '' };
let findingEditorSelection;
let pendingFindingDraft = null;
let selectedCheckpointId = null;

function replaceAudit(nextAudit) {
  workspace = changeAudit(workspace, nextAudit);
  audit = workspace.audit;
}

function establishSavedAudit(nextAudit) {
  workspace = markSaved(workspace, nextAudit);
  audit = workspace.audit;
}

function workspaceSaveState() {
  return isDirty(workspace) ? 'Unsaved changes' : 'All changes saved';
}
let view = new URLSearchParams(location.search).get('view') || 'overview';
let locale = 'en';
const app = document.querySelector('#app');

function normalizeAudit(data) {
  const seed = createSeedAudit();
  const assessments = Array.isArray(data.assessments)
    ? Object.fromEntries(data.assessments.map((item) => [item.id, item.status]))
    : (data.assessments || seed.assessments);
  return { ...seed, ...data, website: data.website || new URL(data.url).hostname, assessments, findings: data.findings || [] };
}

async function selectAudit(id, { discard = false } = {}) {
  if (isDirty(workspace) && !discard) {
    apiStatus = 'Save or discard your unsaved changes before switching workspaces.';
    render();
    return;
  }
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(id)}`);
    if (!response.ok) throw new Error('Selected audit is unavailable');
    establishSavedAudit(normalizeAudit(await response.json()));
    apiStatus = 'Reloaded persisted workspace.';
  } catch {
    apiStatus = 'Unable to load the selected audit.';
  }
  render();
}

async function saveChanges() {
  if (!isDirty(workspace)) return;
  apiStatus = 'Saving changes…';
  render();
  try {
    const response = await fetch('/api/audits', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...audit, findings: [] }),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Save request failed');
    const updated = await fetch(`/api/audits/${encodeURIComponent(audit.id)}`);
    if (!updated.ok) throw new Error('Could not reload saved workspace');
    establishSavedAudit(normalizeAudit(await updated.json()));
    audits = [body, ...audits.filter((item) => item.id !== body.id)];
    apiStatus = 'Changes saved to the persisted workspace.';
  } catch (error) {
    apiStatus = `Could not save changes. Your edits are still unsaved. ${error.message}`;
  }
  render();
}

async function discardAndReload() {
  if (audits.some((item) => item.id === audit.id)) {
    await selectAudit(audit.id, { discard: true });
    return;
  }
  workspace = discardChanges(workspace);
  audit = workspace.audit;
  apiStatus = 'Discarded unsaved local changes.';
  render();
}

async function logout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
  } finally {
    window.location.assign('/login.html');
  }
}

async function loadAudits() {
  try {
    const response = await fetch('/api/audits');
    if (!response.ok) throw new Error('Audit API unavailable');
    audits = await response.json();
    const requestedAudit = new URLSearchParams(location.search).get('audit');
    if (audits.length) await selectAudit(audits.some(item => item.id === requestedAudit) ? requestedAudit : audits[0].id);
    else { apiStatus = 'No persisted audits yet — showing the local prototype example.'; render(); }
  } catch {
    apiStatus = 'API unavailable — showing the local prototype example.';
    render();
  }
}

async function checkPublicationReadiness(publish = false) {
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/readiness?locale=${encodeURIComponent(locale)}`);
    publicationReadiness = await response.json();
    if (!response.ok) throw new Error(publicationReadiness.error || 'Readiness check failed');
    if (publicationReadiness.ready && publish) window.open(`report.html?audit=${encodeURIComponent(audit.id)}&lang=${locale}`, '_blank', 'noopener');
    apiStatus = publicationReadiness.ready ? 'Publication readiness passed.' : 'Publication blocked — resolve the listed evidence and metadata issues.';
  } catch (error) { apiStatus = `Unable to check publication readiness. ${error.message}`; }
  render();
}

async function exportPdf() {
  apiStatus = 'Preparing client-ready PDF…';
  render();
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/export-pdf?locale=${encodeURIComponent(locale)}`, { method: 'POST' });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'PDF export failed');
    apiStatus = `Client-ready PDF exported: ${body.filename}`;
    window.open(body.downloadUrl, '_blank', 'noopener');
  } catch (error) { apiStatus = `PDF export blocked. ${error.message}`; }
  render();
}

async function uploadEvidence(input) {
  const file = input.files?.[0];
  if (!file) return;
  if (isDirty(workspace)) { apiStatus = 'Save changes before attaching evidence so the finding is persisted.'; render(); return; }
  const finding = audit.findings.find((item) => item.id === input.dataset.evidenceUpload);
  const capturedAt = finding?.evidence?.capturedAt;
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/findings/${encodeURIComponent(input.dataset.evidenceUpload)}/evidence?kind=${input.dataset.evidenceKind}`, { method: 'POST', body: file, headers: { 'Content-Type': file.type, 'X-Original-Filename': file.name, ...(capturedAt ? { 'X-Captured-At': capturedAt } : {}) } });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Evidence upload failed');
    const updated = await fetch(`/api/audits/${encodeURIComponent(audit.id)}`);
    establishSavedAudit(normalizeAudit(await updated.json()));
    publicationReadiness = null;
    apiStatus = 'Screenshot attached to the selected finding.';
  } catch (error) { apiStatus = `Could not attach evidence. ${error.message}`; }
  render();
}

const severityClass = (value) => value === 'high' ? 'high' : value === 'medium' ? 'medium' : 'low';
const derivedScore = (report) => {
  const scored = report.sectionScores.filter((section) => section.score !== null);
  return scored.length ? Math.round(scored.reduce((sum, section) => sum + section.score, 0) / scored.length) : 0;
};
const score = (report) => displayScore(audit, derivedScore(report), report.sectionScores.reduce((sum, section) => sum + section.applicableCount, 0));
const scoreLabel = (report) => score(report) === null ? 'Not scored' : score(report);
const scoreWithScale = (report) => score(report) === null ? 'Not scored' : `${score(report)}<small>/100</small>`;
const sectionRows = (report) => report.sectionScores.map(({ name, score: sectionScore, assessedCount, applicableCount }) => `<div class="row"><span>${name}<br><small class="muted">${applicableCount} applicable / ${assessedCount} assessed</small></span><b>${sectionScore === null ? 'Not scored' : `${sectionScore}%`}</b></div>`).join('') || '<p class="muted">No mapped checkpoints have been assessed in this audit.</p>';
const sectionScoreFor = (report, id) => report.sectionScores.find((section) => section.name === checkpointSectionById[id])?.score;
const formatSectionScore = (value) => value === null || value === undefined ? 'Not scored' : `${value}%`;
const auditSubnav = () => { const labels = locale === 'ar' ? {aria:'أقسام مساحة عمل التدقيق',overview:'نظرة عامة',scope:'النطاق والصفحات',firstPass:'التمرير الأول',criteria:'المعايير',findings:'الملاحظات',scorecard:'النتيجة والأولويات',readiness:'الجاهزية',report:'التسليم'} : {aria:'Audit workspace sections',overview:'Overview',scope:'Scope & Pages',firstPass:'First Pass',criteria:'Criteria',findings:'Findings',scorecard:'Score & Priorities',readiness:'Readiness',report:'Delivery'}; return `<nav class="audit-subnav" aria-label="${labels.aria}">${[['overview',labels.overview],['scope',labels.scope],['firstPass',labels.firstPass],['criteria',labels.criteria],['findings',labels.findings],['scorecard',labels.scorecard],['readiness',labels.readiness],['report',labels.report]].map(([key,label]) => `<button type="button" data-view="${key}" aria-current="${view===key?'page':'false'}" class="audit-subnav__item ${view===key?'is-current':''}">${label}</button>`).join('')}</nav>`; };
const operatorCopy = () => locale === 'ar' ? { brand:'مساحة عمل تدقيق UXM', rail:'تنقل المشغّل', system:'نظام المشغّل', operations:'العمليات', audits:'التدقيقات', templates:'قوالب التدقيق', deliveries:'التسليمات', next:'المرحلة التالية', principle:'تشغيل قائم على الأدلة', boundary:'الذكاء يكتشف. البشر يراجعون. الدليل يضبط التسليم.' } : { brand:'UXM Audit workspace', rail:'Operator navigation', system:'Operator system', operations:'Operations', audits:'Audits', templates:'Audit templates', deliveries:'Deliveries', next:'Next slice', principle:'Evidence-led operation', boundary:'AI discovers. Humans validate. Evidence controls delivery.' };
const workspaceRail = () => { const copy=operatorCopy(); return `<aside class="workspace-rail" aria-label="${copy.rail}"><a class="workspace-rail__brand" href="/workspace.html" aria-label="${copy.brand}">UXM<span>Audit</span></a><div><p class="workspace-rail__label">${copy.system}</p><nav class="workspace-rail__nav" aria-label="${copy.rail}"><a class="workspace-rail__link" href="/operations.html">${copy.operations}</a><button type="button" class="workspace-rail__link is-current" data-view="overview">${copy.audits}</button><a class="workspace-rail__link" href="/templates.html">${copy.templates}</a><span class="workspace-rail__future" aria-disabled="true">${copy.deliveries}<small>${copy.next}</small></span></nav></div><div class="workspace-rail__footer"><strong>${copy.principle}</strong><span>${copy.boundary}</span></div></aside>`; };
const readinessStatus = () => publicationReadiness?.ready ? { label: 'Ready to publish', tone: 'is-ready' } : publicationReadiness ? { label: 'Publication blocked', tone: 'is-blocked' } : { label: 'Readiness not checked', tone: '' };

function shell(content) {
  const dirty = isDirty(workspace);
  const report = deriveReport(audit, locale);
  const readiness = readinessStatus();
  app.className = locale === 'ar' ? 'rtl' : '';
  app.dir = locale === 'ar' ? 'rtl' : 'ltr';
  app.lang = locale === 'ar' ? 'ar' : 'en';
  app.innerHTML = `<div class="operator-shell">${workspaceRail()}<div class="operator-workspace"><header class="audit-context-header"><div class="audit-context-header__identity"><p class="audit-context-header__crumb">Audits / ${escapeHtml(audit.website || 'Current audit')}</p><h1 class="audit-context-header__title">${escapeHtml(audit.client)} <span class="audit-context-header__id" dir="ltr">${escapeHtml(audit.id)}</span></h1><div class="audit-context-header__meta"><span class="audit-context-header__status">Score ${scoreLabel(report)}</span><span class="audit-context-header__status ${readiness.tone}">${readiness.label}</span><span class="audit-context-header__status">${Array.isArray(audit.assessments) ? audit.assessments.length : Object.keys(audit.assessments).length} checkpoints</span></div></div><div class="audit-context-header__actions">${dirty ? `<span class="save-state unsaved" aria-live="polite">${workspaceSaveState()}</span><button class="uxm-button uxm-button--ghost audit-context-header__control" data-action="discard">Discard</button><button class="uxm-button uxm-button--primary audit-context-header__control" data-action="save">Save</button>` : ''}<label class="uxm-field audit-context-header__picker audit-context-header__control"><span class="sr-only">Audit</span><select class="uxm-select" aria-label="Audit" data-audit>${audits.length ? audits.map(item => `<option value="${item.id}" ${item.id===audit.id?'selected':''}>${escapeHtml(item.client)}</option>`).join('') : '<option>Local prototype example</option>'}</select></label><div class="audit-context-header__utility"><button class="uxm-button uxm-button--ghost audit-context-header__control" data-action="locale">${locale==='en'?'العربية':'English'}</button><button class="uxm-button uxm-button--primary audit-context-header__control" data-action="export-pdf">PDF report</button><button class="uxm-button uxm-button--ghost audit-context-header__control" data-action="logout">Log out</button></div></div></header>${auditSubnav()}<main class="operator-canvas">${content}</main></div></div>`;
  bind();
  bindAssessmentWorklist();
  bindFindingEditor();
}

function overview() {
  const r = deriveReport(audit, locale);
  const assessed = Array.isArray(audit.assessments) ? audit.assessments.length : Object.keys(audit.assessments).length;
  shell(`<section class="operator-overview"><p class="operator-overview__eyebrow">Audit overview</p><h2 class="operator-overview__headline">A clear operating view of evidence, coverage, and delivery readiness.</h2><p class="operator-overview__intro">${scopeSummary(audit)}</p><div class="operator-facts"><div class="operator-fact"><strong class="operator-fact__value">${scoreWithScale(r)}</strong><span class="operator-fact__label">Official UX health score</span></div><div class="operator-fact"><strong class="operator-fact__value">${assessed}</strong><span class="operator-fact__label">Checkpoints in workspace</span></div><div class="operator-fact"><strong class="operator-fact__value">${audit.findings.length}</strong><span class="operator-fact__label">Findings</span></div></div><div class="operator-overview__grid"><section class="operator-overview__panel"><h2>Continue the audit</h2><p>Advance only through real review work: assess criteria, validate evidence, then resolve readiness blockers before delivery.</p><div class="operator-overview__actions"><button class="button" data-view="criteria">Review criteria</button><button class="button alt" data-view="findings">Open findings queue</button><button class="button alt" data-action="readiness">Check readiness</button></div><div class="operator-next-list"><div class="row"><span>Critical / High priorities</span><b>${r.roadmap.fixNow.length}</b></div><div class="row"><span>Publication state</span><b>${publicationReadiness?.ready ? 'Ready' : 'Needs review'}</b></div></div></section><section class="operator-overview__panel"><h2>Section health</h2><div class="operator-section-health">${sectionRows(r)}</div></section></div></section>`);
}
function criteria() {
  const r = deriveReport(audit, locale);
  const entries = Object.entries(audit.assessments);
  const selectedId = entries.some(([id]) => id === selectedCheckpointId) ? selectedCheckpointId : entries[0]?.[0];
  selectedCheckpointId = selectedId;
  const selectedStatus = audit.assessments[selectedId] || 'not_verified';
  shell(`<section class="criteria-task" aria-labelledby="criteria-title"><header class="criteria-task__header"><div><p class="operator-overview__eyebrow">Human assessment</p><h1 id="criteria-title">Review one checkpoint at a time</h1><p class="muted">Choose a checkpoint, judge the evidence, then record a defensible assessment. Saved assessments remain the official audit state.</p></div><div class="criteria-task__filters" aria-label="Assessment context"><span class="audit-context-header__status">${entries.length} in scope</span><span class="audit-context-header__status">${entries.filter(([, status]) => status === 'issue').length} issues</span><span class="audit-context-header__status">${entries.filter(([, status]) => status === 'not_verified').length} unverified</span></div></header><div class="criteria-task__layout"><section class="assessment-worklist" aria-label="Checkpoint assessment worklist">${entries.map(([id,status]) => `<button type="button" class="assessment-worklist__item ${id === selectedId ? 'is-selected' : ''}" data-checkpoint-select="${id}" aria-pressed="${id === selectedId}"><span><b dir="ltr">${id}</b><strong>${escapeHtml(criterionTitle(id))}</strong></span><span class="assessment-worklist__state">${escapeHtml(status.replace('_',' '))}</span></button>`).join('')}</section><aside class="assessment-inspector" aria-live="polite"><p class="operator-overview__eyebrow">Selected checkpoint</p><h2><span dir="ltr">${selectedId}</span> — ${escapeHtml(criterionTitle(selectedId))}</h2><p class="muted">Section score: ${formatSectionScore(sectionScoreFor(r, selectedId))}. Apply the assessment you can defend with reviewed evidence.</p><label class="uxm-field">Assessment<select class="uxm-select" data-assessment="${selectedId}">${['pass','partial','issue','not_applicable','not_verified'].map(status => `<option value="${status}" ${status === selectedStatus ? 'selected' : ''}>${status.replace('_',' ')}</option>`).join('')}</select></label><div class="uxm-notice"><b>Scoring rule</b><br>Pass = 1 · Partial = 0.5 · Issue = 0. Not applicable and Not verified stay outside the denominator.</div><button class="uxm-button uxm-button--secondary" type="button" data-action="create-linked-finding">Create or review linked finding</button></aside></div><details class="criteria-library"><summary>Reference library & scoring policy</summary><p>Use the UXM library as context, not a competing task surface. This checkpoint belongs to <b>${escapeHtml(checkpointSectionById[selectedId] || 'Unmapped')}</b>.</p></details></section>`);
}
function criterionTitle(id){return ({'NAV-01':'Likely destinations are easy to navigate to','NAV-02':'Navigation labels use user trigger words','NAV-03':'Navigation feedback shows where the user is','FORM-01':'Field labels explain desired input','FORM-02':'Required and optional fields are distinguished','A11Y-01':'Text contrast meets WCAG AA on core task states'})[id]||id;}
function reportText(f, field) { return locale === 'ar' ? (f.arabic?.[field] || f[field] || f.description || 'الترجمة العربية مطلوبة قبل النشر') : (f[field] || f.description || 'Evidence description unavailable'); }
function evidenceSource(value) { if (typeof value === 'string') { try { return evidenceSource(JSON.parse(value)); } catch { return value; } } return value && typeof value === 'object' ? evidenceSource(value.path || value.url) : ''; }
function workspaceEvidence(finding) { const evidence = finding.evidence || {}; const source = evidenceSource(evidence.annotatedImage) || evidenceSource(evidence.imageUrl) || evidenceSource(evidence.image); return source ? `<figure class="evidence"><img src="${escapeHtml(source)}" alt="${escapeHtml(reportText(evidence,'alt'))}"><figcaption>${escapeHtml(reportText(evidence,'alt'))}</figcaption></figure>` : `<div class="evidence publication-blocked"><strong>Evidence blocked</strong><span>Annotated evidence image is required before publication.</span></div>`; }
function findingsLegacy() { const blockers = publicationReadiness?.blockers || []; shell(`<div class="eyebrow">Evidence-backed findings</div><h1>Findings queue</h1><p class="sub">Attach source and annotated screenshots, then check the publication gate.</p><div class="grid"><section class="card"><h2>Add finding</h2><form id="finding-form" class="form"><label class="form-field">Title<input name="title" required placeholder="Required fields are unclear"></label><label class="form-field">Severity<select class="form-select" name="severity" aria-label="Severity"><option value="high">2 High</option><option value="medium">3 Medium</option><option value="low">4 Low</option></select></label><label class="form-field">Page<input name="page" value="Home" required></label><label class="form-field">Journey<select class="form-select" name="journey" aria-label="Journey"><option>Discover</option><option>Understand</option><option>Complete</option></select></label><label class="form-field full">What we observed<textarea name="observed" required></textarea></label><label class="form-field full">Why it matters<textarea name="impact" required></textarea></label><label class="form-field full">Recommendation<textarea name="recommendation" required></textarea></label><label class="form-field full">Evidence description / alt text<input name="alt" required></label><button class="button accent full">Save finding</button></form></section><section class="card"><h2>Publication readiness</h2><button class="button" data-action="readiness">Check readiness</button>${publicationReadiness ? (publicationReadiness.ready ? '<p>Ready to publish.</p>' : `<div class="notice"><b>Publication blocked</b><ul>${blockers.map(b=>`<li>${b.findingId}: ${b.message}</li>`).join('')}</ul></div>`) : ''}<h2>Current queue</h2>${audit.findings.length?audit.findings.map(f=>{const e=f.evidence||{};return `<div class="row"><div><span class="chip ${severityClass(f.severity)}">${f.severity}</span><b> ${f.id}</b><br>${f.title}<br><small class="muted">Source: ${e.sourceImage?'attached':'missing'} · Annotated: ${e.annotatedImage?'attached':'missing'}</small><br><div class="file-upload"><span class="file-upload-label">Source evidence</span><label class="file-upload-button">Choose source image<input class="file-upload-input" type="file" accept="image/png,image/jpeg" data-evidence-upload="${f.id}" data-evidence-kind="source"></label><output class="file-upload-status">${e.sourceImage?.filename || 'No source image selected'}</output></div><div class="file-upload"><span class="file-upload-label">Annotated evidence</span><label class="file-upload-button">Choose annotated image<input class="file-upload-input" type="file" accept="image/png,image/jpeg" data-evidence-upload="${f.id}" data-evidence-kind="annotated"></label><output class="file-upload-status">${e.annotatedImage?.filename || 'No annotated image selected'}</output></div></div></div>`}).join(''):'<p class="muted">No findings yet. Add a finding, save changes, then attach evidence.</p>'}</section></div>`); }
const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character]);
const aiContextFromForm = (form) => {
  const data = Object.fromEntries(new FormData(form));
  return {
    ...data,
    evidence: { alt: data.alt || '', capturedAt: data.capturedAt || '', sourceReference: data.sourceReference || '' },
  };
};

async function requestAiDraft(form) {
  const context = aiContextFromForm(form);
  aiDraftState = { context, draft: null, message: 'Creating an AI draft from your notes and evidence metadata…' };
  render();
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/ai-draft`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(context),
    });
    const body = await response.json();
    if (!response.ok || body.status !== 'ready') {
      aiDraftState = { context, draft: null, message: body.message || 'AI connection unavailable. Your notes are still here.' };
    } else {
      aiDraftState = { context, draft: body.draft, message: 'Draft ready for your review. Nothing has been added or saved.' };
    }
  } catch {
    aiDraftState = { context, draft: null, message: 'AI connection unavailable. Your notes are still here.' };
  }
  render();
}

async function requestProductTypeDetection(form) {
  const data = Object.fromEntries(new FormData(form));
  aiFirstPassState = { ...aiFirstPassState, url: data.firstPassUrl, productType: '', bundle: '', productTypeMessage: 'Checking the public page for a product-type suggestion…' };
  render();
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/detect-product-type`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: data.firstPassUrl }),
    });
    const body = await response.json();
    aiFirstPassState = body.status === 'detected'
      ? { ...aiFirstPassState, productType: body.productType, productTypeMessage: `${body.productTypeLabel} suggested (${body.confidence} confidence). Confirm or change it, then choose a bundle.` }
      : { ...aiFirstPassState, productType: '', productTypeMessage: body.message || 'Choose the product type manually, then choose a bundle.' };
  } catch {
    aiFirstPassState = { ...aiFirstPassState, productType: '', productTypeMessage: 'Automatic detection was inconclusive. Choose the product type manually, then choose a bundle.' };
  }
  render();
}

async function requestAiFirstPass(form) {
  const data = Object.fromEntries(new FormData(form));
  const selectedPages = (data.selectedPages || '').split('\n').map(value => value.trim()).filter(Boolean);
  const request = { url: data.firstPassUrl, productType: data.productType, bundle: data.bundle, selectedPages };
  aiFirstPassState = { ...request, selectedPages: data.selectedPages || '', scope: null, candidates: [], message: 'Validating the commercial scope contract and safely checking public pages…' };
  render();
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/ai-first-pass`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(request) });
    const body = await response.json();
    aiFirstPassState = response.ok && body.status === 'ready'
      ? { ...aiFirstPassState, scope: body.scope, candidates: body.candidates || [], message: 'First pass ready. Candidates remain transient: no score, readiness, report, or finding changed.' }
      : { ...aiFirstPassState, scope: null, candidates: [], message: body.message || body.error || 'No candidates were generated.' };
  } catch {
    aiFirstPassState = { ...aiFirstPassState, scope: null, candidates: [], message: 'AI first pass unavailable. No candidates were generated.' };
  }
  render();
}

function candidateCard(candidate, index) {
  return `<article class="candidate-review findings-workbench"><div class="candidate-review__queue"><div class="eyebrow">${escapeHtml(candidate.reviewState || 'Awaiting review')} · ${escapeHtml(candidate.id || `AIFP-${index + 1}`)}</div><h3>${escapeHtml(candidate.title)}</h3><p><b>${escapeHtml(candidate.pageName || 'Public page')}</b><br>Checkpoint: ${escapeHtml(candidate.checkpointId || 'Not mapped')} · ${escapeHtml(candidate.confidence || 'confidence unknown')}</p></div><div class="candidate-review__evidence"><p class="operator-overview__eyebrow">Evidence / source</p><a href="${escapeHtml(candidate.pageUrl || candidate.evidenceRefs?.[0] || '')}" target="_blank" rel="noreferrer">${escapeHtml(candidate.pageUrl || 'No public source reference')}</a><p>${escapeHtml(candidate.observation)}</p><p><b>Evidence gaps</b><br>${candidate.evidenceGaps.map(escapeHtml).join('<br>') || 'Human evidence review required.'}</p></div><aside class="candidate-review__inspector"><p class="operator-overview__eyebrow">Human review</p><p><b>Why flagged</b><br>${candidate.reasons.map(escapeHtml).join('<br>')}</p><p><b>Duplicate risk</b><br>${escapeHtml(candidate.duplicateRisk || 'unknown')}</p><div class="candidate-review__decision-bar"><button class="button alt" type="button" data-action="reject-candidate" data-candidate="${index}">Reject</button><button class="button alt" type="button" data-action="promote-candidate" data-candidate="${index}">Edit as draft</button><button class="button accent" type="button" data-action="promote-candidate" data-candidate="${index}">Promote for review — evidence</button></div><small>This candidate has not changed the score, readiness, report, or official findings.</small></aside></article>`;
}

function findings() {
  const context = aiDraftState.context || { criterionId: 'NAV-02', category: 'navigation', journey: 'Discover', page: 'Home', title: '', notes: '', alt: '', capturedAt: '', sourceReference: '' };
  const draft = aiDraftState.draft;
  const field = (name, label, value = '', type = 'text') => `<label class="form-field ${name === 'notes' ? 'full' : ''}">${label}${type === 'textarea' ? `<textarea name="${name}">${escapeHtml(value)}</textarea>` : `<input name="${name}" value="${escapeHtml(value)}">`}</label>`;
  const review = draft ? `<section class="ai-review" aria-live="polite"><div class="eyebrow">Human review required</div><h2>AI draft — edit before applying</h2><p class="muted">This proposal is not a finding and has not changed the score or been saved.</p><label class="form-field full">Observation<textarea name="draftObservation">${escapeHtml(draft.observation)}</textarea></label><label class="form-field full">Impact<textarea name="draftImpact">${escapeHtml(draft.impact)}</textarea></label><label class="form-field full">Recommendation<textarea name="draftRecommendation">${escapeHtml(draft.recommendation)}</textarea></label><label class="form-field">Suggested severity<select class="form-select" name="draftSeverity">${['critical','high','medium','low'].map(value => `<option ${value === draft.suggestedSeverity ? 'selected' : ''}>${value}</option>`).join('')}</select></label><div class="ai-checks"><b>Confidence: ${escapeHtml(draft.confidence)}</b><p><b>Missing-evidence checks</b><br>${draft.missingEvidenceChecks.map(escapeHtml).join('<br>') || 'None returned — verify evidence yourself.'}</p><p><b>Duplicate-risk check</b><br>${escapeHtml(draft.duplicateRisk.level || 'unknown')}${draft.duplicateRisk.matches?.length ? `: ${draft.duplicateRisk.matches.map(escapeHtml).join(', ')}` : ''}</p></div><button class="button accent" type="button" data-action="apply-ai-draft">Apply reviewed draft</button></section>` : '';
  const productOptions = [['government_civic','Government / civic service'],['ecommerce','E-commerce'],['saas_digital_product','SaaS / digital product'],['corporate_marketing','Corporate / marketing website'],['content_publisher','Content / publisher'],['custom','Custom']];
  const bundleOptions = [['full_website','Full website'],['selected_pages','Selected pages'],['general_health_check','General health check'],['contact_experience','Contact experience']];
  const scopeContract = aiFirstPassState.scope ? `<details open class="scope-contract"><summary><b>Scope contract</b> — ${escapeHtml(aiFirstPassState.scope.productTypeLabel)} · ${escapeHtml(aiFirstPassState.scope.bundleLabel)}</summary><p><b>Included URLs / pages</b><br>${aiFirstPassState.scope.includedUrls.map(escapeHtml).join('<br>') || 'No public pages fetched.'}</p><p><b>Included journeys</b><br>${aiFirstPassState.scope.includedJourneys.map(escapeHtml).join('<br>')}</p><p><b>Applicable checkpoints</b><br>${escapeHtml(aiFirstPassState.scope.checkpointCount)} of 272 in this product/bundle subset.</p><p><b>Excluded / not verifiable</b><br>${aiFirstPassState.scope.exclusions.map(escapeHtml).join('<br>')}</p><p><b>Candidate findings only</b><br>${escapeHtml(aiFirstPassState.scope.candidateRule)}</p></details><details open><summary><b>What was visited (${aiFirstPassState.scope.visited.length})</b></summary>${aiFirstPassState.scope.visited.map(page => `<div class="row"><span><a href="${escapeHtml(page.url)}" target="_blank" rel="noreferrer">${escapeHtml(page.title)}</a><br><small>${escapeHtml(page.url)} · text capture at ${escapeHtml(page.capturedAt)}</small></span></div>`).join('')}<p><b>Skipped</b><br>${aiFirstPassState.scope.skipped.map(item => `${escapeHtml(item.url)} — ${escapeHtml(item.reason)}`).join('<br>') || 'None'}</p></details>` : '';
  const firstPass = `<section class="card first-pass"><div class="eyebrow">Public, safe, no-login discovery</div><h2>AI preliminary first pass</h2><p class="muted">Choose the saleable product type and scope bundle before running. GET public HTML pages only: no forms, logins, personal data, transactions, or persisted findings.</p><form id="first-pass-form" class="form"><label class="form-field full">Website URL<input required name="firstPassUrl" type="url" value="${escapeHtml(aiFirstPassState.url || audit.url)}"></label><button class="button alt full" type="button" data-action="detect-product-type">Detect product type</button><div class="full ai-status" aria-live="polite">${escapeHtml(aiFirstPassState.productTypeMessage || 'Detect the product type, or choose it manually.')}</div><label class="form-field">Product type<select required class="form-select" name="productType"><option value="">Choose product type</option>${productOptions.map(([value,label]) => `<option value="${value}" ${value === aiFirstPassState.productType ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label class="form-field">Scope bundle<select required class="form-select" name="bundle" ${aiFirstPassState.productType ? '' : 'disabled'}><option value="">Choose scope bundle</option>${bundleOptions.map(([value,label]) => `<option value="${value}" ${value === aiFirstPassState.bundle ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label class="form-field full">Selected pages (one per line)<textarea name="selectedPages" placeholder="/pricing&#10;https://example.com/contact">${escapeHtml(aiFirstPassState.selectedPages)}</textarea><small>Required only for Selected pages. Every entry must resolve to the same public origin.</small></label><div class="notice full"><b>Before execution, UXM will show the scope contract:</b> bundle, product type, included pages/journeys, applicable checkpoint count out of 272, public-only exclusions, and the candidate-only rule.</div><button class="button full" type="submit">Start AI first pass</button></form><div class="ai-status" aria-live="polite">${escapeHtml(aiFirstPassState.message || 'No discovery has run.')}</div>${scopeContract}${aiFirstPassState.scope ? `<div class="candidate-list"><h3>${aiFirstPassState.candidates.length} candidates remaining</h3>${aiFirstPassState.candidates.map(candidateCard).join('') || '<p class="muted">No supported candidates remain in this First Pass queue.</p>'}</div>` : ''}</section>`;
  shell(`<div class="eyebrow">Evidence-backed findings</div><h1>Findings queue</h1><p class="sub">Draft with AI uses only this audit’s selected scope, checkpoint, notes, and evidence metadata. You review and apply it yourself.</p>${firstPass}<div class="grid"><section class="card"><h2>Add finding</h2><form id="finding-copilot-form" class="form">${field('title', 'Working title', context.title)}<label class="form-field">Checkpoint<select class="form-select" name="criterionId">${[...new Set([context.criterionId,...Object.keys(audit.assessments)])].filter(Boolean).map(id => `<option value="${id}" ${id === context.criterionId ? 'selected' : ''}>${id} — ${criterionTitle(id)}</option>`).join('')}</select></label>${field('category', 'Category', context.category)}${field('page', 'Page', context.page)}<label class="form-field">Journey<select class="form-select" name="journey">${['Discover','Understand','Complete'].map(value => `<option ${value === context.journey ? 'selected' : ''}>${value}</option>`).join('')}</select></label>${field('notes', 'Your audit notes', context.notes, 'textarea')}${field('alt', 'Evidence description / alt text', context.alt)}${field('capturedAt', 'Evidence captured at (optional)', context.capturedAt)}${field('sourceReference', 'Evidence source / reference (optional)', context.sourceReference)}<div class="full ai-status" aria-live="polite">${escapeHtml(aiDraftState.message || 'No AI draft yet. Your work stays local until you choose Save changes.')}</div><button class="button alt full" type="button" data-action="draft-ai">Draft with AI</button>${review}</form></section><section class="card"><h2>Publication readiness</h2><button class="button" data-action="readiness">Check readiness</button><h2>Current queue</h2>${audit.findings.length ? audit.findings.map(f => `<div class="row"><div><span class="chip ${severityClass(f.severity)}">${f.severity}</span><b> ${f.id}</b><br>${escapeHtml(f.title)}</div></div>`).join('') : '<p class="muted">No findings added yet.</p>'}</section></div>`);
}

function findingsWorkbench() {
  findings();
  const canvas = document.querySelector('.operator-canvas');
  const queue = [...canvas.querySelectorAll('.card')].find((card) => card.textContent.includes('Current queue'));
  if (!queue) return;
  canvas.classList.add('findings-workbench');
  queue.classList.add('findings-workbench__queue');
  const blockers = publicationReadiness?.blockers || [];
  const evidenceReady = audit.findings.filter((finding) => evidenceSource(finding.evidence?.annotatedImage || finding.evidence?.imageUrl || finding.evidence?.image)).length;
  queue.insertAdjacentHTML('afterbegin', `<aside class="findings-workbench__inspector"><p class="operator-overview__eyebrow">Official delivery state</p><h2>Evidence review status</h2><div class="row"><span>Evidence state</span><b>${evidenceReady} / ${audit.findings.length} attached</b></div><div class="row"><span>Publication state</span><b>${publicationReadiness?.ready ? 'Ready' : blockers.length ? 'Blocked' : 'Not checked'}</b></div><p class="muted">Approved findings remain editable. A candidate becomes official only through the human review flow and complete evidence.</p></aside>`);
}
function scorecard(){const r=deriveReport(audit,locale); shell(`<div class="eyebrow">Review before publish</div><h1>Scorecard & priority review</h1><p class="sub">Critical and High priorities remain visible regardless of numerical score.</p><div class="grid"><section class="card"><div class="score">${scoreLabel(r)}</div><h2>Needs targeted improvement</h2><p class="muted">${Array.isArray(audit.assessments) ? audit.assessments.length : Object.keys(audit.assessments).length} checkpoints in this audit scope</p>${sectionRows(r)}</section><section class="card"><h2>Fix now</h2>${r.roadmap.fixNow.length?r.roadmap.fixNow.map(f=>`<div class="finding"><span class="chip high">2 High</span><h3>${escapeHtml(f.id)} — ${escapeHtml(f.title)}</h3><p>${escapeHtml(f.recommendation)}</p></div>`).join(''):'<p class="muted">No Critical or High findings yet.</p>'}<button class="button" data-view="report">Open client report</button></section></div>`);}
function report(){const r=deriveReport(audit,locale); const ar=locale==='ar'; shell(`<article class="report"><div class="report-head"><div><div class="eyebrow">UXM / ${ar?'تدقيق تجربة المستخدم':'Website UX Audit'}</div><h1>${escapeHtml(audit.client)}</h1><p class="sub">${escapeHtml(audit.website)} · ${escapeHtml(audit.url)}</p></div><button class="button alt" data-view="overview">${ar?'مساحة العمل':'Back to workspace'}</button></div><section class="card"><div class="grid"><div><div class="score">${scoreWithScale(r)}</div><h2>${ar?'يحتاج إلى تحسينات مركزة':'Needs targeted improvement'}</h2><p class="muted">${ar?'تم تقييم نطاق أولي من المعايير الأساسية':'Prototype coverage: initial core criteria assessed'}</p></div><div><h2>${r.labels.roadmap}</h2>${[['fixNow',r.labels.fixNow],['fixNext',r.labels.fixNext],['enhanceLater',r.labels.enhanceLater]].map(([key,label])=>`<div class="row"><span>${label}</span><b>${r.roadmap[key].length}</b></div>`).join('')}</div></div></section><section class="roadmap"><div class="eyebrow">${ar?'الملاحظات':'Findings'}</div><h1>${r.labels.roadmap}</h1>${audit.findings.length?audit.findings.map(f=>`<article class="finding"><span class="chip ${severityClass(f.severity)}">${f.severity==='high'?(ar?'2 عالية':'2 High'):f.severity==='medium'?(ar?'3 متوسطة':'3 Medium'):(ar?'4 منخفضة':'4 Low')}</span><h3>${escapeHtml(f.id)} — ${escapeHtml(reportText(f,'title'))}</h3><div class="grid">${workspaceEvidence(f)}<div><b>${ar?'ما لاحظناه':'What we observed'}</b><p>${escapeHtml(reportText(f,'observed'))}</p><b>${ar?'لماذا يهم ذلك':'Why it matters'}</b><p>${escapeHtml(reportText(f,'impact'))}</p><b>${ar?'التوصية':'Recommendation'}</b><p>${escapeHtml(reportText(f,'recommendation'))}</p></div></div></article>`).join(''):`<div class="notice">${ar?'أضف ملاحظة من مساحة العمل لإظهارها هنا.':'Add a finding in the workspace to populate the report.'}</div>`}</section></article>`);}
function findingEditor() {
  const { finding: existing } = resolveFindingEditorSelection(findingEditorSelection, audit.findings);
  const finding = existing || {
    id: nextFindingId(audit.findings), checkpoint: Object.keys(audit.assessments)[0] || 'NAV-01',
    url: audit.url, page: '', journey: '', severity: 'medium', effort: 'medium', title: '', observed: '', impact: '', recommendation: '',
    evidence: { alt: '', capturedAt: '', capture: { device: '' } }, ...pendingFindingDraft,
  };
  const findingEditorId = existing?.id || '';
  const evidence = finding.evidence || {};
  const capture = evidence.capture || {};
  const copy = locale === 'ar'
    ? { eyebrow: 'الدليل أولاً', title: 'محرر الملاحظة والأدلة', hint: 'لا تصبح اقتراحات الذكاء الاصطناعي ملاحظات رسمية. احفظ مسودة المشغّل، أرفق الدليلين، ثم أكّد الاكتمال بصدق.', save: 'حفظ المسودة', complete: 'تأكيد اكتمال الدليل', source: 'لقطة المصدر', annotated: 'لقطة مشروحة', status: 'حالة الدليل' }
    : { eyebrow: 'Evidence first', title: 'Finding editor & evidence', hint: 'AI candidates are not official findings. Save an operator draft, attach both proofs, then truthfully mark evidence complete.', save: 'Save draft', complete: 'Mark evidence complete', source: 'Source screenshot', annotated: 'Annotated screenshot', status: 'Evidence status' };
  const input = (name, label, value = '', type = 'text', extra = '') => `<label class="form-field">${label}<input ${extra} name="${name}" type="${type}" value="${escapeHtml(value)}" required></label>`;
  const area = (name, label, value = '') => `<label class="form-field full">${label}<textarea name="${name}" required>${escapeHtml(value)}</textarea></label>`;
  const image = (item, label) => item?.path ? `<img src="/${escapeHtml(item.path)}" alt="${escapeHtml(label)}">` : `<span>${escapeHtml(label)} — not attached</span>`;
  shell(`<section class="evidence-first-editor" aria-labelledby="finding-editor-title"><aside class="evidence-first-editor__canvas"><p class="operator-overview__eyebrow">${copy.eyebrow}</p><h1 id="finding-editor-title">${copy.title}</h1><p class="muted">${copy.hint}</p><div class="evidence-first-editor__proof">${image(evidence.sourceImage, copy.source)}</div><label class="evidence-upload file-upload-button"><span>${copy.source}</span><span class="file-upload-status" data-evidence-file-status="source" aria-live="polite">Choose PNG or JPEG</span><input class="file-upload-input" aria-label="${copy.source}" data-evidence-upload="${escapeHtml(finding.id)}" data-evidence-kind="source" type="file" accept="image/png,image/jpeg"></label><div class="evidence-first-editor__proof">${image(evidence.annotatedImage, copy.annotated)}</div><label class="evidence-upload file-upload-button"><span>${copy.annotated}</span><span class="file-upload-status" data-evidence-file-status="annotated" aria-live="polite">Choose PNG or JPEG</span><input class="file-upload-input" aria-label="${copy.annotated}" data-evidence-upload="${escapeHtml(finding.id)}" data-evidence-kind="annotated" type="file" accept="image/png,image/jpeg"></label><p class="notice"><b>${copy.status}:</b> ${escapeHtml(evidence.status || 'draft')}</p></aside><form id="evidence-first-finding-form" class="card form evidence-first-editor__record" data-finding-id="${escapeHtml(finding.id)}" data-existing-finding-id="${escapeHtml(existing?.id || '')}"><div class="full finding-editor-picker"><label class="uxm-field">Finding<select class="uxm-select" data-finding-selector><option value="">New finding</option>${audit.findings.map((item) => `<option value="${escapeHtml(item.id)}" ${item.id === findingEditorId ? 'selected' : ''}>${escapeHtml(item.id)} — ${escapeHtml(item.title)}</option>`).join('')}</select></label><button class="uxm-button uxm-button--secondary" type="button" data-action="new-finding">New finding</button></div><div class="full"><p class="operator-overview__eyebrow">Structured operator record</p><p class="muted">A saved draft remains blocked from readiness and PDF export until complete evidence is persisted.</p></div>${input('id', 'Finding ID', finding.id, 'text', 'dir="ltr"')}<label class="form-field">Checkpoint<select name="checkpoint" required>${Object.keys(audit.assessments).map((id) => `<option value="${id}" ${id === finding.checkpoint ? 'selected' : ''}>${id} — ${criterionTitle(id)}</option>`).join('')}</select></label>${input('url', 'URL', finding.url, 'url', 'dir="ltr"')}${input('page', 'Page', finding.page)}${input('journey', 'Journey', finding.journey)}<label class="form-field">Device / capture<select name="device" required><option value="">Choose device</option>${['Desktop Chrome', 'Mobile Safari', 'Android Chrome', 'Other'].map((value) => `<option ${value === capture.device ? 'selected' : ''}>${value}</option>`).join('')}</select></label>${input('capturedAt', 'Capture timestamp', utcIsoToDatetimeLocal(evidence.capturedAt), 'datetime-local')}<label class="form-field">Severity<select name="severity" required>${['critical', 'high', 'medium', 'low'].map((value) => `<option ${value === finding.severity ? 'selected' : ''}>${value}</option>`).join('')}</select></label><label class="form-field">Effort<select name="effort" required>${['low', 'medium', 'high'].map((value) => `<option ${value === finding.effort ? 'selected' : ''}>${value}</option>`).join('')}</select></label>${input('title', 'Finding title', finding.title)}${area('observation', 'Observation', finding.observed)}${area('impact', 'Impact', finding.impact)}${area('recommendation', 'Recommendation', finding.recommendation)}${input('evidenceAlt', 'Evidence description / alt text', evidence.alt)}<div class="evidence-first-editor__actions full"><button class="button" type="submit" data-action="save-finding-draft">${copy.save}</button><button class="button accent" type="button" data-action="complete-finding-evidence">${copy.complete}</button><button class="button alt" type="button" data-action="readiness">Check readiness</button></div><div class="full ai-status" aria-live="polite">${escapeHtml(apiStatus)}</div></form></section>`);
}

async function saveFindingEditorDraft(form) {
  const values = Object.fromEntries(new FormData(form));
  const draft = buildFindingDraft(values, form.dataset.existingFindingId);
  apiStatus = 'Saving operator draft…'; render();
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/findings`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(draft) });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Draft save failed');
    findingEditorSelection = body.id;
    pendingFindingDraft = null;
    const updated = await fetch(`/api/audits/${encodeURIComponent(audit.id)}`);
    establishSavedAudit(normalizeAudit(await updated.json()));
    publicationReadiness = null;
    apiStatus = 'Draft saved. Attach source and annotated evidence, then explicitly mark it complete.';
  } catch (error) { apiStatus = `Could not save draft. ${error.message}`; }
  render();
}

async function completeFindingEvidence(form) {
  const findingId = form.dataset.findingId;
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/findings/${encodeURIComponent(findingId)}/evidence-complete`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(buildEvidenceCompletePayload(findingId)) });
    const body = await response.json();
    if (!response.ok || body.completed !== true) throw new Error(body.error || 'Evidence completion failed');
    const updated = await fetch(`/api/audits/${encodeURIComponent(audit.id)}`);
    establishSavedAudit(normalizeAudit(await updated.json()));
    publicationReadiness = null;
    apiStatus = 'Evidence is truthfully marked complete and can now satisfy publication readiness.';
  } catch (error) { apiStatus = `Evidence remains incomplete. ${error.message}`; }
  render();
}

function bindFindingEditor() {
  const form = document.querySelector('#evidence-first-finding-form');
  form?.addEventListener('submit', (event) => { event.preventDefault(); saveFindingEditorDraft(form); });
  document.querySelector('[data-action="complete-finding-evidence"]')?.addEventListener('click', () => completeFindingEvidence(form));
  document.querySelector('[data-action="new-finding"]')?.addEventListener('click', () => { pendingFindingDraft = null; findingEditorSelection = NEW_FINDING_DRAFT; render(); });
  document.querySelector('[data-finding-selector]')?.addEventListener('change', (event) => { findingEditorSelection = event.target.value || NEW_FINDING_DRAFT; render(); });
}

function scope() {
  const scopeItems = scopeIncludedItems(audit);
  shell(`<section class="scope-view" aria-labelledby="scope-title"><p class="operator-overview__eyebrow">Scope & pages</p><h1 id="scope-title">Review the persisted audit boundary</h1><p class="operator-overview__intro">This read-only view displays the persisted review boundary: its starting URL, scope summary, and included pages. It does not confirm or edit pages or journeys, create findings, or change the score.</p><div class="operator-overview__grid"><section class="operator-overview__panel"><h2>Current audit boundary</h2><div class="row"><span>Starting URL</span><b dir="ltr">${escapeHtml(audit.url)}</b></div><div class="row"><span>Scope summary</span><b>${escapeHtml(scopeSummary(audit))}</b></div><div class="row"><span>Pages in persisted audit</span><b>${scopeItems.length}</b></div><button class="uxm-button uxm-button--secondary" data-view="criteria">Review scoped criteria</button></section><section class="operator-overview__panel"><h2>Included pages and scope items</h2>${scopeItems.length ? scopeItems.map((item) => `<div class="row"><span>${escapeHtml(item.label)}</span>${item.reference ? `<b dir="ltr">${escapeHtml(item.reference)}</b>` : ''}</div>`).join('') : '<p class="muted">No included pages or scope items are persisted for this audit.</p>'}</section><section class="operator-overview__panel"><h2>Next: safe discovery</h2><p>Use First Pass to propose public pages and candidate observations. It remains separate from persisted assessment work.</p><button class="uxm-button uxm-button--primary" data-view="firstPass">Open First Pass</button></section></div></section>`);
}
function firstPass() {
  shell(`<section class="first-pass-view" aria-labelledby="first-pass-title"><p class="operator-overview__eyebrow">Candidate-only discovery</p><h1 id="first-pass-title">Run a safe candidate-only discovery</h1><p class="operator-overview__intro">Public pages only. This creates transient candidates for human review; it never changes assessment, findings, readiness, or score.</p><section class="operator-overview__panel"><form id="first-pass-form" class="form"><label class="form-field full">Website URL<input required name="firstPassUrl" type="url" value="${escapeHtml(aiFirstPassState.url || audit.url)}"></label><button class="uxm-button uxm-button--secondary full" type="button" data-action="detect-product-type">Detect product type</button><p class="ai-status full" aria-live="polite">${escapeHtml(aiFirstPassState.productTypeMessage || 'Choose a product type and scope bundle.')}</p><label class="form-field">Product type<select required class="form-select" name="productType"><option value="">Choose product type</option>${[['government_civic','Government / civic service'],['ecommerce','E-commerce'],['saas_digital_product','SaaS / digital product'],['corporate_marketing','Corporate / marketing website'],['content_publisher','Content / publisher'],['custom','Custom']].map(([value,label]) => `<option value="${value}" ${value === aiFirstPassState.productType ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label class="form-field">Scope bundle<select required class="form-select" name="bundle" ${aiFirstPassState.productType ? '' : 'disabled'}><option value="">Choose scope bundle</option>${[['full_website','Full website'],['selected_pages','Selected pages'],['general_health_check','General health check'],['contact_experience','Contact experience']].map(([value,label]) => `<option value="${value}" ${value === aiFirstPassState.bundle ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label class="form-field full">Selected pages (one per line)<textarea name="selectedPages">${escapeHtml(aiFirstPassState.selectedPages)}</textarea></label><button class="uxm-button uxm-button--primary full" type="submit">Run preliminary first pass</button></form></section>${aiFirstPassState.candidates.length ? `<div class="candidate-list">${aiFirstPassState.candidates.map(candidateCard).join('')}</div>` : ''}</section>`);
}
function readiness() {
  const blockers = publicationReadiness?.blockers || [];
  shell(`<section class="readiness-view" aria-labelledby="readiness-title"><p class="operator-overview__eyebrow">Delivery gate</p><h1 id="readiness-title">Resolve publication blockers</h1><p class="operator-overview__intro">Check persisted evidence and metadata before delivery. This view never edits scope, assessment, or findings.</p><section class="operator-overview__panel"><div class="row"><span>Current status</span><b>${publicationReadiness?.ready ? 'Ready to publish' : publicationReadiness ? 'Blocked' : 'Not checked'}</b></div><button class="uxm-button uxm-button--primary" data-action="readiness">Check publication readiness</button>${publicationReadiness ? (publicationReadiness.ready ? '<p class="uxm-notice">All persisted publication checks passed.</p>' : `<div class="uxm-notice"><b>Resolve before PDF export</b><ul>${blockers.map((blocker) => `<li><span dir="ltr">${escapeHtml(blocker.findingId || '')}</span> ${escapeHtml(blocker.message)}</li>`).join('')}</ul></div>`) : ''}</section></section>`);
}
function bindAssessmentWorklist() {
  document.querySelectorAll('[data-checkpoint-select]').forEach((button) => button.addEventListener('click', () => { selectedCheckpointId = button.dataset.checkpointSelect; render(); }));
  document.querySelector('[data-assessment]')?.addEventListener('change', (event) => { replaceAudit(updateAssessment(audit, event.target.dataset.assessment, event.target.value)); render(); });
  document.querySelector('[data-action="create-linked-finding"]')?.addEventListener('click', () => {
    const linkedFinding = newFindingStateForCheckpoint(selectedCheckpointId);
    findingEditorSelection = linkedFinding.selection;
    pendingFindingDraft = linkedFinding.pendingFindingDraft;
    view = 'findings';
    render();
  });
}
function render(){({overview,scope,firstPass,criteria,findings:findingEditor,scorecard,readiness,report})[view]();}
function bind(){document.querySelectorAll('[data-view]').forEach(el=>el.onclick=()=>{view=el.dataset.view;render()});document.querySelector('[data-action="logout"]')?.addEventListener('click',logout);document.querySelector('#first-pass-form')?.addEventListener('submit',(event)=>{event.preventDefault();requestAiFirstPass(event.currentTarget)});document.querySelector('[data-action="detect-product-type"]')?.addEventListener('click',()=>requestProductTypeDetection(document.querySelector('#first-pass-form')));document.querySelector('[name="productType"]')?.addEventListener('change',(event)=>{const form=document.querySelector('#first-pass-form');aiFirstPassState={...aiFirstPassState,url:form.elements.firstPassUrl.value,productType:event.target.value,bundle:'',productTypeMessage:event.target.value?'Product type selected manually. Now choose a bundle.':'Detect the product type, or choose it manually.'};render()});document.querySelectorAll('[data-action="promote-candidate"]').forEach(el=>el.addEventListener('click',()=>{const candidate=aiFirstPassState.candidates[Number(el.dataset.candidate)];aiDraftState={candidateId:candidate.id,context:{criterionId:candidate.checkpointId,category:'navigation',journey:'Discover',page:'Public page',title:candidate.title,notes:candidate.reasons.join('\n'),alt:'Validate and attach evidence before applying.',capturedAt:'',sourceReference:candidate.evidenceRefs.join(', ')},draft:{observation:candidate.observation,impact:candidate.impact,recommendation:candidate.recommendation,suggestedSeverity:candidate.suggestedSeverity,confidence:candidate.confidence,missingEvidenceChecks:candidate.evidenceGaps,duplicateRisk:{level:'unknown',matches:[]}},message:'Candidate promoted for review only. Validate and attach evidence before applying.'};render()}));document.querySelectorAll('[data-action="reject-candidate"]').forEach(el=>el.addEventListener('click',()=>{aiFirstPassState.candidates.splice(Number(el.dataset.candidate),1);aiFirstPassState={...aiFirstPassState,message:'Candidate rejected. No audit data changed.'};render()}));document.querySelector('[data-action="draft-ai"]')?.addEventListener('click',()=>requestAiDraft(document.querySelector('#finding-copilot-form')));document.querySelector('[data-action="apply-ai-draft"]')?.addEventListener('click',()=>{const form=document.querySelector('#finding-copilot-form');const context=aiContextFromForm(form);const reviewed={...aiDraftState.draft,observation:new FormData(form).get('draftObservation'),impact:new FormData(form).get('draftImpact'),recommendation:new FormData(form).get('draftRecommendation'),suggestedSeverity:new FormData(form).get('draftSeverity')};pendingFindingDraft = buildAiReviewedFindingDraft(context, reviewed);findingEditorSelection=NEW_FINDING_DRAFT;view='findings';aiFirstPassState=removeReviewedCandidate(aiFirstPassState,aiDraftState.candidateId);aiDraftState={context:null,draft:null,message:'Reviewed draft is ready for the operator editor. Save draft to persist it.'};publicationReadiness=null;render()});document.querySelector('[data-action="locale"]')?.addEventListener('click',()=>{locale=locale==='en'?'ar':'en';publicationReadiness=null;render()});document.querySelector('[data-action="export-pdf"]')?.addEventListener('click',exportPdf);document.querySelector('[data-action="readiness"]')?.addEventListener('click',()=>checkPublicationReadiness());document.querySelector('[data-action="save"]')?.addEventListener('click',saveChanges);document.querySelector('[data-action="discard"]')?.addEventListener('click',discardAndReload);document.querySelector('[data-audit]')?.addEventListener('change',(event)=>selectAudit(event.target.value));document.querySelectorAll('[data-evidence-upload]').forEach(el=>el.addEventListener('change',()=>{const file=el.files?.[0];const status=document.querySelector(`[data-evidence-file-status="${el.dataset.evidenceKind}"]`);if(file && status) status.textContent=`${file.name} selected — uploading…`;uploadEvidence(el)}));document.querySelector('#finding-form')?.addEventListener('submit',(e)=>{e.preventDefault();const d=Object.fromEntries(new FormData(e.currentTarget));replaceAudit(createFinding(audit,{criterionId:'NAV-02',category:'information_architecture',...d,url:audit.url,evidence:{alt:d.alt,status:'pending'}}));publicationReadiness=null;render()});}
loadAudits();
