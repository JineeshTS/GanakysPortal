-- DEP-004: GanaPortal Database Initialization Script
-- Run on fresh PostgreSQL installation

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Create database (if not exists)
SELECT 'CREATE DATABASE ganaportal_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ganaportal_db')\gexec

-- Connect to database
\c ganaportal_db

-- Create schema
CREATE SCHEMA IF NOT EXISTS ganaportal;

-- Set search path
SET search_path TO ganaportal, public;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA ganaportal TO ganaportal;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ganaportal TO ganaportal;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ganaportal TO ganaportal;

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = NOW();
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'GanaPortal database initialized successfully';
END $$;
