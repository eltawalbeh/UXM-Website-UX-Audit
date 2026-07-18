const SUPPORTED_LOCALES = new Set(['en', 'ar']);
const LTR_ISOLATE = '\u2066';
const POP_DIRECTIONAL_ISOLATE = '\u2069';

export function normalizeLocale(locale) {
  const normalized = String(locale || '').trim().toLowerCase().split(/[-_]/)[0];
  return SUPPORTED_LOCALES.has(normalized) ? normalized : 'en';
}

export function directionFor(locale) {
  return normalizeLocale(locale) === 'ar' ? 'rtl' : 'ltr';
}

export function isolateTechnicalValue(value) {
  return `${LTR_ISOLATE}${String(value ?? '')}${POP_DIRECTIONAL_ISOLATE}`;
}

export function translate(messages, key, locale = 'en', variables = {}) {
  const normalized = normalizeLocale(locale);
  const template = messages?.[normalized]?.[key] ?? messages?.en?.[key] ?? key;
  return String(template).replace(/\{([a-zA-Z0-9_]+)\}/g, (match, name) => (
    Object.prototype.hasOwnProperty.call(variables, name) ? String(variables[name]) : match
  ));
}

export function createTranslator(messages, locale = 'en') {
  const normalized = normalizeLocale(locale);
  return (key, variables) => translate(messages, key, normalized, variables);
}

export function applyDocumentLocale(locale, root = globalThis.document?.documentElement) {
  const normalized = normalizeLocale(locale);
  if (root) {
    root.lang = normalized;
    root.dir = directionFor(normalized);
  }
  return normalized;
}

export const supportedLocales = Object.freeze(['en', 'ar']);
