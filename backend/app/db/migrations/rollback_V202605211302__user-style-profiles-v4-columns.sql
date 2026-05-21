-- rollback_V202605211302__user-style-profiles-v4-columns.sql
-- Rollback: remove v4-Δ1 columns from user_style_profiles.
-- HUMAN-AUTHORED ROLLBACK — requires Founder approval before execution.

BEGIN;

ALTER TABLE user_style_profiles DROP COLUMN IF EXISTS brand_tier;
ALTER TABLE user_style_profiles DROP COLUMN IF EXISTS brand_color_primary;

DELETE FROM schema_migrations
    WHERE filename = 'V202605211302__user-style-profiles-v4-columns.sql';

COMMIT;
