#!/usr/bin/env python3
"""
Verify Supabase Setup Script

This script tests your Supabase configuration to ensure:
1. Database connection works
2. Storage buckets exist and are accessible
3. Policies are correctly configured

Run this AFTER setting up buckets and policies in Supabase Dashboard.
"""

import sys
import os
from datetime import date
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import get_client, create_run, get_run_by_id
from app.services import upload_bytes, download_bytes, create_signed_url
from app.services import StorageError, RunsRepoError

print('\n' + '='*70)
print('SUPABASE SETUP VERIFICATION')
print('='*70)

# Test 1: Database Connection
print('\n[TEST 1] Database Connection...')
try:
    client = get_client()
    print('[OK] Connected to Supabase')
except Exception as e:
    print(f'[FAIL] Failed to connect: {e}')
    print('\nCheck your .env file:')
    print('  - SUPABASE_URL should be: https://fdyenyuevcdteropgoqi.supabase.co')
    print('  - SUPABASE_KEY should be your service role key')
    sys.exit(1)

# Test 2: Create a test run in database
print('\n[TEST 2] Database Write (runs table)...')
try:
    test_run = create_run(upload_date=date.today())
    run_id = test_run['id']
    print(f'[OK] Created test run: {run_id}')
except RunsRepoError as e:
    print(f'[FAIL] Failed to create run: {e}')
    print('\nPossible issues:')
    print('  - runs table does not exist (run migration)')
    print('  - RLS is enabled without service_role policy')
    sys.exit(1)

# Test 3: Read from database
print('\n[TEST 3] Database Read (runs table)...')
try:
    retrieved_run = get_run_by_id(run_id)
    if retrieved_run:
        print(f'[OK] Retrieved test run: {run_id}')
    else:
        print('[FAIL] Could not retrieve run')
        sys.exit(1)
except Exception as e:
    print(f'[FAIL] Failed to read run: {e}')
    sys.exit(1)

# Test 4: Upload to 'uploads' bucket
print('\n[TEST 4] Storage Upload (uploads bucket)...')
try:
    test_content = b'This is a test file for verification'
    test_path = f'test/{run_id}/test.txt'
    
    upload_bytes(
        bucket='uploads',
        path=test_path,
        content_bytes=test_content,
        content_type='text/plain'
    )
    print(f'[OK] Uploaded test file to uploads bucket')
except StorageError as e:
    print(f'[FAIL] Failed to upload: {e}')
    print('\nPossible issues:')
    print('  - uploads bucket does not exist')
    print('  - No policy allowing service_role to INSERT')
    sys.exit(1)

# Test 5: Download from 'uploads' bucket
print('\n[TEST 5] Storage Download (uploads bucket)...')
try:
    downloaded = download_bytes(bucket='uploads', path=test_path)
    if downloaded == test_content:
        print('[OK] Downloaded and verified test file')
    else:
        print('[FAIL] Downloaded file does not match')
        sys.exit(1)
except StorageError as e:
    print(f'[FAIL] Failed to download: {e}')
    print('\nPossible issues:')
    print('  - No policy allowing service_role to SELECT')
    sys.exit(1)

# Test 6: Upload to 'outputs' bucket
print('\n[TEST 6] Storage Upload (outputs bucket)...')
try:
    output_path = f'test/{run_id}/output.txt'
    upload_bytes(
        bucket='outputs',
        path=output_path,
        content_bytes=b'Test output file',
        content_type='text/plain'
    )
    print('[OK] Uploaded test file to outputs bucket')
except StorageError as e:
    print(f'[FAIL] Failed to upload: {e}')
    print('\nPossible issues:')
    print('  - outputs bucket does not exist')
    print('  - No policy allowing service_role to INSERT')
    sys.exit(1)

# Test 7: Create signed URL
print('\n[TEST 7] Signed URL Generation...')
try:
    signed_url = create_signed_url(bucket='outputs', path=output_path, expires_in=60)
    if signed_url and 'token=' in signed_url:
        print('[OK] Generated signed URL')
        print(f'  URL: {signed_url[:80]}...')
    else:
        print('[FAIL] Invalid signed URL format')
        sys.exit(1)
except StorageError as e:
    print(f'[FAIL] Failed to create signed URL: {e}')
    sys.exit(1)

# Test 8: Clean up test files
print('\n[TEST 8] Cleanup...')
try:
    from app.services import delete_file
    delete_file('uploads', test_path)
    delete_file('outputs', output_path)
    print('[OK] Cleaned up test files')
except Exception as e:
    print(f'[WARNING] Could not clean up test files: {e}')
    print('  (Not critical - you can delete manually)')

print('\n' + '='*70)
print('ALL TESTS PASSED!')
print('='*70)
print('\nYour Supabase setup is complete and working correctly!')
print('\nNext steps:')
print('  1. Deploy your backend to Render/Railway')
print('  2. Build your frontend')
print('  3. Deploy to Netlify')
print('\nNote: The test run remains in your database.')
print(f'      Run ID: {run_id}')
print('      You can delete it manually if desired.')
print()

