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
    upload_date: date
) -> Tuple[bytes, Dict[str, Any]]:
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
        
    Returns:
        Tuple of (output_excel_bytes, run_summary_dict)
        
    Raises:
        ProcessError: If processing fails or required columns are missing
    """
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
        
        # Step 2: Copy raw_df to working_df (for splitting)
        # Use copy() to ensure we don't modify raw_df
        working_df = raw_df.copy()
        
        # Step 3: Load hold list into a set (for matching) and list (for output)
        hold_set, original_hold_values = load_hold_list(hold_bytes)
        
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
        
        # Step 6: Split into ready_df and hold_df
        ready_df = working_df[~on_hold_mask].copy()
        hold_df = working_df[on_hold_mask].copy()
        
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
        
        return output_bytes, run_summary
        
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

