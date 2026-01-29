'use client'

import { useState, useEffect } from 'react'
import { getDownload, DownloadResponse, AuditTrailEntry } from '@/lib/api'

interface DownloadStepProps {
  runId: string
  onReset: () => void
}

export default function DownloadStep({ runId, onReset }: DownloadStepProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [downloadData, setDownloadData] = useState<DownloadResponse | null>(null)

  useEffect(() => {
    const fetchDownloadLinks = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Real API call
        const data = await getDownload(runId)
        setDownloadData(data)
        setIsLoading(false)
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message)
        } else {
          setError('Failed to fetch download links')
        }
        setIsLoading(false)
      }
    }

    fetchDownloadLinks()
  }, [runId])

  const handleDownload = (url: string, filename: string) => {
    window.open(url, '_blank')
  }

  if (isLoading) {
    return (
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Processing Complete</h2>
        
        <div className="flex flex-col items-center justify-center py-12">
          <svg
            className="animate-spin h-16 w-16 text-blue-600 mb-6"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          
          <p className="text-gray-700 font-medium text-lg mb-2">Preparing Download...</p>
          <p className="text-gray-500 text-sm">Please wait...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Download Error</h2>
        
        <div className="mb-6 p-6 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-start gap-4">
            <svg
              className="w-8 h-8 text-red-600 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                Unable to Fetch Download Links
              </h3>
              <p className="text-sm text-red-700 mb-4">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium"
              >
                Retry
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={onReset}
          className="bg-gray-200 text-gray-700 px-6 py-3 rounded-md hover:bg-gray-300 transition-colors"
        >
          Start Over
        </button>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">
        Processing Complete
      </h2>

      {/* Success Banner */}
      <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
        <div className="flex items-center gap-3">
          <svg
            className="w-8 h-8 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="flex-1">
            <h3 className="text-base font-semibold text-green-800">
              Processing Completed Successfully
            </h3>
            <p className="text-sm text-green-700">
              Your files are ready for download.
            </p>
          </div>
        </div>
      </div>

      {/* Download Links */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Download Output Files</h3>
        
        <div className="space-y-3">
          {/* Excel File Download */}
          {downloadData?.excel_file_url && (
            <button
              onClick={() => handleDownload(downloadData.excel_file_url, 'output.xlsx')}
              className="w-full p-4 bg-white border-2 border-blue-300 rounded-lg hover:bg-blue-50 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-7 h-7 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="font-semibold text-gray-800">Excel Output File</p>
                  <p className="text-sm text-gray-600">Processed AP run with reconciliation</p>
                </div>
              </div>
              <svg
                className="w-6 h-6 text-blue-600 group-hover:translate-x-1 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            </button>
          )}

          {/* PDF File Download (if available) */}
          {downloadData?.pdf_file_url && (
            <button
              onClick={() => handleDownload(downloadData.pdf_file_url!, 'output.pdf')}
              className="w-full p-4 bg-white border-2 border-red-300 rounded-lg hover:bg-red-50 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-7 h-7 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="font-semibold text-gray-800">PDF Report</p>
                  <p className="text-sm text-gray-600">Printable reconciliation report</p>
                </div>
              </div>
              <svg
                className="w-6 h-6 text-red-600 group-hover:translate-x-1 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            </button>
          )}

          {/* Audit Trail Download (if file available) */}
          {downloadData?.audit_trail_url && (
            <button
              onClick={() => handleDownload(downloadData.audit_trail_url!, 'audit_trail.json')}
              className="w-full p-4 bg-white border-2 border-purple-300 rounded-lg hover:bg-purple-50 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-7 h-7 text-purple-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="font-semibold text-gray-800">Audit Trail</p>
                  <p className="text-sm text-gray-600">Complete processing audit log</p>
                </div>
              </div>
              <svg
                className="w-6 h-6 text-purple-600 group-hover:translate-x-1 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Audit Trail Display */}
      {downloadData?.audit_trail && downloadData.audit_trail.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-700">
              Audit Trail ({downloadData.audit_trail.length} entries)
            </h3>
            <span className="text-xs text-gray-500">
              All processing actions and overrides applied
            </span>
          </div>
          
          <div className="bg-white border border-gray-300 rounded-lg overflow-hidden">
            <div className="max-h-96 overflow-y-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                      Timestamp
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                      Action
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                      Details
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase">
                      Rows Affected
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {downloadData.audit_trail.map((entry, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                        {formatTimestamp(entry.timestamp)}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionColor(entry.action)}`}>
                          {entry.action}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-800">
                        {entry.details}
                      </td>
                      <td className="px-4 py-3 text-sm text-center text-gray-600">
                        {entry.affected_rows !== undefined ? entry.affected_rows : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-3 p-3 bg-gray-50 rounded-md border border-gray-200">
            <div className="flex items-start gap-2">
              <svg
                className="w-4 h-4 text-gray-600 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-xs text-gray-600">
                This audit trail shows all actions taken during processing, including manual mappings and overrides. 
                No raw data was modified - all changes were applied as processing rules.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onReset}
          className="flex-1 bg-gray-200 text-gray-700 px-6 py-3 rounded-md hover:bg-gray-300 transition-colors font-medium"
        >
          Process Another File
        </button>
      </div>
    </div>
  )
}

// Helper function to format timestamp
function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return timestamp
  }
}

// Helper function to get color based on action type
function getActionColor(action: string): string {
  const actionLower = action.toLowerCase()
  
  if (actionLower.includes('upload') || actionLower.includes('start')) {
    return 'bg-blue-100 text-blue-800'
  }
  if (actionLower.includes('mapping') || actionLower.includes('override')) {
    return 'bg-purple-100 text-purple-800'
  }
  if (actionLower.includes('process') || actionLower.includes('split')) {
    return 'bg-green-100 text-green-800'
  }
  if (actionLower.includes('hold') || actionLower.includes('force')) {
    return 'bg-red-100 text-red-800'
  }
  if (actionLower.includes('match')) {
    return 'bg-yellow-100 text-yellow-800'
  }
  if (actionLower.includes('complete') || actionLower.includes('finish')) {
    return 'bg-green-100 text-green-800'
  }
  
  return 'bg-gray-100 text-gray-800'
}

