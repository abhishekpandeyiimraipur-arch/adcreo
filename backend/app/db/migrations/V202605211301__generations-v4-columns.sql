-- V202605211301__generations-v4-columns.sql
-- v4-Δ1: add structure_template, active_season, b_roll_performance_signal
-- to generations table. Append-only. NULL-safe defaults.

BEGIN;

ALTER TABLE generations
    ADD COLUMN IF NOT EXISTS structure_template VARCHAR(2)
        DEFAULT NULL
        CHECK (structure_template IN ('T1','T2','T3','T4','T5'));

ALTER TABLE generations
    ADD COLUMN IF NOT EXISTS active_season VARCHAR(30)
        DEFAULT NULL
        REFERENCES seasons(season_tag) ON DELETE SET NULL;

ALTER TABLE generations
    ADD COLUMN IF NOT EXISTS b_roll_performance_signal NUMERIC(4,3)
        DEFAULT NULL
        CHECK (b_roll_performance_signal BETWEEN 0.0 AND 1.0);

INSERT INTO schema_migrations (filename)
VALUES ('V202605211301__generations-v4-columns.sql')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
