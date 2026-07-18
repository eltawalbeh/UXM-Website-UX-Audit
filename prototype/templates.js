const root = document.querySelector('#templates');
const bundleLabels = { full_website: 'Full website', selected_pages: 'Selected pages', general_health_check: 'General health check', contact_experience: 'Contact experience' };
const evidenceLabels = { page_url: 'Page URL', journey: 'Journey', source_screenshot: 'Source screenshot', annotated_screenshot: 'Annotated screenshot', capture_timestamp: 'Capture time', viewport: 'Viewport' };
let state = { templates: [], projects: [], selectedTemplateId: '', selectedProjectId: '', createdAudit: null, message: '', error: '' };
const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character]);

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed');
  return body;
}

async function loadCatalog() {
  try {
    const [templates, projects] = await Promise.all([requestJson('/api/audit-templates'), requestJson('/api/projects')]);
    state.templates = templates;
    state.projects = projects;
    state.selectedProjectId ||= projects[0]?.id || '';
    const project = projects.find(item => item.id === state.selectedProjectId);
    state.selectedTemplateId ||= templates.find(item => item.productType === project?.productType)?.id || templates[0]?.id || '';
  } catch (error) {
    state.error = error.message;
  }
  render();
}

function templateCard(template) {
  const selected = template.id === state.selectedTemplateId;
  return `<article class="card template-card ${selected ? 'template-selected' : ''}">
    <div class="operation-card-head"><div><div class="eyebrow">${escapeHtml(bundleLabels[template.defaultBundle] || template.defaultBundle)}</div><h2>${escapeHtml(template.name)}</h2></div><span class="chip">${template.checkpointIds.length} checkpoints</span></div>
    <p class="muted">${escapeHtml(template.description)}</p>
    <div><b>Default journeys</b><ol class="template-list">${template.journeys.map(journey => `<li>${escapeHtml(journey)}</li>`).join('')}</ol></div>
    <div><b>Evidence contract</b><p class="muted">${template.evidenceRequirements.map(item => escapeHtml(evidenceLabels[item] || item)).join(' · ')}</p></div>
    <button class="button ${selected ? '' : 'alt'} full" type="button" data-use-template="${escapeHtml(template.id)}">${selected ? 'Selected' : 'Use template'}</button>
  </article>`;
}

function render() {
  const selectedTemplate = state.templates.find(item => item.id === state.selectedTemplateId);
  root.className = '';
  root.innerHTML = `<div class="shell"><header class="top"><a class="brand" href="/workspace.html">UXM<span>Audit</span></a><div class="top-actions"><a class="button alt" href="/operations.html">Operations</a><a class="button alt" href="/workspace.html">Audit workspace</a></div></header><main class="operations-main">
    <div class="eyebrow">Reusable setup</div><h1>Audit templates</h1><p class="sub">Start a project-linked audit with a controlled journey and checkpoint baseline. Templates create structure only—not findings, scores, evidence, or AI output.</p>
    ${state.error ? `<div class="notice publication-blocked">${escapeHtml(state.error)}</div>` : ''}${state.message ? `<div class="notice">${escapeHtml(state.message)}</div>` : ''}
    ${state.createdAudit ? `<section class="notice"><b>Audit created.</b> ${state.createdAudit.assessments ? Object.keys(state.createdAudit.assessments).length : 0} checkpoints are ready for manual assessment. <a class="button alt" href="/workspace.html?audit=${encodeURIComponent(state.createdAudit.id)}">Open audit</a></section>` : ''}
    <section class="card template-create"><div><div class="eyebrow">Create baseline</div><h2>New audit from template</h2><p class="muted">All checkpoints start as <b>Not verified</b>. No findings or evidence are generated.</p></div>
    ${state.projects.length && state.templates.length ? `<form id="template-form" class="form"><label class="form-field">Project<select required class="form-select" name="projectId">${state.projects.map(project => `<option value="${escapeHtml(project.id)}" ${project.id === state.selectedProjectId ? 'selected' : ''}>${escapeHtml(project.clientName)} — ${escapeHtml(project.name)}</option>`).join('')}</select></label><label class="form-field">Template<select required class="form-select" name="templateId">${state.templates.map(template => `<option value="${escapeHtml(template.id)}" ${template.id === state.selectedTemplateId ? 'selected' : ''}>${escapeHtml(template.name)} — ${template.checkpointIds.length}</option>`).join('')}</select></label><label class="form-field">Audit title<input name="title" placeholder="Defaults to project name"></label><label class="form-field">URL override<input name="url" type="url" placeholder="Defaults to project URL"></label><label class="form-field">Report language<select class="form-select" name="locale"><option value="en">English</option><option value="ar">Arabic</option></select></label><button class="button" type="submit">Create audit</button></form>` : '<p class="muted">Create a project before using a template.</p>'}</section>
    ${selectedTemplate ? `<section class="template-contract"><div class="metric"><b>${selectedTemplate.checkpointIds.length}</b><span>Official UXM checkpoints</span></div><div class="metric"><b>${selectedTemplate.journeys.length}</b><span>Default journeys</span></div><div class="metric"><b>${selectedTemplate.reportSections.length}</b><span>Report sections</span></div></section>` : ''}
    <section><div class="eyebrow">Catalog v1</div><h2>Choose a template</h2><div class="template-grid">${state.templates.map(templateCard).join('')}</div></section>
  </main></div>`;
  bind();
}

function bind() {
  document.querySelectorAll('[data-use-template]').forEach(button => button.addEventListener('click', () => {
    state.selectedTemplateId = button.dataset.useTemplate;
    state.message = '';
    render();
    document.querySelector('#template-form')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }));
  document.querySelector('[name="projectId"]')?.addEventListener('change', event => {
    state.selectedProjectId = event.target.value;
    const project = state.projects.find(item => item.id === state.selectedProjectId);
    state.selectedTemplateId = state.templates.find(item => item.productType === project?.productType)?.id || state.selectedTemplateId;
    render();
  });
  document.querySelector('[name="templateId"]')?.addEventListener('change', event => {
    state.selectedTemplateId = event.target.value;
    render();
  });
  document.querySelector('#template-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const projectId = data.projectId;
    delete data.projectId;
    if (!data.title) delete data.title;
    if (!data.url) delete data.url;
    try {
      const audit = await requestJson(`/api/projects/${encodeURIComponent(projectId)}/audits/from-template`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      state.createdAudit = audit;
      state.message = `Created ${audit.website} from ${audit.templateId}.`;
      state.error = '';
      const projects = await requestJson('/api/projects');
      state.projects = projects;
      render();
    } catch (error) {
      state.error = error.message;
      state.message = '';
      render();
    }
  });
}

loadCatalog();
