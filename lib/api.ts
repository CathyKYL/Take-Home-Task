// API Client for backend communication

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

// Types for API responses
export interface Run {
  run_id: string
  status: string
  created_at: string
}

export interface InspectResponse {
  run_id: string
  status: string
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

export interface MappingPayload {
  account_name_column: string
  created_date_column?: string
  modified_date_column?: string
  overrides: {
    hold_name_to_ap_name: Record<string, string>
    row_level_holds: Array<{
      match_field: string
      match_value: string
      force_on_hold: boolean
    }>
  }
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

