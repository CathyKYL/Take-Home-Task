-- Migration: Add manual_hold_mappings_json column
-- This column stores manual vendor name mappings when automatic matching fails

ALTER TABLE runs 
ADD COLUMN IF NOT EXISTS manual_hold_mappings_json JSONB;

-- Comment on column
COMMENT ON COLUMN runs.manual_hold_mappings_json IS 'Manual vendor name mappings from hold list to AP file (when auto-match fails)';

