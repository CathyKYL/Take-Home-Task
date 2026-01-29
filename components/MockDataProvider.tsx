// Mock data for testing without backend
import { InspectResponse } from '@/lib/api'

export const MOCK_INSPECT_DATA: InspectResponse = {
  run_id: 'mock-run-123',
  status: 'completed',
  counts: {
    total_payments: 150,
    matched: 120,
    unmatched: 10,
    holds: 20,
    unique_ap_accounts: 45,
    total_hold_names: 15
  },
  column_mappings: {
    account_name: 'Account Name',
    created_date: 'Created',
    modified_date: 'Last Modified Date'
  },
  preview_rows: [
    {
      'Account Name': 'Acme Corporation',
      'Amount': 1500.00,
      'Created': '2026-01-15',
      'Invoice Number': 'INV-001',
      'Case Number': '12345'
    },
    {
      'Account Name': 'XYZ Industries',
      'Amount': 2500.00,
      'Created': '2026-01-16',
      'Invoice Number': 'INV-002',
      'Case Number': '12346'
    },
    {
      'Account Name': 'ACME LLC',
      'Amount': 750.00,
      'Created': '2026-01-17',
      'Invoice Number': 'INV-003',
      'Case Number': '12347'
    }
  ],
  unmatched_payments: ['ACME LLC', 'ABC Industries', 'Tech Solutions Inc'],
  available_ap_names: [
    'Acme Corporation',
    'Acme, LLC',
    'XYZ Industries',
    'XYZ Corp',
    'Tech Solutions',
    'ABC Industries Inc'
  ],
  warnings: [
    'Date format inconsistency detected in 3 rows',
    'Some account names may need manual matching'
  ]
}

export const MOCK_DOWNLOAD_DATA = {
  excel_file_url: 'https://example.com/mock-download.xlsx',
  pdf_file_url: 'https://example.com/mock-report.pdf',
  audit_trail_url: 'https://example.com/mock-audit.json',
  summary: {
    total_payments: 150,
    matched: 120,
    unmatched: 10,
    holds: 20
  },
  audit_trail: [
    {
      timestamp: '2026-01-29T14:30:00Z',
      action: 'File Upload',
      details: 'Uploaded AP file: Example_AP_run_data.xlsx (150 rows)',
      affected_rows: 150
    },
    {
      timestamp: '2026-01-29T14:30:05Z',
      action: 'Column Detection',
      details: "Detected Account Name column: 'Account Name'"
    },
    {
      timestamp: '2026-01-29T14:30:30Z',
      action: 'Vendor Name Mapping',
      details: "Mapped 'ACME LLC' → 'Acme, LLC'",
      affected_rows: 5
    },
    {
      timestamp: '2026-01-29T14:30:31Z',
      action: 'Forced Hold Rule',
      details: "Force hold on Case Number = '12345'",
      affected_rows: 3
    },
    {
      timestamp: '2026-01-29T14:30:45Z',
      action: 'Hold Detection',
      details: 'Matched 120 payments to hold list',
      affected_rows: 120
    },
    {
      timestamp: '2026-01-29T14:30:46Z',
      action: 'Override Applied',
      details: 'Applied 2 vendor name mappings',
      affected_rows: 8
    },
    {
      timestamp: '2026-01-29T14:30:47Z',
      action: 'Split Processing',
      details: 'Split into: 130 proceed, 20 on hold',
      affected_rows: 150
    },
    {
      timestamp: '2026-01-29T14:30:50Z',
      action: 'Processing Complete',
      details: 'Generated output files successfully'
    }
  ]
}

