import json
import tempfile
import unittest
from pathlib import Path

from backend.storage import AuditRepository


class AuditRepositoryTests(unittest.TestCase):
    def test_imported_pilot_persists_and_backup_is_created(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = AuditRepository(root / "uxm-audit.db", root / "backups")
            pilot = {
                "id": "pilot_demo", "client": "Demo", "url": "https://example.com",
                "locale": "ar", "findings": [{"id": "UXM-001", "severity": "high"}],
            }
            repo.upsert_audit(pilot, source="pilot")

            loaded = repo.get_audit("pilot_demo")
            backup = repo.backup()

            self.assertEqual(loaded["client"], "Demo")
            self.assertEqual(loaded["findings"][0]["id"], "UXM-001")
            self.assertTrue(backup.exists())
            self.assertEqual(len(repo.list_audits()), 1)
    def test_client_project_and_audit_relationship_persists_with_derived_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = AuditRepository(root / "uxm-audit.db", root / "backups")
            client = repo.create_client({"name": "Acme Jordan", "contactName": "Rana", "email": "rana@example.com", "phone": "+962700000000", "notes": "Priority account"})
            project = repo.create_project({"clientId": client["id"], "name": "Public website", "baseUrl": "https://example.com", "productType": "corporate_marketing", "owner": "Abdullah"})
            audit = {"id": "audit_acme_1", "client": "Acme Jordan", "url": "https://example.com", "locale": "en", "findings": []}
            repo.upsert_audit(audit)

            repo.link_audit_to_project("audit_acme_1", project["id"])
            repo.update_project_status(project["id"], "in_review")

            clients = repo.list_clients()
            projects = repo.list_projects(client["id"])
            loaded_audit = repo.get_audit("audit_acme_1")
            self.assertEqual(clients[0]["projectCount"], 1)
            self.assertEqual(clients[0]["auditCount"], 1)
            self.assertEqual(projects[0]["status"], "in_review")
            self.assertEqual(projects[0]["auditCount"], 1)
            self.assertEqual(loaded_audit["projectId"], project["id"])

    def test_project_rejects_unknown_client_and_invalid_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = AuditRepository(root / "uxm-audit.db", root / "backups")
            with self.assertRaises(LookupError):
                repo.create_project({"clientId": "missing", "name": "X", "baseUrl": "https://example.com"})
            client = repo.create_client({"name": "Client"})
            project = repo.create_project({"clientId": client["id"], "name": "Project", "baseUrl": "https://example.com"})
            with self.assertRaises(ValueError):
                repo.update_project_status(project["id"], "published-ish")
    def test_unlinked_existing_audits_backfill_into_idempotent_client_projects(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = AuditRepository(root / "uxm-audit.db", root / "backups")
            repo.upsert_audit({"id": "pilot_one", "client": "Legacy Client", "website": "Main site", "url": "https://example.com", "findings": []})
            repo.upsert_audit({"id": "pilot_two", "client": "Legacy Client", "website": "Service portal", "url": "https://service.example.com", "findings": []})

            first = repo.backfill_operations_from_audits()
            second = repo.backfill_operations_from_audits()

            self.assertEqual(first, {"clientsCreated": 1, "projectsCreated": 2, "auditsLinked": 2})
            self.assertEqual(second, {"clientsCreated": 0, "projectsCreated": 0, "auditsLinked": 0})
            self.assertEqual(len(repo.list_clients()), 1)
            self.assertEqual(len(repo.list_projects()), 2)
            self.assertTrue(all(repo.get_audit(audit_id).get("projectId") for audit_id in ("pilot_one", "pilot_two")))


if __name__ == "__main__":
    unittest.main()
