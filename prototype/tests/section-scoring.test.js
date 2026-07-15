import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { checkpointSectionById, deriveSectionScores } from '../src/section-scoring.js';

const pilot = async (name) => JSON.parse(await readFile(new URL(`../../pilots/${name}/audit.json`, import.meta.url), 'utf8'));

test('maps real checkpoint IDs to their immutable UXM library sections', () => {
  assert.equal(checkpointSectionById['HP-18'], 'Homepage & First Impression');
  assert.equal(checkpointSectionById['NAV-01'], 'Navigation & Information Architecture');
  assert.equal(checkpointSectionById['FORM-13'], 'Forms & Data Entry');
  assert.equal(checkpointSectionById['FORM-28'], 'Forms & Data Entry');
  assert.equal(checkpointSectionById['PRIV-02'], 'Privacy & Consent');
  assert.equal(checkpointSectionById['A11Y-01'], 'Accessibility');
  assert.equal(checkpointSectionById['UNKNOWN-01'], undefined);
});

test('scores only applicable statuses and reports assessed and applicable counts', () => {
  const result = deriveSectionScores([
    { id: 'FORM-13', status: 'pass' },
    { id: 'FORM-15', status: 'partial' },
    { id: 'FORM-18', status: 'issue' },
    { id: 'FORM-28', status: 'not_verified' },
    { id: 'FORM-29', status: 'not_applicable' },
  ]);

  assert.deepEqual(result, [{
    name: 'Forms & Data Entry', score: 50, assessedCount: 5, applicableCount: 3,
  }]);
});

test('does not emit irrelevant zero-score sections for a scoped audit', () => {
  const result = deriveSectionScores([{ id: 'HP-18', status: 'issue' }]);

  assert.deepEqual(result, [{
    name: 'Homepage & First Impression', score: 0, assessedCount: 1, applicableCount: 1,
  }]);
  assert.equal(result.some((section) => section.name === 'Accessibility'), false);
  assert.equal(result.some((section) => section.name === 'Forms & Data Entry'), false);
});

test('uses actual pilot checkpoint sections and excludes unverified pilot checks', async () => {
  const audit = await pilot('jordan-gov-onyourservice');
  const result = deriveSectionScores(audit.assessments);

  assert.deepEqual(result.map(({ name, assessedCount, applicableCount }) => ({ name, assessedCount, applicableCount })), [
    { name: 'Navigation & Information Architecture', assessedCount: 1, applicableCount: 1 },
    { name: 'Forms & Data Entry', assessedCount: 7, applicableCount: 5 },
    { name: 'Privacy & Consent', assessedCount: 1, applicableCount: 1 },
    { name: 'Content & Microcopy', assessedCount: 1, applicableCount: 1 },
    { name: 'Task Completion & Conversion', assessedCount: 1, applicableCount: 1 },
    { name: 'Interface & Visual Design', assessedCount: 1, applicableCount: 1 },
    { name: 'Accessibility', assessedCount: 2, applicableCount: 0 },
    { name: 'Mobile & Responsive', assessedCount: 1, applicableCount: 0 },
  ]);
  assert.equal(result.some((section) => section.name === 'navigation'), false);
  assert.equal(result.some((section) => section.name === 'accessibility' && section.score === 0), false);
});
