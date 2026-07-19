from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


class EvidenceCompletionConflict(ValueError):
    """The operator's completion decision no longer matches persisted evidence."""


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
            connection.execute("""
                CREATE TABLE IF NOT EXISTS audit_requests (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, company TEXT NOT NULL,
                    website TEXT NOT NULL, service TEXT NOT NULL, scope_note TEXT NOT NULL,
                    preferred_contact TEXT NOT NULL, locale TEXT NOT NULL DEFAULT 'en',
                    fingerprint TEXT NOT NULL UNIQUE, status TEXT NOT NULL DEFAULT 'received',
                    client_id TEXT REFERENCES clients(id) ON DELETE RESTRICT,
                    project_id TEXT REFERENCES projects(id) ON DELETE RESTRICT,
                    audit_id TEXT REFERENCES audits(id) ON DELETE RESTRICT,
                    created_at TEXT NOT NULL, converted_at TEXT
                )
            """)
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(audits)").fetchall()}
            if "project_id" not in columns:
                connection.execute("ALTER TABLE audits ADD COLUMN project_id TEXT REFERENCES projects(id) ON DELETE SET NULL")
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def _request_value(data: dict, field: str, label: str, limit: int = 1000) -> str:
        value = data.get(field, "")
        if not isinstance(value, str) or not (value := value.strip()):
            raise ValueError(f"{label} is required")
        if len(value) > limit:
            raise ValueError(f"{label} is too long")
        return value

    def _validated_audit_request(self, data: dict) -> dict:
        if not isinstance(data, dict):
            raise ValueError("Request must be a JSON object")
        name = self._request_value(data, "name", "Name", 160)
        email = self._request_value(data, "email", "Email", 254).lower()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Email must be valid")
        company = self._request_value(data, "company", "Company or organization", 200)
        website = self._request_value(data, "website", "Website URL", 2048)
        parsed = urlparse(website)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Website URL must start with http:// or https://")
        service = self._request_value(data, "service", "Audit need or service", 200)
        scope_note = self._request_value(data, "scopeNote", "Scope note", 4000)
        preferred_contact = self._request_value(data, "preferredContact", "Preferred contact", 100)
        locale = str(data.get("locale") or "en").strip().lower()
        fingerprint = hashlib.sha256(f"{email}|{website.casefold()}|{service.casefold()}".encode("utf-8")).hexdigest()
        return {"name": name, "email": email, "company": company, "website": website, "service": service,
                "scopeNote": scope_note, "preferredContact": preferred_contact, "locale": locale if locale in {"en", "ar"} else "en", "fingerprint": fingerprint}

    @staticmethod
    def _request_record(row) -> dict:
        return {"id": row["id"], "name": row["name"], "email": row["email"], "company": row["company"], "website": row["website"], "service": row["service"], "scopeNote": row["scope_note"], "preferredContact": row["preferred_contact"], "locale": row["locale"], "status": row["status"], "clientId": row["client_id"], "projectId": row["project_id"], "auditId": row["audit_id"], "createdAt": row["created_at"], "convertedAt": row["converted_at"]}

    def create_audit_request(self, data: dict) -> tuple[dict | None, bool]:
        # Honeypot responses are deliberately indistinguishable from duplicate confirmations.
        if isinstance(data, dict) and str(data.get("contactWebsite") or "").strip():
            return None, True
        request = self._validated_audit_request(data)
        now, request_id = datetime.now(timezone.utc).isoformat(), f"request_{uuid.uuid4().hex[:16]}"
        connection = self._connect()
        try:
            try:
                connection.execute("INSERT INTO audit_requests (id,name,email,company,website,service,scope_note,preferred_contact,locale,fingerprint,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (request_id, request["name"], request["email"], request["company"], request["website"], request["service"], request["scopeNote"], request["preferredContact"], request["locale"], request["fingerprint"], "received", now))
                connection.commit()
                row = connection.execute("SELECT * FROM audit_requests WHERE id = ?", (request_id,)).fetchone()
                return self._request_record(row), False
            except sqlite3.IntegrityError:
                row = connection.execute("SELECT * FROM audit_requests WHERE fingerprint = ?", (request["fingerprint"],)).fetchone()
                return self._request_record(row), True
        finally:
            connection.close()

    def list_request_audits(self) -> list[dict]:
        connection = self._connect()
        try:
            rows = connection.execute("SELECT * FROM audit_requests ORDER BY created_at DESC").fetchall()
        finally:
            connection.close()
        return [self._request_record(row) for row in rows]

    def convert_audit_request(self, request_id: str) -> dict:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            claimed = connection.execute("UPDATE audit_requests SET status = 'converting' WHERE id = ? AND status = 'received'", (request_id,))
            if claimed.rowcount != 1:
                request = connection.execute("SELECT status FROM audit_requests WHERE id = ?", (request_id,)).fetchone()
                connection.rollback()
                if request is None:
                    raise LookupError("Audit request not found")
                raise ValueError("Audit request has already been converted")
            request = connection.execute("SELECT * FROM audit_requests WHERE id = ?", (request_id,)).fetchone()
            now = datetime.now(timezone.utc).isoformat()
            client_id, project_id, audit_id = f"client_{uuid.uuid4().hex[:12]}", f"project_{uuid.uuid4().hex[:12]}", f"audit_{uuid.uuid4().hex[:16]}"
            contact_notes = f"Requested service: {request['service']}\nPreferred contact: {request['preferred_contact']}\nScope note: {request['scope_note']}"
            connection.execute("INSERT INTO clients (id,name,contact_name,email,phone,notes,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (client_id, request["company"], request["name"], request["email"], "", contact_notes, "active", now, now))
            project_name = f"{request['company']} — {request['service']}"
            connection.execute("INSERT INTO projects (id,client_id,name,base_url,product_type,owner,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (project_id, client_id, project_name, request["website"], "", "", "draft", now, now))
            audit = {"id": audit_id, "client": request["company"], "website": project_name, "url": request["website"], "locale": request["locale"], "source": f"request:{request_id}", "projectId": project_id, "service": request["service"], "scope": {"requestNote": request["scope_note"], "status": "awaiting_operator_scope"}, "findings": [], "assessments": {}, "status": "draft"}
            connection.execute("INSERT INTO audits (id,client,url,locale,source,body,updated_at,project_id) VALUES (?,?,?,?,?,?,?,?)", (audit_id, audit["client"], audit["url"], audit["locale"], audit["source"], json.dumps(audit, ensure_ascii=False), now, project_id))
            converted_count = connection.execute("UPDATE audit_requests SET status = ?, client_id = ?, project_id = ?, audit_id = ?, converted_at = ? WHERE id = ? AND status = 'converting'", ("converted", client_id, project_id, audit_id, now, request_id)).rowcount
            if converted_count != 1:
                raise RuntimeError("Audit request conversion could not be finalized")
            connection.commit()
            converted = connection.execute("SELECT * FROM audit_requests WHERE id = ?", (request_id,)).fetchone()
            return {"request": self._request_record(converted), "client": self.get_client(client_id), "project": self.get_project(project_id), "audit": audit}
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
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

    def save_audit_preserving_findings(self, audit: dict, source: str = "workspace") -> None:
        """Atomically save workspace fields without allowing a stale payload to overwrite findings."""
        updated_at = datetime.now(timezone.utc).isoformat()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT body FROM audits WHERE id = ?", (audit["id"],)).fetchone()
            if row is not None:
                audit = {**audit, "findings": json.loads(row["body"]).get("findings", [])}
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
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
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

    def get_project(self, project_id: str) -> dict | None:
        return next((project for project in self.list_projects() if project["id"] == project_id), None)

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

    @staticmethod
    def _normalize_capture_timestamp(value: str) -> str:
        if not isinstance(value, str) or not (value := value.strip()):
            raise ValueError("Evidence capture timestamp is required")
        if len(value) > 80:
            raise ValueError("Evidence capture timestamp is too long")
        try:
            captured_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("Evidence capture timestamp must be an ISO timestamp") from error
        if captured_at.tzinfo is None:
            raise ValueError("Evidence capture timestamp must include a timezone")
        return captured_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def attach_evidence(self, audit_id: str, finding_id: str, kind: str, body: bytes, mime_type: str, original_filename: str, captured_at: str = "") -> dict:
        if kind not in {"source", "annotated"}:
            raise ValueError("Evidence kind must be source or annotated")
        if Path(original_filename).name != original_filename or ".." in original_filename:
            raise ValueError("Unsafe filename")
        normalized_captured_at = self._normalize_capture_timestamp(captured_at) if captured_at else ""
        # Preserve the preflight lookup for a prompt not-found response, but never
        # mutate its snapshot: completion may race between this read and the write.
        if self.get_audit(audit_id) is None:
            raise LookupError("Audit not found")
        extension = ".png" if mime_type == "image/png" else ".jpg"
        filename = f"{uuid.uuid4().hex}{extension}"
        evidence_path = self.evidence_dir / filename
        evidence = {
            "filename": filename,
            "path": f"evidence/{filename}",
            "mimeType": mime_type,
            "originalFilename": original_filename,
            "bytes": len(body),
            "uploadedAt": datetime.now(timezone.utc).isoformat(),
        }
        connection = self._connect()
        wrote_file = False
        try:
            # The transaction must include the re-read and replacement.  Otherwise
            # a stale completion snapshot can restore the previous asset afterward.
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT body FROM audits WHERE id = ?", (audit_id,)).fetchone()
            if row is None:
                raise LookupError("Audit not found")
            audit = json.loads(row["body"])
            finding = self._finding_by_id(audit, finding_id)
            evidence_path.write_bytes(body)
            wrote_file = True
            evidence_record = finding.setdefault("evidence", {})
            evidence_record[f"{kind}Image"] = evidence
            # A changed asset invalidates every prior completion decision.
            evidence_record["status"] = "draft"
            finding.pop("evidenceComplete", None)
            if normalized_captured_at:
                evidence_record["capturedAt"] = normalized_captured_at
                evidence["capturedAt"] = normalized_captured_at
            connection.execute(
                "UPDATE audits SET body = ?, updated_at = ? WHERE id = ?",
                (json.dumps(audit, ensure_ascii=False), datetime.now(timezone.utc).isoformat(), audit_id),
            )
            connection.commit()
            return evidence
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            if wrote_file:
                evidence_path.unlink(missing_ok=True)
            raise
        finally:
            connection.close()

    @staticmethod
    def _finding_by_id(audit: dict, finding_id: str) -> dict:
        finding = next((item for item in audit.get("findings", []) if item.get("id") == finding_id), None)
        if finding is None:
            raise LookupError("Finding not found")
        return finding

    def save_finding_draft(self, audit_id: str, data: dict) -> dict:
        """Persist an operator-authored draft without claiming its evidence is complete."""
        if not isinstance(data, dict):
            raise ValueError("Finding draft must be a JSON object")
        if data.get("candidateId"):
            raise ValueError("AI candidate payloads cannot become official findings automatically")
        required = ("id", "checkpoint", "url", "page", "journey", "severity", "effort", "title", "observed", "impact", "recommendation")
        missing = [field for field in required if not isinstance(data.get(field), str) or not data[field].strip()]
        if missing:
            raise ValueError(f"Finding metadata is required: {', '.join(missing)}")
        if data["severity"] not in {"critical", "high", "medium", "low"}:
            raise ValueError("Invalid finding severity")
        if data["effort"] not in {"low", "medium", "high"}:
            raise ValueError("Invalid finding effort")
        limits = {"id": 80, "checkpoint": 80, "url": 2048, "page": 200, "journey": 200,
                  "title": 240, "observed": 4000, "impact": 4000, "recommendation": 4000}
        for field, limit in limits.items():
            if len(data[field].strip()) > limit:
                raise ValueError(f"Finding {field} is too long")
        parsed_url = urlparse(data["url"].strip())
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Finding URL must start with http:// or https://")
        evidence = data.get("evidence") if isinstance(data.get("evidence"), dict) else {}
        capture = evidence.get("capture") if isinstance(evidence.get("capture"), dict) else {}
        if not isinstance(capture.get("device"), str) or not capture["device"].strip():
            raise ValueError("Evidence capture device is required")
        if capture["device"].strip() not in {"Desktop Chrome", "Mobile Safari", "Android Chrome", "Other"}:
            raise ValueError("Invalid evidence capture device")
        captured_at = self._normalize_capture_timestamp(evidence.get("capturedAt"))
        alt = evidence.get("alt")
        if not isinstance(alt, str) or not (alt := alt.strip()) or len(alt) > 500 or len(alt.split()) < 3:
            raise ValueError("Evidence alt text must be a descriptive 3-to-500-character phrase")
        finding = {key: value for key, value in data.items() if key not in {"candidateId", "evidenceComplete", "editingFindingId"}}
        # Attachments are created only by attach_evidence.  The editor can update
        # descriptive capture metadata, but it must never be able to attach a
        # filename/path supplied by the client (including one owned by another
        # finding) or carry a completion state forward.
        finding["evidence"] = {
            "alt": alt,
            "capturedAt": captured_at,
            "capture": {"device": capture["device"].strip()},
            "status": "draft",
        }
        connection = self._connect()
        try:
            # Claim the write transaction before inspecting the JSON document, so two
            # new drafts cannot both decide that the same ID is still available.
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT body FROM audits WHERE id = ?", (audit_id,)).fetchone()
            if row is None:
                raise LookupError("Audit not found")
            audit = json.loads(row["body"])
            existing = next((index for index, item in enumerate(audit.get("findings", [])) if item.get("id") == finding["id"]), None)
            if existing is None:
                if data.get("editingFindingId"):
                    raise ValueError("Finding no longer exists")
                audit.setdefault("findings", []).append(finding)
            else:
                if data.get("editingFindingId") != finding["id"]:
                    raise ValueError("A finding with this ID already exists")
                # Preserve uploaded image references when an operator edits prose or metadata.
                previous_evidence = audit["findings"][existing].get("evidence") or {}
                for image_key in ("sourceImage", "annotatedImage"):
                    if image_key in previous_evidence and image_key not in finding["evidence"]:
                        finding["evidence"][image_key] = previous_evidence[image_key]
                audit["findings"][existing] = finding
            connection.execute(
                "UPDATE audits SET body = ?, updated_at = ? WHERE id = ?",
                (json.dumps(audit, ensure_ascii=False), datetime.now(timezone.utc).isoformat(), audit_id),
            )
            connection.commit()
            return finding
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def mark_evidence_complete(self, audit_id: str, finding_id: str) -> dict:
        """Mark evidence complete only after persisted, operator-uploaded proof exists."""
        # Record the decision's source revision before waiting for the write lock.
        # If an upload replaced evidence while this request was in flight, that
        # completion decision is stale and the replacement's draft state wins.
        baseline_audit = self.get_audit(audit_id)
        if baseline_audit is None:
            raise LookupError("Audit not found")
        baseline_finding = self._finding_by_id(baseline_audit, finding_id)
        baseline_evidence = json.dumps(baseline_finding.get("evidence") or {}, ensure_ascii=False, sort_keys=True)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT body FROM audits WHERE id = ?", (audit_id,)).fetchone()
            if row is None:
                raise LookupError("Audit not found")
            audit = json.loads(row["body"])
            finding = self._finding_by_id(audit, finding_id)
            evidence = finding.get("evidence") or {}
            # Re-read after acquiring the lock.  A concurrent replacement changes
            # this revision, so it must remain draft rather than restoring a stale
            # completion state or asset metadata.
            if json.dumps(evidence, ensure_ascii=False, sort_keys=True) != baseline_evidence:
                raise EvidenceCompletionConflict("Evidence changed while completion was pending; review and confirm it again")
            capture = evidence.get("capture") if isinstance(evidence.get("capture"), dict) else {}
            if not evidence.get("capturedAt") or not capture.get("device"):
                raise ValueError("Truthful capture metadata is required before evidence can be complete")
            evidence["capturedAt"] = self._normalize_capture_timestamp(evidence["capturedAt"])
            for key, label in (("sourceImage", "source image"), ("annotatedImage", "annotated image")):
                image = evidence.get(key) if isinstance(evidence.get(key), dict) else {}
                filename = image.get("filename")
                if not filename or not (self.evidence_dir / filename).is_file():
                    raise ValueError(f"A persisted {label} is required before evidence can be complete")
            evidence["status"] = "complete"
            finding["evidence"] = evidence
            finding["evidenceComplete"] = True
            connection.execute(
                "UPDATE audits SET body = ?, updated_at = ? WHERE id = ?",
                (json.dumps(audit, ensure_ascii=False), datetime.now(timezone.utc).isoformat(), audit_id),
            )
            connection.commit()
            return finding
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

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
            if evidence.get("status") != "complete" or finding.get("evidenceComplete") is not True:
                block("evidence_not_explicitly_complete", "Evidence must be explicitly marked complete by an operator.")
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
