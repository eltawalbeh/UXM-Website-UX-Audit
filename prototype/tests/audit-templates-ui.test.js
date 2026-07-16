import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const html = fs.readFileSync(new URL('../templates.html', import.meta.url), 'utf8');
const js = fs.readFileSync(new URL('../templates.js', import.meta.url), 'utf8');
const operations = fs.readFileSync(new URL('../operations.html', import.meta.url), 'utf8') + fs.readFileSync(new URL('../operations.js', import.meta.url), 'utf8');
const workspace = fs.readFileSync(new URL('../app.js', import.meta.url), 'utf8');

test('template catalog creates a project-linked audit with an explicit clean baseline', () => {
  assert.match(`${html}\n${js}`, /Audit templates/);
  assert.match(js, /\/api\/audit-templates/);
  assert.match(js, /audits\/from-template/);
  assert.match(js, /Create audit/);
  assert.match(js, /not verified/i);
  assert.match(js, /No findings or evidence are generated/);
});

test('templates are reachable from both operations and audit workspace', () => {
  assert.match(operations, /templates\.html/);
  assert.match(workspace, /templates\.html/);
});
