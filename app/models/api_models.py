# Pydantic models for API request/response schemas
# Defines the contract for all endpoints

from typing import Optional, Dict, List, Any
from datetime import date, datetime
from pydantic import BaseModel, Field
from uuid import UUID


# ============================================================================
# POST /runs - Create a new run
# ============================================================================

class CreateRunRequest(BaseModel):
    """Request to create a new processing run"""
    # upload_date will be set to today's UTC date by default
    upload_date: Optional[date] = None


class CreateRunResponse(BaseModel):
    """Response after creating a run"""
    run_id: UUID
    upload_date: date
    status: str  # "uploaded"
    created_at: datetime


# ============================================================================
# POST /runs/{run_id}/upload - Upload AP and Hold List files
# ============================================================================

# Request: multipart/form-data with files
# - ap_file: UploadFile (required)
# - hold_file: UploadFile (optional)

class UploadResponse(BaseModel):
    """Response after uploading files"""
    run_id: UUID
    status: str  # "uploaded"
    ap_upload_path: str
    hold_upload_path: Optional[str] = None
    message: str


# ============================================================================
# GET /runs/{run_id}/inspect - Inspect uploaded file schema and preview
# ============================================================================

class ColumnInfo(BaseModel):
    """Information about a detected column"""
    name: str
    data_type: str  # "string", "number", "date", "boolean"
    sample_values: List[Any]
    null_count: int
    total_count: int


class MappingSuggestion(BaseModel):
    """Suggested mapping for a required field"""
    required_field: str
    suggested_column: Optional[str] = None
    confidence: Optional[str] = None  # "high", "medium", "low"
    reason: Optional[str] = None


class InspectResponse(BaseModel):
    """Response from inspecting uploaded file"""
    run_id: UUID
    status: str  # "inspected"
    
    # Detected schema
    detected_columns: List[ColumnInfo]
    total_rows: int
    
    # Mapping suggestions (deterministic fuzzy match)
    required_fields: List[str]
    suggested_mapping: Dict[str, Optional[str]]  # required_field -> suggested_column
    suggestions: List[MappingSuggestion]
    
    # Preview data (first 5 rows)
    preview_data: List[Dict[str, Any]]
    
    # Unmatched hold names (for manual review in Step 3)
    unmatched_hold_names: List[str] = []
    available_ap_values: Dict[str, List[str]] = {}  # field_name -> unique values


# ============================================================================
# POST /runs/{run_id}/mapping - Save confirmed mapping and format config
# ============================================================================

class ManualHoldMapping(BaseModel):
    """Manual mapping for unmatched hold name"""
    hold_name: str
    field: str  # Column name in AP file (e.g., "Account Name", "Invoice Number")
    value: str  # Value to match in that field


class DateStampingConfig(BaseModel):
    """Configuration for manual date stamping"""
    enabled: bool = Field(
        default=False,
        description="Whether to apply date stamping"
    )
    apply_to_tabs: List[str] = Field(
        default=[],
        description="Which tabs to apply date stamping: 'ready_to_pay', 'payment_on_hold', or both"
    )
    columns_to_update: List[str] = Field(
        default=[],
        description="Which date columns to update: 'created_date', 'modified_date', or both"
    )
    stamp_date: Optional[str] = Field(
        default=None,
        description="Date to stamp in YYYY-MM-DD format"
    )


class MappingRequest(BaseModel):
    """User-confirmed column mapping and format configuration"""
    # Column mapping: required_field -> actual_column_name
    mapping: Dict[str, str] = Field(
        ...,
        description="Map required fields to actual column names from uploaded file"
    )
    
    # Format configuration
    format_config: Optional[Dict[str, Any]] = Field(
        default={},
        description="Date formats, number formats, etc."
    )
    
    # Manual hold mappings (for unmatched hold names)
    manual_hold_mappings: List[ManualHoldMapping] = Field(
        default=[],
        description="Manual mappings for hold names not auto-matched"
    )
    
    # Date stamping configuration (manual)
    date_stamping: Optional[DateStampingConfig] = Field(
        default=None,
        description="Manual date stamping preferences"
    )


class MappingResponse(BaseModel):
    """Response after saving mapping"""
    run_id: UUID
    status: str  # "inspected"
    confirmed_mapping: Dict[str, str]
    format_config: Dict[str, Any]
    message: str


# ============================================================================
# POST /runs/{run_id}/run - Process files and generate output
# ============================================================================

class ProcessRequest(BaseModel):
    """Optional parameters for processing"""
    # Reserved for future use (e.g., filters, options)
    pass


class RunSummary(BaseModel):
    """Summary of processing run for auditability"""
    total_raw_rows: int
    ready_to_pay_rows: int
    payment_on_hold_rows: int
    hold_list_rows: int
    
    # Reconciliation check
    reconciliation_valid: bool  # ready_to_pay + payment_on_hold == total_raw
    reconciliation_message: str
    
    # Missing account names
    missing_account_name_count: int
    
    # Processing metadata
    processing_time_seconds: float
    output_file_size_bytes: int


class ProcessResponse(BaseModel):
    """Response after processing run"""
    run_id: UUID
    status: str  # "completed" or "failed"
    output_path: Optional[str] = None
    run_summary: Optional[RunSummary] = None
    error_message: Optional[str] = None


# ============================================================================
# GET /runs/{run_id}/download - Get signed URL for output file
# ============================================================================

class DownloadResponse(BaseModel):
    """Response with signed download URL"""
    run_id: UUID
    status: str
    excel_file_url: str  # Main download URL (matches frontend expectation)
    pdf_file_url: Optional[str] = None  # Optional PDF report
    audit_trail_url: Optional[str] = None  # Optional audit trail file
    summary: Optional[Dict[str, Any]] = None  # Run summary stats
    audit_trail: Optional[List[Dict[str, Any]]] = None  # Audit trail entries
    
    # Additional metadata
    download_url: Optional[str] = None  # Alias for excel_file_url (deprecated)
    expires_in_seconds: Optional[int] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None


# ============================================================================
# Error responses
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    run_id: Optional[UUID] = None



