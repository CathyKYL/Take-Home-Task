# API routes for runs endpoints
# Implements the complete workflow: create -> upload -> inspect -> mapping -> process -> download

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID
import io

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

from app.models import (
    CreateRunRequest,
    CreateRunResponse,
    UploadResponse,
    InspectResponse,
    ColumnInfo,
    MappingSuggestion,
    MappingRequest,
    MappingResponse,
    ProcessRequest,
    ProcessResponse,
    RunSummary,
    DownloadResponse,
    ErrorResponse,
)
from app.services import (
    create_run,
    get_run_by_id,
    update_run,
    update_run_paths,
    save_detected_schema,
    save_mapping,
    save_run_summary,
    mark_run_failed,
    upload_bytes,
    download_bytes,
    create_signed_url,
    RunsRepoError,
    StorageError,
)
from app.processing import (
    inspect_ap_excel,
    get_column_info,
    load_hold_list_names,
    find_unmatched_holds,
    extract_unique_field_values,
    process_run,
    InspectError,
    ProcessError,
)


router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=CreateRunResponse, status_code=201)
async def create_new_run(request: CreateRunRequest = None):
    """
    Create a new processing run.
    
    Sets upload_date to today's UTC date if not provided.
    Initial status is 'uploaded' (ready for file upload).
    """
    try:
        # Use provided upload_date or default to today UTC
        if request and request.upload_date:
            upload_date = request.upload_date
        else:
            upload_date = date.today()
        
        # Create run in database
        run_record = create_run(upload_date=upload_date)
        
        return CreateRunResponse(
            run_id=UUID(run_record["id"]),
            upload_date=run_record["upload_date"],
            status=run_record["status"],
            created_at=run_record["created_at"]
        )
        
    except RunsRepoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create run: {str(e)}")


