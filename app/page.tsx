'use client'

import { useState, useEffect } from 'react'
import UploadStep from '@/components/UploadStep'
import InspectingStep from '@/components/InspectingStep'
import ConfirmStep from '@/components/ConfirmStep'
import DownloadStep from '@/components/DownloadStep'
import { InspectResponse } from '@/lib/api'
import { MOCK_INSPECT_DATA } from '@/components/MockDataProvider'

type Step = 'upload' | 'inspecting' | 'confirm' | 'download'

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>('upload')
  const [runId, setRunId] = useState<string | null>(null)
  const [inspectData, setInspectData] = useState<InspectResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [mockMode, setMockMode] = useState(false)

  // Check for mock mode in URL or localStorage
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlMock = params.get('mock') === 'true'
    const storedMock = localStorage.getItem('mockMode') === 'true'
    setMockMode(urlMock || storedMock)
  }, [])

  const getStepNumber = (step: Step): number => {
    const steps: Step[] = ['upload', 'inspecting', 'confirm', 'download']
    return steps.indexOf(step) + 1
  }

  const handleUploadComplete = (newRunId: string) => {
    setRunId(newRunId)
    setError(null)
    setCurrentStep('inspecting')
  }

  const handleInspectComplete = (data: InspectResponse) => {
    setInspectData(data)
    setError(null)
    setCurrentStep('confirm')
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
  }

  const handleReset = () => {
    setCurrentStep('upload')
    setRunId(null)
    setInspectData(null)
    setError(null)
  }

  const toggleMockMode = () => {
    const newMockMode = !mockMode
    setMockMode(newMockMode)
    localStorage.setItem('mockMode', String(newMockMode))
    if (newMockMode) {
      // Reset to upload when enabling mock mode
      handleReset()
    }
  }

  const jumpToConfirm = () => {
    if (mockMode) {
      setRunId('mock-run-123')
      setInspectData(MOCK_INSPECT_DATA)
      setCurrentStep('confirm')
      setError(null)
    }
  }

  const jumpToDownload = () => {
    if (mockMode) {
      setRunId('mock-run-123')
      setCurrentStep('download')
      setError(null)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 'upload':
        return (
          <UploadStep
            onNext={handleUploadComplete}
            onError={handleError}
          />
        )
      case 'inspecting':
        return (
          <InspectingStep
            runId={runId!}
            onNext={handleInspectComplete}
            onError={handleError}
          />
        )
      case 'confirm':
        return (
          <ConfirmStep
            runId={runId!}
            inspectData={inspectData!}
            onNext={() => setCurrentStep('download')}
            onSkip={() => setCurrentStep('download')}
          />
        )
      case 'download':
        return (
          <DownloadStep
            runId={runId!}
            onReset={handleReset}
          />
        )
      default:
        return null
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl w-full">
        <h1 className="text-3xl font-semibold text-gray-800 mb-2">
          Bill.com Processing
        </h1>
        <p className="text-gray-600 mb-6">
          Process Bill.com vendor payments and reconcile to payment holds
        </p>

        {/* Mock Mode Banner */}
        {mockMode && (
          <div className="mb-6 p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-yellow-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <span className="text-sm font-semibold text-yellow-800">
                  Mock Mode Active - Testing UI Without Backend
                </span>
              </div>
              <button
                onClick={toggleMockMode}
                className="text-xs bg-yellow-200 text-yellow-800 px-3 py-1 rounded hover:bg-yellow-300 transition-colors"
              >
                Disable
              </button>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentStep('upload')}
                className="text-xs bg-white text-gray-700 px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                Go to Upload
              </button>
              <button
                onClick={jumpToConfirm}
                className="text-xs bg-white text-gray-700 px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                Jump to Confirm
              </button>
              <button
                onClick={jumpToDownload}
                className="text-xs bg-white text-gray-700 px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                Jump to Download
              </button>
            </div>
          </div>
        )}

        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Step {getStepNumber(currentStep)} of 4
          </p>
          {!mockMode && (
            <button
              onClick={toggleMockMode}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
            >
              Enable Mock Mode
            </button>
          )}
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-start gap-3">
              <svg
                className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
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
                <h3 className="text-sm font-semibold text-red-800 mb-1">
                  Error
                </h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
        )}

        {renderStep()}
      </div>
    </main>
  )
}

