const arabic = {
  'How it works': 'كيف نعمل', 'Services': 'الخدمات', 'Methodology': 'المنهجية', 'Operator login': 'دخول المشغّل',
  'Request an audit': 'طلب تدقيق', 'Evidence-led UX Audit System': 'نظام تدقيق تجربة المستخدم القائم على الأدلة',
  'Find what blocks the experience. Prove what needs to change.': 'اكتشف ما يعيق التجربة. وأثبت ما يحتاج إلى تغيير.',
  'UX Mosaic turns observed experience issues into human-validated findings, clear priorities, and delivery-ready reports.': 'تحوّل UX Mosaic مشكلات التجربة المرصودة إلى ملاحظات يراجعها الخبراء وأولويات واضحة وتقارير جاهزة للتسليم.',
  'Evidence controls delivery.': 'الدليل يضبط ما يصل إلى التسليم.', 'Every published recommendation remains traceable to a reviewed observation, its scope, and its supporting evidence.': 'كل توصية منشورة ترتبط بملاحظة مراجعة ونطاقها والدليل الداعم لها.',
  'AI surfaces review candidates inside the agreed public scope.': 'يستخرج الذكاء الاصطناعي مرشحات للمراجعة ضمن النطاق العام المتفق عليه.', 'Human review separates observations from assumptions.': 'تفصل المراجعة البشرية بين الملاحظات والافتراضات.', 'Approved findings link to evidence, context, and recommendation.': 'ترتبط الملاحظات المعتمدة بالدليل والسياق والتوصية.', 'Readiness gates protect what reaches the report and PDF.': 'تحمي بوابات الجاهزية ما يصل إلى التقرير وملف PDF.',
  'Evidence-led review of critical public journeys, content, interfaces, and recovery states.': 'مراجعة قائمة على الأدلة للرحلات العامة الأساسية والمحتوى والواجهات وحالات الاستعادة.', 'Focused diagnosis for civic, customer-service, and digital service entry points.': 'تشخيص مركز لنقاط بدء الخدمات الحكومية وخدمة العملاء والخدمات الرقمية.', 'Clear priorities, annotated evidence, and bilingual decision documents.': 'أولويات واضحة وأدلة مشروحة ووثائق قرار ثنائية اللغة.',
  'AI candidate': 'مرشح الذكاء الاصطناعي', ' is not an approved finding.': ' ليس ملاحظة معتمدة.', 'Not verified': 'غير متحقق منه', ' is not a failed checkpoint.': ' ليس نقطة فشل.', 'Evidence complete': 'اكتمال الدليل', ' is required before delivery.': ' مطلوب قبل التسليم.',
  'Client examples and outcomes are shared only when publication has been approved.': 'تُشارك أمثلة العملاء والنتائج فقط عند اعتماد النشر.', 'Start with the experience you need to understand.': 'ابدأ بالتجربة التي تحتاج إلى فهمها.',
  'From public experience to a decision-ready delivery.': 'من التجربة العامة إلى تسليم جاهز لاتخاذ القرار.',
  'Discover with AI': 'اكتشف بالذكاء الاصطناعي', 'Validate with experts': 'تحقق مع الخبراء', 'Prove with evidence': 'أثبت بالدليل', 'Deliver with confidence': 'سلّم بثقة',
  'Audit work that makes the next decision clearer.': 'تدقيق يجعل القرار التالي أوضح.', 'Website UX Audit': 'تدقيق تجربة الموقع', 'Service Experience Review': 'مراجعة تجربة الخدمة', 'Delivery-ready Reporting': 'تقارير جاهزة للتسليم',
  'Measured. Human-approved. Honest about what is not verified.': 'مقاس. معتمد بشرياً. وصادق بشأن ما لم يتم التحقق منه.',
  'Selected work': 'أعمال مختارة', 'Selected work available on request.': 'أعمال مختارة متاحة عند الطلب.',
  'Make the next UX decision evidence-led.': 'اجعل قرار تجربة المستخدم التالي قائماً على الأدلة.'
};
// Public Arabic variant: ?locale=ar
const params = new URLSearchParams(location.search);
if (params.get('locale') === 'ar') {
  document.documentElement.dir = 'rtl';
  document.documentElement.lang = 'ar';
  document.querySelectorAll('[data-i18n="request"]').forEach((node) => { node.textContent = 'طلب تدقيق'; });
  document.querySelectorAll('[data-i18n="how"]').forEach((node) => { node.textContent = 'كيف نعمل'; });
  document.querySelectorAll('h1,h2,h3,p,strong,span,a,b').forEach((node) => {
    if (node.children.length === 0 && arabic[node.textContent.trim()]) node.textContent = arabic[node.textContent.trim()];
  });
  document.querySelectorAll('.public-method__rules p').forEach((node, index) => { node.textContent = ['مرشح الذكاء الاصطناعي ليس ملاحظة معتمدة.', 'غير متحقق منه ليس نقطة فشل.', 'اكتمال الدليل مطلوب قبل التسليم.'][index]; });
  document.title = 'UX Mosaic — نظام تدقيق تجربة المستخدم القائم على الأدلة';
  document.querySelector('meta[name="description"]')?.setAttribute('content', 'تدقيق تجربة المستخدم القائم على الأدلة من UX Mosaic.');
  document.querySelector('.route-principle')?.setAttribute('aria-label', 'معيار التدقيق القائم على الأدلة');
  document.querySelector('.route-header__actions')?.setAttribute('aria-label', 'التنقل الرئيسي');
  document.querySelector('.route-brand')?.setAttribute('aria-label', 'الصفحة الرئيسية لـ UX Mosaic');
}
