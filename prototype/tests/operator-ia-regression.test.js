import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('context controls share one design-system control family with a consistent control height', async () => {
  const [app, css] = await Promise.all([read('../app.js'), read('../workspace-polish.css')]);

  assert.match(app, /audit-context-header__control/);
  assert.match(app, /uxm-button/);
  assert.match(app, /uxm-select/);
  assert.match(css, /\.audit-context-header__control[^}]*min-height:\s*56px/is);
  assert.match(css, /\.audit-context-header__picker\s+\.uxm-select[^}]*min-height:\s*56px/is);
  assert.match(css, /\.audit-context-header__actions\s+\.uxm-button[^}]*padding-inline/is);
});

test('scope, first pass, and readiness have separate work-purpose renderers and exactly one current view', async () => {
  const app = await read('../app.js');

  for (const view of ['scope', 'firstPass', 'readiness']) {
    assert.match(app, new RegExp(`function ${view}\\(\\)`));
    assert.match(app, /\(\{overview,scope,firstPass,criteria,findings:findingEditor,scorecard,readiness,report\}\)/);
  }
  assert.doesNotMatch(app, /scope:findingsWorkbench,firstPass:findingsWorkbench/);
  assert.match(app, /Review the persisted audit boundary/);
  assert.match(app, /This read-only view displays the persisted review boundary/);
  assert.doesNotMatch(app, /Confirm the pages and journeys that belong in this audit/);
  assert.match(app, /Run a safe candidate-only discovery/);
  assert.match(app, /Resolve publication blockers/);
  assert.match(app, /aria-current="\$\{view===key\?'page':'false'\}"/);
});

test('scope surface renders every persisted included item and its truthful count', async () => {
  const app = await read('../app.js');

  assert.match(app, /const scopeItems = scopeIncludedItems\(audit\);/);
  assert.match(app, /Pages in persisted audit<\/span><b>\$\{scopeItems\.length\}<\/b>/);
  assert.match(app, /<h2>Included pages and scope items<\/h2>/);
  assert.match(app, /scopeItems\.map\(\(item\) =>/);
  assert.match(app, /item\.reference/);
});

test('assessment status has one change binding and retains the selected checkpoint after render', async () => {
  const app = await read('../app.js');

  assert.equal((app.match(/\[data-assessment\]/g) || []).length, 1, 'only the assessment worklist owns the change binding');
  assert.match(app, /selectedCheckpointId = selectedId;/);
  assert.match(app, /function bindAssessmentWorklist\(\)[\s\S]*?\[data-assessment\][\s\S]*?render\(\);/);
});

test('criteria creates a new linked finding at the selected checkpoint without crossing persistence or AI boundaries', async () => {
  const app = await read('../app.js');

  assert.match(app, /data-action="create-linked-finding"/);
  assert.match(app, /selectedCheckpointId = selectedId;/);
  assert.match(app, /newFindingStateForCheckpoint\(selectedCheckpointId\)/);
  assert.match(app, /findingEditorSelection = linkedFinding\.selection;/);
  assert.match(app, /pendingFindingDraft = linkedFinding\.pendingFindingDraft;/);
});

test('operator navigation uses truthful operations and audit-template labels', async () => {
  const app = await read('../app.js');

  assert.doesNotMatch(app, /portfolio:'Portfolio'/);
  assert.match(app, /operations:'Operations'/);
  assert.match(app, /templates:'Audit templates'/);
  assert.match(app, /href="\/operations\.html"[^>]*>\$\{copy\.operations\}/);
});

test('criteria is a task-first assessment worklist with selectable inspector and secondary library details', async () => {
  const [app, css] = await Promise.all([read('../app.js'), read('../workspace-polish.css')]);

  assert.match(app, /assessment-worklist/);
  assert.match(app, /data-checkpoint-select/);
  assert.match(app, /assessment-inspector/);
  assert.match(app, /<details class="criteria-library"/);
  assert.doesNotMatch(app, /criteria-workbench__table/);
  assert.match(css, /\.assessment-worklist[^}]*grid-template-columns:/s);
  assert.match(css, /\.assessment-inspector[^}]*position:\s*sticky/s);
});

test('finding editor puts the evidence canvas first and exposes accessible custom file controls', async () => {
  const [app, css] = await Promise.all([read('../app.js'), read('../workspace-polish.css')]);

  assert.match(app, /evidence-first-editor__canvas[\s\S]*evidence-first-editor__record/s);
  assert.match(app, /file-upload-button/);
  assert.match(app, /file-upload-input/);
  assert.match(app, /data-evidence-kind="source"/);
  assert.match(app, /data-evidence-kind="annotated"/);
  assert.match(app, /data-evidence-file-status/);
  assert.match(app, /selected — uploading…/);
  assert.match(app, /finding-editor-picker[\s\S]*uxm-select[\s\S]*uxm-button/s);
  assert.match(css, /\.finding-editor-picker[^}]*align-items:\s*end/s);
  assert.match(css, /\.finding-editor-picker\s+\.uxm-button[^}]*min-height:\s*44px/s);
  assert.match(css, /\.evidence-upload\s+\.file-upload-input[^}]*opacity:\s*0/s);
  assert.match(css, /\.evidence-upload\.file-upload-button[^}]*border:/s);
  assert.match(css, /\.evidence-upload\.file-upload-button[^}]*background:/s);
  assert.match(css, /\.evidence-upload\.file-upload-button[^}]*cursor:\s*pointer/s);
  assert.match(css, /\.evidence-upload\.file-upload-button:hover[^}]*background:/s);
  assert.match(css, /\.evidence-upload\.file-upload-button:focus-within[^}]*outline:/s);
});

test('criteria and editor have true-390 responsive, keyboard-focus, and RTL contracts', async () => {
  const [app, css] = await Promise.all([read('../app.js'), read('../workspace-polish.css')]);

  assert.match(css, /@media\s*\(max-width:\s*390px\)/);
  assert.match(css, /\.assessment-worklist[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/s);
  assert.match(css, /\.evidence-first-editor[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/s);
  assert.match(css, /:focus-visible/);
  assert.match(app, /app\.dir = locale === 'ar' \? 'rtl' : 'ltr'/);
  assert.match(css, /\.rtl\s+\.assessment-inspector/);
});
