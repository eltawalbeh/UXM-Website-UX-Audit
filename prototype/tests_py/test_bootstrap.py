"""Fresh-clone bootstrap coverage using an isolated database and evidence directory."""

from __future__ import annotations

import importlib.util
import shutil
import sqlite3
import tempfile
from contextlib import closing
import unittest
from pathlib import Path


PROTOTYPE_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = PROTOTYPE_ROOT.parent


def load_bootstrap_module():
    script = AUDIT_ROOT / "scripts" / "bootstrap_prototype.py"
    spec = importlib.util.spec_from_file_location("bootstrap_prototype", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FreshCloneBootstrapTests(unittest.TestCase):
    def test_bootstrap_creates_missing_database_imports_pilots_and_materializes_evidence(self):
        bootstrap = load_bootstrap_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            database = root / "prototype" / "data" / "uxm-audit.db"
            evidence = root / "prototype" / "evidence"

            imported = bootstrap.bootstrap(AUDIT_ROOT, database_path=database, evidence_dir=evidence)

            self.assertTrue(database.is_file())
            self.assertEqual(imported, {
                "pilot_ammancity_eservices_20260715": 2,
                "pilot_jordan_gov_onyourservice_20260714": 5,
                "pilot_tawasal_bekhedmetcom_20260714": 4,
            })
            with closing(sqlite3.connect(database)) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM audits").fetchone()[0], 3)
            self.assertTrue((evidence / "annotated" / "jordan-gov-onyourservice" / "UXM-001.png").is_file())
            self.assertTrue((evidence / "raw" / "tawasal" / "sendotp.png").is_file())

    def test_bootstrap_is_idempotent_and_restores_missing_evidence_without_using_a_runtime_database(self):
        bootstrap = load_bootstrap_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            database = root / "prototype" / "data" / "uxm-audit.db"
            evidence = root / "prototype" / "evidence"

            first = bootstrap.bootstrap(AUDIT_ROOT, database_path=database, evidence_dir=evidence)
            shutil.rmtree(evidence / "raw" / "tawasal")
            second = bootstrap.bootstrap(AUDIT_ROOT, database_path=database, evidence_dir=evidence)

            self.assertEqual(second, first)
            self.assertTrue((evidence / "raw" / "tawasal" / "sendotp.png").is_file())
            with closing(sqlite3.connect(database)) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM audits").fetchone()[0], 3)


if __name__ == "__main__":
    unittest.main()
