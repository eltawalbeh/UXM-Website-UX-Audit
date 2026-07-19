import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

test('request-audit public surface submits every intake field and has an honest confirmation state', async () => {
  const [html, script] = await Promise.all([
    readFile(new URL('../request-audit.html', import.meta.url), 'utf8'),
    readFile(new URL('../request-audit.js', import.meta.url), 'utf8'),
  ]);

  for (const field of ['name', 'email', 'company', 'website', 'service', 'scopeNote', 'preferredContact']) {
    assert.match(html, new RegExp(`name=["']${field}["']`, 'i'), field);
  }
  assert.doesNotMatch(html, /\bdisabled\b/i);
  assert.match(html, /request-audit\.js/i);
  assert.match(script, /fetch\(['"]\/api\/request-audits['"]/);
  assert.match(script, /credentials:\s*['"]same-origin['"]/);
  assert.match(script, /received/i);
  assert.match(script, /No audit has started/i);
  assert.match(script, /document\.documentElement\.dir\s*=\s*['"]rtl['"]/);
  assert.match(script, /طلب تدقيق/i);
});

test('operator operations page exposes a dedicated intake queue and explicit conversion action', async () => {
  const operations = await readFile(new URL('../operations.js', import.meta.url), 'utf8');

  assert.match(operations, /\/api\/request-audits/);
  assert.match(operations, /Request intake/);
  assert.match(operations, /Create client, project & audit/);
  assert.match(operations, /create-audit/);
  assert.match(operations, /No audit has started/i);
});
