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
| `error_message` | TEXT | Error details if failed |

