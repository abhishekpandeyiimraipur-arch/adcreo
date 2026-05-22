#!/usr/bin/env python3
# backend/ci/broll_coverage_check.py
# [TDD-BROLL]-J: Library coverage check.
# For every (category, role) combination required for T1 template,
# assert >= 1 active clip exists in broll_clips.
# Exits 0 on pass, 1 on failure — blocks deploy on any uncovered slot.

import os
import sys
import psycopg2

REQUIRED = [
    ("d2c_beauty",       "hook"),
    ("d2c_beauty",       "context"),
    ("d2c_beauty",       "cta_bg"),
    ("packaged_food",    "hook"),
    ("packaged_food",    "context"),
    ("packaged_food",    "cta_bg"),
    ("electronics",      "hook"),
    ("electronics",      "context"),
    ("electronics",      "cta_bg"),
    ("hard_accessories", "hook"),
    ("hard_accessories", "context"),
    ("hard_accessories", "cta_bg"),
    ("home_kitchen",     "hook"),
    ("home_kitchen",     "context"),
    ("home_kitchen",     "cta_bg"),
    ("d2c_fashion",      "hook"),
    ("d2c_fashion",      "context"),
    ("d2c_fashion",      "cta_bg"),
]

def main():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    conn = psycopg2.connect(dsn)
    cur  = conn.cursor()

    cur.execute("""
        SELECT category, role, COUNT(*)
        FROM broll_clips
        WHERE is_active = TRUE
        GROUP BY category, role
    """)
    live = {(row[0], row[1]): row[2] for row in cur.fetchall()}
    cur.close()
    conn.close()

    failures = []
    for category, role in REQUIRED:
        count = live.get((category, role), 0)
        if count == 0:
            failures.append(f"  MISSING: ({category}, {role})")
        else:
            print(f"  OK: ({category}, {role}) = {count} clip(s)")

    if failures:
        print("\nCOVERAGE CHECK FAILED:")
        for f in failures:
            print(f)
        sys.exit(1)
    else:
        print(f"\nCOVERAGE CHECK PASSED — all {len(REQUIRED)} required slots covered.")
        sys.exit(0)

if __name__ == "__main__":
    main()
