import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('development tokens are generated from the 178 live Figma variables', async () => {
  const [raw, generated, aliases] = await Promise.all([
    read('../src/ui/figma-variables.json'),
    read('../src/ui/figma-tokens.css'),
    read('../src/ui/tokens.css'),
  ]);
  const variables = JSON.parse(raw);

  assert.equal(Object.keys(variables).length, 178);
  for (const [name, value] of Object.entries({
    'color/navy-900': '#1b1c2f',
    'color/blue-600': '#4175b9',
    'brand/primary': '#007aff',
    'border/default': '#dcdce0',
    'border/subtle': '#e8e8eb',
    'background/secondary': '#f7f7f7',
    'text/primary': '#1a1a1f',
    'brand/success': '#a5f3b2',
    'type-scale/display': '40',
    'spacing/md': '24',
    'radius/6': '6',
  })) assert.equal(variables[name], value, `${name} drifted from live Figma`);

  assert.match(generated, /--figma-brand-primary:\s*#007aff/i);
  assert.match(generated, /--figma-spacing-md:\s*24px/i);
  assert.match(generated, /--figma-radius-6:\s*6px/i);
  assert.match(aliases, /@import\s+url\(['"]\.\/figma-tokens\.css['"]\)/i);
  assert.match(aliases, /--uxm-action-blue:\s*var\(--figma-brand-primary\)/i);
  assert.match(aliases, /--uxm-border-neutral:\s*var\(--figma-border-default\)/i);
  assert.doesNotMatch(aliases, /--uxm-border-neutral:[^;]*mint/i);
});

test('typography applies the approved Thmanyah Sans override instead of Figma placeholder families', async () => {
  const [base, tokens, workspace, report] = await Promise.all([
    read('../src/ui/base.css'),
    read('../src/ui/tokens.css'),
    read('../styles.css'),
    read('../report-print.css'),
  ]);

  assert.match(tokens, /--uxm-font-ui:\s*"Thmanyah Sans",\s*Arial/i);
  assert.match(tokens, /--uxm-font-display:\s*"Thmanyah Sans",\s*Arial/i);
  assert.doesNotMatch(tokens, /--uxm-font-(?:ui|display):[^;]*(?:Cairo|Inter|Manrope)/i);
  assert.match(tokens, /--uxm-type-display:\s*40px/i);
  assert.match(tokens, /--uxm-type-heading-1:\s*28px/i);
  assert.match(tokens, /--uxm-type-caption:\s*13px/i);
  assert.match(base, /font-family:\s*"Thmanyah Sans"/i);
  assert.doesNotMatch(base, /font-family:\s*"(?:Cairo|Inter|Manrope)"/i);
  assert.match(workspace, /@import\s+url\(['"]\.\/src\/ui\/tokens\.css['"]\)/i);
  assert.doesNotMatch(`${workspace}\n${report}`, /(?:font-family|font):[^;}\n]*(?:Cairo|Inter|Manrope|Georgia|IBM Plex|Tahoma)/i);
  assert.match(report, /@import\s+url\(['"]\.\/src\/ui\/base\.css['"]\)/i);
  assert.doesNotMatch(`${base}\n${workspace}\n${report}`, /fonts\.googleapis\.com/i);
});

test('browser-native components mirror the live Figma component variants and states', async () => {
  const [css, specimen] = await Promise.all([
    read('../src/ui/components.css'),
    read('../design-system.html'),
  ]);

  assert.match(css, /\.uxm-button[^}]*min-width:\s*160px[^}]*min-height:\s*41px/is);
  assert.match(css, /\.uxm-button--large[^}]*min-width:\s*200px[^}]*min-height:\s*49px/is);
  assert.match(css, /\.uxm-button[^}]*border-radius:\s*var\(--figma-radius-6\)/is);
  for (const variant of ['primary', 'secondary', 'ghost', 'success']) assert.match(css, new RegExp(`\\.uxm-button--${variant}\\b`));

  for (const status of ['critical', 'high', 'medium', 'low', 'info', 'success', 'warning', 'neutral']) {
    assert.match(css, new RegExp(`\\[data-status="${status}"\\]`));
  }
  for (const state of ['focused', 'error', 'disabled']) assert.match(css, new RegExp(`\\.uxm-field\\[data-state="${state}"\\]`));
  assert.match(css, /\.uxm-tab\[aria-selected="true"\][^}]*var\(--figma-brand-primary\)/is);
  assert.match(css, /\.uxm-table\s*\{[^}]*color:\s*var\(--figma-text-secondary\)/is);
  assert.match(css, /\.uxm-table tr\[aria-selected="true"\]/i);
  for (const variant of ['outline', 'elevated', 'dark']) assert.match(css, new RegExp(`\\.uxm-card--${variant}\\b`));
  assert.match(css, /\.uxm-sticky-actions[^}]*position:\s*sticky/is);
  assert.match(specimen, /data-status="critical"/);
  assert.match(specimen, /data-state="error"/);
  assert.match(specimen, /dir="rtl"/);
});

test('shared icon and i18n helpers stay consistent, safe, directional, and bidi-aware', async () => {
  const [{ icon }, i18n] = await Promise.all([
    import('../src/ui/icons.js'),
    import('../src/i18n.js'),
  ]);

  const check = icon('check');
  assert.match(check, /^<svg\b/);
  assert.match(check, /aria-hidden="true"/);
  assert.match(check, /width="20" height="20"/);
  assert.match(check, /stroke-width="2"/);
  assert.doesNotMatch(check, /[✅❌⚠️]/u);
  assert.match(icon('arrowForward'), /data-icon-directional="true"/);
  assert.doesNotMatch(icon('search'), /data-icon-directional/);
  assert.throws(() => icon('not-a-real-icon'), /Unknown UXM icon/);
  assert.equal(i18n.normalizeLocale('ar-JO'), 'ar');
  assert.equal(i18n.directionFor('ar'), 'rtl');
  assert.equal(i18n.isolateTechnicalValue('UXM-102'), '\u2066UXM-102\u2069');

  const messages = { en: { fallback: 'Verified' }, ar: { welcome: 'مرحباً، {name}' } };
  assert.equal(i18n.translate(messages, 'welcome', 'ar', { name: 'عبدالله' }), 'مرحباً، عبدالله');
  assert.equal(i18n.translate(messages, 'fallback', 'ar'), 'Verified');
});

test('local Figma font and brand assets are packaged for offline operation', async () => {
  const assets = [
    '../assets/brand/uxmosaic-horizontal-dark.png',
    '../assets/fonts/thmanyah-sans/thmanyahsans-Regular.woff2',
  ];
  for (const path of assets) assert.ok((await readFile(new URL(path, import.meta.url))).length > 1000, `${path} missing`);

  const workspace = await read('../styles.css');
  assert.match(workspace, /--ink:\s*var\(--uxm-ink\)/i);
  assert.match(workspace, /--line:\s*var\(--uxm-border-neutral\)/i);
});