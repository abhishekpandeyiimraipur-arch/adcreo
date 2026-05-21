-- V202605211300__broll-v4-tables-and-columns.sql
-- v4-Δ1 additive migrations: feature_flags, broll_clip_usage, seasons,
-- generations new columns, user_style_profiles new columns.
-- Append-only. All IF NOT EXISTS guarded. Single transaction.

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════
-- (22) feature_flags
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS feature_flags (
    key         TEXT PRIMARY KEY,
    value       JSONB NOT NULL DEFAULT 'false',
    description TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO feature_flags (key, value, description)
VALUES (
    'broll_v4_routing_enabled',
    'false',
    'Gates v4-Δ1 B-roll template router. FALSE = T1-only legacy path.'
)
ON CONFLICT (key) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════
-- (23) broll_clip_usage — rotation history
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS broll_clip_usage (
    user_id  UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    clip_id  VARCHAR(20) NOT NULL REFERENCES broll_clips(clip_id) ON DELETE CASCADE,
    gen_id   UUID        NOT NULL REFERENCES generations(gen_id) ON DELETE CASCADE,
    used_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, clip_id, gen_id)
);

CREATE INDEX IF NOT EXISTS idx_broll_usage_user_recent
    ON broll_clip_usage (user_id, used_at DESC);

-- ═══════════════════════════════════════════════════════════════════════
-- (24) seasons — festive season lookup
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS seasons (
    season_tag   VARCHAR(30) PRIMARY KEY,
    display_name VARCHAR(60) NOT NULL,
    active_from  DATE        NOT NULL,
    active_to    DATE        NOT NULL,
    is_active    BOOLEAN     NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_season_window CHECK (active_from <= active_to)
);

INSERT INTO seasons (season_tag, display_name, active_from, active_to, is_active) VALUES
    ('diwali',          'Diwali',          '2026-10-20', '2026-10-25', FALSE),
    ('holi',            'Holi',            '2027-03-01', '2027-03-15', FALSE),
    ('wedding_season',  'Wedding Season',  '2026-11-01', '2026-12-31', FALSE),
    ('monsoon',         'Monsoon',         '2026-06-01', '2026-09-30', FALSE),
    ('new_year',        'New Year',        '2026-12-28', '2027-01-02', FALSE),
    ('raksha_bandhan',  'Raksha Bandhan',  '2026-08-07', '2026-08-09', FALSE)
ON CONFLICT (season_tag) DO NOTHING;

INSERT INTO schema_migrations (filename)
VALUES ('V202605211300__broll-v4-tables-and-columns.sql')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
