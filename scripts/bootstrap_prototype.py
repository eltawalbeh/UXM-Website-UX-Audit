"""Create a fresh UXM Audit runtime database from the committed pilot fixtures.

This command is safe to run repeatedly.  It never relies on an existing local
runtime database: the committed pilot JSON and repository evidence are the
source of truth for every run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def bootstrap(
    audit_root: Path,
    database_path: Path | None = None,
    evidence_dir: Path | None = None,
) -> dict[str, int]:
    """Initialize a local SQLite runtime and upsert the committed pilot audits."""
    audit_root = Path(audit_root).resolve()
    prototype_root = audit_root / "prototype"
    database_path = Path(database_path) if database_path else prototype_root / "data" / "uxm-audit.db"
    evidence_dir = Path(evidence_dir) if evidence_dir else prototype_root / "evidence"

    # The bootstrap script is invoked from the repository root, whereas the
    # backend package lives below prototype/ and the migration helper is here.
    for import_root in (prototype_root, Path(__file__).resolve().parent):
        if str(import_root) not in sys.path:
            sys.path.insert(0, str(import_root))
    from backend.storage import AuditRepository
    from import_pilots_to_prototype import import_pilots

    repository = AuditRepository(database_path, database_path.parent / "backups", evidence_dir)
    return import_pilots(audit_root / "pilots", repository, audit_root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap the UXM Audit local runtime from committed pilot fixtures.")
    parser.add_argument("--database", type=Path, help="Override the default prototype/data/uxm-audit.db path")
    parser.add_argument("--evidence-dir", type=Path, help="Override the default prototype/evidence path")
    args = parser.parse_args()

    audit_root = Path(__file__).resolve().parents[1]
    database_path = args.database or audit_root / "prototype" / "data" / "uxm-audit.db"
    created = not database_path.exists()
    imported = bootstrap(audit_root, database_path=database_path, evidence_dir=args.evidence_dir)
    state = "created" if created else "updated"
    print(f"Bootstrap {state} {database_path}")
    for audit_id, finding_count in imported.items():
        print(f"  {audit_id}: {finding_count} publishable findings")


if __name__ == "__main__":
    main()
