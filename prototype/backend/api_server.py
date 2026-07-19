from __future__ import annotations

import argparse
import ipaddress
import json
import mimetypes
import re
import shutil
import subprocess
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from backend.audit_copilot import build_context, configured_drafter
from backend.audit_templates import get_audit_template, load_audit_templates
from backend.ai_first_pass import build_first_pass_context, configured_first_pass_drafter, detect_product_type, explore_public_pages, finalize_scope, safe_public_url, scope_request
from backend.auth import SessionStore, session_cookie, session_token, verify_credentials
from backend.storage import AuditRepository


def chrome_pdf_exporter(base_url: str):
    chrome = next((Path(candidate) for candidate in (
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        shutil.which("google-chrome"), shutil.which("chrome"),
    ) if candidate and Path(candidate).is_file()), None)
    if chrome is None:
        raise RuntimeError("Google Chrome is required for direct PDF export")

    def export(audit_id: str, locale: str, output_path: Path):
        report_url = f"{base_url}/report.html?audit={audit_id}&lang={locale}"
        result = subprocess.run([
            str(chrome), "--headless", "--disable-gpu", "--no-first-run",
            "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=5000", f"--print-to-pdf={output_path}", report_url,
        ], capture_output=True, text=True, timeout=45)
        if result.returncode or not output_path.is_file() or output_path.stat().st_size < 100:
            raise RuntimeError(f"Chrome PDF export failed: {result.stderr.strip() or result.stdout.strip()}")
    return export


