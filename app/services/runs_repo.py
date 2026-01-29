# Runs repository
# Database operations for the runs table

from typing import Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
from supabase import Client
from .supabase_client import get_client


class RunsRepoError(Exception):
    """Custom exception for runs repository operations"""
    pass


def create_run(upload_date: date) -> Dict[str, Any]:
    """
    Create a new run record in the database.
    
    Args:
        upload_date: Date to be used for stamping output files
        
    Returns:
        dict: Created run record with id, created_at, upload_date, status
        
    Raises:
        RunsRepoError: If creation fails
    """
    try:
        client: Client = get_client()
        
        # Insert new run record
        response = client.table("runs").insert({
            "upload_date": upload_date.isoformat(),
            "status": "uploaded"
        }).execute()
        
        if not response.data or len(response.data) == 0:
            raise RunsRepoError("Failed to create run: no data returned")
        
        return response.data[0]
        
    except RunsRepoError:
        raise
    except Exception as e:
        raise RunsRepoError(f"Failed to create run: {str(e)}")


def get_run_by_id(run_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Retrieve a run record by ID.
    
    Args:
        run_id: UUID of the run
        
    Returns:
        dict: Run record, or None if not found
        
    Raises:
        RunsRepoError: If query fails
    """
    try:
        client: Client = get_client()
        
        response = client.table("runs").select("*").eq("id", str(run_id)).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        return response.data[0]
        
    except Exception as e:
        raise RunsRepoError(f"Failed to get run {run_id}: {str(e)}")


def update_run(run_id: UUID, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a run record with new values.
    
    Args:
        run_id: UUID of the run to update
        updates: Dictionary of fields to update
        
    Returns:
        dict: Updated run record
        
    Raises:
        RunsRepoError: If update fails or run not found
    """
    try:
        client: Client = get_client()
        
        # Ensure JSON fields are properly serialized
        for key in ['detected_schema_json', 'suggested_mapping_json', 
                    'confirmed_mapping_json', 'format_config_json', 'run_summary_json']:
            if key in updates and updates[key] is not None:
                # Supabase Python client handles JSON serialization automatically
                pass
        
        response = client.table("runs").update(updates).eq("id", str(run_id)).execute()
        
        if not response.data or len(response.data) == 0:
            raise RunsRepoError(f"Run not found: {run_id}")
        
        return response.data[0]
        
    except RunsRepoError:
        raise
    except Exception as e:
        raise RunsRepoError(f"Failed to update run {run_id}: {str(e)}")


def update_run_status(run_id: UUID, status: str, error_message: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the status of a run (convenience method).
    
    Args:
        run_id: UUID of the run
        status: New status value
        error_message: Optional error message if status is 'failed'
        
    Returns:
        dict: Updated run record
        
    Raises:
        RunsRepoError: If update fails
    """
    updates = {"status": status}
    
    if error_message is not None:
        updates["error_message"] = error_message
    
    return update_run(run_id, updates)


def update_run_paths(
    run_id: UUID,
    ap_upload_path: Optional[str] = None,
    hold_upload_path: Optional[str] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update file paths for a run (convenience method).
    
    Args:
        run_id: UUID of the run
        ap_upload_path: Path to AP file in storage
        hold_upload_path: Path to Hold List file in storage
        output_path: Path to output file in storage
        
    Returns:
        dict: Updated run record
        
    Raises:
        RunsRepoError: If update fails
    """
    updates = {}
    
    if ap_upload_path is not None:
        updates["ap_upload_path"] = ap_upload_path
    if hold_upload_path is not None:
        updates["hold_upload_path"] = hold_upload_path
    if output_path is not None:
        updates["output_path"] = output_path
    
    return update_run(run_id, updates)


def save_detected_schema(run_id: UUID, schema_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save detected schema from uploaded file (convenience method).
    
    Args:
        run_id: UUID of the run
        schema_json: Detected schema as dictionary
        
    Returns:
        dict: Updated run record
        
    Raises:
        RunsRepoError: If update fails
    """
    return update_run(run_id, {
        "detected_schema_json": schema_json,
        "status": "inspected"
    })


def save_mapping(
    run_id: UUID,
    confirmed_mapping: Dict[str, str],
    format_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save user-confirmed mapping and format config (convenience method).
    
    Args:
        run_id: UUID of the run
        confirmed_mapping: User-confirmed column mappings
        format_config: Format configuration (date formats, etc.)
        
    Returns:
        dict: Updated run record
        
    Raises:
        RunsRepoError: If update fails
    """
    return update_run(run_id, {
        "confirmed_mapping_json": confirmed_mapping,
        "format_config_json": format_config
    })


def save_run_summary(
    run_id: UUID,
    run_summary: Dict[str, Any],
    output_path: str
) -> Dict[str, Any]:
    """
    Save processing summary and mark run as completed (convenience method).
    
    Args:
        run_id: UUID of the run
        run_summary: Processing summary with row counts, reconciliation, etc.
        output_path: Path to generated output file
        
    Returns:
        dict: Updated run record
        
    Raises:
        RunsRepoError: If update fails
    """
    return update_run(run_id, {
        "run_summary_json": run_summary,
        "output_path": output_path,
        "status": "completed"
    })


def mark_run_failed(run_id: UUID, error_message: str) -> Dict[str, Any]:
    """
    Mark a run as failed with error message (convenience method).
    
    Args:
        run_id: UUID of the run
        error_message: Error description
        
    Returns:
        dict: Updated run record
        
    Raises:
        RunsRepoError: If update fails
    """
    return update_run(run_id, {
        "status": "failed",
        "error_message": error_message
    })


