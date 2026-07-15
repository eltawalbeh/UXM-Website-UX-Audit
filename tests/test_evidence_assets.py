"""Regression checks for publishable pilot finding evidence assets."""

import json
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AUDITS = sorted(ROOT.glob("pilots/*/audit.json"))


def box_tuple(box: dict) -> tuple[int, int, int, int]:
    return tuple(box[key] for key in ("left", "top", "right", "bottom"))


def assert_valid_box(box: dict, width: int, height: int, context: str) -> None:
    assert set(box) == {"left", "top", "right", "bottom"}, f"{context}: invalid box keys"
    assert all(isinstance(value, int) for value in box.values()), f"{context}: box values must be integers"
    left, top, right, bottom = box_tuple(box)
    assert 0 <= left < right <= width, f"{context}: box exceeds image width {width}"
    assert 0 <= top < bottom <= height, f"{context}: box exceeds image height {height}"


def publishable_findings(audit: dict) -> list[dict]:
    return [finding for finding in audit["findings"] if not finding.get("excludedFromPublication", False)]


def evidence_path(evidence: dict, field: str) -> Path:
    image = evidence[field]
    return ROOT / (image["path"] if isinstance(image, dict) else image)


def test_publishable_findings_have_specific_bounded_crop_and_focus_mappings():
    assert AUDITS, "Expected at least one pilot audit"
    mappings_by_source = defaultdict(list)

    for audit_path in AUDITS:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        for finding in publishable_findings(audit):
            evidence = finding["evidence"]
            assert evidence["capturedAt"], finding["id"]
            for field in ("sourceImage", "annotatedImage"):
                image_path = evidence_path(evidence, field)
                assert image_path.is_file(), f"{audit_path}: {finding['id']} missing {image_path}"
                with Image.open(image_path) as image:
                    image.verify()

            annotation = evidence.get("annotation")
            assert annotation and annotation.get("type") == "cropped_callout", f"{finding['id']} missing crop mapping"
            crop, focus = annotation.get("cropBox"), annotation.get("focusBox")
            assert isinstance(crop, dict) and isinstance(focus, dict), f"{finding['id']} missing crop/focus boxes"
            source_path = evidence_path(evidence, "sourceImage")
            with Image.open(source_path) as source, Image.open(evidence_path(evidence, "annotatedImage")) as annotated:
                assert_valid_box(crop, source.width, source.height, f"{finding['id']} crop")
                crop_width = crop["right"] - crop["left"]
                crop_height = crop["bottom"] - crop["top"]
                assert_valid_box(focus, crop_width, crop_height, f"{finding['id']} focus")
                assert annotated.size == (crop_width, crop_height), f"{finding['id']} annotated asset does not match crop"
                assert annotated.width < source.width or annotated.height < source.height, f"{finding['id']} is not a focused crop"
            assert annotation.get("marker") == "1", f"{finding['id']} missing numbered marker"
            mappings_by_source[str(evidence_path(evidence, "sourceImage"))].append((finding["id"], box_tuple(crop), box_tuple(focus)))

    for source, mappings in mappings_by_source.items():
        crop_boxes = [crop for _, crop, _ in mappings]
        focus_boxes = [focus for _, _, focus in mappings]
        assert len(crop_boxes) == len(set(crop_boxes)), f"{source}: generic identical crop boxes are forbidden"
        assert len(focus_boxes) == len(set(focus_boxes)), f"{source}: generic identical focus boxes are forbidden"


def test_excluded_findings_have_honest_reasons_and_no_publishable_evidence_claim():
    excluded = []
    for audit_path in AUDITS:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        for finding in audit["findings"]:
            if finding.get("excludedFromPublication"):
                excluded.append(finding)
                evidence = finding["evidence"]
                assert evidence["captureMetadata"]["sourceSupportsFinding"] is False
                assert evidence.get("evidencePending") is True
                assert evidence.get("evidencePendingReason")
                assert finding.get("exclusionReason") == evidence["evidencePendingReason"]

    assert {finding["id"] for finding in excluded if finding["page"].startswith(("English SendOTP", "BekhedmetCom dashboard"))} == {"UXM-003", "UXM-006"}


def test_every_finding_has_readiness_capture_data_and_honest_support_status():
    for audit_path in AUDITS:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        for finding in audit["findings"]:
            evidence = finding["evidence"]
            if finding.get("excludedFromPublication"):
                assert evidence.get("evidencePending") is True
                assert evidence.get("evidencePendingReason")
                continue
            assert evidence.get("capturedAt") == "2026-07-14"
            for field in ("sourceImage", "annotatedImage"):
                image = evidence[field]
                assert isinstance(image, dict), f"{finding['id']} {field} is not readiness metadata"
                assert image.get("filename")
                assert evidence_path(evidence, field).is_file()