def create_server(repository, static_root: Path, host: str = "127.0.0.1", port: int = 4173, pdf_exporter=None, ai_drafter=None, ai_first_pass_explorer=None, ai_first_pass_drafter=None, require_auth: bool = True):
    static_root = Path(static_root).resolve()
    sessions = SessionStore()
    repository.backfill_operations_from_audits()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/auth/session":
                self._json(200, {"authenticated": self._authenticated()})
                return
            if path in {"/api/clients", "/api/projects", "/api/audit-templates", "/api/audits"} and not self._require_operator():
                return
            if path == "/api/clients":
                self._json(200, repository.list_clients())
                return
            if path == "/api/projects":
                client_id = parse_qs(urlparse(self.path).query).get("clientId", [None])[0]
                self._json(200, repository.list_projects(client_id))
                return
            if path == "/api/audit-templates":
                self._json(200, load_audit_templates())
                return
            if path == "/api/audits":
                self._json(200, repository.list_audits())
                return
            readiness_match = re.fullmatch(r"/api/audits/([^/]+)/readiness", path)
            if readiness_match:
                if not self._require_operator():
                    return
                try:
                    locale = parse_qs(urlparse(self.path).query).get("locale", [None])[0]
                    self._json(200, repository.publication_readiness(readiness_match.group(1), locale))
                except LookupError as error:
                    self._json(404, {"error": str(error)})
                return
            if path.startswith("/api/audits/"):
                if not self._require_operator():
                    return
                audit = repository.get_audit(path.removeprefix("/api/audits/"))
                if audit is None:
                    self._json(404, {"error": "Audit not found"})
                else:
                    self._json(200, audit)
                return
            self._static(path)

        def do_POST(self):
            path = urlparse(self.path).path
            if path == "/api/auth/login":
                try:
                    credentials = self._request_json()
                    if not isinstance(credentials, dict):
                        raise ValueError("Login request must be a JSON object")
                    email = credentials.get("email", "")
                    password = credentials.get("password", "")
                    if not isinstance(email, str) or not isinstance(password, str):
                        raise ValueError("Email and password are required")
                except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                    self._json(400, {"error": str(error)})
                    return
                if not verify_credentials(email, password):
                    self._json(401, {"error": "Invalid email or password"})
                    return
                self._json(200, {"authenticated": True}, {"Set-Cookie": self._session_cookie(sessions.issue())})
                return
            if path == "/api/auth/logout":
                sessions.revoke(session_token(self.headers.get("Cookie")))
                self._empty(204, {"Set-Cookie": self._session_cookie("", max_age=0)})
                return
            if not self._require_operator():
                return
            if path == "/api/backups":
                backup = repository.backup()
                self._json(201, {"path": str(backup)})
                return
            if path == "/api/clients":
                try:
                    self._json(201, repository.create_client(self._request_json()))
                except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as error:
                    self._json(400, {"error": str(error)})
                return
            if path == "/api/projects":
                try:
                    self._json(201, repository.create_project(self._request_json()))
                except LookupError as error:
                    self._json(404, {"error": str(error)})
                except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as error:
                    self._json(400, {"error": str(error)})
                return
            template_match = re.fullmatch(r"/api/projects/([^/]+)/audits/from-template", path)
            if template_match:
                self._create_from_template(template_match.group(1))
                return
            status_match = re.fullmatch(r"/api/projects/([^/]+)/status", path)
            if status_match:
                try:
                    self._json(200, repository.update_project_status(status_match.group(1), self._request_json().get("status")))
                except LookupError as error:
                    self._json(404, {"error": str(error)})
                except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as error:
                    self._json(400, {"error": str(error)})
                return
            link_match = re.fullmatch(r"/api/projects/([^/]+)/audits/([^/]+)", path)
            if link_match:
                try:
                    self._json(200, repository.link_audit_to_project(link_match.group(2), link_match.group(1)))
                except LookupError as error:
                    self._json(404, {"error": str(error)})
                return
            export_match = re.fullmatch(r"/api/audits/([^/]+)/export-pdf", path)
            if export_match:
                self._export_pdf(export_match.group(1))
                return
            draft_match = re.fullmatch(r"/api/audits/([^/]+)/ai-draft", path)
            if draft_match:
                self._draft_with_ai(draft_match.group(1))
                return
            detect_match = re.fullmatch(r"/api/audits/([^/]+)/detect-product-type", path)
            if detect_match:
                self._detect_product_type(detect_match.group(1))
                return
            first_pass_match = re.fullmatch(r"/api/audits/([^/]+)/ai-first-pass", path)
            if first_pass_match:
                self._first_pass_with_ai(first_pass_match.group(1))
                return
            evidence_match = re.fullmatch(r"/api/audits/([^/]+)/findings/([^/]+)/evidence", path)
            if evidence_match:
                self._upload_evidence(evidence_match.group(1), evidence_match.group(2))
                return
            if path != "/api/audits":
                self._json(404, {"error": "Not found"})
                return
            try:
                audit = self._request_json()
                for field in ("id", "client", "url"):
                    if not isinstance(audit.get(field), str) or not audit[field]:
                        raise ValueError(f"{field} is required")
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self._json(400, {"error": str(error)})
                return
            repository.upsert_audit(audit)
            summary = next(item for item in repository.list_audits() if item["id"] == audit["id"])
            self._json(201, summary)

        def _create_from_template(self, project_id: str):
            project = repository.get_project(project_id)
            if project is None:
                self._json(404, {"error": "Project not found"})
                return
            try:
                request_data = self._request_json()
                template_id = str(request_data.get("templateId", "")).strip()
                template = get_audit_template(template_id)
                if template is None:
                    self._json(404, {"error": "Audit template not found"})
                    return
                target_url = str(request_data.get("url") or project["baseUrl"]).strip()
                if not target_url.startswith(("http://", "https://")):
                    raise ValueError("Audit URL must start with http:// or https://")
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self._json(400, {"error": str(error)})
                return
            audit = {
                "id": f"audit_{uuid.uuid4().hex[:16]}",
                "client": project["clientName"],
                "website": str(request_data.get("title") or project["name"]).strip(),
                "url": target_url,
                "locale": str(request_data.get("locale") or "en"),
                "source": f"template:{template['id']}",
                "projectId": project["id"],
                "templateId": template["id"],
                "templateVersion": "1.0.0",
                "productType": template["productType"],
                "scope": {
                    "productType": template["productType"],
                    "bundle": template["defaultBundle"],
                    "templateId": template["id"],
                    "checkpointCount": len(template["checkpointIds"]),
                },
                "journeys": list(template["journeys"]),
                "assessments": {checkpoint_id: "not_verified" for checkpoint_id in template["checkpointIds"]},
                "findings": [],
                "evidenceRequirements": list(template["evidenceRequirements"]),
                "reportSections": list(template["reportSections"]),
                "status": "draft",
            }
            repository.upsert_audit(audit)
            self._json(201, repository.get_audit(audit["id"]))

        def _draft_with_ai(self, audit_id: str):
            audit = repository.get_audit(audit_id)
            if audit is None:
                self._json(404, {"error": "Audit not found"})
                return
            try:
                request_data = self._request_json()
                if not isinstance(request_data, dict):
                    raise ValueError("Draft request must be a JSON object")
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self._json(400, {"error": str(error)})
                return
            drafter = ai_drafter or configured_drafter
            result = drafter(build_context(audit, request_data))
            # Drafting is deliberately read-only: no finding, evidence, assessment, or score is persisted here.
            self._json(200 if result.get("status") == "ready" else 503, result)

        def _detect_product_type(self, audit_id: str):
            audit = repository.get_audit(audit_id)
            if audit is None:
                self._json(404, {"error": "Audit not found"})
                return
            try:
                request_data = self._request_json()
                target_url = safe_public_url(request_data.get("url") or audit.get("url"))
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self._json(400, {"error": str(error)})
                return
            exploration = explore_public_pages(target_url, {"bundle": "general_health_check", "selectedPages": []})
            if exploration.get("status") != "ready":
                self._json(200, {"status": "needs_input", "message": "Product type could not be detected from the public page. Choose it manually."})
                return
            page = exploration["scope"]["visited"][0]
            self._json(200, detect_product_type(page["url"], f"{page.get('title', '')} {page.get('textExcerpt', '')}"))

        def _first_pass_with_ai(self, audit_id: str):
            audit = repository.get_audit(audit_id)
            if audit is None:
                self._json(404, {"error": "Audit not found"})
                return
            try:
                request_data = self._request_json()
                if not isinstance(request_data, dict):
                    raise ValueError("First-pass request must be a JSON object")
                target_url = safe_public_url(request_data.get("url") or audit.get("url"))
                requested_scope = scope_request(request_data, target_url)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self._json(400, {"error": str(error)})
                return
            explorer = ai_first_pass_explorer or explore_public_pages
            exploration = explorer(target_url, requested_scope)
            if exploration.get("status") != "ready":
                self._json(503, exploration)
                return
            scope = finalize_scope(exploration.get("scope") or {}, requested_scope)
            drafter = ai_first_pass_drafter or configured_first_pass_drafter
            result = drafter(build_first_pass_context(audit, scope))
            # Discovery is deliberately transient: never persist candidates, evidence, findings, scores, readiness, or report data.
            if result.get("status") != "ready":
                self._json(503, result)
                return
            self._json(200, {"status": "ready", "scope": scope, "candidates": result.get("candidates", [])})

        def _export_pdf(self, audit_id: str):
            locale = parse_qs(urlparse(self.path).query).get("locale", ["en"])[0]
            try:
                readiness = repository.publication_readiness(audit_id, locale)
                if not readiness["ready"]:
                    self._json(409, {"error": "Publication readiness failed", "readiness": readiness})
                    return
                audit = repository.get_audit(audit_id)
                safe_client = re.sub(r"[^a-z0-9]+", "-", audit["client"].lower()).strip("-") or "client"
                filename = f"{safe_client}-uxm-client-report-{datetime.now():%Y%m%d-%H%M%S}.pdf"
                output_path = static_root / "artifacts" / "exports" / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
                exporter = pdf_exporter or chrome_pdf_exporter(f"http://{self.server.server_address[0]}:{self.server.server_address[1]}")
                exporter(audit_id, locale if locale == "ar" else "en", output_path)
                self._json(201, {"filename": filename, "downloadUrl": f"/artifacts/exports/{filename}"})
            except LookupError as error:
                self._json(404, {"error": str(error)})
            except (RuntimeError, subprocess.TimeoutExpired) as error:
                self._json(500, {"error": str(error)})

        def _upload_evidence(self, audit_id: str, finding_id: str):
            mime_type = self.headers.get("Content-Type", "").split(";", 1)[0].lower()
            original_filename = self.headers.get("X-Original-Filename", "")
            captured_at = self.headers.get("X-Captured-At", "")
            kind = urlparse(self.path).query.partition("kind=")[2].split("&", 1)[0]
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if length < 1 or length > 5 * 1024 * 1024:
                    if length > 0:
                        self.rfile.read(length)
                    raise ValueError("Evidence must be between 1 byte and 5 MiB")
                if mime_type not in {"image/png", "image/jpeg"}:
                    raise ValueError("Only PNG and JPEG evidence is accepted")
                body = self.rfile.read(length)
                valid = (mime_type == "image/png" and body.startswith(b"\x89PNG\r\n\x1a\n")) or (mime_type == "image/jpeg" and body.startswith(b"\xff\xd8\xff"))
                if not valid:
                    raise ValueError("Evidence content does not match its image MIME type")
                evidence = repository.attach_evidence(audit_id, finding_id, kind, body, mime_type, original_filename, captured_at)
            except (ValueError, LookupError) as error:
                self._json(400 if isinstance(error, ValueError) else 404, {"error": str(error)})
                return
            self._json(201, evidence)

        def _authenticated(self):
            return not require_auth or sessions.active(session_token(self.headers.get("Cookie")))

        def _session_cookie(self, token: str, max_age: int = 8 * 60 * 60) -> str:
            return session_cookie(token, max_age=max_age, secure=not self._is_loopback_http())

        def _is_loopback_http(self) -> bool:
            if self.headers.get("X-Forwarded-Proto", "").lower() == "https":
                return False
            host = self.headers.get("Host", "")
            if host.startswith("["):
                hostname = host[1:].split("]", 1)[0]
            else:
                hostname = host.split(":", 1)[0]
            if hostname.lower() == "localhost":
                return True
            try:
                return ipaddress.ip_address(hostname).is_loopback
            except ValueError:
                return False

        def _require_operator(self):
            if self._authenticated():
                return True
            self._json(401, {"error": "Operator authentication required"})
            return False

        def _request_json(self):
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def _json(self, status: int, body, headers=None):
            encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(encoded)

        def _empty(self, status: int, headers=None):
            self.send_response(status)
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.end_headers()

        def _static(self, request_path: str):
            relative_path = "index.html" if request_path == "/" else request_path.lstrip("/")
            if self._is_never_served_static(relative_path):
                self.send_error(404, "Not found")
                return
            if relative_path in {"workspace.html", "operations.html", "templates.html"} and not self._require_operator():
                return
            if self._is_sensitive_static(relative_path) and not self._require_operator():
                return
            target = (static_root / relative_path).resolve()
            if static_root not in target.parents and target != static_root:
                self.send_error(403, "Forbidden")
                return
            if not target.is_file():
                self.send_error(404, "Not found")
                return
            body = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(str(target))[0] or "application/octet-stream")
            if target.suffix.lower() == ".pdf":
                self.send_header("Content-Disposition", f'attachment; filename="{target.name}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionAbortedError):
                # Browsers may cancel a static request during navigation; this must not crash a request thread.
                return

        @staticmethod
        def _is_never_served_static(relative_path: str) -> bool:
            return any(part.lower().startswith(".env") for part in Path(relative_path).parts)

        @staticmethod
        def _is_sensitive_static(relative_path: str) -> bool:
            path = Path(relative_path)
            protected_roots = {"artifacts", "backend", "data", "evidence"}
            protected_suffixes = {".db", ".key", ".pem", ".sqlite", ".sqlite3"}
            return (
                bool(path.parts and path.parts[0].lower() in protected_roots)
                or path.suffix.lower() in protected_suffixes
            )

        def log_message(self, format, *args):
            return

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description="Serve the UXM Audit API and frontend.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    repository = AuditRepository(root / "data" / "uxm-audit.db", root / "data" / "backups", root / "evidence")
    server = create_server(repository, root, host=args.host, port=args.port)
    print(f"UXM Audit running at http://{args.host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
