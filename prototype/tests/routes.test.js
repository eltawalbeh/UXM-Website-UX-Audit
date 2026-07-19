import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createStaticServer } from '../server.mjs';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

async function withServer(run) {
  const server = createStaticServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try { await run(`http://127.0.0.1:${server.address().port}`); }
  finally { await new Promise((resolve) => server.close(resolve)); }
}

test('canonical product surfaces are served as distinct frontend documents', async () => {
  const routes = {
    '/': ['public', 'UX Mosaic'],
    '/login.html': ['login', 'Operator login'],
    '/request-audit.html': ['request-audit', 'Request an audit'],
    '/workspace.html': ['operator', 'UXM Audit Workspace'],
    '/report.html': ['shared-report', 'UXM Client Report'],
  };

  await withServer(async (baseUrl) => {
    for (const [route, [surface, title]] of Object.entries(routes)) {
      const response = await fetch(baseUrl + route);
      const html = await response.text();
      assert.equal(response.status, 200, route);
      assert.match(html, new RegExp(`data-surface=["']${surface}["']`), route);
      assert.match(html, new RegExp(`<title>[^<]*${title}`, 'i'), route);
    }
  });
});

test('public routes do not boot the operator application', async () => {
  const [landing, login, request, workspace, report] = await Promise.all([
    read('../index.html'), read('../login.html'), read('../request-audit.html'),
    read('../workspace.html'), read('../report.html'),
  ]);

  for (const html of [landing, login, request, workspace, report]) {
    assert.match(html, /<link\s+rel=["']icon["']\s+href=["']data:,["']/i);
  }
  for (const html of [landing, login, request]) {
    assert.doesNotMatch(html, /src=["']app\.js["']/i);
    assert.match(html, /src\/ui\/tokens\.css/i);
    assert.match(html, /src\/ui\/base\.css/i);
  }
  assert.match(landing, /href=["']request-audit\.html["']/i);
  assert.match(landing, /href=["']login\.html["']/i);
  assert.match(workspace, /id=["']app["']/i);
  assert.match(workspace, /src=["']app\.js["']/i);
  assert.match(report, /id=["']report-app["']/i);
  assert.match(report, /src=["']report\.js["']/i);
  assert.doesNotMatch([landing, login, request, workspace, report].join('\n'), /client portal/i);
});

test('public landing exposes the evidence-led conversion journey without fabricated proof', async () => {
  const landing = await read('../index.html');

  assert.match(landing, /How it works/);
  assert.match(landing, /Services/);
  assert.match(landing, /Methodology/);
  assert.match(landing, /Selected work available on request/);
  assert.match(landing, /Discover with AI/);
  assert.match(landing, /Validate with experts/);
  assert.match(landing, /Prove with evidence/);
  assert.match(landing, /Deliver with confidence/);
  assert.match(landing, /src=["']landing\.js["']/i);
  assert.match(landing, /data-i18n=["']request["']/i);
  assert.match(landing, /data-i18n=["']how["']/i);
  const landingScript = await read('../landing.js');
  assert.match(landingScript, /locale=ar/);
  assert.match(landingScript, /document\.documentElement\.dir\s*=\s*['"]rtl['"]/);
  assert.match(landingScript, /طلب تدقيق/);
});


test('local operator launcher opens the canonical workspace route', async () => {
  const launcher = await read('../START-UXM-AUDIT.bat');
  assert.match(launcher, /http:\/\/127\.0\.0\.1:4173\/workspace\.html/i);
});

test('workspace mobile navigation keeps every operator control visible without an overflow strip', async () => {
  const css = await read('../styles.css');
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.top-actions\s*\{[^}]*grid-template-columns:\s*repeat\(2/is);
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.layout\s*>\s*nav\s*\{[^}]*display:\s*grid[^}]*overflow:\s*visible/is);
  assert.match(css, /\.layout\s*>\s*nav\s*\.workspace-picker\s*\{[^}]*grid-column:\s*1\s*\/\s*-1/is);
});

test('shared report cover keeps headings readable on its dark surface', async () => {
  const css = await read('../report-print.css');
  assert.match(css, /\.cover-page\s+h1[^}]*color:\s*inherit/is);
  assert.match(css, /\.closing-page\s+h2[^}]*color:\s*inherit/is);
});

test('operator links use the canonical workspace route instead of the public landing page', async () => {
  const [app, operations, templates] = await Promise.all([
    read('../app.js'), read('../operations.js'), read('../templates.js'),
  ]);
  const source = `${app}\n${operations}\n${templates}`;

  assert.match(app, /href=["']\/workspace\.html["']/i);
  assert.doesNotMatch(source, /href=["']\/(?:\?audit=[^"']*)?["']/i);
  assert.match(operations, /\/workspace\.html\?audit=/i);
  assert.match(templates, /\/workspace\.html\?audit=/i);
});
