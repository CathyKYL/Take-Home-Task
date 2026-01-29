'use client'

import { useState, useEffect } from 'react'
import FileUploadBox from './FileUploadBox'
import { createRun, uploadFiles } from '@/lib/api'

interface UploadStepProps {
  onNext: (runId: string) => void
  onError: (error: string) => void
}

export default function UploadStep({ onNext, onError }: UploadStepProps) {
  const [apFile, setApFile] = useState<File | null>(null)
  const [holdFile, setHoldFile] = useState<File | null>(null)
  const [processingDate, setProcessingDate] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  // Set default date to today on mount
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0]
    setProcessingDate(today)
  }, [])

  const bothFilesSelected = apFile !== null && holdFile !== null

  const handleNext = async () => {
    if (!bothFilesSelected || !apFile || !holdFile) return

    setIsLoading(true)
    
    try {
      // Step 1: Create a new run
      const run = await createRun()
      
      // Step 2: Upload files
      await uploadFiles(run.run_id, apFile, holdFile, processingDate)
      
      // Step 3: Move to inspecting step
      onNext(run.run_id)
    } catch (error) {
      if (error instanceof Error) {
        onError(error.message)
      } else {
        onError('An unexpected error occurred during upload')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      {/* Input Files Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Input Files</h3>

        {/* Vendor Payment Excel File */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Vendor Payment Excel File <span className="text-red-500">*</span>
          </label>
          <FileUploadBox
            file={apFile}
            onFileSelect={setApFile}
            accept=".xlsx,.xls,.xlsm"
          />
        </div>

        {/* Payment Hold List File */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Payment Hold List File <span className="text-red-500">*</span>
          </label>
          <FileUploadBox
            file={holdFile}
            onFileSelect={setHoldFile}
            accept=".xlsx,.xls,.xlsm"
          />
        </div>

        <p className="text-xs text-gray-500">
          Accepted formats: .xlsx, .xls, .xlsm &lt;size: 10MB
        </p>
      </div>

      {/* Parameters Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Parameters</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Processing Date
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Date to use for processing (default is today's date)
          </p>
          <input
            type="date"
            value={processingDate}
            onChange={(e) => setProcessingDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Validation Warning */}
      {!bothFilesSelected && (
        <div className="mb-4 p-3 bg-gray-50 border border-gray-300 rounded-md">
          <p className="text-sm text-gray-700">
            Both files are required to proceed
          </p>
        </div>
      )}

      {/* Next Button */}
      <button
        onClick={handleNext}
        disabled={!bothFilesSelected || isLoading}
        className={`w-full py-3 px-6 rounded-md font-medium transition-colors flex items-center justify-center gap-2 ${
          bothFilesSelected && !isLoading
            ? 'bg-gray-900 text-white hover:bg-gray-800'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-5 w-5 text-white"
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
            Uploading...
          </>
        ) : (
          'Start Processing'
        )}
      </button>

      {/* Ready Status */}
      {bothFilesSelected && (
        <div className="mt-4 flex items-center justify-center gap-2">
          <div className="w-5 h-5 bg-gray-900 rounded-full flex items-center justify-center">
            <svg
              className="w-3 h-3 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <span className="text-sm text-gray-900 font-medium">
            Ready to Process
          </span>
        </div>
      )}
    </div>
  )
}

