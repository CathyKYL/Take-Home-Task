# Inspection logic for uploaded AP Excel files
# Detects schema, provides preview, and suggests column mappings using deterministic fuzzy matching

import io
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from rapidfuzz import fuzz, process


class InspectError(Exception):
    """Custom exception for inspection errors"""
    pass


# Known field candidates for fuzzy matching
FIELD_CANDIDATES = {
    "account_name": [
        "servicer: account name",
        "account name",
        "payee",
        "vendor",
        "supplier"
    ],
    "created_date": [
        "created date",
        "date created",
        "created_at"
    ],
    "modified_date": [
        "last modified date",
        "modified date",
        "updated_at",
        "date modified"
    ]
}


def normalize_column_name(column: str) -> str:
    """
    Normalize column name for fuzzy matching.
    
    Args:
        column: Original column name
        
    Returns:
        str: Normalized column name (lowercase, stripped)
    """
    if column is None:
        return ""
    return str(column).strip().lower()


def fuzzy_match_column(
    column_name: str,
    candidates: List[str],
    threshold: int = 60
) -> List[Tuple[str, float, str]]:
    """
    Find best matching candidates for a column name using fuzzy matching.
    
    Args:
        column_name: Column name to match
        candidates: List of candidate patterns to match against
        threshold: Minimum similarity score (0-100)
        
    Returns:
        List of tuples: (candidate, score, confidence_level)
        Sorted by score descending, returns top 3 matches
    """
    normalized = normalize_column_name(column_name)
    
    if not normalized:
        return []
    
    # Use rapidfuzz to find best matches
    matches = process.extract(
        normalized,
        candidates,
        scorer=fuzz.ratio,
        limit=3
    )
    
    results = []
    for candidate, score, _ in matches:
        if score >= threshold:
            # Determine confidence level
            if score >= 90:
                confidence = "high"
            elif score >= 75:
                confidence = "medium"
            else:
                confidence = "low"
            
            results.append((candidate, score, confidence))
    
    return results


def suggest_mapping_for_field(
    field_name: str,
    columns: List[str],
    candidates: List[str]
) -> Dict[str, Any]:
    """
    Suggest the best column mapping for a required field.
    
    Args:
        field_name: Required field name (e.g., "account_name")
        columns: List of actual column names from the Excel file
        candidates: List of candidate patterns to match
        
    Returns:
        dict: Mapping suggestion with top matches
    """
    all_matches = []
    
    # Score each column against all candidates
    for col in columns:
        normalized_col = normalize_column_name(col)
        
        # Check exact match first
        if normalized_col in [normalize_column_name(c) for c in candidates]:
            return {
                "field": field_name,
                "suggested_column": col,
                "confidence": "high",
                "score": 100.0,
                "reason": "Exact match found",
                "alternatives": []
            }
        
        # Fuzzy match against all candidates
        for candidate in candidates:
            score = fuzz.ratio(normalized_col, normalize_column_name(candidate))
            if score >= 60:  # Threshold
                all_matches.append({
                    "column": col,
                    "candidate": candidate,
                    "score": score
                })
    
    # Sort by score descending
    all_matches.sort(key=lambda x: x["score"], reverse=True)
    
    if not all_matches:
        return {
            "field": field_name,
            "suggested_column": None,
            "confidence": None,
            "score": 0.0,
            "reason": "No matching column found",
            "alternatives": []
        }
    
    # Best match
    best = all_matches[0]
    
    # Determine confidence
    if best["score"] >= 90:
        confidence = "high"
    elif best["score"] >= 75:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Get alternatives (top 3)
    alternatives = []
    for match in all_matches[1:4]:  # Get next 3
        alt_confidence = "high" if match["score"] >= 90 else "medium" if match["score"] >= 75 else "low"
        alternatives.append({
            "column": match["column"],
            "confidence": alt_confidence,
            "score": match["score"]
        })
    
    return {
        "field": field_name,
        "suggested_column": best["column"],
        "confidence": confidence,
        "score": best["score"],
        "reason": f"Fuzzy match with '{best['candidate']}' (similarity: {best['score']:.0f}%)",
        "alternatives": alternatives
    }


