const root = document.querySelector('#operations');
const statusLabels = {
  draft: 'Draft', in_review: 'In review', evidence_complete: 'Evidence complete',
  ready_for_client: 'Ready for client', delivered: 'Delivered',
};
const productTypes = {
  government_civic: 'Government / civic', ecommerce: 'E-commerce', saas_digital_product: 'SaaS / digital product',
  corporate_marketing: 'Corporate / marketing', content_publisher: 'Content / publisher', custom: 'Custom',
};
let state = { clients: [], projects: [], audits: [], requests: [], query: '', message: '', error: '' };
const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character]);

async function jsonRequest(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed');
  return body;
}

async function loadOperations(message = '') {
  try {
    const [clients, projects, audits, requests] = await Promise.all([
      jsonRequest('/api/clients'), jsonRequest('/api/projects'), jsonRequest('/api/audits'), jsonRequest('/api/request-audits'),
    ]);
    state = { ...state, clients, projects, audits, requests, message, error: '' };
  } catch (error) {
    state = { ...state, error: error.message, message: '' };
  }
  render();
}

function clientOptions(selected = '') {
  return `<option value="">Choose client</option>${state.clients.map(client => `<option value="${escapeHtml(client.id)}" ${client.id === selected ? 'selected' : ''}>${escapeHtml(client.name)}</option>`).join('')}`;
}

function unlinkedAuditOptions() {
  const linked = new Set(state.projects.flatMap(project => project.auditIds || []));
  const available = state.audits.filter(audit => !audit.projectId && !linked.has(audit.id));
  return `<option value="">Choose audit</option>${available.map(audit => `<option value="${escapeHtml(audit.id)}">${escapeHtml(audit.client)} — ${escapeHtml(audit.url)}</option>`).join('')}`;
}

function projectCard(project) {
  const audits = state.audits.filter(audit => audit.projectId === project.id);
  return `<article class="card operation-project" data-search="${escapeHtml(`${project.name} ${project.clientName} ${project.baseUrl}`.toLowerCase())}">
    <div class="operation-card-head"><div><div class="eyebrow">${escapeHtml(project.clientName)}</div><h3>${escapeHtml(project.name)}</h3><a href="${escapeHtml(project.baseUrl)}" target="_blank" rel="noreferrer">${escapeHtml(project.baseUrl)}</a></div><span class="chip">${project.auditCount} audit${project.auditCount === 1 ? '' : 's'}</span></div>
    <div class="operation-meta"><span>${escapeHtml(productTypes[project.productType] || 'Product type not set')}</span><span>Owner: ${escapeHtml(project.owner || 'Unassigned')}</span></div>
    <label class="form-field">Project status<select class="form-select" data-project-status="${escapeHtml(project.id)}">${Object.entries(statusLabels).map(([value,label]) => `<option value="${value}" ${value === project.status ? 'selected' : ''}>${label}</option>`).join('')}</select></label>
    <div class="operation-audits"><b>Linked audits</b>${audits.length ? audits.map(audit => `<div class="row"><span>${escapeHtml(audit.id)} · ${audit.findingCount} findings</span><a class="button alt" href="/workspace.html?audit=${encodeURIComponent(audit.id)}">Open audit</a></div>`).join('') : '<p class="muted">No audits linked yet.</p>'}</div>
    <div class="operation-link"><select class="form-select" data-audit-picker="${escapeHtml(project.id)}">${unlinkedAuditOptions()}</select><button class="button alt" type="button" data-link-audit="${escapeHtml(project.id)}">Link audit</button></div>
  </article>`;
}

function requestCard(request) {
  const converted = request.status === 'converted';
  return `<article class="card"><div class="operation-card-head"><div><div class="eyebrow">${escapeHtml(request.service)}</div><h3>${escapeHtml(request.company)}</h3><p>${escapeHtml(request.name)} · <a href="mailto:${escapeHtml(request.email)}">${escapeHtml(request.email)}</a></p></div><span class="chip">${escapeHtml(request.status)}</span></div><p><a href="${escapeHtml(request.website)}" target="_blank" rel="noreferrer">${escapeHtml(request.website)}</a></p><p>${escapeHtml(request.scopeNote)}</p><p class="muted">Preferred contact: ${escapeHtml(request.preferredContact)}. ${converted ? 'Created by an operator.' : 'No audit has started.'}</p>${converted ? `<a class="button alt" href="/workspace.html?audit=${encodeURIComponent(request.auditId)}">Open audit</a>` : `<button class="button" type="button" data-convert-request="${escapeHtml(request.id)}">Create client, project & audit</button>`}</article>`;
}

