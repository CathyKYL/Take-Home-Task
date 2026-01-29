# External service integrations
# Handles Supabase Storage (uploads/outputs buckets) and Postgres (runs table) operations

from .supabase_client import get_client, get_supabase_client
from .storage_service import (
    upload_bytes,
    download_bytes,
    create_signed_url,
    delete_file,
    get_public_url,
    StorageError,
)
from .runs_repo import (
    create_run,
    get_run_by_id,
    update_run,
    update_run_status,
    update_run_paths,
    save_detected_schema,
    save_mapping,
    save_run_summary,
    save_audit_trail,
    mark_run_failed,
    RunsRepoError,
)

__all__ = [
    # Client
    "get_client",
    "get_supabase_client",
    # Storage
    "upload_bytes",
    "download_bytes",
    "create_signed_url",
    "delete_file",
    "get_public_url",
    "StorageError",
    # Runs repository
    "create_run",
    "get_run_by_id",
    "update_run",
    "update_run_status",
    "update_run_paths",
    "save_detected_schema",
    "save_mapping",
    "save_run_summary",
    "save_audit_trail",
    "mark_run_failed",
    "RunsRepoError",
]

