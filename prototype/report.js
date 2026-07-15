import { renderReport } from './src/report-renderer.js';

const app = document.querySelector('#report-app');
const params = new URLSearchParams(location.search);
const auditId = params.get('audit');
let locale = params.get('lang') === 'ar' ? 'ar' : 'en';

function renderLanguageControls(audit) {
  const control = document.createElement('nav');
  control.className = 'language-controls no-print';
  control.innerHTML = `<a href="report.html?audit=${encodeURIComponent(audit.id)}&lang=en" lang="en">English</a><a href="report.html?audit=${encodeURIComponent(audit.id)}&lang=ar" lang="ar">العربية</a>`;
  app.prepend(control);
}

async function load() {
  if (!auditId) {
    app.innerHTML = '<section class="report-error"><h1>Report unavailable</h1><p>Select an audit with <code>?audit=your-audit-id</code>.</p></section>';
    return;
  }
  try {
    const response = await fetch(`/api/audits/${encodeURIComponent(auditId)}`);
    if (!response.ok) throw new Error(response.status === 404 ? 'Audit not found.' : 'Report data could not be loaded.');
    const audit = await response.json();
    if (!params.has('lang')) locale = audit.locale === 'ar' ? 'ar' : 'en';
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr';
    document.title = `${audit.client} — UXM Client Report`;
    app.innerHTML = renderReport(audit, locale);
    renderLanguageControls(audit);
    app.querySelector('[data-export-pdf]')?.addEventListener('click', async (event) => {
      const button = event.currentTarget;
      button.disabled = true;
      button.textContent = locale === 'ar' ? 'جارٍ تجهيز التقرير…' : 'Preparing PDF…';
      try {
        const exportResponse = await fetch(`/api/audits/${encodeURIComponent(audit.id)}/export-pdf?locale=${encodeURIComponent(locale)}`, { method: 'POST' });
        const body = await exportResponse.json();
        if (!exportResponse.ok) throw new Error(body.error || 'PDF export failed.');
        const download = document.createElement('a');
        download.href = body.downloadUrl;
        download.download = body.filename;
        document.body.append(download);
        download.click();
        download.remove();
        button.textContent = locale === 'ar' ? 'تم تنزيل التقرير' : 'PDF downloaded';
      } catch (error) {
        button.textContent = locale === 'ar' ? `تعذر التصدير: ${error.message}` : `Export failed: ${error.message}`;
        button.classList.add('export-error');
      } finally {
        button.disabled = false;
      }
    });
  } catch (error) {
    app.innerHTML = `<section class="report-error"><h1>Report unavailable</h1><p>${error.message}</p></section>`;
  }
}
load();
