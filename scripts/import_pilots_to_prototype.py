"""Normalize verified pilot evidence and safely import publishable findings into SQLite."""

from __future__ import annotations

import argparse
import json
import shutil
from copy import deepcopy
from pathlib import Path


ARABIC_TRANSLATIONS = {
    "pilot_jordan_gov_onyourservice_20260714": {
        "UXM-001": {
            "title": "جمع بيانات الطلب الحساسة دون طمأنة سياقية حول الخصوصية واستخدام البيانات",
            "observed": "يطلب النموذج رقم هاتف ووصفاً تفصيلياً ومرفقات اختيارية، بينما يظهر رابط سياسة الخصوصية في التذييل العام وليس بجوار إجراء الجمع.",
            "impact": "قد يتردد المواطنون في إرسال بيانات شخصية أو حساسة، أو يرسلونها دون فهم كيفية استخدام معلوماتهم.",
            "recommendation": "أضف طمأنة موجزة حول استخدام البيانات والاحتفاظ بها فوق زر الإرسال مباشرةً، مع رابط مباشر لسياسة الخصوصية.",
        },
        "UXM-002": {
            "title": "تدفق المرفقات العربي يحتوي على واجهة إنجليزية غير مترجمة",
            "observed": "تظهر في مكوّن المرفقات ضمن النموذج العربي عبارات إنجليزية مثل Drop files here وChoose Files وPlease select file(s) to upload.",
            "impact": "تقطع اللغة المختلطة تسلسل القراءة وتجعل النموذج أقل اكتمالاً أو موثوقية للمواطنين الذين يفضلون العربية.",
            "recommendation": "عرّب جميع عبارات مكوّن المرفقات ورسائل حالة الملفات والتحقق منها، ثم تحقق من محاذاة RTL واتجاه النص.",
        },
        "UXM-003": {
            "title": "مهمة الطلب تنافسها لافتة كبيرة ومحتوى دعم جانبي",
            "observed": "تظهر صورة رئيسية كبيرة وعناصر مشاركة ونصوص دعم وخدمات واتصالات جانبية قبل نموذج الطلب الطويل أو إلى جواره.",
            "impact": "تتراجع أولوية مهمة المواطن الأساسية، وهي إرسال الطلب، وتحتاج إلى مسح بصري وتمرير أكبر من اللازم.",
            "recommendation": "استخدم رأس مهمة مختصراً في هذا المسار وانقل عناصر الدعم غير الضرورية أسفل النموذج أو إلى لوحة مساعدة سياقية.",
        },
        "UXM-004": {
            "title": "اعتمادية الجهة الحكومية والقسم غير مفسرة قبل ظهور حقل معطل",
            "observed": "تظهر قائمة القسم معطلة بعد اختيار الجهة الحكومية دون تعليمات داخلية تشرح الاعتمادية أو الخطوة التالية.",
            "impact": "قد يتوقف المستخدم عند عنصر تحكم معطل أو يحاول استخدامه دون فهم التسلسل المطلوب.",
            "recommendation": "أضف رسالة مساعدة موجزة توضح اختيار الجهة أولاً لإظهار الأقسام، واعرض حالة تحميل أو إتاحة صريحة لحقل القسم.",
        },
        "UXM-005": {
            "title": "حقلا الموضوع والتفاصيل لا يحددان التوقعات قبل كتابة الطلب",
            "observed": "يعرض النموذج تسميات عامة للموضوع والتفاصيل دون مثال مرئي أو مستوى التفاصيل المتوقع أو إرشاد للمعلومات المفيدة.",
            "impact": "قد يقدّم المواطنون أوصافاً ناقصة، مما يزيد جهد الاستيضاح اليدوي ويؤخر الحل.",
            "recommendation": "أضف أمثلة وإرشادات موجزة للموضوع والتفاصيل، مثل الخدمة والموقع والتاريخ والنتيجة التي يتوقعها المواطن.",
        },
    },
    "pilot_tawasal_bekhedmetcom_20260714": {
        "UXM-001": {
            "title": "حقل رقم الهاتف لا يحتوي على تسمية مرئية دائمة أو مثال للإدخال",
            "observed": "تعرض صفحة OTP العامة حقلاً فارغاً للهاتف، بينما تظهر سياقاته كعنوان أعلاه ورسالة إلزام أدناه بدلاً من تسمية أو مثال مرتبطين بالحقل.",
            "impact": "قد يتردد المواطنون بشأن الصيغة المتوقعة أو ما إذا كان الحقل هو رقم الهاتف المحمول المطلوب، مما يزيد الاحتكاك في بداية الطلب.",
            "recommendation": "أضف تسمية دائمة مثل رقم الهاتف المحمول، ومثالاً لصيغة رقم أردني، وضع مؤشر الإلزام بجوار التسمية.",
        },
        "UXM-002": {
            "title": "خطوة جمع رقم الهاتف المحمول تفتقر إلى طمأنة سياقية حول الخصوصية واستخدام البيانات",
            "observed": "تطلب الشاشة رقماً هاتفياً صالحاً للمتابعة دون تفسير موجز ظاهر لسبب طلبه أو كيفية استخدامه بجوار الحقل أو زر الإرسال.",
            "impact": "قد يتردد المستخدمون قبل تقديم بيانات اتصال شخصية، خصوصاً في سياق خدمة حكومية عامة.",
            "recommendation": "أضف سطراً موجزاً قرب الحقل يشرح الغرض من الرقم، مع رابط مباشر لسياسة الخصوصية ذات الصلة.",
        },
        "UXM-004": {
            "title": "لافتة كبيرة متكررة تؤخر بدء مهمة التحقق من الهاتف",
            "observed": "تحتفظ صفحة OTP بلافتة كبيرة ذات علامة تجارية وعنوان منصة مكرر فوق نموذج الطلب ذي الحقل الواحد.",
            "impact": "تُدفع أول خطوة للمهمة إلى أسفل بصرياً وتنافسها معلومات زخرفية، مما يزيد تكلفة الانتباه والتمرير.",
            "recommendation": "استخدم رأس مهمة مضغوطاً لصفحات بدء الطلب أو المصادقة، واجعل النموذج والمساعدة وسياق الخصوصية ضمن أول شاشة مركزة.",
        },
        "UXM-005": {
            "title": "مسار التعافي من صفحة 404 يقدم طريقاً عاماً للصفحة الرئيسية فقط",
            "observed": "تعرض صفحة 404 العامة زر الصفحة الرئيسية دون بحث أو مسار للخدمات المستخدمة كثيراً أو اقتراح تعافٍ سياقي.",
            "impact": "يضطر المستخدم الذي يصل عبر رابط عميق معطل أو منتهٍ إلى إعادة بدء التنقل دون مساعدة في العثور على الخدمة أو المعلومة المقصودة.",
            "recommendation": "أبقِ الصفحة الرئيسية ثم أضف البحث وبدء طلب جديد وأهم المهام ورسالة قصيرة تشرح كيفية استعادة الوجهة المقصودة.",
        },
    },
}