@router.post("/{run_id}/upload", response_model=UploadResponse)
async def upload_files(
    run_id: UUID,
    ap_file: UploadFile = File(..., description="AP Excel file"),
    hold_file: Optional[UploadFile] = File(None, description="Hold List Excel file (optional)")
):
    """
    Upload AP and optional Hold List files to Supabase Storage.
    
    Files are stored in the 'uploads' bucket under the run_id path.
    Updates run status to 'uploaded'.
    """
    try:
        # Verify run exists
        run_record = get_run_by_id(run_id)
        if not run_record:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        
        # Read AP file
        ap_content = await ap_file.read()
        ap_filename = ap_file.filename or "ap_file.xlsx"
        
        # Upload AP file to storage
        ap_path = f"{run_id}/{ap_filename}"
        upload_bytes(
            bucket="uploads",
            path=ap_path,
            content_bytes=ap_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Upload hold file if provided
        hold_path = None
        if hold_file:
            hold_content = await hold_file.read()
            hold_filename = hold_file.filename or "hold_list.xlsx"
            hold_path = f"{run_id}/{hold_filename}"
            upload_bytes(
                bucket="uploads",
                path=hold_path,
                content_bytes=hold_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Update run record with paths and status
        update_run_paths(
            run_id=run_id,
            ap_upload_path=ap_path,
            hold_upload_path=hold_path
        )
        
        update_run(run_id, {"status": "uploaded"})
        
        return UploadResponse(
            run_id=run_id,
            status="uploaded",
            ap_upload_path=ap_path,
            hold_upload_path=hold_path,
            message="Files uploaded successfully"
        )
        
    except HTTPException:
        raise
    except StorageError as e:
        await mark_run_failed(run_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except RunsRepoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        await mark_run_failed(run_id, str(e))
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{run_id}/inspect", response_model=InspectResponse)
async def inspect_run(run_id: UUID):
    """
    Inspect uploaded AP file: detect schema, provide preview, suggest mappings.
    
    Downloads AP file from storage, analyzes it, and stores results in database.
    Updates run status to 'inspected'.
    """
    try:
        # Get run record
        run_record = get_run_by_id(run_id)
        if not run_record:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        
        # Verify AP file was uploaded
        ap_path = run_record.get("ap_upload_path")
        if not ap_path:
            raise HTTPException(
                status_code=400,
                detail="No AP file uploaded. Please upload files first."
            )
        
        # Download AP file from storage
        ap_bytes = download_bytes(bucket="uploads", path=ap_path)
        
        # Inspect the file
        inspection_result = inspect_ap_excel(ap_bytes)
        
        # Get detailed column info
        column_info_list = get_column_info(ap_bytes)
        
        # Check for unmatched hold names (if hold list was uploaded)
        unmatched_hold_names = []
        available_ap_values = {}
        hold_path = run_record.get("hold_upload_path")
        
        if hold_path:
            try:
                # Download hold list
                hold_bytes = download_bytes(bucket="uploads", path=hold_path)
                
                # Extract hold list names
                hold_list_names = load_hold_list_names(hold_bytes)
                
                # Get account name column from suggested mapping
                account_column = inspection_result["suggested_mapping"].get("account_name")
                
                if account_column and account_column in inspection_result["columns"]:
                    # Extract AP account names from preview rows
                    ap_account_names = []
                    for row in inspection_result["preview_rows"]:
                        if account_column in row and row[account_column]:
                            ap_account_names.append(str(row[account_column]))
                    
                    # Find unmatched holds
                    unmatched_hold_names = find_unmatched_holds(
                        ap_account_names=ap_account_names,
                        hold_list_names=hold_list_names
                    )
                    
                    # If there are unmatched holds, extract unique field values for manual mapping
                    if unmatched_hold_names:
                        available_ap_values = extract_unique_field_values(ap_bytes)
                        
            except Exception as e:
                # Don't fail the whole inspect if hold checking fails
                print(f"Warning: Could not check for unmatched holds: {str(e)}")
        
        # Build detected schema to store
        detected_schema = {
            "sheet_names": inspection_result["sheet_names"],
            "selected_sheet": inspection_result["selected_sheet"],
            "columns": inspection_result["columns"],
            "normalized_columns": inspection_result["normalized_columns"],
            "total_rows": inspection_result["total_rows"],
            "column_info": column_info_list
        }
        
        # Build suggested mapping to store
        suggested_mapping = {
            "mapping_suggestions": inspection_result["mapping_suggestions"],
            "suggested_mapping": inspection_result["suggested_mapping"]
        }
        
        # Store in database
        save_detected_schema(run_id, detected_schema)
        update_run(run_id, {
            "suggested_mapping_json": suggested_mapping,
            "status": "inspected"
        })
        
        # Build response
        column_info_models = [
            ColumnInfo(**col_info) for col_info in column_info_list
        ]
        
        mapping_suggestions = []
        for field, suggestion in inspection_result["mapping_suggestions"].items():
            mapping_suggestions.append(
                MappingSuggestion(
                    required_field=suggestion["field"],
                    suggested_column=suggestion["suggested_column"],
                    confidence=suggestion["confidence"],
                    reason=suggestion["reason"]
                )
            )
        
        # Determine required fields from FIELD_CANDIDATES
        from app.processing import FIELD_CANDIDATES
        required_fields = list(FIELD_CANDIDATES.keys())
        
        return InspectResponse(
            run_id=run_id,
            status="inspected",
            detected_columns=column_info_models,
            total_rows=inspection_result["total_rows"],
            required_fields=required_fields,
            suggested_mapping=inspection_result["suggested_mapping"],
            suggestions=mapping_suggestions,
            preview_data=inspection_result["preview_rows"],
            unmatched_hold_names=unmatched_hold_names,
            available_ap_values=available_ap_values
        )
        
    except HTTPException:
        raise
    except (InspectError, StorageError) as e:
        await mark_run_failed(run_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except RunsRepoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        await mark_run_failed(run_id, str(e))
        raise HTTPException(status_code=500, detail=f"Inspection failed: {str(e)}")


@router.post("/{run_id}/mapping", response_model=MappingResponse)
async def confirm_mapping(run_id: UUID, request: MappingRequest):
    """
    Save user-confirmed column mapping and format configuration.
    
    Validates the mapping and stores it in the database.
    Updates run status to 'mapped' (ready for processing).
    """
    try:
        # Get run record
        run_record = get_run_by_id(run_id)
        if not run_record:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        
        # Verify run has been inspected
        if run_record["status"] not in ["inspected", "mapped"]:
            raise HTTPException(
                status_code=400,
                detail=f"Run must be inspected before mapping. Current status: {run_record['status']}"
            )
        
        # Validate required fields
        if "account_name" not in request.mapping:
            raise HTTPException(
                status_code=400,
                detail="Missing required field in mapping: 'account_name'"
            )
        
        # Convert manual hold mappings to dict format
        manual_mappings_list = [
            {"hold_name": m.hold_name, "field": m.field, "value": m.value}
            for m in request.manual_hold_mappings
        ]
        
        # Save mapping to database
        save_mapping(
            run_id=run_id,
            confirmed_mapping=request.mapping,
            format_config=request.format_config or {},
            manual_hold_mappings=manual_mappings_list
        )
        
        update_run(run_id, {"status": "mapped"})
        
        return MappingResponse(
            run_id=run_id,
            status="mapped",
            confirmed_mapping=request.mapping,
            format_config=request.format_config or {},
            message="Mapping confirmed and saved"
        )
        
    except HTTPException:
        raise
    except RunsRepoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save mapping: {str(e)}")


@router.post("/{run_id}/run", response_model=ProcessResponse)
async def process_and_generate_output(run_id: UUID, request: ProcessRequest = None):
    """
    Process AP file with confirmed mapping and generate output Excel.
    
    Downloads files from storage, processes them, generates output with
    4 tabs (Ready_To_Pay, Payment_On_Hold, Hold_List, Raw), uploads to
    outputs bucket, and stores run summary.
    
    Updates run status to 'completed' on success or 'failed' on error.
    """
    try:
        # Get run record
        run_record = get_run_by_id(run_id)
        if not run_record:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        
        # Verify run has confirmed mapping
        if run_record["status"] not in ["mapped", "completed", "failed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Run must have confirmed mapping before processing. Current status: {run_record['status']}"
            )
        
        # Get required data from run record
        ap_path = run_record.get("ap_upload_path")
        hold_path = run_record.get("hold_upload_path")
        confirmed_mapping = run_record.get("confirmed_mapping_json")
        format_config = run_record.get("format_config_json") or {}
        manual_hold_mappings = run_record.get("manual_hold_mappings_json") or []
        upload_date = run_record.get("upload_date")
        
        if not ap_path:
            raise HTTPException(status_code=400, detail="No AP file found for this run")
        
        if not confirmed_mapping:
            raise HTTPException(status_code=400, detail="No confirmed mapping found")
        
        # Update status to processing
        update_run(run_id, {"status": "processing"})
        
        # Download files from storage
        ap_bytes = download_bytes(bucket="uploads", path=ap_path)
        
        hold_bytes = None
        if hold_path:
            hold_bytes = download_bytes(bucket="uploads", path=hold_path)
        
        # Convert upload_date string to date object if needed
        if isinstance(upload_date, str):
            upload_date = date.fromisoformat(upload_date)
        
        # Process the files
        import time
        start_time = time.time()
        
        output_bytes, run_summary_dict = process_run(
            ap_bytes=ap_bytes,
            hold_bytes=hold_bytes,
            mapping=confirmed_mapping,
            format_config=format_config,
            upload_date=upload_date,
            manual_hold_mappings=manual_hold_mappings
        )
        
        processing_time = time.time() - start_time
        
        # Add processing metadata to summary
        run_summary_dict["processing_time_seconds"] = round(processing_time, 2)
        run_summary_dict["output_file_size_bytes"] = len(output_bytes)
        
        # Upload output to storage
        output_path = f"{run_id}/ap_output.xlsx"
        upload_bytes(
            bucket="outputs",
            path=output_path,
            content_bytes=output_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Save run summary and mark as completed
        save_run_summary(
            run_id=run_id,
            run_summary=run_summary_dict,
            output_path=output_path
        )
        
        return ProcessResponse(
            run_id=run_id,
            status="completed",
            output_path=output_path,
            run_summary=RunSummary(**run_summary_dict),
            error_message=None
        )
        
    except HTTPException:
        raise
    except ProcessError as e:
        # Mark as failed and return error
        mark_run_failed(run_id, str(e))
        return ProcessResponse(
            run_id=run_id,
            status="failed",
            output_path=None,
            run_summary=None,
            error_message=str(e)
        )
    except (StorageError, RunsRepoError) as e:
        mark_run_failed(run_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        mark_run_failed(run_id, str(e))
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/{run_id}/download", response_model=DownloadResponse)
async def download_output(run_id: UUID):
    """
    Get signed URL for downloading the processed output Excel file.
    
    Returns a temporary signed URL that expires in 1 hour.
    """
    try:
        # Get run record
        run_record = get_run_by_id(run_id)
        if not run_record:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        
        # Verify run is completed
        if run_record["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Run is not completed. Current status: {run_record['status']}"
            )
        
        # Get output path
        output_path = run_record.get("output_path")
        if not output_path:
            raise HTTPException(status_code=404, detail="No output file found for this run")
        
        # Get file size from run summary
        run_summary = run_record.get("run_summary_json") or {}
        file_size = run_summary.get("output_file_size_bytes", 0)
        
        # Create signed URL (expires in 1 hour)
        expires_in = 3600
        signed_url = create_signed_url(
            bucket="outputs",
            path=output_path,
            expires_in=expires_in
        )
        
        # Extract filename from path
        file_name = output_path.split("/")[-1]
        
        return DownloadResponse(
            run_id=run_id,
            status=run_record["status"],
            download_url=signed_url,
            expires_in_seconds=expires_in,
            file_name=file_name,
            file_size_bytes=file_size
        )
        
    except HTTPException:
        raise
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RunsRepoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")


@router.get("/{run_id}", response_model=dict)
async def get_run_status(run_id: UUID):
    """
    Get current status and details of a run.
    
    Useful for checking run progress and retrieving stored data.
    """
    try:
        run_record = get_run_by_id(run_id)
        if not run_record:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        
        return run_record
        
    except HTTPException:
        raise
    except RunsRepoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get run: {str(e)}")



