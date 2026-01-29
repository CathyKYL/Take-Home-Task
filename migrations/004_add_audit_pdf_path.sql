-- Migration: Add audit PDF path column to runs table
-- This stores the path to the generated PDF audit trail report

ALTER TABLE runs 
ADD COLUMN IF NOT EXISTS audit_pdf_path TEXT;

-- Add documentation
COMMENT ON COLUMN runs.audit_pdf_path IS 'Path to the PDF audit trail report in outputs bucket';

