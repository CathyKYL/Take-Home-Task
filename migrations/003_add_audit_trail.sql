-- Migration: Add audit trail storage to runs table
-- This column stores a complete log of all processing actions

ALTER TABLE runs 
ADD COLUMN IF NOT EXISTS audit_trail_json JSONB;

-- Add index for efficient queries on audit trail
CREATE INDEX IF NOT EXISTS idx_runs_audit_trail ON runs USING GIN (audit_trail_json);

-- Comment on column
COMMENT ON COLUMN runs.audit_trail_json IS 'Complete audit trail of all processing actions with timestamps, action types, and affected row counts';

