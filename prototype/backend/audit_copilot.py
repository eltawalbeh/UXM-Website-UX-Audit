"""Provider-neutral, evidence-aware draft generation for UXM findings.

The service never creates or saves findings. It only returns a proposed draft that
must be reviewed and explicitly applied by the workspace user.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REQUIRED_DRAFT_FIELDS = (
    "observation", "impact", "recommendation", "suggestedSeverity", "confidence",
    "missingEvidenceChecks", "duplicateRisk",
)


def build_context(audit: dict, request: dict) -> dict:
    evidence = request.get("evidence") if isinstance(request.get("evidence"), dict) else {}
    findings = audit.get("findings") if isinstance(audit.get("findings"), list) else []
    return {
        "auditId": audit.get("id"),
        "client": audit.get("client"),
        "url": audit.get("url"),
        "scope": audit.get("scope", ""),
        "checkpoint": request.get("criterionId", ""),
        "category": request.get("category", ""),
        "journey": request.get("journey", ""),
        "page": request.get("page", ""),
        "notes": request.get("notes", ""),
        "evidence": evidence,
        "existingFindings": [{
            "id": item.get("id"), "title": item.get("title", ""), "category": item.get("category", ""),
            "journey": item.get("journey", ""), "page": item.get("page", ""), "observed": item.get("observed", ""),
        } for item in findings],
    }


def _unavailable(message: str) -> dict:
    return {"status": "unavailable", "message": f"AI connection unavailable. {message}"}


def _extract_draft(response: dict) -> dict | None:
    if isinstance(response.get("draft"), dict):
        return response["draft"]
    content = response.get("output_text")
    if not content:
        choices = response.get("choices") or []
        if choices and isinstance(choices[0], dict):
            content = (choices[0].get("message") or {}).get("content")
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    if not isinstance(content, str):
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def _valid_draft(draft: object) -> bool:
    return isinstance(draft, dict) and all(field in draft for field in REQUIRED_DRAFT_FIELDS) and draft.get("suggestedSeverity") in {"critical", "high", "medium", "low"} and draft.get("confidence") in {"high", "medium", "low"} and isinstance(draft.get("missingEvidenceChecks"), list) and isinstance(draft.get("duplicateRisk"), dict)


def configured_drafter(context: dict) -> dict:
    endpoint = os.getenv("UXM_AI_ENDPOINT", "").strip()
    api_key = os.getenv("UXM_AI_API_KEY", "").strip()
    model = os.getenv("UXM_AI_MODEL", "").strip()
    if not endpoint:
        return _unavailable("Configure UXM_AI_ENDPOINT (and UXM_AI_API_KEY if your provider requires it), then try again.")

    instructions = (
        "You are a UX audit copilot. Use only the supplied audit context. Do not claim to have viewed "
        "evidence that is not described in the context. Return JSON only with observation, impact, recommendation, "
        "suggestedSeverity (critical|high|medium|low), confidence (high|medium|low), missingEvidenceChecks (array), "
        "and duplicateRisk ({level: none|possible|likely, matches: [finding IDs]}). Mark gaps as missing evidence; "
        "never invent facts. This is a draft for human review, not a final audit finding."
    )
    payload = {"model": model or "configured-by-provider", "messages": [
        {"role": "system", "content": instructions},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
    ], "response_format": {"type": "json_object"}, "max_tokens": 900}
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        request = Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urlopen(request, timeout=90) as response:
            body = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
        return _unavailable(f"The configured provider could not be reached ({error}). Your notes are still here.")

    draft = _extract_draft(body if isinstance(body, dict) else {})
    if not _valid_draft(draft):
        return _unavailable("The configured provider did not return the required evidence-aware draft. Your notes are still here.")
    return {"status": "ready", "draft": draft}
