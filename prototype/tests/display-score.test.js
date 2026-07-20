import test from 'node:test';
import assert from 'node:assert/strict';
import { displayScore, scopeIncludedItems, scopeSummary } from '../src/display-score.js';

test('persisted audit score is authoritative over prototype-derived score', () => {
  assert.equal(displayScore({ assessmentSummary: { score: 57 } }, 33), 57);
});

test('prototype falls back to derived score when no persisted summary exists', () => {
  assert.equal(displayScore({}, 67), 67);
});

test('template baseline remains unscored until at least one checkpoint is assessed', () => {
  assert.equal(displayScore({ templateId: 'government-civic-v1' }, 0, 0), null);
});

test('object audit scope renders the included public scope without object leakage', () => {
  assert.equal(scopeSummary({ scope: { included: ['Public form', 'Navigation'] } }), 'Public form · Navigation');
});

test('object-shaped persisted scope items retain their page labels and URLs', () => {
  const included = scopeIncludedItems({
    scope: {
      included: [
        { title: 'Pricing', url: 'https://example.test/pricing' },
        { label: 'Contact journey', href: '/contact' },
      ],
    },
  });

  assert.deepEqual(included, [
    { label: 'Pricing', reference: 'https://example.test/pricing' },
    { label: 'Contact journey', reference: '/contact' },
  ]);
});
