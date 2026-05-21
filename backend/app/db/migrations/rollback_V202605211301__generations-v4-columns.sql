-- rollback_V202605211301__generations-v4-columns.sql
-- Rollback: remove v4-Δ1 columns from generations.
-- HUMAN-AUTHORED ROLLBACK — requires Founder approval before execution.

BEGIN;

ALTER TABLE generations DROP COLUMN IF EXISTS structure_template;
ALTER TABLE generations DROP COLUMN IF EXISTS active_season;
ALTER TABLE generations DROP COLUMN IF EXISTS b_roll_performance_signal;

DELETE FROM schema_migrations
    WHERE filename = 'V202605211301__generations-v4-columns.sql';

COMMIT;
