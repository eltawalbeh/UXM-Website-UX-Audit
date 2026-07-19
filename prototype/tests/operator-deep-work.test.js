import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('deep-work surfaces keep criteria, evidence, and human candidate decisions structurally separate', async () => {
  const [app, css] = await Promise.all([
    read('../app.js'),
    read('../workspace-polish.css'),
  ]);

  assert.match(app, /criteria-workbench/);
  assert.match(app, /findings-workbench/);
  assert.match(app, /candidate-review/);
  assert.match(app, /candidate-review__decision-bar/);
  assert.match(app, /Reject/);
  assert.match(app, /Edit as draft/);
  assert.match(app, /Promote for review/);
  assert.match(app, /not changed the score/);

  assert.match(css, /\.criteria-workbench\s*\{[^}]*grid-template-columns:/s);
  assert.match(css, /\.findings-workbench\s*\{[^}]*grid-template-columns:/s);
  assert.match(css, /\.candidate-review__decision-bar\s*\{[^}]*position:\s*sticky/s);
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.criteria-workbench\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/s);
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.findings-workbench\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/s);
});

test('approved findings render as an evidence-first queue with an explicit publication state', async () => {
  const app = await read('../app.js');
  const css = await read('../workspace-polish.css');

  assert.match(app, /findings-workbench__queue/);
  assert.match(app, /Evidence state/);
  assert.match(app, /Publication state/);
  assert.match(app, /Evidence review status/);
  assert.match(css, /\.findings-workbench__queue\s*\{[^}]*border:/s);
  assert.match(css, /\.findings-workbench__inspector\s*\{[^}]*position:\s*sticky/s);
});
