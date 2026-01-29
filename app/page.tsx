'use client'

import { useState } from 'react'
import UploadStep from '@/components/UploadStep'
import InspectingStep from '@/components/InspectingStep'
import ConfirmStep from '@/components/ConfirmStep'
import DownloadStep from '@/components/DownloadStep'
import { InspectResponse } from '@/lib/api'

type Step = 'upload' | 'inspecting' | 'confirm' | 'download'

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>('upload')
  const [runId, setRunId] = useState<string | null>(null)
  const [inspectData, setInspectData] = useState<InspectResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

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
          AP Sorting Agent
        </h1>
        <p className="text-gray-600 mb-6">
          An agent that automatically sorts your accounting records into "Ready for Payment" or "Payment Hold."
        </p>

        <div className="mb-6">
          <p className="text-sm text-gray-500">
            Step {getStepNumber(currentStep)} of 4
          </p>
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

