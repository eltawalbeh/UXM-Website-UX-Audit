import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createStaticServer } from '../server.mjs';

test('static server returns the prototype home page', async () => {
  const server = createStaticServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  const response = await fetch(`http://127.0.0.1:${port}/`);
  const html = await response.text();
  server.close();

  assert.equal(response.status, 200);
  assert.match(html, /UXM Audit/);
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
