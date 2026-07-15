from __future__ import annotations

import argparse
import json
import mimetypes
import re
import shutil
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from backend.audit_copilot import build_context, configured_drafter
from backend.ai_first_pass import build_first_pass_context, configured_first_pass_drafter, explore_public_pages, finalize_scope, safe_public_url, scope_request
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


def create_server(repository, static_root: Path, host: str = "127.0.0.1", port: int = 4173, pdf_exporter=None, ai_drafter=None, ai_first_pass_explorer=None, ai_first_pass_drafter=None):
    static_root = Path(static_root).resolve()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/audits":
                self._json(200, repository.list_audits())
                return
            readiness_match = re.fullmatch(r"/api/audits/([^/]+)/readiness", path)
            if readiness_match:
                try:
                    locale = parse_qs(urlparse(self.path).query).get("locale", [None])[0]
                    self._json(200, repository.publication_readiness(readiness_match.group(1), locale))
                except LookupError as error:
                    self._json(404, {"error": str(error)})
                return
            if path.startswith("/api/audits/"):
                audit = repository.get_audit(path.removeprefix("/api/audits/"))
                if audit is None:
                    self._json(404, {"error": "Audit not found"})
                else:
                    self._json(200, audit)
                return
            self._static(path)

        def do_POST(self):
            path = urlparse(self.path).path
            if path == "/api/backups":
                backup = repository.backup()
                self._json(201, {"path": str(backup)})
                return
            export_match = re.fullmatch(r"/api/audits/([^/]+)/export-pdf", path)
            if export_match:
                self._export_pdf(export_match.group(1))
                return
            draft_match = re.fullmatch(r"/api/audits/([^/]+)/ai-draft", path)
            if draft_match:
                self._draft_with_ai(draft_match.group(1))
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

        def _request_json(self):
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def _json(self, status: int, body):
            encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _static(self, request_path: str):
            relative_path = "index.html" if request_path == "/" else request_path.lstrip("/")
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
