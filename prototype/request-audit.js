const form = document.querySelector('#request-audit-form');
const status = document.querySelector('#request-status');
const toggle = document.querySelector('#locale-toggle');
const translations = {
  en: { back: 'Back to website', kicker: 'Start with a clear scope', title: 'Request an audit', intro: 'Tell UX Mosaic where the experience needs attention. Scope and access are confirmed before any audit begins.', name: 'Name', email: 'Work email', company: 'Company or organization', website: 'Website URL', service: 'Audit need or service', scope: 'Scope note', contact: 'Preferred contact', choose: 'Choose one', uxAudit: 'UX audit', accessibility: 'Accessibility review', expert: 'Expert review', other: 'Other', emailOption: 'Email', phone: 'Phone', video: 'Video call', submit: 'Send request', privacy: 'A human operator reviews every request before an audit is created.', scopePlaceholder: 'What journey, product area, or concern should we review?', received: 'Thank you. Your request has been received. No audit has started; an operator will review the scope first.', error: 'We could not submit your request. Please review the form and try again.' },
  ar: { back: 'العودة إلى الموقع', kicker: 'ابدأ بنطاق واضح', title: 'اطلب تدقيقاً', intro: 'أخبر UX Mosaic أين تحتاج التجربة إلى اهتمام. يتم تأكيد النطاق والوصول قبل بدء أي تدقيق.', name: 'الاسم', email: 'البريد الإلكتروني للعمل', company: 'الشركة أو المؤسسة', website: 'رابط الموقع', service: 'احتياج أو خدمة التدقيق', scope: 'ملاحظة عن النطاق', contact: 'وسيلة التواصل المفضلة', choose: 'اختر واحداً', uxAudit: 'تدقيق تجربة المستخدم', accessibility: 'مراجعة إمكانية الوصول', expert: 'مراجعة خبير', other: 'أخرى', emailOption: 'البريد الإلكتروني', phone: 'الهاتف', video: 'مكالمة مرئية', submit: 'إرسال الطلب', privacy: 'يراجع مشغّل بشري كل طلب قبل إنشاء تدقيق.', scopePlaceholder: 'ما الرحلة أو جزء المنتج أو المشكلة التي تريد مراجعتها؟', received: 'شكراً لك. تم استلام طلبك. لم يبدأ أي تدقيق؛ سيراجع المشغّل النطاق أولاً.', error: 'تعذر إرسال طلبك. يرجى مراجعة النموذج والمحاولة مرة أخرى.' },
};
let locale = new URLSearchParams(location.search).get('locale') === 'ar' ? 'ar' : 'en';
function applyLocale() {
  const copy = translations[locale];
  document.documentElement.lang = locale;
  if (locale === 'ar') {
    document.documentElement.dir = 'rtl';
  } else {
    document.documentElement.dir = 'ltr';
  }
  document.querySelectorAll('[data-i18n]').forEach(node => { node.textContent = copy[node.dataset.i18n]; });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(node => { node.placeholder = copy[node.dataset.i18nPlaceholder]; });
  toggle.textContent = locale === 'ar' ? 'English' : 'العربية';
}
toggle.addEventListener('click', () => { locale = locale === 'en' ? 'ar' : 'en'; applyLocale(); });
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const payload = { ...Object.fromEntries(new FormData(form)), locale };
    const response = await fetch('/api/request-audits', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error);
    form.hidden = true;
    status.textContent = translations[locale].received;
  } catch (error) {
    status.textContent = error.message || translations[locale].error;
    button.disabled = false;
  }
});
applyLocale();
