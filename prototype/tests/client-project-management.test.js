import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const htmlPath = new URL('../operations.html', import.meta.url);
const jsPath = new URL('../operations.js', import.meta.url);

test('operations workspace exposes real client and project management flows', () => {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const js = fs.readFileSync(jsPath, 'utf8');
  const surface = `${html}\n${js}`;
  assert.match(surface, /Client & project operations/);
  assert.match(surface, /Create client/);
  assert.match(surface, /Create project/);
  assert.match(js, /\/api\/clients/);
  assert.match(js, /\/api\/projects/);
  assert.match(js, /ready_for_client/);
  assert.match(js, /Link audit/);
  assert.match(js, /auditCount/);
  assert.match(js, /projectCount/);
});
