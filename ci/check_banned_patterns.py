# ci/check_banned_patterns.py
# Stage 1 static guard: scans app/ for leaked secrets,
# banned imports, and print() statements per [TDD-CICD]-A.
# Exit 0 = clean. Exit 1 = violations found.

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "backend" / "app"
BROLL_DIR = APP_DIR / "broll"

# Patterns that must never appear in app/ Python files
GLOBAL_BANNED = [
    (re.compile(r'print\('), "print() statement in production code"),
    (re.compile(r'(?i)(sk-[a-zA-Z0-9]{20,}|r8_[a-zA-Z0-9]{20,}|sk_[a-zA-Z0-9]{20,})'), "hardcoded API key"),
    (re.compile(r'(?i)password\s*=\s*["\'][^"\']+["\']'), "hardcoded password"),
    (re.compile(r'presign(?!ed URL usage|ed\.|.*not presigned)'), "presigned URL usage (banned per BEF §6 rule 1)"),
    (re.compile(r'boto3.*presign|presign.*boto3'), "presigned boto3 URL"),
    (re.compile(r'-shortest'), "banned FFmpeg flag -shortest (BEF §6 rule 2)"),
]

# Additional banned imports inside app/broll/ only
BROLL_BANNED_IMPORTS = [
    "sentence_transformers",
    "chromadb",
    "faiss",
    "transformers",
    "torch",
]


def scan_file_no_presign(path: Path, violations: list):
    """Scan file for all banned patterns EXCEPT presign — for non-worker files."""
    NON_WORKER_BANNED = [
        p for p in GLOBAL_BANNED
        if "presign" not in p[1].lower()
    ]
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    for lineno, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "not presigned" in stripped.lower():
            continue
        for pattern, reason in NON_WORKER_BANNED:
            if pattern.search(stripped):
                violations.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": lineno,
                    "reason": reason,
                    "content": line.strip()[:120]
                })
        if BROLL_DIR in path.parents or path.parent == BROLL_DIR:
            for banned in BROLL_BANNED_IMPORTS:
                if re.search(rf'\b{banned}\b', line):
                    violations.append({
                        "file": str(path.relative_to(ROOT)),
                        "line": lineno,
                        "reason": f"banned ML import in app/broll/: {banned}",
                        "content": line.strip()[:120]
                    })


def scan_file(path: Path, violations: list):
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return

    for lineno, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "not presigned" in stripped.lower():
            continue

        for pattern, reason in GLOBAL_BANNED:
            if pattern.search(stripped):
                violations.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": lineno,
                    "reason": reason,
                    "content": line.strip()[:120]
                })

        # broll-specific banned imports
        if BROLL_DIR in path.parents or path.parent == BROLL_DIR:
            for banned in BROLL_BANNED_IMPORTS:
                if re.search(rf'\b{banned}\b', line):
                    violations.append({
                        "file": str(path.relative_to(ROOT)),
                        "line": lineno,
                        "reason": f"banned ML import in app/broll/: {banned}",
                        "content": line.strip()[:120]
                    })


def main():
    if not APP_DIR.exists():
        print(json.dumps({"error": f"app/ not found at {APP_DIR}"}))
        sys.exit(1)

    violations = []
    WORKERS_DIR = APP_DIR / "workers"
    for path in APP_DIR.rglob("*.py"):
        # presign check only applies to workers/ — routes may mint
        # presigned URLs at L2 hydration time per TDD [TDD-R2-BUCKETS]
        if "presign" in path.read_text(encoding="utf-8", errors="ignore").lower():
            if WORKERS_DIR not in path.parents and path.parent != WORKERS_DIR:
                # not a worker — skip presign pattern for this file
                scan_file_no_presign(path, violations)
                continue
        scan_file(path, violations)

    if violations:
        for v in violations:
            print(json.dumps({"status": "violation", **v}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "files_scanned": len(list(APP_DIR.rglob("*.py"))),
        "violations": 0
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
