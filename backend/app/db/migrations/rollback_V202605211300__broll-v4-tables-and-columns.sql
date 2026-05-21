-- rollback_V202605211300__broll-v4-tables-and-columns.sql
-- Rollback: drop tables added in V202605211300 (reverse order of creation).
-- HUMAN-AUTHORED ROLLBACK — requires Founder approval before execution.

BEGIN;

DROP TABLE IF EXISTS broll_clip_usage;
DROP TABLE IF EXISTS seasons;
DROP TABLE IF EXISTS feature_flags;

DELETE FROM schema_migrations
    WHERE filename = 'V202605211300__broll-v4-tables-and-columns.sql';

COMMIT;
