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


if __name__ == "__main__":
    unittest.main()
