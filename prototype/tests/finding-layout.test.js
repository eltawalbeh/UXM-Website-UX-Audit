import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { renderReport } from '../src/report-renderer.js';

const layoutCss = new URL('../report-print.css', import.meta.url);
const audit = {
  id: 'layout-contract', client: 'Layout Contract', url: 'https://example.test',
  findings: [{
    id: 'UXM-LAYOUT', severity: 'high', category: 'usability', page: 'Service', journey: 'Complete',
    title: 'Evidence and prose remain balanced', observed: 'A long observation verifies the narrative column stays usable.',
    impact: 'Narrow prose is difficult to read.', recommendation: 'Keep both columns bounded.',
    evidence: { annotatedImage: { path: 'evidence/layout.png' }, description: 'Annotated proof.' },
  }],
};

test('finding-page DOM and CSS contract gives evidence the editorial majority and keeps narrative readable', async () => {
  const html = renderReport(audit);
  const css = await readFile(layoutCss, 'utf8');

  assert.match(html, /<div class="finding-layout"><figure class="evidence-canvas finding-evidence"><img /);
  assert.match(html, /<div class="finding-story">/);
  assert.match(css, /\.finding-layout\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1\.32fr\)\s+minmax\(330px,\s*\.92fr\)/s);
  assert.match(css, /\.finding-evidence\s*\{[^}]*min-height:\s*310px/s);
  assert.match(css, /\.finding-evidence img\s*\{[^}]*object-fit:\s*contain/s);
  assert.match(css, /\.finding-story\s*\{[^}]*font-size:\s*15px/s);
  assert.match(css, /@media\s*\(max-width:\s*900px\)\s*\{[\s\S]*?\.finding-layout\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/);
  assert.match(css, /@media print\s*\{[\s\S]*?\.finding-evidence\s*\{[^}]*min-height:\s*0/);
});
