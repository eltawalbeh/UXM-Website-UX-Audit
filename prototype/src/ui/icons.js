const paths = Object.freeze({
  home: '<path d="m3 11 9-8 9 8v10h-6v-6H9v6H3Z"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  close: '<path d="M6 6l12 12M18 6 6 18"/>',
  warning: '<path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v4m0 3h.01"/>',
  error: '<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6m0-6-6 6"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  arrowForward: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
  arrowBack: '<path d="M19 12H5m5-5-5 5 5 5"/>',
  chevron: '<path d="m9 18 6-6-6-6"/>',
  externalLink: '<path d="M14 4h6v6m0-6-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  evidence: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 15 3-3 3 3 2-2 3 3M8 8h.01"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  unlock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 7-2.6"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M5 21h14"/>',
  upload: '<path d="M12 16V4m-5 5 5-5 5 5M5 21h14"/>',
  edit: '<path d="m4 20 4.5-1 10-10a2.1 2.1 0 0 0-3-3l-10 10L4 20Z"/>',
  delete: '<path d="M4 7h16M9 7V4h6v3m3 0-1 14H7L6 7m4 4v6m4-6v6"/>',
  add: '<path d="M12 5v14M5 12h14"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M20 12a8 8 0 0 0-.2-1.7l2-1.5-2-3.5-2.4 1a8 8 0 0 0-3-1.7L14 2h-4l-.4 2.6a8 8 0 0 0-3 1.7l-2.4-1-2 3.5 2 1.5A8 8 0 0 0 4 12c0 .6.1 1.2.2 1.7l-2 1.5 2 3.5 2.4-1a8 8 0 0 0 3 1.7L10 22h4l.4-2.6a8 8 0 0 0 3-1.7l2.4 1 2-3.5-2-1.5c.1-.5.2-1.1.2-1.7Z"/>',
  filter: '<path d="M3 5h18l-7 8v6l-4 2v-8Z"/>',
  eye: '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/>',
});

const directionalIcons = new Set(['arrowForward', 'arrowBack', 'chevron', 'externalLink']);

const escapeAttribute = (value) => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[character]);

export function icon(name, { label = '', size = 20 } = {}) {
  const path = paths[name];
  if (!path) throw new Error(`Unknown UXM icon: ${name}`);
  const numericSize = Number.isFinite(Number(size)) ? Math.max(12, Math.min(64, Number(size))) : 20;
  const accessibility = label
    ? `role="img" aria-label="${escapeAttribute(label)}"`
    : 'aria-hidden="true"';
  const directional = directionalIcons.has(name) ? ' data-icon-directional="true"' : '';
  return `<svg${directional} ${accessibility} width="${numericSize}" height="${numericSize}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" focusable="false">${path}</svg>`;
}

export const iconNames = Object.freeze(Object.keys(paths));
