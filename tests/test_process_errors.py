# Tests for error handling in process function

import pytest
from app.processing import process_run, ProcessError
from datetime import date


class TestProcessErrors:
    """Test error handling and validation."""
    
    def test_missing_account_name_mapping_raises_error(self, ap_excel_bytes, hold_excel_bytes, sample_upload_date):
        """Test that missing account_name in mapping raises clear error."""
        invalid_mapping = {
            "created_date": "Created Date",
            # Missing account_name - should raise error
        }
        
        with pytest.raises(ProcessError) as exc_info:
            process_run(
                ap_bytes=ap_excel_bytes,
                hold_bytes=hold_excel_bytes,
                mapping=invalid_mapping,
                format_config={},
                upload_date=sample_upload_date
            )
        
        assert "account_name" in str(exc_info.value).lower()
    
    def test_invalid_mapped_column_raises_error(self, ap_excel_bytes, hold_excel_bytes, sample_upload_date):
        """Test that mapping to non-existent column raises clear error."""
        invalid_mapping = {
            "account_name": "NonExistentColumn",  # This column doesn't exist
        }
        
        with pytest.raises(ProcessError) as exc_info:
            process_run(
                ap_bytes=ap_excel_bytes,
                hold_bytes=hold_excel_bytes,
                mapping=invalid_mapping,
                format_config={},
                upload_date=sample_upload_date
            )
        
        error_msg = str(exc_info.value).lower()
        assert "nonexistentcolumn" in error_msg or "not found" in error_msg
    
    def test_process_works_without_hold_list(self, ap_excel_bytes, sample_mapping, sample_upload_date, sample_ap_data):
        """Test that processing works when no hold list is provided."""
        output_bytes, run_summary = process_run(
            ap_bytes=ap_excel_bytes,
            hold_bytes=None,  # No hold list
            mapping=sample_mapping,
            format_config={},
            upload_date=sample_upload_date
        )
        
        # All rows should be in Ready_To_Pay
        assert run_summary["ready_to_pay_rows"] == len(sample_ap_data)
        assert run_summary["payment_on_hold_rows"] == 0
        assert run_summary["reconciliation_valid"] is True



