import { createSeedAudit, updateAssessment, createFinding, deriveReport } from './src/audit-state.js';
import { checkpointSectionById } from './src/section-scoring.js';
import { displayScore, scopeSummary } from './src/display-score.js';
import { applyAiDraft, beginWorkspace, changeAudit, discardChanges, isDirty, markSaved } from './src/workspace-state.js';
import { removeReviewedCandidate } from './src/ai-first-pass-state.js';

let workspace = beginWorkspace(createSeedAudit());
let audit = workspace.audit;
let audits = [];
let apiStatus = 'Loading persisted audits…';
let publicationReadiness = null;
let aiDraftState = { context: null, draft: null, message: '' };
let aiFirstPassState = { url: '', productType: '', productTypeMessage: '', bundle: '', selectedPages: '', scope: null, candidates: [], message: '' };

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
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(audit),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Save request failed');
    establishSavedAudit(audit);
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

async function loadAudits() {
  try {
    const response = await fetch('/api/audits');
    if (!response.ok) throw new Error('Audit API unavailable');
    audits = await response.json();
    if (audits.length) await selectAudit(audits[0].id);
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
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/findings/${encodeURIComponent(input.dataset.evidenceUpload)}/evidence?kind=${input.dataset.evidenceKind}`, { method: 'POST', body: file, headers: { 'Content-Type': file.type, 'X-Original-Filename': file.name, 'X-Captured-At': new Date().toISOString() } });
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
const score = (report) => displayScore(audit, derivedScore(report));
const sectionRows = (report) => report.sectionScores.map(({ name, score: sectionScore, assessedCount, applicableCount }) => `<div class="row"><span>${name}<br><small class="muted">${applicableCount} applicable / ${assessedCount} assessed</small></span><b>${sectionScore === null ? 'Not scored' : `${sectionScore}%`}</b></div>`).join('') || '<p class="muted">No mapped checkpoints have been assessed in this audit.</p>';
const sectionScoreFor = (report, id) => report.sectionScores.find((section) => section.name === checkpointSectionById[id])?.score;
const formatSectionScore = (value) => value === null || value === undefined ? 'Not scored' : `${value}%`;
const nav = () => `<nav><label class="workspace-picker">Workspace audit<select data-audit>${audits.length ? audits.map(item => `<option value="${item.id}" ${item.id===audit.id?'selected':''}>${item.client}</option>`).join('') : '<option>Local prototype example</option>'}</select><small>${apiStatus}</small></label>${[['overview','Overview'],['criteria','Criteria'],['findings','Findings'],['scorecard','Scorecard'],['report','Client report']].map(([key,label]) => `<button data-view="${key}" class="${view===key?'active':''}">${label}</button>`).join('')}<div class="health"><b>${Array.isArray(audit.assessments) ? audit.assessments.length : Object.keys(audit.assessments).length}</b>assessments in workspace<br><br><b>${audit.findings.length}</b>evidence-backed findings</div></nav>`;

function shell(content) { const dirty = isDirty(workspace); app.className = locale === 'ar' ? 'rtl' : ''; app.innerHTML = `<div class="shell"><header class="top"><div class="brand" aria-label="UXM Audit">UXM<span>Audit</span></div><div class="top-actions">${dirty ? `<span class="save-state unsaved" aria-live="polite">${workspaceSaveState()}</span><button class="button alt" data-action="discard">Discard</button><button class="button" data-action="save">Save</button>` : ''}<button class="button alt" data-action="locale">${locale==='en'?'العربية':'English'}</button><button class="button" data-action="export-pdf">PDF report</button></div></header><div class="layout">${nav()}<main class="main">${content}</main></div></div>`; bind(); }
function overview() { const r=deriveReport(audit,locale); shell(`<div class="eyebrow">Internal workspace</div><h1>${audit.client} — Website Audit</h1><p class="sub">${scopeSummary(audit)}</p><div class="metrics"><div class="metric"><b>${score(r)}</b><span class="muted">Provisional UX health score</span></div><div class="metric"><b>${r.roadmap.fixNow.length}</b><span class="muted">Critical / High priorities</span></div><div class="metric"><b>${audit.findings.length}</b><span class="muted">Evidence-backed findings</span></div></div><div class="grid"><section class="card"><h2>Continue audit</h2><p class="muted">Review the criteria, capture evidence, then let the roadmap organize the work.</p><button class="button" data-view="criteria">Review criteria</button> <button class="button alt" data-view="findings">Add finding</button></section><section class="card"><h2>Section health</h2>${sectionRows(r)}</section></div>`); }
function criteria() { const r=deriveReport(audit,locale); shell(`<div class="eyebrow">Assessment library</div><h1>Criteria review</h1><p class="sub">Change a checkpoint status and watch section health update immediately.</p><table class="criteria"><thead><tr><th>ID</th><th>Checkpoint</th><th>Assessment</th><th>Section score</th></tr></thead><tbody>${Object.entries(audit.assessments).map(([id,status])=>`<tr><td><b>${id}</b></td><td>${criterionTitle(id)}</td><td><select data-assessment="${id}">${['pass','partial','issue','not_applicable','not_verified'].map(s=>`<option value="${s}" ${s===status?'selected':''}>${s.replace('_',' ')}</option>`).join('')}</select></td><td>${formatSectionScore(sectionScoreFor(r, id))}</td></tr>`).join('')}</tbody></table><div class="notice">Pass = 1, Partial = 0.5, Issue = 0. Not applicable and Not verified are excluded from scoring.</div>`); }
function criterionTitle(id){return ({'NAV-01':'Likely destinations are easy to navigate to','NAV-02':'Navigation labels use user trigger words','NAV-03':'Navigation feedback shows where the user is','FORM-01':'Field labels explain desired input','FORM-02':'Required and optional fields are distinguished','A11Y-01':'Text contrast meets WCAG AA on core task states'})[id]||id;}
function reportText(f, field) { return locale === 'ar' ? (f.arabic?.[field] || f[field] || f.description || 'الترجمة العربية مطلوبة قبل النشر') : (f[field] || f.description || 'Evidence description unavailable'); }
function evidenceSource(value) { if (typeof value === 'string') { try { return evidenceSource(JSON.parse(value)); } catch { return value; } } return value && typeof value === 'object' ? evidenceSource(value.path || value.url) : ''; }
function workspaceEvidence(finding) { const evidence = finding.evidence || {}; const source = evidenceSource(evidence.annotatedImage) || evidenceSource(evidence.imageUrl) || evidenceSource(evidence.image); return source ? `<figure class="evidence"><img src="${source}" alt="${reportText(evidence,'alt')}"><figcaption>${reportText(evidence,'alt')}</figcaption></figure>` : `<div class="evidence publication-blocked"><strong>Evidence blocked</strong><span>Annotated evidence image is required before publication.</span></div>`; }
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
  return `<article class="candidate"><div class="eyebrow">${escapeHtml(candidate.reviewState || 'Awaiting review')} · candidate ${escapeHtml(candidate.id || index + 1)}</div><h3>${escapeHtml(candidate.title)}</h3><p><b>${escapeHtml(candidate.pageName || 'Public page')}</b><br><a href="${escapeHtml(candidate.pageUrl || candidate.evidenceRefs?.[0] || '')}" target="_blank" rel="noreferrer">${escapeHtml(candidate.pageUrl || '')}</a><br>Journey: ${escapeHtml(candidate.journey || 'Not specified')} · Checkpoint: ${escapeHtml(candidate.checkpointId || 'Not mapped')}</p><p>${escapeHtml(candidate.observation)}</p><p><b>Why flagged</b><br>${candidate.reasons.map(escapeHtml).join('<br>')}</p><p><b>Evidence links / captures</b><br>${candidate.evidenceRefs.map(url => `<a href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(url)}</a>`).join('<br>')}</p><p><b>Confidence:</b> ${escapeHtml(candidate.confidence)} · <b>Duplicate risk:</b> ${escapeHtml(candidate.duplicateRisk || 'unknown')} · <b>Gaps:</b><br>${candidate.evidenceGaps.map(escapeHtml).join('<br>')}</p><button class="button accent" type="button" data-action="promote-candidate" data-candidate="${index}">Promote for review</button> <button class="button alt" type="button" data-action="reject-candidate" data-candidate="${index}">Reject</button></article>`;
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

function scorecard(){const r=deriveReport(audit,locale); shell(`<div class="eyebrow">Review before publish</div><h1>Scorecard & priority review</h1><p class="sub">Critical and High priorities remain visible regardless of numerical score.</p><div class="grid"><section class="card"><div class="score">${score(r)}</div><h2>Needs targeted improvement</h2><p class="muted">${Array.isArray(audit.assessments) ? audit.assessments.length : Object.keys(audit.assessments).length} checks assessed in this audit scope</p>${sectionRows(r)}</section><section class="card"><h2>Fix now</h2>${r.roadmap.fixNow.length?r.roadmap.fixNow.map(f=>`<div class="finding"><span class="chip high">2 High</span><h3>${f.id} — ${f.title}</h3><p>${f.recommendation}</p></div>`).join(''):'<p class="muted">No Critical or High findings yet.</p>'}<button class="button" data-view="report">Open client report</button></section></div>`);}
function report(){const r=deriveReport(audit,locale); const ar=locale==='ar'; shell(`<article class="report"><div class="report-head"><div><div class="eyebrow">UXM / ${ar?'تدقيق تجربة المستخدم':'Website UX Audit'}</div><h1>${audit.client}</h1><p class="sub">${audit.website} · ${audit.url}</p></div><button class="button alt" data-view="overview">${ar?'مساحة العمل':'Back to workspace'}</button></div><section class="card"><div class="grid"><div><div class="score">${score(r)}<small>/100</small></div><h2>${ar?'يحتاج إلى تحسينات مركزة':'Needs targeted improvement'}</h2><p class="muted">${ar?'تم تقييم نطاق أولي من المعايير الأساسية':'Prototype coverage: initial core criteria assessed'}</p></div><div><h2>${r.labels.roadmap}</h2>${[['fixNow',r.labels.fixNow],['fixNext',r.labels.fixNext],['enhanceLater',r.labels.enhanceLater]].map(([key,label])=>`<div class="row"><span>${label}</span><b>${r.roadmap[key].length}</b></div>`).join('')}</div></div></section><section class="roadmap"><div class="eyebrow">${ar?'الملاحظات':'Findings'}</div><h1>${r.labels.roadmap}</h1>${audit.findings.length?audit.findings.map(f=>`<article class="finding"><span class="chip ${severityClass(f.severity)}">${f.severity==='high'?(ar?'2 عالية':'2 High'):f.severity==='medium'?(ar?'3 متوسطة':'3 Medium'):(ar?'4 منخفضة':'4 Low')}</span><h3>${f.id} — ${reportText(f,'title')}</h3><div class="grid">${workspaceEvidence(f)}<div><b>${ar?'ما لاحظناه':'What we observed'}</b><p>${reportText(f,'observed')}</p><b>${ar?'لماذا يهم ذلك':'Why it matters'}</b><p>${reportText(f,'impact')}</p><b>${ar?'التوصية':'Recommendation'}</b><p>${reportText(f,'recommendation')}</p></div></div></article>`).join(''):`<div class="notice">${ar?'أضف ملاحظة من مساحة العمل لإظهارها هنا.':'Add a finding in the workspace to populate the report.'}</div>`}</section></article>`);}
function render(){({overview,criteria,findings,scorecard,report})[view]();}
function bind(){document.querySelectorAll('[data-view]').forEach(el=>el.onclick=()=>{view=el.dataset.view;render()});document.querySelector('#first-pass-form')?.addEventListener('submit',(event)=>{event.preventDefault();requestAiFirstPass(event.currentTarget)});document.querySelector('[data-action="detect-product-type"]')?.addEventListener('click',()=>requestProductTypeDetection(document.querySelector('#first-pass-form')));document.querySelector('[name="productType"]')?.addEventListener('change',(event)=>{const form=document.querySelector('#first-pass-form');aiFirstPassState={...aiFirstPassState,url:form.elements.firstPassUrl.value,productType:event.target.value,bundle:'',productTypeMessage:event.target.value?'Product type selected manually. Now choose a bundle.':'Detect the product type, or choose it manually.'};render()});document.querySelectorAll('[data-action="promote-candidate"]').forEach(el=>el.addEventListener('click',()=>{const candidate=aiFirstPassState.candidates[Number(el.dataset.candidate)];aiDraftState={candidateId:candidate.id,context:{criterionId:candidate.checkpointId,category:'navigation',journey:'Discover',page:'Public page',title:candidate.title,notes:candidate.reasons.join('\n'),alt:'Validate and attach evidence before applying.',capturedAt:'',sourceReference:candidate.evidenceRefs.join(', ')},draft:{observation:candidate.observation,impact:candidate.impact,recommendation:candidate.recommendation,suggestedSeverity:candidate.suggestedSeverity,confidence:candidate.confidence,missingEvidenceChecks:candidate.evidenceGaps,duplicateRisk:{level:'unknown',matches:[]}},message:'Candidate promoted for review only. Validate and attach evidence before applying.'};render()}));document.querySelectorAll('[data-action="reject-candidate"]').forEach(el=>el.addEventListener('click',()=>{aiFirstPassState.candidates.splice(Number(el.dataset.candidate),1);aiFirstPassState={...aiFirstPassState,message:'Candidate rejected. No audit data changed.'};render()}));document.querySelector('[data-action="draft-ai"]')?.addEventListener('click',()=>requestAiDraft(document.querySelector('#finding-copilot-form')));document.querySelector('[data-action="apply-ai-draft"]')?.addEventListener('click',()=>{const form=document.querySelector('#finding-copilot-form');const context=aiContextFromForm(form);const reviewed={...aiDraftState.draft,observation:new FormData(form).get('draftObservation'),impact:new FormData(form).get('draftImpact'),recommendation:new FormData(form).get('draftRecommendation'),suggestedSeverity:new FormData(form).get('draftSeverity')};replaceAudit(applyAiDraft(audit,context,reviewed));aiFirstPassState=removeReviewedCandidate(aiFirstPassState,aiDraftState.candidateId);aiDraftState={context:null,draft:null,message:'Reviewed draft applied locally. Save changes when you are ready.'};publicationReadiness=null;render()});document.querySelector('[data-action="locale"]')?.addEventListener('click',()=>{locale=locale==='en'?'ar':'en';publicationReadiness=null;render()});document.querySelector('[data-action="export-pdf"]')?.addEventListener('click',exportPdf);document.querySelector('[data-action="readiness"]')?.addEventListener('click',()=>checkPublicationReadiness());document.querySelector('[data-action="save"]')?.addEventListener('click',saveChanges);document.querySelector('[data-action="discard"]')?.addEventListener('click',discardAndReload);document.querySelector('[data-audit]')?.addEventListener('change',(event)=>selectAudit(event.target.value));document.querySelectorAll('[data-assessment]').forEach(el=>el.onchange=()=>{replaceAudit(updateAssessment(audit,el.dataset.assessment,el.value));render()});document.querySelectorAll('[data-evidence-upload]').forEach(el=>el.addEventListener('change',()=>uploadEvidence(el)));document.querySelector('#finding-form')?.addEventListener('submit',(e)=>{e.preventDefault();const d=Object.fromEntries(new FormData(e.currentTarget));replaceAudit(createFinding(audit,{criterionId:'NAV-02',category:'information_architecture',...d,url:audit.url,evidence:{alt:d.alt,status:'pending'}}));publicationReadiness=null;render()});}
loadAudits();
