"""Create finding-specific annotated evidence for the public Amman pilot."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "UXM-001": ("raw/ammancity/eservices-catalog-20260715.png", (520, 375, 1140, 525), (220, 40, 520, 110)),
    "UXM-002": ("raw/ammancity/eservices-catalog-20260715.png", (0, 430, 465, 660), (0, 15, 330, 205)),
    "UXM-003": ("raw/ammancity/eservices-search-malaab-20260715.png", (215, 620, 540, 1050), (20, 20, 305, 395)),
    "UXM-004": ("raw/ammancity/service-card-7-viewer-20260715.png", (300, 95, 755, 480), (25, 40, 440, 370)),
    "UXM-005": ("raw/ammancity/user-guide-10-viewer-20260715.png", (300, 55, 755, 480), (20, 15, 445, 415)),
}


def font(size):
    for candidate in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    destination_dir = ROOT / "evidence" / "annotated" / "ammancity-eservices"
    destination_dir.mkdir(parents=True, exist_ok=True)
    for finding_id, (source_relative, crop_box, focus_box) in SOURCES.items():
        with Image.open(ROOT / "evidence" / source_relative) as opened:
            crop = opened.convert("RGB").crop(crop_box)
        draw = ImageDraw.Draw(crop)
        draw.rounded_rectangle(focus_box, radius=10, outline="#B8141E", width=7)
        cx, cy = focus_box[0] + 24, focus_box[1] + 24
        draw.ellipse((cx - 21, cy - 21, cx + 21, cy + 21), fill="#B8141E")
        draw.text((cx, cy), "1", fill="white", anchor="mm", font=font(22))
        crop.save(destination_dir / f"{finding_id}.png", optimize=True)


if __name__ == "__main__":
    main()
