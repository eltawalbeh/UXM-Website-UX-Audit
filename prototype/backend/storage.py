from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


class AuditRepository:
    def __init__(self, database_path: Path, backup_dir: Path, evidence_dir: Path | None = None):
        self.database_path = Path(database_path)
        self.backup_dir = Path(backup_dir)
        self.evidence_dir = Path(evidence_dir) if evidence_dir else self.database_path.parent / "evidence"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        connection = self._connect()
        try:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS audits (
                    id TEXT PRIMARY KEY,
                    client TEXT NOT NULL,
                    url TEXT NOT NULL,
                    locale TEXT NOT NULL,
                    source TEXT NOT NULL,
                    body TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            connection.commit()
        finally:
            connection.close()

    def upsert_audit(self, audit: dict, source: str = "workspace") -> None:
        updated_at = datetime.now(timezone.utc).isoformat()
        connection = self._connect()
        try:
            connection.execute("""
                INSERT INTO audits (id, client, url, locale, source, body, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  client=excluded.client, url=excluded.url, locale=excluded.locale,
                  source=excluded.source, body=excluded.body, updated_at=excluded.updated_at
            """, (audit["id"], audit["client"], audit["url"], audit.get("locale", "en"), source,
                  json.dumps(audit, ensure_ascii=False), updated_at))
            connection.commit()
        finally:
            connection.close()

    def get_audit(self, audit_id: str) -> dict | None:
        connection = self._connect()
        try:
            row = connection.execute("SELECT body FROM audits WHERE id = ?", (audit_id,)).fetchone()
        finally:
            connection.close()
        return json.loads(row["body"]) if row else None

    def list_audits(self) -> list[dict]:
        connection = self._connect()
        try:
            rows = connection.execute("SELECT id, client, url, locale, source, updated_at, body FROM audits ORDER BY updated_at DESC").fetchall()
        finally:
            connection.close()
        return [{"id": row["id"], "client": row["client"], "url": row["url"], "locale": row["locale"], "source": row["source"], "updatedAt": row["updated_at"], "findingCount": len(json.loads(row["body"]).get("findings", []))} for row in rows]

    def attach_evidence(self, audit_id: str, finding_id: str, kind: str, body: bytes, mime_type: str, original_filename: str, captured_at: str = "") -> dict:
        if kind not in {"source", "annotated"}:
            raise ValueError("Evidence kind must be source or annotated")
        if Path(original_filename).name != original_filename or ".." in original_filename:
            raise ValueError("Unsafe filename")
        audit = self.get_audit(audit_id)
        if audit is None:
            raise LookupError("Audit not found")
        finding = next((item for item in audit.get("findings", []) if item.get("id") == finding_id), None)
        if finding is None:
            raise LookupError("Finding not found")
        extension = ".png" if mime_type == "image/png" else ".jpg"
        filename = f"{uuid.uuid4().hex}{extension}"
        (self.evidence_dir / filename).write_bytes(body)
        evidence = {
            "filename": filename,
            "path": f"evidence/{filename}",
            "mimeType": mime_type,
            "originalFilename": original_filename,
            "bytes": len(body),
            "uploadedAt": datetime.now(timezone.utc).isoformat(),
        }
        evidence_record = finding.setdefault("evidence", {})
        evidence_record[f"{kind}Image"] = evidence
        if captured_at:
            evidence_record["capturedAt"] = captured_at
            evidence["capturedAt"] = captured_at
        self.upsert_audit(audit)
        return evidence

    def publication_readiness(self, audit_id: str, locale: str | None = None) -> dict:
        audit = self.get_audit(audit_id)
        if audit is None:
            raise LookupError("Audit not found")
        blockers = []
        arabic_required = (locale or audit.get("locale")) == "ar"
        for finding in audit.get("findings", []):
            finding_id = finding.get("id", "Unknown finding")
            # Excluded findings are retained in source audits for traceability but
            # are intentionally outside the publication set and cannot block it.
            if finding.get("excludedFromPublication"):
                continue
            evidence = finding.get("evidence") or {}
            def block(code, message):
                blockers.append({"findingId": finding_id, "code": code, "message": message})
            if evidence.get("status") == "pending":
                block("pending_evidence", "Evidence is still pending.")
            for kind, code in (("sourceImage", "missing_source_image"), ("annotatedImage", "missing_annotated_image")):
                image = evidence.get(kind) or {}
                filename = image.get("filename") if isinstance(image, dict) else None
                if not filename or not (self.evidence_dir / filename).is_file():
                    block(code, f"{kind.replace('Image', ' image')} is required.")
            for field, code in (("page", "missing_page"), ("journey", "missing_journey"), ("url", "missing_url")):
                if not finding.get(field):
                    block(code, f"Finding {field} is required.")
            if not evidence.get("capturedAt"):
                block("missing_capture_metadata", "Evidence capture timestamp is required.")
            if arabic_required:
                arabic = finding.get("arabic") or {}
                if not all(arabic.get(field) for field in ("title", "observed", "impact", "recommendation")):
                    block("missing_arabic_translation", "Arabic title, observation, impact, and recommendation are required.")
        return {"auditId": audit_id, "ready": not blockers, "blockers": blockers}

    def backup(self) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        destination = self.backup_dir / f"uxm-audit-{stamp}.db"
        source = self._connect()
        target = sqlite3.connect(destination)
        try:
            source.backup(target)
            target.commit()
        finally:
            target.close()
            source.close()
        return destination
