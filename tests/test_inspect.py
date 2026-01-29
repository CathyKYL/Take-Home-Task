# Tests for inspect functionality

import pytest
from app.processing import inspect_ap_excel, InspectError


class TestInspect:
    """Test suite for inspection functionality."""
    
    def test_inspect_returns_correct_structure(self, ap_excel_bytes):
        """Test that inspect returns all required fields."""
        result = inspect_ap_excel(ap_excel_bytes)
        
        # Verify all required keys are present
        assert "sheet_names" in result
        assert "selected_sheet" in result
        assert "columns" in result
        assert "normalized_columns" in result
        assert "total_rows" in result
        assert "preview_rows" in result
        assert "mapping_suggestions" in result
        assert "suggested_mapping" in result
    
    def test_inspect_detects_correct_row_count(self, ap_excel_bytes, sample_ap_data):
        """Test that inspect correctly counts rows."""
        result = inspect_ap_excel(ap_excel_bytes)
        
        assert result["total_rows"] == len(sample_ap_data)
    
    def test_inspect_preview_limited_to_15_rows(self, ap_excel_bytes):
        """Test that preview is limited to first 15 rows."""
        result = inspect_ap_excel(ap_excel_bytes)
        
        # Our sample has 5 rows, so preview should have 5
        assert len(result["preview_rows"]) <= 15
        assert len(result["preview_rows"]) == 5  # Our sample size
    
    def test_inspect_suggests_account_name_mapping(self, ap_excel_bytes):
        """Test that inspect suggests mapping for account name."""
        result = inspect_ap_excel(ap_excel_bytes)
        
        # Should suggest "Vendor Name" for account_name field
        assert "account_name" in result["mapping_suggestions"]
        suggestion = result["mapping_suggestions"]["account_name"]
        
        assert suggestion["suggested_column"] == "Vendor Name"
        assert suggestion["confidence"] in ["high", "medium", "low"]
    
    def test_inspect_does_not_modify_data(self, ap_excel_bytes):
        """
        CRITICAL: Inspect must not modify any data.
        Preview rows should contain original values.
        """
        result = inspect_ap_excel(ap_excel_bytes)
        
        # Check first preview row has expected original values
        first_row = result["preview_rows"][0]
        
        assert first_row["Vendor Name"] == "ACME Corp"
        assert first_row["Invoice Number"] == "INV-001"
        assert first_row["Amount"] == 1500.0


