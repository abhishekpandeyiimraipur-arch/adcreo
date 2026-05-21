-- V202605211302__user-style-profiles-v4-columns.sql
-- v4-Δ1: add brand_tier, brand_color_primary to user_style_profiles.
-- Append-only. NULL-safe defaults.

BEGIN;

ALTER TABLE user_style_profiles
    ADD COLUMN IF NOT EXISTS brand_tier VARCHAR(10)
        DEFAULT NULL
        CHECK (brand_tier IN ('budget', 'mid', 'premium'));

ALTER TABLE user_style_profiles
    ADD COLUMN IF NOT EXISTS brand_color_primary VARCHAR(7)
        DEFAULT NULL
        CHECK (brand_color_primary ~ '^#[0-9A-Fa-f]{6}$');



COMMIT;
