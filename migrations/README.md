# Database Migrations

SQL migration files for Supabase Postgres database setup.

## Running Migrations

### Option 1: Supabase Dashboard (SQL Editor)
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the migration file contents
4. Execute the SQL

### Option 2: Supabase CLI
```bash
supabase db push
```

## Migration Files

- `001_create_runs_table.sql` - Creates the main runs table for tracking AP processing operations
- `002_add_manual_hold_mappings.sql` - Adds column for manual vendor name mappings
- `003_add_audit_trail.sql` - Adds column for complete audit trail storage
- `004_add_audit_pdf_path.sql` - Adds column for PDF audit trail report path
- `005_add_date_stamping_config.sql` - Adds column for manual date stamping configuration

## Runs Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `created_at` | TIMESTAMPTZ | Run creation timestamp |
| `upload_date` | DATE | Date used for stamping output files |
| `status` | TEXT | Run status (uploaded, inspected, processing, completed, failed) |
| `ap_upload_path` | TEXT | Path to AP file in uploads bucket |
| `hold_upload_path` | TEXT | Path to Hold List file in uploads bucket |
| `output_path` | TEXT | Path to output file in outputs bucket |
| `detected_schema_json` | JSONB | Detected column schema from upload |
| `suggested_mapping_json` | JSONB | Suggested column mappings |
| `confirmed_mapping_json` | JSONB | User-confirmed mappings |
| `format_config_json` | JSONB | Format configuration |
| `run_summary_json` | JSONB | Processing summary and audit info |
| `manual_hold_mappings_json` | JSONB | Manual vendor name mappings |
| `audit_trail_json` | JSONB | Complete audit trail of all processing actions |
| `audit_pdf_path` | TEXT | Path to PDF audit trail report in outputs bucket |
| `date_stamping_config_json` | JSONB | User configuration for manual date stamping |
| `error_message` | TEXT | Error details if failed |