def inspect_ap_excel(ap_bytes: bytes) -> Dict[str, Any]:
    """
    Inspect uploaded AP Excel file and extract schema, preview, and mapping suggestions.
    
    This function performs READ-ONLY inspection - no data transformation or cleaning.
    
    Args:
        ap_bytes: Excel file content as bytes
        
    Returns:
        dict: Inspection results containing:
            - sheet_names: List of sheet names
            - selected_sheet: Name of the sheet being inspected
            - columns: List of original column names
            - normalized_columns: List of normalized column names
            - total_rows: Total number of data rows
            - preview_rows: First 15 rows as JSON-serializable records
            - mapping_suggestions: Suggested mappings for known fields
            
    Raises:
        InspectError: If inspection fails
    """
    try:
        # Read Excel file from bytes
        excel_file = io.BytesIO(ap_bytes)
        
        # Get all sheet names
        xl_file = pd.ExcelFile(excel_file)
        sheet_names = xl_file.sheet_names
        
        if not sheet_names:
            raise InspectError("No sheets found in Excel file")
        
        # Read first sheet
        selected_sheet = sheet_names[0]
        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
        
        if df.empty:
            raise InspectError(f"Sheet '{selected_sheet}' is empty")
        
        # Extract column headers (original)
        columns = df.columns.tolist()
        
        # Normalize column names for matching
        normalized_columns = [normalize_column_name(col) for col in columns]
        
        # Get total rows (excluding header)
        total_rows = len(df)
        
        # Get preview rows (first 15)
        preview_df = df.head(15)
        
        # Convert to JSON-serializable records
        # Handle NaN, NaT, and other non-serializable values
        preview_rows = []
        for _, row in preview_df.iterrows():
            record = {}
            for col in columns:
                value = row[col]
                
                # Handle pandas NA types
                if pd.isna(value):
                    record[col] = None
                # Handle datetime
                elif pd.api.types.is_datetime64_any_dtype(type(value)):
                    record[col] = value.isoformat() if not pd.isna(value) else None
                # Handle numeric types
                elif isinstance(value, (pd.Int64Dtype, pd.Float64Dtype)) or \
                     pd.api.types.is_numeric_dtype(type(value)):
                    record[col] = None if pd.isna(value) else float(value) if isinstance(value, float) else int(value)
                else:
                    record[col] = str(value) if value is not None else None
            
            preview_rows.append(record)
        
        # Generate mapping suggestions for known fields
        mapping_suggestions = {}
        suggested_mapping = {}
        
        for field_name, candidates in FIELD_CANDIDATES.items():
            suggestion = suggest_mapping_for_field(field_name, columns, candidates)
            mapping_suggestions[field_name] = suggestion
            
            # Build simple suggested_mapping dict
            if suggestion["suggested_column"]:
                suggested_mapping[field_name] = suggestion["suggested_column"]
        
        # Build result
        result = {
            "sheet_names": sheet_names,
            "selected_sheet": selected_sheet,
            "columns": columns,
            "normalized_columns": normalized_columns,
            "total_rows": total_rows,
            "preview_rows": preview_rows,
            "mapping_suggestions": mapping_suggestions,
            "suggested_mapping": suggested_mapping
        }
        
        return result
        
    except InspectError:
        raise
    except Exception as e:
        raise InspectError(f"Failed to inspect Excel file: {str(e)}")


