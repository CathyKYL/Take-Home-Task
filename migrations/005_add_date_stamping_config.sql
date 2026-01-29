-- Migration: Add date stamping configuration column to runs table
-- This stores user's manual date stamping preferences

ALTER TABLE runs 
ADD COLUMN IF NOT EXISTS date_stamping_config_json JSONB;

-- Add documentation
COMMENT ON COLUMN runs.date_stamping_config_json IS 'User configuration for manual date stamping (which tabs, which columns, which date)';

