// API Client for backend communication
// Uses relative paths for same-origin requests (frontend and backend served from same domain)
// In development, configure Next.js proxy or run both servers
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

// Types for API responses
export interface Run {
  run_id: string
  status: string
  created_at: string
}

export interface InspectResponse {
  run_id: string
  status: string
  detected_columns?: any[]
  total_rows?: number
  required_fields?: string[]
  suggested_mapping?: Record<string, string | null>
  suggestions?: any[]
  preview_data?: any[]
  unmatched_hold_names?: string[]
  available_ap_values?: Record<string, string[]>
  // Legacy fields (for backward compatibility with mock data)
  unmatched_payments?: string[]
  available_ap_names?: string[]
  warnings?: string[]
  counts?: {
    total_payments: number
    matched: number
    unmatched: number
    holds: number
    unique_ap_accounts?: number
    total_hold_names?: number
  }
  column_mappings?: {
    account_name?: string
    created_date?: string
    modified_date?: string
  }
  preview_rows?: any[]
}

export interface AuditTrailEntry {
  timestamp: string
  action: string
  details: string
  user?: string
  affected_rows?: number
}

export interface DownloadResponse {
  excel_file_url: string
  pdf_file_url?: string
  audit_trail_url?: string
  summary?: {
    total_payments?: number
    matched?: number
    unmatched?: number
    holds?: number
  }
  audit_trail?: AuditTrailEntry[]
}

export interface ApiError {
  error: string
  detail?: string
}

// Helper function to handle API errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `Error: ${response.status} ${response.statusText}`
    
    try {
      const errorData: ApiError = await response.json()
      errorMessage = errorData.error || errorData.detail || errorMessage
    } catch {
      // If error response is not JSON, use status text
    }
    
    throw new Error(errorMessage)
  }
  
  return response.json()
}

/**
 * Create a new run
 * POST /runs
 */
export async function createRun(): Promise<Run> {
  try {
    const response = await fetch(`${API_BASE_URL}/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    return handleResponse<Run>(response)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to create run: ${error.message}`)
    }
    throw new Error('Failed to create run: Unknown error')
  }
}

/**
 * Upload files to a run
 * POST /runs/{runId}/upload (multipart)
 */
export async function uploadFiles(
  runId: string,
  apFile: File,
  holdFile: File,
  processingDate?: string
): Promise<{ message: string }> {
  try {
    const formData = new FormData()
    formData.append('ap_file', apFile)
    formData.append('hold_file', holdFile)
    
    if (processingDate) {
      formData.append('processing_date', processingDate)
    }
    
    const response = await fetch(`${API_BASE_URL}/runs/${runId}/upload`, {
      method: 'POST',
      body: formData,
    })
    
    return handleResponse<{ message: string }>(response)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to upload files: ${error.message}`)
    }
    throw new Error('Failed to upload files: Unknown error')
  }
}

/**
 * Inspect a run (check for issues, get unmatched items)
 * GET /runs/{runId}/inspect
 */
export async function inspectRun(runId: string): Promise<InspectResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/runs/${runId}/inspect`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    return handleResponse<InspectResponse>(response)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to inspect run: ${error.message}`)
    }
    throw new Error('Failed to inspect run: Unknown error')
  }
}

export interface ManualHoldMapping {
  hold_name: string
  field: string
  value: string
}

export interface AccountingPeriodAdjustment {
  enabled: boolean
  cutoff_date: string | null  // YYYY-MM-DD format - dates before this will be modified
  new_date: string | null  // YYYY-MM-DD format - what to change old dates to
  apply_to_tabs: string[]  // 'ready_to_pay' | 'payment_on_hold'
  columns_to_check: string[]  // 'created_date' | 'modified_date'
}

export interface MappingPayload {
  mapping: Record<string, string>  // e.g., { account_name: "Account Name" }
  format_config?: Record<string, any>
  manual_hold_mappings?: ManualHoldMapping[]
  accounting_period_adjustment?: AccountingPeriodAdjustment
}

/**
 * Save manual mapping overrides
 * POST /runs/{runId}/mapping
 */
export async function saveMapping(
  runId: string,
  mappingPayload: MappingPayload
): Promise<{ message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/runs/${runId}/mapping`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(mappingPayload),
    })
    
    return handleResponse<{ message: string }>(response)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to save mapping: ${error.message}`)
    }
    throw new Error('Failed to save mapping: Unknown error')
  }
}

/**
 * Run the processing workflow
 * POST /runs/{runId}/run
 */
export async function runProcessing(runId: string): Promise<{ message: string; status: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/runs/${runId}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    return handleResponse<{ message: string; status: string }>(response)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to run processing: ${error.message}`)
    }
    throw new Error('Failed to run processing: Unknown error')
  }
}

/**
 * Get download links for processed files
 * GET /runs/{runId}/download
 */
export async function getDownload(runId: string): Promise<DownloadResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/runs/${runId}/download`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    return handleResponse<DownloadResponse>(response)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to get download links: ${error.message}`)
    }
    throw new Error('Failed to get download links: Unknown error')
  }
}

