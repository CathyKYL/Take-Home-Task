-- Migration: Create runs table for tracking AP processing runs
-- This table stores metadata for each upload/process operation

CREATE TABLE IF NOT EXISTS runs (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    upload_date DATE NOT NULL,
    
    -- Status tracking
    status TEXT NOT NULL,
    -- Possible values: 'uploaded', 'inspected', 'processing', 'completed', 'failed'
    
    -- File paths in Supabase Storage
    ap_upload_path TEXT,           -- Path to uploaded AP Excel file in 'uploads' bucket
    hold_upload_path TEXT,         -- Path to uploaded Hold List Excel in 'uploads' bucket
    output_path TEXT,              -- Path to generated output Excel in 'outputs' bucket
    
    -- Processing metadata (stored as JSONB for flexibility)
    detected_schema_json JSONB,    -- Column names/types detected from uploaded AP file
    suggested_mapping_json JSONB,  -- AI-suggested column mappings (if any)
    confirmed_mapping_json JSONB,  -- User-confirmed column mappings
    format_config_json JSONB,      -- Format preferences (date formats, etc.)
    run_summary_json JSONB,        -- Summary: row counts, reconciliation, missing accounts
    
    -- Error handling
    error_message TEXT             -- Error details if status='failed'
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_upload_date ON runs(upload_date DESC);

-- Comment on table
COMMENT ON TABLE runs IS 'Tracks each AP processing run with metadata, file paths, and audit information';