function render() {
  const assigned = state.audits.filter(audit => audit.projectId).length;
  const query = state.query.trim().toLowerCase();
  const visibleProjects = state.projects.filter(project => !query || `${project.name} ${project.clientName} ${project.baseUrl}`.toLowerCase().includes(query));
  root.className = '';
  root.innerHTML = `<div class="shell"><header class="top"><a class="brand" href="/workspace.html" aria-label="UXM Audit workspace">UXM<span>Audit</span></a><div class="top-actions"><a class="button alt" href="/templates.html">Templates</a><a class="button alt" href="/workspace.html">Audit workspace</a></div></header><main class="operations-main">
    <div class="eyebrow">Internal operations</div><h1>Client & project operations</h1><p class="sub">Organize clients, projects, lifecycle status, and linked audits without changing client-facing reports.</p>
    ${state.error ? `<div class="notice publication-blocked">${escapeHtml(state.error)}</div>` : ''}${state.message ? `<div class="notice">${escapeHtml(state.message)}</div>` : ''}
    <section class="metrics"><div class="metric"><b>${state.clients.length}</b><span>Clients</span></div><div class="metric"><b>${state.projects.length}</b><span>Projects</span></div><div class="metric"><b>${assigned}/${state.audits.length}</b><span>Audits linked</span></div></section>
    <section class="operations-directory"><div class="operation-directory-head"><div><div class="eyebrow">Human review required</div><h2>Request intake</h2></div><span class="chip">${state.requests.filter(request => request.status === 'received').length} awaiting review</span></div>${state.requests.length ? `<div class="operations-projects">${state.requests.map(requestCard).join('')}</div>` : '<div class="card"><p class="muted">No audit requests have been received.</p></div>'}</section>
    <section class="operations-forms"><article class="card"><h2>Create client</h2><form id="client-form" class="form"><label class="form-field">Client name<input required name="name"></label><label class="form-field">Contact name<input name="contactName"></label><label class="form-field">Email<input name="email" type="email"></label><label class="form-field">Phone<input name="phone"></label><label class="form-field full">Notes<textarea name="notes"></textarea></label><button class="button full">Create client</button></form></article>
    <article class="card"><h2>Create project</h2>${state.clients.length ? `<form id="project-form" class="form"><label class="form-field">Client<select required name="clientId" class="form-select">${clientOptions()}</select></label><label class="form-field">Project name<input required name="name"></label><label class="form-field full">Base URL<input required name="baseUrl" type="url"></label><label class="form-field">Product type<select name="productType" class="form-select"><option value="">Not set</option>${Object.entries(productTypes).map(([value,label]) => `<option value="${value}">${label}</option>`).join('')}</select></label><label class="form-field">Owner<input name="owner" value="Abdullah"></label><button class="button full">Create project</button></form>` : '<p class="muted">Create a client first.</p>'}</article></section>
    <section class="operations-directory"><div class="operation-directory-head"><div><div class="eyebrow">Portfolio</div><h2>Projects</h2></div><label class="form-field operation-search">Search<input id="operation-search" type="search" value="${escapeHtml(state.query)}" placeholder="Client, project, or URL"></label></div>
    ${visibleProjects.length ? `<div class="operations-projects">${visibleProjects.map(projectCard).join('')}</div>` : `<div class="card"><p class="muted">${state.projects.length ? 'No projects match this search.' : 'No projects yet. Create the first client and project above.'}</p></div>`}
    </section>
    <section class="card"><h2>Clients</h2>${state.clients.length ? state.clients.map(client => `<div class="row"><span><b>${escapeHtml(client.name)}</b><br><small>${escapeHtml(client.contactName || client.email || 'No contact added')}</small></span><span>${client.projectCount} projects · ${client.auditCount} audits</span></div>`).join('') : '<p class="muted">No clients yet.</p>'}</section>
  </main></div>`;
  bind();
}

function bind() {
  document.querySelector('#client-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    try {
      await jsonRequest('/api/clients', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(event.currentTarget))) });
      await loadOperations('Client created.');
    } catch (error) { state.error = error.message; render(); }
  });
  document.querySelector('#project-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    try {
      await jsonRequest('/api/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(event.currentTarget))) });
      await loadOperations('Project created.');
    } catch (error) { state.error = error.message; render(); }
  });
  document.querySelectorAll('[data-project-status]').forEach(select => select.addEventListener('change', async () => {
    try {
      await jsonRequest(`/api/projects/${encodeURIComponent(select.dataset.projectStatus)}/status`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: select.value }) });
      await loadOperations('Project status updated.');
    } catch (error) { state.error = error.message; render(); }
  }));
  document.querySelectorAll('[data-link-audit]').forEach(button => button.addEventListener('click', async () => {
    const projectId = button.dataset.linkAudit;
    const auditId = document.querySelector(`[data-audit-picker="${CSS.escape(projectId)}"]`)?.value;
    if (!auditId) { state.error = 'Choose an audit to link.'; render(); return; }
    try {
      await jsonRequest(`/api/projects/${encodeURIComponent(projectId)}/audits/${encodeURIComponent(auditId)}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
      await loadOperations('Audit linked to project.');
    } catch (error) { state.error = error.message; render(); }
  }));
  document.querySelectorAll('[data-convert-request]').forEach(button => button.addEventListener('click', async () => {
    try {
      await jsonRequest(`/api/request-audits/${encodeURIComponent(button.dataset.convertRequest)}/create-audit`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
      await loadOperations('Client, project, and draft audit created. No AI First Pass has started.');
    } catch (error) { state.error = error.message; render(); }
  }));
  document.querySelector('#operation-search')?.addEventListener('input', event => { state.query = event.target.value; render(); document.querySelector('#operation-search')?.focus(); });
}

loadOperations();
