-- V202605211400__add-d2c-fashion-greenzone.sql
-- Adds d2c_fashion to green_zone_category ENUM.
-- Additive only. ALTER TYPE ADD VALUE is append-only per [TDD-MIGRATION-SAFETY]-A.

BEGIN;

ALTER TYPE green_zone_category ADD VALUE IF NOT EXISTS 'd2c_fashion';

COMMIT;
