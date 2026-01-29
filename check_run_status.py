#!/usr/bin/env python3
"""
Check the status of runs in Supabase to debug failures.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Checking recent runs in Supabase...")
print("=" * 80)

try:
    # Get last 10 runs
    response = supabase.table("runs").select("*").order("created_at", desc=True).limit(10).execute()
    
    if not response.data:
        print("No runs found in database")
        sys.exit(0)
    
    print(f"\nFound {len(response.data)} recent runs:\n")
    
    for i, run in enumerate(response.data, 1):
        print(f"\n{'='*80}")
        print(f"Run #{i}")
        print(f"{'='*80}")
        print(f"  ID: {run['id']}")
        print(f"  Status: {run['status']}")
        print(f"  Created: {run['created_at']}")
        print(f"  Upload Date: {run.get('upload_date', 'N/A')}")
        
        if run.get('error_message'):
            print(f"  [ERROR] {run['error_message']}")
        
        if run.get('ap_upload_path'):
            print(f"  [OK] AP File: {run['ap_upload_path']}")
        
        if run.get('hold_upload_path'):
            print(f"  [OK] Hold File: {run['hold_upload_path']}")
        
        if run.get('output_path'):
            print(f"  [OK] Output: {run['output_path']}")
        
        if run.get('audit_trail_json'):
            audit_entries = run['audit_trail_json']
            print(f"  [INFO] Audit Trail: {len(audit_entries)} entries")
        
        if run.get('audit_pdf_path'):
            print(f"  [INFO] PDF: {run['audit_pdf_path']}")
    
    # Count by status
    print(f"\n{'='*80}")
    print("Status Summary:")
    print(f"{'='*80}")
    
    statuses = {}
    for run in response.data:
        status = run['status']
        statuses[status] = statuses.get(status, 0) + 1
    
    for status, count in sorted(statuses.items()):
        icon = "[OK]" if status == "completed" else "[FAIL]" if status == "failed" else "[WAIT]"
        print(f"  {icon} {status}: {count}")
    
    print("\n")

except Exception as e:
    print(f"[ERROR] Error querying database: {e}")
    sys.exit(1)

