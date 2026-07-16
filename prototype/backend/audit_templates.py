import json
from copy import deepcopy
from pathlib import Path

from .ai_first_pass import load_checkpoint_library


TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "data" / "audit-templates.v1.json"
REQUIRED_EVIDENCE = {"page_url", "journey", "source_screenshot", "annotated_screenshot", "capture_timestamp", "viewport"}
REQUIRED_REPORT_SECTIONS = {"cover", "snapshot", "scope", "methodology", "scorecard", "roadmap", "findings", "conclusion"}


def load_audit_templates(path: Path = TEMPLATE_PATH) -> list[dict]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    templates = payload.get("templates", [])
    official_ids = {item["id"] for item in load_checkpoint_library()}
    seen_ids = set()
    for template in templates:
        template_id = str(template.get("id", "")).strip()
        checkpoint_ids = template.get("checkpointIds", [])
        if not template_id or template_id in seen_ids:
            raise ValueError("Audit template IDs must be non-empty and unique")
        if not template.get("name") or not template.get("productType") or not template.get("journeys"):
            raise ValueError(f"Audit template {template_id} is incomplete")
        if len(checkpoint_ids) != len(set(checkpoint_ids)) or not set(checkpoint_ids).issubset(official_ids):
            raise ValueError(f"Audit template {template_id} contains duplicate or unknown checkpoint IDs")
        if not REQUIRED_EVIDENCE.issubset(set(template.get("evidenceRequirements", []))):
            raise ValueError(f"Audit template {template_id} is missing evidence requirements")
        if not REQUIRED_REPORT_SECTIONS.issubset(set(template.get("reportSections", []))):
            raise ValueError(f"Audit template {template_id} is missing report sections")
        seen_ids.add(template_id)
    return deepcopy(templates)


def get_audit_template(template_id: str, path: Path = TEMPLATE_PATH) -> dict | None:
    return next((item for item in load_audit_templates(path) if item["id"] == template_id), None)