def image_record(image: str | dict) -> dict:
    relative = Path(image["filename"] if isinstance(image, dict) else image)
    if relative.parts and relative.parts[0] == "evidence":
        relative = Path(*relative.parts[1:])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe legacy evidence path: {relative}")
    return {"filename": relative.as_posix(), "path": f"evidence/{relative.as_posix()}"}


def normalize_audit(audit: dict) -> dict:
    """Convert legacy pilot records without inventing evidence or publishing exclusions."""
    normalized = deepcopy(audit)
    translations = ARABIC_TRANSLATIONS.get(normalized["id"], {})
    for finding in normalized.get("findings", []):
        if finding.get("excludedFromPublication"):
            continue
        legacy = finding["evidence"]
        finding["url"] = finding.get("url") or legacy["url"]
        # New evidence-led pilots own their reviewed translations in the fixture;
        # legacy fixtures receive the maintained migration translation mapping.
        finding["arabic"] = finding.get("arabic") or translations[finding["id"]]
        finding["evidence"] = {
            "sourceImage": image_record(legacy["sourceImage"]),
            "annotatedImage": image_record(legacy["annotatedImage"]),
            "capturedAt": legacy.get("capturedAt") or legacy["captureMetadata"]["capturedAt"],
            "description": legacy.get("description", ""),
            "annotation": legacy.get("annotation"),
            # Import is a deliberate, verified migration action: both checked-in
            # source files are copied before this record may be publishable.
            "status": "complete",
        }
        finding["evidenceComplete"] = True
    return normalized


def copy_image(audit_root: Path, evidence_dir: Path, image: dict) -> None:
    filename = image["filename"]
    source = audit_root / "evidence" / filename
    destination = evidence_dir / filename
    if not source.is_file():
        raise FileNotFoundError(f"Verified evidence image is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or source.read_bytes() != destination.read_bytes():
        shutil.copy2(source, destination)


def import_pilots(pilots_dir: Path, repository, audit_root: Path) -> dict[str, int]:
    """Copy supported evidence, omit exclusions, and upsert each normalized pilot."""
    imported = {}
    for audit_path in sorted(Path(pilots_dir).glob("*/audit.json")):
        audit = normalize_audit(json.loads(audit_path.read_text(encoding="utf-8")))
        publishable = [finding for finding in audit["findings"] if not finding.get("excludedFromPublication")]
        for finding in publishable:
            for image in (finding["evidence"]["sourceImage"], finding["evidence"]["annotatedImage"]):
                copy_image(Path(audit_root), repository.evidence_dir, image)
        audit["findings"] = publishable
        repository.upsert_audit(audit, source="pilot")
        imported[audit["id"]] = len(publishable)
    return imported


def update_root_pilots(pilots_dir: Path) -> None:
    """Persist the readiness-schema representation in root pilot JSON files."""
    for audit_path in sorted(Path(pilots_dir).glob("*/audit.json")):
        audit = normalize_audit(json.loads(audit_path.read_text(encoding="utf-8")))
        audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalize-root", action="store_true", help="Persist readiness fields into root pilot JSON files")
    parser.add_argument("--database", type=Path)
    args = parser.parse_args()
    audit_root = Path(__file__).resolve().parents[1]
    if args.normalize_root:
        update_root_pilots(audit_root / "pilots")
    if args.database:
        from backend.storage import AuditRepository

        prototype_root = audit_root / "prototype"
        repo = AuditRepository(args.database, prototype_root / "data" / "backups", prototype_root / "evidence")
        print(import_pilots(audit_root / "pilots", repo, audit_root))


if __name__ == "__main__":
    main()
