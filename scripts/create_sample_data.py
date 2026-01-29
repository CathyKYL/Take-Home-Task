#!/usr/bin/env python3
"""
Create sample Excel files for demo purposes
Generates realistic AP transactions and hold list
"""

import pandas as pd
from pathlib import Path


def create_sample_ap_file():
    """Create sample AP transactions Excel file"""
    data = {
        "Vendor Name": [
            "ACME Corporation",
            "Tech Solutions Inc",
            "Office Supplies Ltd",
            "Global Consulting Group",
            "Hardware Store Co",
            "Software Licensing LLC",
            "Building Services Inc",
            "Marketing Agency",
            "Legal Services LLP",
            "Cloud Hosting Provider"
        ],
        "Invoice Number": [
            "INV-2026-001",
            "INV-2026-002",
            "INV-2026-003",
            "INV-2026-004",
            "INV-2026-005",
            "INV-2026-006",
            "INV-2026-007",
            "INV-2026-008",
            "INV-2026-009",
            "INV-2026-010"
        ],
        "Amount": [
            1500.00,
            2300.50,
            750.00,
            5000.00,
            320.75,
            4500.00,
            1200.00,
            3800.00,
            2500.00,
            1950.00
        ],
        "Description": [
            "Monthly office supplies",
            "Software licenses - Q1 2026",
            "Paper and printing materials",
            "Strategic advisory services",
            "Equipment repair and maintenance",
            "Annual software subscription",
            "Janitorial services - January",
            "Digital marketing campaign",
            "Legal consultation - contract review",
            "Cloud hosting - January 2026"
        ],
        "Due Date": [
            "2026-02-15",
            "2026-03-01",
            "2026-02-28",
            "2026-03-15",
            "2026-02-20",
            "2026-03-10",
            "2026-02-25",
            "2026-03-05",
            "2026-02-28",
            "2026-03-01"
        ],
        "PO Number": [
            "PO-1001",
            "PO-1002",
            "PO-1003",
            "PO-1004",
            "PO-1005",
            "PO-1006",
            "PO-1007",
            "PO-1008",
            "PO-1009",
            "PO-1010"
        ],
        "Invoice Date": [
            "2026-01-15",
            "2026-01-16",
            "2026-01-17",
            "2026-01-18",
            "2026-01-19",
            "2026-01-20",
            "2026-01-21",
            "2026-01-22",
            "2026-01-23",
            "2026-01-24"
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Create sample_data directory if it doesn't exist
    output_dir = Path("sample_data")
    output_dir.mkdir(exist_ok=True)
    
    # Save to Excel
    output_path = output_dir / "sample_ap_transactions.xlsx"
    df.to_excel(output_path, index=False, sheet_name="AP Transactions")
    
    print(f"✅ Created sample AP file: {output_path}")
    print(f"   - {len(df)} transactions")
    print(f"   - Total amount: ${df['Amount'].sum():,.2f}")
    
    return output_path


def create_sample_hold_list():
    """Create sample hold list Excel file"""
    data = {
        "Hold Vendors": [
            "Tech Solutions Inc",
            "Hardware Store Co",
            "Legal Services LLP"
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Create sample_data directory if it doesn't exist
    output_dir = Path("sample_data")
    output_dir.mkdir(exist_ok=True)
    
    # Save to Excel
    output_path = output_dir / "sample_hold_list.xlsx"
    df.to_excel(output_path, index=False, sheet_name="Hold List")
    
    print(f"✅ Created sample hold list: {output_path}")
    print(f"   - {len(df)} vendors on hold")
    print(f"   - {', '.join(df['Hold Vendors'].tolist())}")
    
    return output_path


def main():
    """Create all sample files"""
    print("🔨 Creating sample data files...\n")
    
    ap_path = create_sample_ap_file()
    hold_path = create_sample_hold_list()
    
    print("\n✨ Sample files created successfully!")
    print("\nExpected results after processing:")
    print("  - Ready to Pay: 7 transactions")
    print("  - Payment on Hold: 3 transactions")
    print("  - Total: 10 transactions")


if __name__ == "__main__":
    main()

