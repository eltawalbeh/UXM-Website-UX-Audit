import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createStaticServer } from '../server.mjs';

test('static server returns the separated public landing page', async () => {
  const server = createStaticServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  const response = await fetch(`http://127.0.0.1:${port}/`);
  const html = await response.text();
  server.close();

  assert.equal(response.status, 200);
  assert.match(html, /data-surface="public"/);
  assert.match(html, /UX Mosaic/);
  assert.doesNotMatch(html, /src="app\.js"/);
});

test('workspace exposes evidence attachment and readiness-gated publication controls', async () => {
  const app = await readFile(new URL('../app.js', import.meta.url), 'utf8');

  assert.match(app, /data-evidence-upload/);
  assert.match(app, /\/readiness/);
  assert.match(app, /Publication blocked/);
  assert.match(app, /PDF report/);
  assert.match(app, /\/export-pdf/);
  assert.match(app, /workspaceEvidence\(f\)/);
});

test('workspace composes the approved operator shell around persisted audit context', async () => {
  const app = await readFile(new URL('../app.js', import.meta.url), 'utf8');

  assert.match(app, /workspace-rail/);
  assert.match(app, /audit-context-header/);
  assert.match(app, /audit-subnav/);
  assert.match(app, /Operations/);
  assert.match(app, /Audit templates/);
  assert.match(app, /Deliveries/);
  assert.match(app, /Scope & Pages/);
  assert.match(app, /Score & Priorities/);
  assert.match(app, /Readiness/);
  assert.match(app, /audit\.id/);
  assert.match(app, /publicationReadiness/);
});

test('operator workspace exposes a logout control that calls the session logout endpoint', async () => {
  const app = await readFile(new URL('../app.js', import.meta.url), 'utf8');

  assert.match(app, /data-action=["']logout["']/i);
  assert.match(app, />Log out</i);
  assert.match(app, /fetch\(['"]\/api\/auth\/logout['"],\s*\{\s*method:\s*['"]POST['"]/);
  assert.match(app, /window\.location\.assign\(['"]\/login\.html['"]\)/);
});

test('workspace mobile audit navigation exposes every section without a horizontal strip', async () => {
  const css = await readFile(new URL('../workspace-polish.css', import.meta.url), 'utf8');

  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.audit-subnav\s*\{[^}]*display:\s*grid[^}]*overflow:\s*visible/is);
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.audit-subnav\s*\{[^}]*grid-template-columns:\s*repeat\(2/is);
});

test('workspace mobile primary navigation keeps Operations through Deliveries visible', async () => {
  const css = await readFile(new URL('../workspace-polish.css', import.meta.url), 'utf8');

  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.workspace-rail__nav\s*\{[^}]*display:\s*grid[^}]*overflow:\s*visible/is);
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.workspace-rail__nav\s*\{[^}]*grid-column:\s*1\s*\/\s*-1/is);
});
