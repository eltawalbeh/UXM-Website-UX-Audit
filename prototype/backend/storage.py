from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


class AuditRepository:
    PROJECT_STATUSES = {"draft", "in_review", "evidence_complete", "ready_for_client", "delivered"}

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
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self):
        connection = self._connect()
        try:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact_name TEXT NOT NULL DEFAULT '',
                    email TEXT NOT NULL DEFAULT '',
                    phone TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
                    name TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    product_type TEXT NOT NULL DEFAULT '',
                    owner TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS audits (
                    id TEXT PRIMARY KEY,
                    client TEXT NOT NULL,
                    url TEXT NOT NULL,
                    locale TEXT NOT NULL,
                    source TEXT NOT NULL,
                    body TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL
                )
            """)
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(audits)").fetchall()}
            if "project_id" not in columns:
                connection.execute("ALTER TABLE audits ADD COLUMN project_id TEXT REFERENCES projects(id) ON DELETE SET NULL")
            connection.commit()
        finally:
            connection.close()

    def upsert_audit(self, audit: dict, source: str = "workspace") -> None:
        updated_at = datetime.now(timezone.utc).isoformat()
        connection = self._connect()
        try:
            connection.execute("""
                INSERT INTO audits (id, client, url, locale, source, body, updated_at, project_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  client=excluded.client, url=excluded.url, locale=excluded.locale,
                  source=excluded.source, body=excluded.body, updated_at=excluded.updated_at,
                  project_id=excluded.project_id
            """, (audit["id"], audit["client"], audit["url"], audit.get("locale", "en"), source,
                  json.dumps(audit, ensure_ascii=False), updated_at, audit.get("projectId")))
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
        summaries = []
        for row in rows:
            body = json.loads(row["body"])
            summaries.append({"id": row["id"], "client": row["client"], "url": row["url"], "locale": row["locale"],
                              "source": row["source"], "updatedAt": row["updated_at"],
                              "findingCount": len(body.get("findings", [])), "projectId": body.get("projectId"),
                              "status": body.get("status", "draft")})
        return summaries

    def create_client(self, data: dict) -> dict:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("Client name is required")
        now = datetime.now(timezone.utc).isoformat()
        client_id = str(data.get("id") or f"client_{uuid.uuid4().hex[:12]}")
        values = (client_id, name, str(data.get("contactName", "")).strip(), str(data.get("email", "")).strip(),
                  str(data.get("phone", "")).strip(), str(data.get("notes", "")).strip(), "active", now, now)
        connection = self._connect()
        try:
            connection.execute("INSERT INTO clients (id,name,contact_name,email,phone,notes,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)", values)
            connection.commit()
        finally:
            connection.close()
        return self.get_client(client_id)

    def get_client(self, client_id: str) -> dict | None:
        connection = self._connect()
        try:
            row = connection.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        finally:
            connection.close()
        if not row:
            return None
        return {"id": row["id"], "name": row["name"], "contactName": row["contact_name"], "email": row["email"],
                "phone": row["phone"], "notes": row["notes"], "status": row["status"],
                "createdAt": row["created_at"], "updatedAt": row["updated_at"]}

    def list_clients(self) -> list[dict]:
        connection = self._connect()
        try:
            rows = connection.execute("""
                SELECT c.*, COUNT(DISTINCT p.id) AS project_count, COUNT(DISTINCT a.id) AS audit_count
                FROM clients c LEFT JOIN projects p ON p.client_id = c.id
                LEFT JOIN audits a ON a.project_id = p.id
                GROUP BY c.id ORDER BY c.updated_at DESC
            """).fetchall()
        finally:
            connection.close()
        return [{"id": row["id"], "name": row["name"], "contactName": row["contact_name"], "email": row["email"],
                 "phone": row["phone"], "notes": row["notes"], "status": row["status"],
                 "createdAt": row["created_at"], "updatedAt": row["updated_at"],
                 "projectCount": row["project_count"], "auditCount": row["audit_count"]} for row in rows]

    def create_project(self, data: dict) -> dict:
        client_id = str(data.get("clientId", "")).strip()
        if not self.get_client(client_id):
            raise LookupError("Client not found")
        name = str(data.get("name", "")).strip()
        base_url = str(data.get("baseUrl", "")).strip()
        if not name or not base_url:
            raise ValueError("Project name and base URL are required")
        status = str(data.get("status") or "draft")
        if status not in self.PROJECT_STATUSES:
            raise ValueError("Invalid project status")
        now = datetime.now(timezone.utc).isoformat()
        project_id = str(data.get("id") or f"project_{uuid.uuid4().hex[:12]}")
        connection = self._connect()
        try:
            connection.execute("INSERT INTO projects (id,client_id,name,base_url,product_type,owner,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                               (project_id, client_id, name, base_url, str(data.get("productType", "")), str(data.get("owner", "")), status, now, now))
            connection.commit()
        finally:
            connection.close()
        return self.get_project(project_id)

    def get_project(self, project_id: str) -> dict | None:
        projects = self.list_projects()
        return next((project for project in projects if project["id"] == project_id), None)

    def list_projects(self, client_id: str | None = None) -> list[dict]:
        connection = self._connect()
        try:
            where, params = ("WHERE p.client_id = ?", (client_id,)) if client_id else ("", ())
            rows = connection.execute(f"""
                SELECT p.*, c.name AS client_name, COUNT(a.id) AS audit_count
                FROM projects p JOIN clients c ON c.id = p.client_id
                LEFT JOIN audits a ON a.project_id = p.id
                {where} GROUP BY p.id ORDER BY p.updated_at DESC
            """, params).fetchall()
        finally:
            connection.close()
        return [{"id": row["id"], "clientId": row["client_id"], "clientName": row["client_name"], "name": row["name"],
                 "baseUrl": row["base_url"], "productType": row["product_type"], "owner": row["owner"],
                 "status": row["status"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
                 "auditCount": row["audit_count"]} for row in rows]

    def update_project_status(self, project_id: str, status: str) -> dict:
        if status not in self.PROJECT_STATUSES:
            raise ValueError("Invalid project status")
        connection = self._connect()
        try:
            cursor = connection.execute("UPDATE projects SET status = ?, updated_at = ? WHERE id = ?", (status, datetime.now(timezone.utc).isoformat(), project_id))
            if cursor.rowcount != 1:
                raise LookupError("Project not found")
            connection.commit()
        finally:
            connection.close()
        return self.get_project(project_id)

    def link_audit_to_project(self, audit_id: str, project_id: str) -> dict:
        if not self.get_project(project_id):
            raise LookupError("Project not found")
        audit = self.get_audit(audit_id)
        if audit is None:
            raise LookupError("Audit not found")
        audit["projectId"] = project_id
        self.upsert_audit(audit)
        return audit

    def backfill_operations_from_audits(self) -> dict:
        counts = {"clientsCreated": 0, "projectsCreated": 0, "auditsLinked": 0}
        clients_by_name = {client["name"].casefold(): client for client in self.list_clients()}
        projects_by_id = {project["id"]: project for project in self.list_projects()}
        summaries = self.list_audits()
        for project_id, project in projects_by_id.items():
            if project.get("productType"):
                continue
            linked = next((summary for summary in summaries if summary.get("projectId") == project_id), None)
            if linked and (".gov." in linked["url"].lower() or "ammancity.gov" in linked["url"].lower()):
                connection = self._connect()
                try:
                    connection.execute("UPDATE projects SET product_type = ?, updated_at = ? WHERE id = ?", ("government_civic", datetime.now(timezone.utc).isoformat(), project_id))
                    connection.commit()
                finally:
                    connection.close()
                project["productType"] = "government_civic"
        for summary in summaries:
            if summary.get("projectId"):
                continue
            audit = self.get_audit(summary["id"])
            client_name = str(audit.get("client") or "Unassigned client").strip()
            client = clients_by_name.get(client_name.casefold())
            if client is None:
                client_id = f"client_{uuid.uuid5(uuid.NAMESPACE_URL, f'uxm-client:{client_name.casefold()}').hex[:12]}"
                client = self.create_client({"id": client_id, "name": client_name})
                clients_by_name[client_name.casefold()] = client
                counts["clientsCreated"] += 1
            audit_id = str(audit["id"])
            project_id = f"project_{uuid.uuid5(uuid.NAMESPACE_URL, 'uxm-audit:' + audit_id).hex[:12]}"
            scope = audit.get("scope") if isinstance(audit.get("scope"), dict) else {}
            inferred_product_type = audit.get("productType") or scope.get("productType", "")
            if not inferred_product_type and (".gov." in audit["url"].lower() or "ammancity.gov" in audit["url"].lower()):
                inferred_product_type = "government_civic"
            if project_id not in projects_by_id:
                project = self.create_project({
                    "id": project_id, "clientId": client["id"], "name": audit.get("website") or audit.get("title") or "Website audit",
                    "baseUrl": audit["url"], "productType": inferred_product_type,
                    "owner": audit.get("auditor", ""), "status": audit.get("status") if audit.get("status") in self.PROJECT_STATUSES else "draft",
                })
                projects_by_id[project_id] = project
                counts["projectsCreated"] += 1
            elif inferred_product_type and not projects_by_id[project_id].get("productType"):
                connection = self._connect()
                try:
                    connection.execute("UPDATE projects SET product_type = ?, updated_at = ? WHERE id = ?", (inferred_product_type, datetime.now(timezone.utc).isoformat(), project_id))
                    connection.commit()
                finally:
                    connection.close()
                projects_by_id[project_id]["productType"] = inferred_product_type
            self.link_audit_to_project(audit["id"], project_id)
            counts["auditsLinked"] += 1
        return counts

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
