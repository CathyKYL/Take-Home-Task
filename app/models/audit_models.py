# Audit Trail Models
# Pydantic models for audit trail entries and responses

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    """Single audit trail entry documenting a processing action"""
    timestamp: str  # ISO format timestamp
    action: str  # Human-readable action name (e.g., "Hold Detection")
    action_type: str  # Machine-readable action type (e.g., "hold_detection")
    details: str  # Detailed description of the action
    rows_affected: Optional[int] = None  # Number of rows affected by this action
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-01-29T14:30:31.123Z",
                "action": "Hold Detection",
                "action_type": "hold_detection",
                "details": "Matched 131 payments to hold list",
                "rows_affected": 131,
                "metadata": {"matched_vendors": 11}
            }
        }


class AuditTrail(BaseModel):
    """Complete audit trail for a processing run"""
    run_id: str
    entries: List[AuditEntry]
    total_entries: int = Field(description="Total number of audit entries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "entries": [],
                "total_entries": 5
            }
        }

