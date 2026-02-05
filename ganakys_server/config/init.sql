-- Initialize PostgreSQL extensions for Ganakys Academy
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create full-text search indexes (will be applied after Serverpod migrations)
-- These are run once on initial setup
