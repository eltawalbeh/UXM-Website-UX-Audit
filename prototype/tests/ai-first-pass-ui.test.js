import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const app = fs.readFileSync(new URL('../app.js', import.meta.url), 'utf8');

test('First Pass requires a product type and commercial scope bundle before run', () => {
  assert.match(app, /Product type/);
  assert.match(app, /Government \/ civic service/);
  assert.match(app, /E-commerce/);
  assert.match(app, /SaaS \/ digital product/);
  assert.match(app, /Corporate \/ marketing website/);
  assert.match(app, /Content \/ publisher/);
  assert.match(app, /Custom/);
  assert.match(app, /Full website/);
  assert.match(app, /Selected pages/);
  assert.match(app, /General health check/);
  assert.match(app, /Contact experience/);
  assert.match(app, /Selected pages \(one per line\)/);
  assert.match(app, /Detect product type/);
  assert.match(app, /detect-product-type/);
  assert.match(app, /name="bundle" \$\{aiFirstPassState\.productType \? '' : 'disabled'\}/);
});

test('First Pass UI makes the contract and human-only candidate boundary explicit', () => {
  assert.match(app, /Scope contract/);
  assert.match(app, /Applicable checkpoints/);
  assert.match(app, /Excluded \/ not verifiable/);
  assert.match(app, /Candidate findings only/);
  assert.match(app, /What was visited/);
  assert.match(app, /checkpointId/);
  assert.match(app, /reviewState/);
  assert.match(app, /Promote for review/);
  assert.match(app, /Reject/);
  assert.match(app, /candidateId:candidate\.id/);
  assert.match(app, /criterionId:candidate\.checkpointId/);
  assert.match(app, /removeReviewedCandidate\(aiFirstPassState,aiDraftState\.candidateId\)/);
  assert.match(app, /candidates remaining/);
  assert.doesNotMatch(app, /fetch\([^\n]*ai-first-pass[^\n]*method:\s*'POST'[^\n]*\/api\/audits['"]/);
});
