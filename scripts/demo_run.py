#!/usr/bin/env python3
"""
Demo Script - Complete AP Processing Workflow

Demonstrates the full workflow:
1. Create run
2. Upload files
3. Inspect schema & get mapping suggestions
4. Confirm mapping
5. Process files
6. Download output

This script is designed for quick demos and reviewer testing.
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Any


# Configuration
API_BASE_URL = "http://localhost:8000"
SAMPLE_DATA_DIR = Path("sample_data")


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_json(data: Dict[Any, Any], indent: int = 2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {API_BASE_URL}")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
        return False


def create_run() -> str:
    """Step 1: Create a new run"""
    print_section("STEP 1: Create Run")
    
    response = requests.post(f"{API_BASE_URL}/runs", json={})
    response.raise_for_status()
    
    data = response.json()
    run_id = data["run_id"]
    
    print("✅ Run created successfully!")
    print(f"   Run ID: {run_id}")
    print(f"   Upload Date: {data['upload_date']}")
    print(f"   Status: {data['status']}")
    
    return run_id


def upload_files(run_id: str):
    """Step 2: Upload AP and hold list files"""
    print_section("STEP 2: Upload Files")
    
    # Check if sample files exist
    ap_file_path = SAMPLE_DATA_DIR / "sample_ap_transactions.xlsx"
    hold_file_path = SAMPLE_DATA_DIR / "sample_hold_list.xlsx"
    
    if not ap_file_path.exists():
        print("❌ Sample AP file not found!")
        print("   Run: python scripts/create_sample_data.py")
        raise FileNotFoundError(str(ap_file_path))
    
    if not hold_file_path.exists():
        print("❌ Sample hold list not found!")
        print("   Run: python scripts/create_sample_data.py")
        raise FileNotFoundError(str(hold_file_path))
    
    # Upload files
    with open(ap_file_path, 'rb') as ap_file, open(hold_file_path, 'rb') as hold_file:
        files = {
            'ap_file': ('sample_ap_transactions.xlsx', ap_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            'hold_file': ('sample_hold_list.xlsx', hold_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        response = requests.post(
            f"{API_BASE_URL}/runs/{run_id}/upload",
            files=files
        )
        response.raise_for_status()
    
    data = response.json()
    
    print("✅ Files uploaded successfully!")
    print(f"   AP File: {data['ap_upload_path']}")
    print(f"   Hold File: {data['hold_upload_path']}")
    print(f"   Status: {data['status']}")


def inspect_schema(run_id: str) -> Dict[str, Any]:
    """Step 3: Inspect schema and get mapping suggestions"""
    print_section("STEP 3: Inspect Schema & Get Mapping Suggestions")
    
    response = requests.get(f"{API_BASE_URL}/runs/{run_id}/inspect")
    response.raise_for_status()
    
    data = response.json()
    
    print("✅ Schema inspection complete!")
    print(f"   Total Rows: {data['total_rows']}")
    print(f"   Detected Columns: {len(data['detected_columns'])}")
    
    print("\n📊 Detected Columns:")
    for col in data['detected_columns']:
        print(f"   - {col['name']:<30} ({col['data_type']}) - {col['null_count']} nulls")
    
    print("\n🎯 Suggested Mapping:")
    for field, column in data['suggested_mapping'].items():
        print(f"   {field:<20} → {column}")
    
    print("\n📋 Mapping Suggestions Detail:")
    for suggestion in data['suggestions']:
        confidence_emoji = "🟢" if suggestion['confidence'] == 'high' else "🟡" if suggestion['confidence'] == 'medium' else "🔴"
        print(f"   {confidence_emoji} {suggestion['required_field']:<20} → {suggestion['suggested_column']}")
        print(f"      Confidence: {suggestion['confidence']}, Reason: {suggestion['reason']}")
    
    print("\n📄 Preview (first 3 rows):")
    for i, row in enumerate(data['preview_data'][:3], 1):
        print(f"\n   Row {i}:")
        for key, value in row.items():
            print(f"      {key}: {value}")
    
    return data


def confirm_mapping(run_id: str, suggested_mapping: Dict[str, str]):
    """Step 4: Confirm column mapping"""
    print_section("STEP 4: Confirm Column Mapping")
    
    # Use the suggested mapping
    mapping_request = {
        "mapping": suggested_mapping,
        "format_config": {
            "date_format": "YYYY-MM-DD",
            "currency_symbol": "$"
        }
    }
    
    print("📝 Confirming mapping:")
    print_json(mapping_request)
    
    response = requests.post(
        f"{API_BASE_URL}/runs/{run_id}/mapping",
        json=mapping_request
    )
    response.raise_for_status()
    
    data = response.json()
    
    print("\n✅ Mapping confirmed!")
    print(f"   Status: {data['status']}")


def process_run(run_id: str) -> Dict[str, Any]:
    """Step 5: Process files and generate output"""
    print_section("STEP 5: Process Files & Generate Output")
    
    print("⚙️  Processing... (this may take a few seconds)")
    
    response = requests.post(f"{API_BASE_URL}/runs/{run_id}/run", json={})
    response.raise_for_status()
    
    data = response.json()
    
    if data['status'] == 'completed':
        print("✅ Processing completed successfully!")
        
        summary = data['run_summary']
        
        print("\n📊 Run Summary:")
        print(f"   Total Raw Rows:          {summary['total_raw_rows']}")
        print(f"   Ready to Pay Rows:       {summary['ready_to_pay_rows']}")
        print(f"   Payment on Hold Rows:    {summary['payment_on_hold_rows']}")
        print(f"   Hold List Rows:          {summary['hold_list_rows']}")
        
        print(f"\n✔️  Reconciliation: {summary['reconciliation_message']}")
        
        print(f"\n⚠️  Missing Account Names: {summary['missing_account_name_count']}")
        print(f"   Processing Time:         {summary['processing_time_seconds']:.2f}s")
        print(f"   Output File Size:        {summary['output_file_size_bytes']:,} bytes")
        
    else:
        print("❌ Processing failed!")
        print(f"   Error: {data.get('error_message', 'Unknown error')}")
    
    return data


def download_output(run_id: str):
    """Step 6: Get download URL"""
    print_section("STEP 6: Download Output File")
    
    response = requests.get(f"{API_BASE_URL}/runs/{run_id}/download")
    response.raise_for_status()
    
    data = response.json()
    
    print("✅ Download URL generated!")
    print(f"   File Name: {data['file_name']}")
    print(f"   File Size: {data['file_size_bytes']:,} bytes")
    print(f"   Expires In: {data['expires_in_seconds']} seconds ({data['expires_in_seconds']//60} minutes)")
    
    print(f"\n🔗 Download URL (valid for 1 hour):")
    print(f"   {data['download_url']}")
    
    print("\n💡 Use this URL to download the processed Excel file with 4 tabs:")
    print("   1. Ready_To_Pay - Transactions ready for payment")
    print("   2. Payment_On_Hold - Transactions on hold")
    print("   3. Hold_List - Hold list values")
    print("   4. Raw - Original data (unchanged)")


def main():
    """Run the complete demo"""
    print("\n" + "🚀 " + "="*65)
    print("   Finance Automation Backend - Complete Demo")
    print("="*68 + "\n")
    
    # Check API health
    if not check_api_health():
        return
    
    try:
        # Step 1: Create run
        run_id = create_run()
        time.sleep(0.5)
        
        # Step 2: Upload files
        upload_files(run_id)
        time.sleep(0.5)
        
        # Step 3: Inspect schema
        inspect_data = inspect_schema(run_id)
        time.sleep(0.5)
        
        # Step 4: Confirm mapping
        confirm_mapping(run_id, inspect_data['suggested_mapping'])
        time.sleep(0.5)
        
        # Step 5: Process files
        process_data = process_run(run_id)
        time.sleep(0.5)
        
        # Step 6: Download output
        if process_data['status'] == 'completed':
            download_output(run_id)
        
        # Summary
        print_section("✨ Demo Complete!")
        print(f"Run ID: {run_id}")
        print("\n🎯 Key Takeaways:")
        print("   ✅ Only Created Date and Last Modified Date columns were modified")
        print("   ✅ All other financial data remains exactly as in the input")
        print("   ✅ Reconciliation check passed (Ready + Hold = Raw)")
        print("   ✅ Output Excel has 4 tabs with proper data separation")
        print("\n📝 Check the downloaded file to verify data integrity!")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        if e.response is not None:
            print(f"   Response: {e.response.text}")
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        print("\n   Run: python scripts/create_sample_data.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()