def get_column_info(ap_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extract detailed column information including data types and sample values.
    
    Args:
        ap_bytes: Excel file content as bytes
        
    Returns:
        List of dicts with column information (name, data_type, sample_values, null_count, total_count)
        
    Raises:
        InspectError: If extraction fails
    """
    try:
        excel_file = io.BytesIO(ap_bytes)
        xl_file = pd.ExcelFile(excel_file)
        sheet_name = xl_file.sheet_names[0]
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        column_info = []
        
        for col in df.columns:
            # Determine data type
            dtype = df[col].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                data_type = "number"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                data_type = "date"
            elif pd.api.types.is_bool_dtype(dtype):
                data_type = "boolean"
            else:
                data_type = "string"
            
            # Get sample values (first 3 non-null)
            sample_values = []
            non_null_values = df[col].dropna()
            for val in non_null_values.head(3):
                if pd.api.types.is_datetime64_any_dtype(type(val)):
                    sample_values.append(val.isoformat())
                elif isinstance(val, (int, float)):
                    sample_values.append(float(val) if isinstance(val, float) else int(val))
                else:
                    sample_values.append(str(val))
            
            # Count nulls
            null_count = int(df[col].isna().sum())
            total_count = len(df)
            
            column_info.append({
                "name": col,
                "data_type": data_type,
                "sample_values": sample_values,
                "null_count": null_count,
                "total_count": total_count
            })
        
        return column_info
        
    except Exception as e:
        raise InspectError(f"Failed to extract column info: {str(e)}")


def load_hold_list_names(hold_bytes: bytes) -> List[str]:
    """
    Extract account names from hold list Excel file.
    
    Args:
        hold_bytes: Hold list Excel file as bytes
        
    Returns:
        List of normalized hold names
        
    Raises:
        InspectError: If hold list cannot be read
    """
    try:
        hold_file = io.BytesIO(hold_bytes)
        hold_df = pd.read_excel(hold_file, sheet_name=0)
        
        if hold_df.empty:
            return []
        
        # Try to find the account name column (first column or best match)
        account_column = hold_df.columns[0]
        for col in hold_df.columns:
            col_lower = str(col).lower()
            if 'account' in col_lower or 'name' in col_lower or 'vendor' in col_lower:
                account_column = col
                break
        
        # Extract unique names, normalize and filter out empty
        hold_names = hold_df[account_column].dropna().unique().tolist()
        hold_names = [normalize_name(str(name)) for name in hold_names if name]
        
        return hold_names
        
    except Exception as e:
        raise InspectError(f"Failed to load hold list: {str(e)}")


def normalize_name(name: str) -> str:
    """Normalize account name for matching"""
    if not name:
        return ""
    # Remove extra whitespace, convert to lowercase
    return " ".join(str(name).strip().lower().split())


def find_unmatched_holds(
    ap_account_names: List[str],
    hold_list_names: List[str],
    threshold: int = 80
) -> List[str]:
    """
    Find hold list names that aren't found in AP file using fuzzy matching.
    
    Args:
        ap_account_names: List of account names from AP file
        hold_list_names: List of names from hold list
        threshold: Minimum fuzzy match score (0-100) to consider a match
        
    Returns:
        List of hold names not found in AP file
    """
    if not hold_list_names:
        return []
    
    if not ap_account_names:
        return hold_list_names
    
    # Normalize all AP names
    normalized_ap_names = [normalize_name(name) for name in ap_account_names]
    
    unmatched = []
    for hold_name in hold_list_names:
        normalized_hold = normalize_name(hold_name)
        
        # Check if any AP name matches this hold name
        found_match = False
        for ap_name in normalized_ap_names:
            score = fuzz.ratio(normalized_hold, ap_name)
            if score >= threshold:
                found_match = True
                break
        
        if not found_match:
            unmatched.append(hold_name)
    
    return unmatched


def extract_unique_field_values(ap_bytes: bytes, max_values_per_field: int = 100) -> Dict[str, List[str]]:
    """
    Extract unique values for each field in AP file (for dropdown options).
    
    Args:
        ap_bytes: AP Excel file as bytes
        max_values_per_field: Maximum number of unique values to return per field
        
    Returns:
        Dict mapping field name to list of unique values
    """
    try:
        ap_file = io.BytesIO(ap_bytes)
        xl_file = pd.ExcelFile(ap_file)
        
        if not xl_file.sheet_names:
            return {}
        
        df = pd.read_excel(ap_file, sheet_name=xl_file.sheet_names[0])
        
        if df.empty:
            return {}
        
        field_values = {}
        for column in df.columns:
            # Get unique non-null values
            unique_vals = df[column].dropna().unique()
            
            # Convert to strings and sort
            str_vals = [str(v) for v in unique_vals if v]
            str_vals = sorted(str_vals)[:max_values_per_field]
            
            field_values[column] = str_vals
        
        return field_values
        
    except Exception as e:
        raise InspectError(f"Failed to extract field values: {str(e)}")



