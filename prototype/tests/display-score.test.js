import test from 'node:test';
import assert from 'node:assert/strict';
import { displayScore, scopeSummary } from '../src/display-score.js';

test('persisted audit score is authoritative over prototype-derived score', () => {
  assert.equal(displayScore({ assessmentSummary: { score: 57 } }, 33), 57);
});

test('prototype falls back to derived score when no persisted summary exists', () => {
  assert.equal(displayScore({}, 67), 67);
});

test('object audit scope renders the included public scope without object leakage', () => {
  assert.equal(scopeSummary({ scope: { included: ['Public form', 'Navigation'] } }), 'Public form · Navigation');
});
