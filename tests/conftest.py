# Pytest configuration and shared fixtures

import io
from datetime import date
import pandas as pd
import pytest


@pytest.fixture
def sample_ap_data():
    """
    Create synthetic AP data for testing.
    Returns a DataFrame with realistic AP transaction data.
    """
    data = {
        "Vendor Name": ["ACME Corp", "Tech Solutions Inc", "Office Supplies Ltd", "Consulting Group", "Hardware Store"],
        "Invoice Number": ["INV-001", "INV-002", "INV-003", "INV-004", "INV-005"],
        "Amount": [1500.00, 2300.50, 750.00, 5000.00, 320.75],
        "Description": ["Monthly supplies", "Software licenses", "Paper products", "Advisory services", "Equipment repair"],
        "Due Date": ["2026-02-15", "2026-03-01", "2026-02-28", "2026-03-15", "2026-02-20"],
        "PO Number": ["PO-1001", "PO-1002", "PO-1003", "PO-1004", "PO-1005"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_hold_list():
    """
    Create synthetic hold list for testing.
    Returns a DataFrame with vendor names to be put on hold.
    """
    data = {
        "Hold Vendors": ["Tech Solutions Inc", "Hardware Store"]
    }
    return pd.DataFrame(data)


@pytest.fixture
def ap_excel_bytes(sample_ap_data):
    """
    Convert sample AP data to Excel bytes.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sample_ap_data.to_excel(writer, sheet_name='Sheet1', index=False)
    output.seek(0)
    return output.read()


@pytest.fixture
def hold_excel_bytes(sample_hold_list):
    """
    Convert sample hold list to Excel bytes.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sample_hold_list.to_excel(writer, sheet_name='Sheet1', index=False)
    output.seek(0)
    return output.read()


@pytest.fixture
def sample_mapping():
    """
    Sample column mapping for testing.
    """
    return {
        "account_name": "Vendor Name",
        "created_date": "Created Date",
        "modified_date": "Last Modified Date"
    }


@pytest.fixture
def sample_upload_date():
    """
    Sample upload date for testing.
    """
    return date(2026, 1, 29)


