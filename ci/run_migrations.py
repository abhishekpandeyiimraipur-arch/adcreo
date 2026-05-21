# ci/run_migrations.py
import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
import asyncpg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "backend" / "app" / "db" / "migrations"

FORBIDDEN_PATTERNS = [
    re.compile(r"DROP\s+TABLE", re.IGNORECASE),
    re.compile(r"DROP\s+COLUMN", re.IGNORECASE),
    re.compile(r"RENAME", re.IGNORECASE),
    re.compile(r"TRUNCATE", re.IGNORECASE),
    re.compile(r"ALTER\s+COLUMN.*TYPE", re.IGNORECASE),
    re.compile(r"ALTER\s+COLUMN.*SET\s+NOT\s+NULL", re.IGNORECASE),
]

def get_migration_files():
    if not MIGRATIONS_DIR.exists():
        return []
    files = [f for f in MIGRATIONS_DIR.iterdir() if f.is_file() and f.suffix == ".sql"]
    files.sort(key=lambda f: f.name)
    return files

def do_dry_run():
    files = get_migration_files()
    has_violation = False
    
    for f in files:
        violation_found = False
        try:
            content = f.read_text(encoding="utf-8")
            # The spec says "greps for forbidden patterns", implying line-by-line matching
            for line in content.splitlines():
                for pattern in FORBIDDEN_PATTERNS:
                    if pattern.search(line):
                        violation_found = True
                        has_violation = True
                        break
                if violation_found:
                    break
        except Exception:
            pass
        
        status = "forbidden" if violation_found else "dry_run_ok"
        print(json.dumps({"file": f.name, "status": status}))
        
    if has_violation:
        sys.exit(1)
    else:
        sys.exit(0)

async def do_apply():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing.")
    
    files = get_migration_files()
    
    try:
        conn = await asyncpg.connect(db_url)
        
        # Ensure schema_migrations table exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Start a transaction for all unapplied migrations
        async with conn.transaction():
            # Get already applied migrations
            applied_records = await conn.fetch("SELECT filename FROM schema_migrations")
            applied_set = {r["filename"] for r in applied_records}
            
            for f in files:
                if f.name in applied_set:
                    print(json.dumps({"file": f.name, "status": "skipped"}))
                    continue
                
                content = f.read_text(encoding="utf-8")
                await conn.execute(content)
                await conn.execute("INSERT INTO schema_migrations (filename) VALUES ($1)", f.name)
                print(json.dumps({"file": f.name, "status": "applied"}))
                
        await conn.close()
        sys.exit(0)
    except Exception as e:
        # asyncpg auto-rolls back when exiting async with conn.transaction() on exception
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Migration runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    group.add_argument("--apply", action="store_true", help="Run and apply migrations")
    
    args = parser.parse_args()
    
    if args.dry_run:
        do_dry_run()
    elif args.apply:
        asyncio.run(do_apply())

if __name__ == "__main__":
    main()
