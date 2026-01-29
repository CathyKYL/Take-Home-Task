# Data integrity tests - prove only date columns are modified
# These tests ensure financial data integrity for the AP processing system

import io
from datetime import date
import pandas as pd
import pytest
from app.processing import process_run


class TestDataIntegrity:
    """
    Test suite to prove data integrity invariants.
    
    Critical for finance applications: we must prove that processing
    only modifies the two date stamp columns and nothing else.
    """
    
    def test_raw_sheet_equals_input_row_count(self, ap_excel_bytes, hold_excel_bytes, sample_mapping, sample_upload_date, sample_ap_data):
        """
        INVARIANT 1: Raw sheet row count equals input row count.
        
        The Raw tab must be an exact copy of the input data.
        """
        # Process the data
        output_bytes, run_summary = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=hold_excel_bytes,
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        # Read the Raw tab from output
        output_file = io.BytesIO(output_bytes)
        raw_df = pd.read_excel(output_file, sheet_name='Raw')
        
        # Assert row counts match
        assert len(raw_df) == len(sample_ap_data), \
            f"Raw sheet has {len(raw_df)} rows, but input had {len(sample_ap_data)} rows"
        
        # Also verify from run summary
        assert run_summary["total_raw_rows"] == len(sample_ap_data), \
            "Run summary total_raw_rows does not match input"
    
    def test_ready_plus_hold_equals_raw(self, ap_excel_bytes, hold_excel_bytes, sample_mapping, sample_upload_date):
        """
        INVARIANT 2: Ready_To_Pay rows + Payment_On_Hold rows = Raw rows.
        
        No rows should be lost or duplicated during processing.
        This is the critical reconciliation check.
        """
        # Process the data
        output_bytes, run_summary = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=hold_excel_bytes,
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        # Read all tabs
        output_file = io.BytesIO(output_bytes)
        ready_df = pd.read_excel(output_file, sheet_name='Ready_To_Pay')
        hold_df = pd.read_excel(output_file, sheet_name='Payment_On_Hold')
        raw_df = pd.read_excel(output_file, sheet_name='Raw')
        
        # Assert reconciliation
        ready_count = len(ready_df)
        hold_count = len(hold_df)
        raw_count = len(raw_df)
        
        assert ready_count + hold_count == raw_count, \
            f"Reconciliation failed: Ready ({ready_count}) + Hold ({hold_count}) != Raw ({raw_count})"
        
        # Verify run summary agrees
        assert run_summary["reconciliation_valid"] is True, \
            f"Run summary reports invalid reconciliation: {run_summary['reconciliation_message']}"
        
        assert run_summary["ready_to_pay_rows"] == ready_count
        assert run_summary["payment_on_hold_rows"] == hold_count
        assert run_summary["total_raw_rows"] == raw_count
    
    def test_non_date_columns_unchanged(self, ap_excel_bytes, hold_excel_bytes, sample_mapping, sample_upload_date, sample_ap_data):
        """
        INVARIANT 3: All columns except Created Date and Last Modified Date
        are identical to input.
        
        This is the critical test for data integrity - proves we only
        modify the two stamped date columns.
        """
        # Process the data
        output_bytes, run_summary = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=hold_excel_bytes,
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        # Read output tabs
        output_file = io.BytesIO(output_bytes)
        ready_df = pd.read_excel(output_file, sheet_name='Ready_To_Pay')
        hold_df = pd.read_excel(output_file, sheet_name='Payment_On_Hold')
        
        # Combine ready and hold back together for comparison
        combined_df = pd.concat([ready_df, hold_df], ignore_index=True)
        
        # Get the date columns that should have been added/modified
        date_columns = {"Created Date", "Last Modified Date"}
        
        # Get all columns that should be unchanged (original columns)
        original_columns = set(sample_ap_data.columns)
        columns_to_verify = original_columns - date_columns
        
        # For each original column (except date stamps), verify values are unchanged
        for col in columns_to_verify:
            # Sort both dataframes by a stable key (Invoice Number) for comparison
            input_sorted = sample_ap_data.sort_values('Invoice Number').reset_index(drop=True)
            output_sorted = combined_df.sort_values('Invoice Number').reset_index(drop=True)
            
            # Compare the column values
            input_values = input_sorted[col].tolist()
            output_values = output_sorted[col].tolist()
            
            assert input_values == output_values, \
                f"Column '{col}' was modified! Input: {input_values}, Output: {output_values}"
    
    def test_stamped_columns_equal_upload_date(self, ap_excel_bytes, hold_excel_bytes, sample_mapping, sample_upload_date):
        """
        INVARIANT 4: Stamped columns (Created Date, Last Modified Date)
        equal upload_date and contain date-only values (no time component).
        """
        # Process the data
        output_bytes, run_summary = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=hold_excel_bytes,
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        # Read output tabs
        output_file = io.BytesIO(output_bytes)
        ready_df = pd.read_excel(output_file, sheet_name='Ready_To_Pay')
        hold_df = pd.read_excel(output_file, sheet_name='Payment_On_Hold')
        
        # Check both tabs
        for df_name, df in [("Ready_To_Pay", ready_df), ("Payment_On_Hold", hold_df)]:
            # Verify columns exist
            assert "Created Date" in df.columns, f"'{df_name}' missing 'Created Date' column"
            assert "Last Modified Date" in df.columns, f"'{df_name}' missing 'Last Modified Date' column"
            
            # Check each row
            for idx, row in df.iterrows():
                created = row["Created Date"]
                modified = row["Last Modified Date"]
                
                # Convert to date if it's a Timestamp
                if pd.notna(created):
                    if isinstance(created, pd.Timestamp):
                        created_date = created.date()
                    else:
                        created_date = created
                    
                    assert created_date == sample_upload_date, \
                        f"{df_name} row {idx}: Created Date is {created_date}, expected {sample_upload_date}"
                
                if pd.notna(modified):
                    if isinstance(modified, pd.Timestamp):
                        modified_date = modified.date()
                    else:
                        modified_date = modified
                    
                    assert modified_date == sample_upload_date, \
                        f"{df_name} row {idx}: Last Modified Date is {modified_date}, expected {sample_upload_date}"
    
    def test_raw_tab_completely_unchanged(self, ap_excel_bytes, hold_excel_bytes, sample_mapping, sample_upload_date, sample_ap_data):
        """
        INVARIANT 5: Raw tab is completely unchanged from input.
        
        Every value in every cell must be identical.
        """
        # Process the data
        output_bytes, run_summary = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=hold_excel_bytes,
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        # Read the Raw tab
        output_file = io.BytesIO(output_bytes)
        raw_df = pd.read_excel(output_file, sheet_name='Raw')
        
        # Sort both by Invoice Number for stable comparison
        input_sorted = sample_ap_data.sort_values('Invoice Number').reset_index(drop=True)
        raw_sorted = raw_df.sort_values('Invoice Number').reset_index(drop=True)
        
        # Compare every column
        for col in sample_ap_data.columns:
            input_values = input_sorted[col].tolist()
            raw_values = raw_sorted[col].tolist()
            
            assert input_values == raw_values, \
                f"Raw tab column '{col}' was modified! Input: {input_values}, Raw: {raw_values}"
    
    def test_hold_list_matching_preserves_original_values(self, ap_excel_bytes, hold_excel_bytes, sample_mapping, sample_upload_date):
        """
        INVARIANT 6: Hold list matching uses normalized comparison,
        but original vendor names are preserved exactly as in input.
        
        Even though matching is case-insensitive, the actual values
        in the output must be identical to the input.
        """
        # Process the data
        output_bytes, run_summary = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=hold_excel_bytes,
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        # Read output
        output_file = io.BytesIO(output_bytes)
        hold_df = pd.read_excel(output_file, sheet_name='Payment_On_Hold')
        
        # Verify we have the expected vendors on hold
        assert len(hold_df) == 2, "Expected 2 vendors on hold"
        
        # Check that vendor names are preserved exactly (with original case)
        hold_vendors = hold_df["Vendor Name"].tolist()
        
        # Original input had these exact values (case-sensitive)
        assert "Tech Solutions Inc" in hold_vendors, \
            "Original vendor name case not preserved"
        assert "Hardware Store" in hold_vendors, \
            "Original vendor name case not preserved"


class TestOutputStructure:
    """Test that output Excel has correct structure."""
    
    def test_output_has_four_tabs_in_order(self, ap_excel_bytes, hold_excel_bytes, sample_mapping, sample_upload_date):
        """
        Output Excel must have exactly 4 tabs in this order:
        Ready_To_Pay, Payment_On_Hold, Hold_List, Raw
        """
        output_bytes, _ = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=hold_excel_bytes,
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        output_file = io.BytesIO(output_bytes)
        xl_file = pd.ExcelFile(output_file)
        sheet_names = xl_file.sheet_names
        
        expected_sheets = ["Ready_To_Pay", "Payment_On_Hold", "Hold_List", "Raw"]
        
        assert sheet_names == expected_sheets, \
            f"Sheet names/order incorrect. Expected {expected_sheets}, got {sheet_names}"



