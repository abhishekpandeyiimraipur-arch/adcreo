# ci/validate_compliance_taxonomy.py
# Stage 1 static guard: ensures all compliance_log.check_type values
# are members of the 4 canonical strings per BEF §14.4.
# Exit 0 = clean. Exit 1 = violations found.

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "backend" / "app"

CANONICAL = {"c2pa_sign", "sgi_burn_in", "declaration_capture", "freshness_check"}

# Matches: check_type='c2pa_sign' or check_type="c2pa_sign"
PATTERN = re.compile(r'check_type\s*[=:]\s*["\']([^"\']+)["\']')


def main():
    violations = []
    files_scanned = 0

    for path in APP_DIR.rglob("*.py"):
        files_scanned += 1
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for match in PATTERN.finditer(stripped):
                value = match.group(1)
                if value not in CANONICAL:
                    violations.append({
                        "file": str(path.relative_to(ROOT)),
                        "line": lineno,
                        "check_type": value,
                        "reason": f"unknown check_type '{value}' — must be one of {sorted(CANONICAL)}"
                    })

    if violations:
        for v in violations:
            print(json.dumps({"status": "violation", **v}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "files_scanned": files_scanned,
        "violations": 0,
        "canonical_values": sorted(CANONICAL)
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
