# Processing logic for AP Excel files
# Splits data into Ready_To_Pay and Payment_On_Hold based on hold list matching

import io
from typing import Dict, Any, Tuple, Optional, Set, List
from datetime import date
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


class ProcessError(Exception):
    """Custom exception for processing errors"""
    pass


def normalize_for_matching(value: Any) -> str:
    """
    Normalize a value for matching purposes only.
    Does NOT modify the original value.
    
    Args:
        value: Value to normalize
        
    Returns:
        str: Normalized string (lowercase, stripped)
    """
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().lower()


def load_hold_list(hold_bytes: Optional[bytes]) -> Tuple[Set[str], List[str]]:
    """
    Load hold list from Excel file into a set of normalized strings for matching
    and a list of original values for output.
    
    Args:
        hold_bytes: Hold list Excel file as bytes (optional)
        
    Returns:
        Tuple of (normalized_set, original_values_list)
        - normalized_set: Set of normalized strings for matching
        - original_values_list: List of original values for Hold_List output
        
    Raises:
        ProcessError: If hold list cannot be loaded
    """
    if hold_bytes is None:
        return set(), []
    
    try:
        hold_file = io.BytesIO(hold_bytes)
        
        # Read first sheet
        xl_file = pd.ExcelFile(hold_file)
        if not xl_file.sheet_names:
            return set(), []
        
        hold_df = pd.read_excel(hold_file, sheet_name=xl_file.sheet_names[0])
        
        if hold_df.empty:
            return set(), []
        
        # Extract all values from first column
        hold_set = set()
        original_values = []
        first_column = hold_df.iloc[:, 0]
        
        for value in first_column:
            # Skip null values
            if pd.isna(value):
                continue
            
            # Store original value
            original_value = str(value).strip() if value else None
            if original_value:
                original_values.append(original_value)
                
                # Normalize for matching
                normalized = normalize_for_matching(value)
                if normalized:
                    hold_set.add(normalized)
        
        return hold_set, original_values
        
    except Exception as e:
        raise ProcessError(f"Failed to load hold list: {str(e)}")


def check_on_hold(row: pd.Series, account_column: str, hold_set: Set[str]) -> bool:
    """
    Check if a row should be on hold based on account name matching.
    Uses normalized matching but does NOT modify original values.
    
    Args:
        row: DataFrame row
        account_column: Name of the account column to check
        hold_set: Set of normalized hold list values
        
    Returns:
        bool: True if row is on hold, False otherwise
    """
    if not hold_set:
        return False
    
    if account_column not in row.index:
        return False
    
    account_value = row[account_column]
    normalized_value = normalize_for_matching(account_value)
    
    return normalized_value in hold_set


