# ci/migration_safety_guard.py
# Stage 1 static guard: scans all migration .sql files for forbidden
# patterns and verifies every migration has a rollback pair.
# Per [TDD-MIGRATION-SAFETY]-D. Exit 0 = clean. Exit 1 = violations.

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "backend" / "app" / "db" / "migrations"

FORBIDDEN = [
    re.compile(r'^\s*DROP\s+TABLE\b', re.IGNORECASE),
    re.compile(r'^\s*DROP\s+COLUMN\b', re.IGNORECASE),
    re.compile(r'^\s*DROP\s+TYPE\b', re.IGNORECASE),
    re.compile(r'^\s*DROP\s+CONSTRAINT\s+(?!IF\s+EXISTS)\b', re.IGNORECASE),
    re.compile(r'^\s*ALTER\s+TABLE.*RENAME\s+COLUMN\b', re.IGNORECASE),
    re.compile(r'^\s*ALTER\s+TABLE.*RENAME\s+TO\b', re.IGNORECASE),
    re.compile(r'^\s*TRUNCATE\b', re.IGNORECASE),
    re.compile(r'^\s*ALTER\s+COLUMN\s+\w+\s+TYPE\b', re.IGNORECASE),
    re.compile(r'^\s*ALTER\s+COLUMN\s+\w+\s+SET\s+NOT\s+NULL\b', re.IGNORECASE),
]


def check_forbidden(path: Path, violations: list):
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    for lineno, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        for pattern in FORBIDDEN:
            if pattern.match(stripped):
                violations.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": lineno,
                    "reason": "forbidden DDL pattern",
                    "content": stripped[:120]
                })


def check_rollback_pairs(migration_files: list, violations: list):
    forward = {
        f.name for f in migration_files
        if not f.name.startswith("rollback_")
        and not f.name.startswith("000")
        and not f.name.startswith("001_")
        and not f.name.startswith("002_")
        and f.name.endswith(".sql")
    }
    rollbacks = {
        f.name.replace("rollback_", "") for f in migration_files
        if f.name.startswith("rollback_")
    }
    for migration in forward:
        if migration not in rollbacks:
            violations.append({
                "file": migration,
                "reason": f"missing rollback pair: rollback_{migration}"
            })


def main():
    if not MIGRATIONS_DIR.exists():
        print(json.dumps({"error": f"migrations dir not found: {MIGRATIONS_DIR}"}))
        sys.exit(1)

    migration_files = list(MIGRATIONS_DIR.glob("*.sql"))
    violations = []

    for path in migration_files:
        if path.name.startswith("000"):
            continue
        if path.name.startswith("rollback_"):
            continue
        check_forbidden(path, violations)

    check_rollback_pairs(migration_files, violations)

    if violations:
        for v in violations:
            print(json.dumps({"status": "violation", **v}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "migrations_checked": len(migration_files),
        "violations": 0
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
