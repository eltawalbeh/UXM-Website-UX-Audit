import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const app = fs.readFileSync(new URL('../app.js', import.meta.url), 'utf8');
const css = fs.readFileSync(new URL('../workspace-polish.css', import.meta.url), 'utf8');

test('Main OS is the default Admin destination and uses the approved labelled navigation groups', () => {
  assert.match(app, /get\('view'\) \|\| 'mainOS'/);
  assert.match(app, /function mainOperatingSystem\(/);
  assert.match(app, /Global Administration/);
  assert.match(app, /Selected Audit Workflow/);
  assert.match(app, /Main OS/);
  assert.match(app, /Client Details/);
  assert.match(app, /Templates Overview/);
  assert.match(app, /Score Priority/);
});

test('Main OS renders truthful dispatch and registry data with a deferred Start Here entry', () => {
  assert.match(app, /PRIORITY DISPATCH QUEUE/);
  assert.match(app, /ACTIVE AUDIT \/ DRAFT REGISTRY/);
  assert.match(app, /buildAdminDashboard\(audits, dashboardReadiness\)/);
  assert.match(app, /dashboardDataAvailable/);
  assert.match(app, /Dashboard data unavailable/);
  assert.match(app, /data-action="retry-dashboard"/);
  assert.match(app, /Persisted audit registry loaded\./);
  assert.match(app, /Start Here \(New Audit\)/);
  assert.match(app, /data-action="start-here" disabled aria-disabled="true"/);
  assert.match(app, /URL-first setup begins in Slice 4\.11/);
  assert.match(app, /لوحة الإدارة/);
  assert.match(app, /قائمة العمل ذات الأولوية/);
  assert.match(app, /سجل التدقيقات والمسودات النشطة/);
  assert.match(app, /data-open-audit/);
});

test('Main OS CSS follows the approved 260px labelled sidebar and responsive system layout', () => {
  assert.match(css, /\.admin-system-sidebar\s*\{[^}]*width:\s*260px/s);
  assert.match(css, /\.admin-system-topbar\s*\{[^}]*min-height:\s*72px/s);
  assert.match(css, /\.main-os-registry/s);
  assert.match(css, /\.main-os-header \.uxm-button\[disabled\] \{ opacity: 1;/);
  assert.match(css, /@media\s*\(max-width:\s*720px\)[\s\S]*\.admin-system-sidebar/s);
});