def process_run(
    ap_bytes: bytes,
    hold_bytes: Optional[bytes],
    mapping: Dict[str, str],
    format_config: Dict[str, Any],
    upload_date: date,
    manual_hold_mappings: List[Dict[str, str]] = None
) -> Tuple[bytes, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process AP Excel file: split into Ready_To_Pay and Payment_On_Hold,
    stamp dates, and generate output Excel.
    
    CRITICAL: Only modifies Created Date and Last Modified Date columns.
    All other data remains unchanged.
    
    Args:
        ap_bytes: AP Excel file as bytes
        hold_bytes: Hold list Excel file as bytes (optional)
        mapping: Confirmed column mapping (required_field -> actual_column)
        format_config: Format configuration (not used yet, reserved for future)
        upload_date: Date to stamp in Created/Modified date columns (date only)
        manual_hold_mappings: Manual mappings for unmatched hold names (optional)
        
    Returns:
        Tuple of (output_excel_bytes, run_summary_dict, audit_entries)
        
    Raises:
        ProcessError: If processing fails or required columns are missing
    """
    from datetime import datetime
    
    # Initialize audit trail
    audit_entries = []
    
    try:
        # Step 1: Read AP file into raw_df
        ap_file = io.BytesIO(ap_bytes)
        xl_file = pd.ExcelFile(ap_file)
        
        if not xl_file.sheet_names:
            raise ProcessError("No sheets found in AP file")
        
        # Read first sheet - this is our raw data
        raw_df = pd.read_excel(ap_file, sheet_name=xl_file.sheet_names[0])
        
        if raw_df.empty:
            raise ProcessError("AP file is empty")
        
        # Audit: File loaded
        audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": "File Loaded",
            "action_type": "file_load",
            "details": f"Loaded AP file with {len(raw_df)} transactions from sheet '{xl_file.sheet_names[0]}'",
            "rows_affected": len(raw_df)
        })
        
        # Step 2: Copy raw_df to working_df (for splitting)
        # Use copy() to ensure we don't modify raw_df
        working_df = raw_df.copy()
        
        # Step 3: Load hold list into a set (for matching) and list (for output)
        hold_set, original_hold_values = load_hold_list(hold_bytes)
        
        # Audit: Hold list loaded
        if hold_bytes:
            audit_entries.append({
                "timestamp": datetime.now().isoformat(),
                "action": "Hold List Loaded",
                "action_type": "hold_load",
                "details": f"Loaded hold list with {len(hold_set)} unique vendors",
                "rows_affected": len(hold_set)
            })
        
        # Step 4: Validate required mapping
        if "account_name" not in mapping:
            raise ProcessError("Missing required mapping: 'account_name' must be provided in mapping")
        
        account_column = mapping["account_name"]
        
        # Verify the mapped column exists in the data
        if account_column not in working_df.columns:
            raise ProcessError(f"Mapped column '{account_column}' not found in AP file. Available columns: {list(working_df.columns)}")
        
        # Step 5: Determine which rows are on hold
        # Use normalized matching but DO NOT modify original values
        on_hold_mask = working_df.apply(
            lambda row: check_on_hold(row, account_column, hold_set),
            axis=1
        )
        
        # Step 5.5: Apply manual hold mappings (if any)
        manual_hold_count = 0
        if manual_hold_mappings:
            for mapping_rule in manual_hold_mappings:
                field_name = mapping_rule.get("field")
                field_value = mapping_rule.get("value")
                
                # Check if the field exists in the DataFrame
                if field_name and field_value and field_name in working_df.columns:
                    # Mark rows with matching field value as on hold
                    manual_hold_mask = working_df[field_name].astype(str) == str(field_value)
                    manual_hold_count += manual_hold_mask.sum()
                    on_hold_mask = on_hold_mask | manual_hold_mask
            
            # Audit: Manual mappings applied
            if manual_hold_count > 0:
                audit_entries.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "Override Applied",
                    "action_type": "manual_mapping",
                    "details": f"Applied {len(manual_hold_mappings)} manual vendor mappings, affecting {manual_hold_count} additional transactions",
                    "rows_affected": manual_hold_count
                })
        
        # Step 6: Split into ready_df and hold_df
        ready_df = working_df[~on_hold_mask].copy()
        hold_df = working_df[on_hold_mask].copy()
        
        # Audit: Hold detection complete
        audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": "Hold Detection",
            "action_type": "hold_detection",
            "details": f"Matched {len(hold_df)} payments to hold list",
            "rows_affected": len(hold_df)
        })
        
        # Audit: Split processing
        audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": "Split Processing",
            "action_type": "split_processing",
            "details": f"Split into: {len(ready_df)} ready to pay, {len(hold_df)} on hold",
            "rows_affected": len(raw_df)
        })
        
        # Step 7: Handle Created Date and Last Modified Date columns
        # Determine column names to use
        created_col = mapping.get("created_date", "Created Date")
        modified_col = mapping.get("modified_date", "Last Modified Date")
        
        # If mapped columns don't exist, create them with exact names
        if created_col not in ready_df.columns:
            created_col = "Created Date"
        if modified_col not in ready_df.columns:
            modified_col = "Last Modified Date"
        
        # Set date values (date only, no time) for Ready_To_Pay
        ready_df[created_col] = upload_date
        ready_df[modified_col] = upload_date
        
        # Set date values (date only, no time) for Payment_On_Hold
        hold_df[created_col] = upload_date
        hold_df[modified_col] = upload_date
        
        # Audit: Date stamping
        total_stamped = len(ready_df) + len(hold_df)
        audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": "Date Stamping",
            "action_type": "date_stamp",
            "details": f"Stamped '{created_col}' and '{modified_col}' with {upload_date} on {total_stamped} transactions",
            "rows_affected": total_stamped
        })
        
        # Step 8: Prepare Hold_List tab (use ORIGINAL values, not normalized)
        if original_hold_values:
            # Create a simple DataFrame from the original hold values
            hold_list_df = pd.DataFrame(original_hold_values, columns=["Hold List Values"])
        else:
            hold_list_df = pd.DataFrame(columns=["Hold List Values"])
        
        # Step 9: Calculate run summary for auditability
        total_raw_rows = len(raw_df)
        ready_to_pay_rows = len(ready_df)
        payment_on_hold_rows = len(hold_df)
        hold_list_rows = len(hold_list_df)
        
        # Reconciliation check: Ready + Hold must equal Raw
        reconciliation_valid = (ready_to_pay_rows + payment_on_hold_rows) == total_raw_rows
        
        if reconciliation_valid:
            reconciliation_message = f"Ready_To_Pay ({ready_to_pay_rows}) + Payment_On_Hold ({payment_on_hold_rows}) = Raw ({total_raw_rows}). ✓"
        else:
            reconciliation_message = f"RECONCILIATION FAILED: Ready_To_Pay ({ready_to_pay_rows}) + Payment_On_Hold ({payment_on_hold_rows}) != Raw ({total_raw_rows})"
        
        # Count missing account names
        missing_account_name_count = int(working_df[account_column].isna().sum())
        
        run_summary = {
            "total_raw_rows": total_raw_rows,
            "ready_to_pay_rows": ready_to_pay_rows,
            "payment_on_hold_rows": payment_on_hold_rows,
            "hold_list_rows": hold_list_rows,
            "reconciliation_valid": reconciliation_valid,
            "reconciliation_message": reconciliation_message,
            "missing_account_name_count": missing_account_name_count
        }
        
        # Step 10: Write output Excel with 4 tabs
        output_bytes = write_output_excel(
            ready_df=ready_df,
            hold_df=hold_df,
            hold_list_df=hold_list_df,
            raw_df=raw_df
        )
        
        # Audit: Processing complete
        audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": "Processing Complete",
            "action_type": "processing_complete",
            "details": "Generated output Excel file with 4 tabs: Ready_To_Pay, Payment_On_Hold, Hold_List, Raw",
            "rows_affected": None
        })
        
        return output_bytes, run_summary, audit_entries
        
    except ProcessError:
        raise
    except Exception as e:
        raise ProcessError(f"Processing failed: {str(e)}")


def write_output_excel(
    ready_df: pd.DataFrame,
    hold_df: pd.DataFrame,
    hold_list_df: pd.DataFrame,
    raw_df: pd.DataFrame
) -> bytes:
    """
    Write output Excel file with exactly 4 tabs in order:
    Ready_To_Pay, Payment_On_Hold, Hold_List, Raw
    
    Args:
        ready_df: Ready to pay transactions
        hold_df: Transactions on hold
        hold_list_df: Hold list values
        raw_df: Raw data (unchanged)
        
    Returns:
        bytes: Excel file as bytes
        
    Raises:
        ProcessError: If Excel generation fails
    """
    try:
        output = io.BytesIO()
        
        # Use openpyxl engine for better control
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Tab 1: Ready_To_Pay
            ready_df.to_excel(writer, sheet_name='Ready_To_Pay', index=False)
            
            # Tab 2: Payment_On_Hold
            hold_df.to_excel(writer, sheet_name='Payment_On_Hold', index=False)
            
            # Tab 3: Hold_List
            hold_list_df.to_excel(writer, sheet_name='Hold_List', index=False)
            
            # Tab 4: Raw (unchanged)
            raw_df.to_excel(writer, sheet_name='Raw', index=False)
        
        output.seek(0)
        return output.read()
        
    except Exception as e:
        raise ProcessError(f"Failed to write output Excel: {str(e)}")


def validate_mapping(mapping: Dict[str, str], columns: list) -> None:
    """
    Validate that all mapped columns exist in the data.
    
    Args:
        mapping: Column mapping dictionary
        columns: List of actual column names
        
    Raises:
        ProcessError: If any mapped column is missing
    """
    missing_columns = []
    
    for field, column_name in mapping.items():
        if column_name not in columns:
            missing_columns.append(f"{field} -> '{column_name}'")
    
    if missing_columns:
        raise ProcessError(
            f"Mapping validation failed. The following mapped columns were not found in the file:\n"
            f"{', '.join(missing_columns)}\n"
            f"Available columns: {', '.join(columns)}"
        )

