-- rollback_V202605211400__add-d2c-fashion-greenzone.sql
-- NOTE: Postgres does not support removing ENUM values.
-- Rollback is a no-op. Manual intervention required if d2c_fashion must be removed.
-- HUMAN-AUTHORED — requires Founder approval before execution.

-- No automated rollback possible for ALTER TYPE ADD VALUE.
-- To remove: DROP TYPE and recreate (requires table rebuild — production risk).
-- Decision: accept d2c_fashion as permanent GreenZone category.
SELECT 1; -- no-op
