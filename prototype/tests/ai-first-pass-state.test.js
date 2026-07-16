import test from 'node:test';
import assert from 'node:assert/strict';
import { removeReviewedCandidate } from '../src/ai-first-pass-state.js';

test('accepting a manually reviewed candidate removes it from the First Pass queue', () => {
  const state = {
    candidates: [
      { id: 'AIFP-001', title: 'First' },
      { id: 'AIFP-002', title: 'Second' },
      { id: 'AIFP-003', title: 'Third' },
    ],
    message: 'First pass ready.',
  };

  const next = removeReviewedCandidate(state, 'AIFP-002');

  assert.deepEqual(next.candidates.map(candidate => candidate.id), ['AIFP-001', 'AIFP-003']);
  assert.match(next.message, /reviewed candidate accepted/i);
  assert.deepEqual(state.candidates.map(candidate => candidate.id), ['AIFP-001', 'AIFP-002', 'AIFP-003']);
});

test('accepting a non-First-Pass draft leaves the candidate queue unchanged', () => {
  const state = { candidates: [{ id: 'AIFP-001' }], message: '' };
  assert.equal(removeReviewedCandidate(state, '').candidates.length, 1);
});
