"""Generate finding-specific, annotated evidence crops and update pilot metadata."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_METADATA = {
    "capturedAt": "2026-07-14",
    "method": "Chrome headless public desktop capture",
}

# Each supported finding maps to its own source-space crop and crop-relative focus
# rectangle. Focus rectangles are deliberately tight around the UI evidence, never a
# generic proportional box.
FINDING_SOURCES = {
    "jordan-gov-onyourservice": {
        "source": "evidence/raw/jordan/onyourservice.png",
        "findings": {
            "UXM-001": {"crop": (600, 800, 1380, 1420), "focus": (15, 20, 765, 600)},
            "UXM-002": {"crop": (620, 1155, 1360, 1345), "focus": (20, 35, 720, 140)},
            "UXM-003": {"crop": (50, 115, 1390, 850), "focus": (0, 0, 1340, 370)},
            "UXM-004": {"crop": (600, 680, 1380, 850), "focus": (20, 35, 760, 130)},
            "UXM-005": {"crop": (620, 860, 1360, 1160), "focus": (10, 35, 730, 290)},
        },
    },
    "tawasal-bekhedmetcom": {
        "source": "evidence/raw/tawasal/sendotp.png",
        "findings": {
            "UXM-001": {"crop": (700, 550, 1400, 850), "focus": (10, 80, 690, 230)},
            "UXM-002": {"crop": (180, 600, 1400, 850), "focus": (0, 40, 1200, 230)},
            "UXM-004": {"crop": (0, 100, 1440, 510), "focus": (0, 0, 1440, 380)},
            "UXM-005": {
                "source": "evidence/raw/tawasal/404.png",
                "crop": (500, 250, 940, 630),
                "focus": (80, 180, 380, 350),
            },
            "UXM-003": {
                "excluded": "The available capture is Arabic and does not substantiate the English-language copy observation; no matching English screenshot was captured.",
            },
            "UXM-006": {
                "source": "evidence/raw/tawasal/dashboard.png",
                "excluded": "The raw dashboard capture displays a 404 page and does not substantiate the satisfaction-metric observation.",
            },
        },
    },
}


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def as_box(values: tuple[int, int, int, int]) -> dict[str, int]:
    return dict(zip(("left", "top", "right", "bottom"), values, strict=True))


def validate_box(box: tuple[int, int, int, int], width: int, height: int, label: str) -> None:
    left, top, right, bottom = box
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(f"{label} {box} exceeds {width}x{height}")


def annotate(source: Path, destination: Path, crop_box: tuple[int, int, int, int], focus_box: tuple[int, int, int, int]) -> None:
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    validate_box(crop_box, *image.size, "crop")
    crop = image.crop(crop_box)
    validate_box(focus_box, *crop.size, "focus")
    draw = ImageDraw.Draw(crop)
    draw.rounded_rectangle(focus_box, radius=12, outline=(184, 20, 30), width=8)
    marker_x, marker_y = focus_box[0] + 22, focus_box[1] + 22
    draw.ellipse((marker_x - 22, marker_y - 22, marker_x + 22, marker_y + 22), fill=(184, 20, 30))
    draw.text((marker_x, marker_y - 1), "1", fill="white", font=font(24), anchor="mm")
    destination.parent.mkdir(parents=True, exist_ok=True)
    crop.save(destination, format="PNG", optimize=True)


def source_dimensions(source_path: Path) -> dict[str, int]:
    with Image.open(source_path) as source_image:
        return {"width": source_image.width, "height": source_image.height}


def update_audit(audit_path: Path) -> None:
    pilot = audit_path.parent.name
    configuration = FINDING_SOURCES[pilot]
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    for finding in audit["findings"]:
        override = configuration["findings"].get(finding["id"], {})
        source_relative = override.get("source", configuration["source"])
        source_path = ROOT / source_relative
        evidence = finding["evidence"]
        excluded_reason = override.get("excluded")
        evidence["sourceImage"] = source_relative
        evidence["captureMetadata"] = {
            **CAPTURE_METADATA,
            "captureType": "full-page screenshot",
            "imageDimensions": source_dimensions(source_path),
            "sourceSupportsFinding": excluded_reason is None,
        }
        annotated_relative = f"evidence/annotated/{pilot}/{finding['id']}.png"
        annotated_path = ROOT / annotated_relative

        if excluded_reason:
            finding["excludedFromPublication"] = True
            finding["exclusionReason"] = excluded_reason
            evidence["evidencePending"] = True
            evidence["evidencePendingReason"] = excluded_reason
            evidence.pop("annotatedImage", None)
            evidence.pop("annotation", None)
            annotated_path.unlink(missing_ok=True)
            continue

        crop_box = override["crop"]
        focus_box = override["focus"]
        finding.pop("excludedFromPublication", None)
        finding.pop("exclusionReason", None)
        evidence.pop("evidencePending", None)
        evidence.pop("evidencePendingReason", None)
        evidence["annotatedImage"] = annotated_relative
        evidence["annotation"] = {
            "type": "cropped_callout",
            "cropBox": as_box(crop_box),
            "focusBox": as_box(focus_box),
            "marker": "1",
            "color": "#B13D2A",
        }
        annotate(source_path, annotated_path, crop_box, focus_box)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for audit_path in sorted((ROOT / "pilots").glob("*/audit.json")):
        update_audit(audit_path)


if __name__ == "__main__":
    main()
