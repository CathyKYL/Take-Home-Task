'use client'

import { useState } from 'react'
import { InspectResponse, saveMapping, runProcessing, MappingPayload } from '@/lib/api'

interface ConfirmStepProps {
  runId: string
  inspectData: InspectResponse
  onNext: () => void
  onSkip: () => void
}

interface ManualHoldMapping {
  hold_name: string
  field: string
  value: string
}

export default function ConfirmStep({ runId, inspectData, onNext, onSkip }: ConfirmStepProps) {
  const [manualHoldMappings, setManualHoldMappings] = useState<ManualHoldMapping[]>([])
  const [expandedHolds, setExpandedHolds] = useState<Set<string>>(new Set())
  const [selectedFields, setSelectedFields] = useState<Record<string, string>>({})
  const [selectedValues, setSelectedValues] = useState<Record<string, string>>({})
  const [isProcessing, setIsProcessing] = useState(false)
  
  // Accounting period adjustment configuration
  const [adjustmentEnabled, setAdjustmentEnabled] = useState(false)
  const [cutoffDate, setCutoffDate] = useState<string>(() => {
    // Default to today's date
    const today = new Date()
    return today.toISOString().split('T')[0]
  })
  const [newDate, setNewDate] = useState<string>(() => {
    // Default to today's date
    const today = new Date()
    return today.toISOString().split('T')[0]
  })
  const [applyToTabs, setApplyToTabs] = useState<string[]>([])
  const [columnsToCheck, setColumnsToCheck] = useState<string[]>([])

  const unmatchedHolds = inspectData.unmatched_hold_names || []
  const availableFields = Object.keys(inspectData.available_ap_values || {})
  const detectedAccountColumn = inspectData.suggested_mapping?.account_name || 'Account Name'

  const toggleExpand = (holdName: string) => {
    const newExpanded = new Set(expandedHolds)
    if (newExpanded.has(holdName)) {
      newExpanded.delete(holdName)
    } else {
      newExpanded.add(holdName)
    }
    setExpandedHolds(newExpanded)
  }

  const handleFieldChange = (holdName: string, field: string) => {
    setSelectedFields(prev => ({ ...prev, [holdName]: field }))
    // Reset selected value when field changes
    setSelectedValues(prev => ({ ...prev, [holdName]: '' }))
  }

  const handleValueChange = (holdName: string, value: string) => {
    setSelectedValues(prev => ({ ...prev, [holdName]: value }))
  }

  const addMapping = (holdName: string) => {
    const field = selectedFields[holdName]
    const value = selectedValues[holdName]

    if (!field || !value) {
      alert('Please select both a field and a value')
      return
    }

    // Check if mapping already exists
    const existingIndex = manualHoldMappings.findIndex(m => m.hold_name === holdName)
    
    if (existingIndex >= 0) {
      // Update existing mapping
      const newMappings = [...manualHoldMappings]
      newMappings[existingIndex] = { hold_name: holdName, field, value }
      setManualHoldMappings(newMappings)
    } else {
      // Add new mapping
      setManualHoldMappings(prev => [...prev, { hold_name: holdName, field, value }])
    }

    // Collapse the expanded section
    const newExpanded = new Set(expandedHolds)
    newExpanded.delete(holdName)
    setExpandedHolds(newExpanded)
  }

  const removeMapping = (holdName: string) => {
    setManualHoldMappings(prev => prev.filter(m => m.hold_name !== holdName))
  }
  
  const toggleTab = (tab: string) => {
    setApplyToTabs(prev => 
      prev.includes(tab) 
        ? prev.filter(t => t !== tab)
        : [...prev, tab]
    )
  }
  
  const toggleColumn = (column: string) => {
    setColumnsToCheck(prev => 
      prev.includes(column) 
        ? prev.filter(c => c !== column)
        : [...prev, column]
    )
  }

  const handleRunProcessing = async () => {
    setIsProcessing(true)
    
    try {
      // Prepare accounting period adjustment config
      const adjustmentConfig = adjustmentEnabled ? {
        enabled: true,
        cutoff_date: cutoffDate,
        new_date: newDate,
        apply_to_tabs: applyToTabs,
        columns_to_check: columnsToCheck
      } : {
        enabled: false,
        cutoff_date: null,
        new_date: null,
        apply_to_tabs: [],
        columns_to_check: []
      }
      
      // Save mapping with manual hold mappings and accounting period adjustment config
      await saveMapping(runId, {
        mapping: { account_name: detectedAccountColumn },
        manual_hold_mappings: manualHoldMappings,
        accounting_period_adjustment: adjustmentConfig
      })

      // Run processing
      await runProcessing(runId)

      // Move to download step
      onNext()
    } catch (error) {
      alert(`Processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleSkip = async () => {
    setIsProcessing(true)
    
    try {
      // Prepare accounting period adjustment config (same as Run Processing)
      const adjustmentConfig = adjustmentEnabled ? {
        enabled: true,
        cutoff_date: cutoffDate,
        new_date: newDate,
        apply_to_tabs: applyToTabs,
        columns_to_check: columnsToCheck
      } : {
        enabled: false,
        cutoff_date: null,
        new_date: null,
        apply_to_tabs: [],
        columns_to_check: []
      }
      
      // Save mapping without manual mappings
      await saveMapping(runId, {
        mapping: { account_name: detectedAccountColumn },
        manual_hold_mappings: [],
        accounting_period_adjustment: adjustmentConfig
      })

      // Run processing
      await runProcessing(runId)

      // Move to download step
      onNext()
    } catch (error) {
      alert(`Processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const getMappingForHold = (holdName: string) => {
    return manualHoldMappings.find(m => m.hold_name === holdName)
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Confirm & Continue
      </h2>

      {/* Description */}
      <div className="mb-6 p-4 bg-gray-50 border-l-4 border-gray-900 rounded">
        <p className="text-sm text-gray-700">
          Before we finalize the results, take a moment to review and make sure everything looks right.
        </p>
      </div>

      {/* Unmatched holds section */}
      {unmatchedHolds.length > 0 ? (
        <div className="mb-6">
          <div className="p-4 bg-gray-50 border border-gray-300 rounded-md mb-4">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-gray-700 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-gray-900 mb-1">
                  {unmatchedHolds.length} {unmatchedHolds.length === 1 ? 'Name' : 'Names'} on Payment Hold Not Found in Uploaded AP File
                </h3>
                <p className="text-sm text-gray-700">
                  We couldn't automatically match these names from your Payment Hold List. If these should be on hold, please manually match them below.
                </p>
              </div>
            </div>
          </div>

          {/* List of unmatched holds */}
          <div className="space-y-2">
            {unmatchedHolds.map(holdName => {
              const isExpanded = expandedHolds.has(holdName)
              const existingMapping = getMappingForHold(holdName)
              const selectedField = selectedFields[holdName] || ''
              const selectedValue = selectedValues[holdName] || ''
              const availableValues = selectedField ? (inspectData.available_ap_values?.[selectedField] || []) : []

              return (
                <div key={holdName} className="border border-gray-300 rounded-md overflow-hidden">
                  {/* Header */}
                  <button
                    onClick={() => toggleExpand(holdName)}
                    className="w-full px-4 py-3 bg-white hover:bg-gray-50 flex items-center justify-between transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-gray-700 font-medium">{holdName}</span>
                      {existingMapping && (
                        <span className="text-xs bg-gray-900 text-white px-2 py-1 rounded">
                          Mapped
                        </span>
                      )}
                    </div>
                    <svg 
                      className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Expanded content */}
                  {isExpanded && (
                    <div className="px-4 py-4 bg-gray-50 border-t border-gray-200">
                      <p className="text-sm text-gray-600 mb-3">Match this to a row in your AP file:</p>
                      
                      <div className="grid grid-cols-2 gap-3 mb-3">
                        {/* Field dropdown */}
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Field Name
                          </label>
                          <select
                            value={selectedField}
                            onChange={(e) => handleFieldChange(holdName, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="">-- Select field --</option>
                            {availableFields.map(field => (
                              <option key={field} value={field}>{field}</option>
                            ))}
                          </select>
                        </div>

                        {/* Value dropdown */}
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Field Value
                          </label>
                          <select
                            value={selectedValue}
                            onChange={(e) => handleValueChange(holdName, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            disabled={!selectedField}
                          >
                            <option value="">-- Select value --</option>
                            {availableValues.map(value => (
                              <option key={value} value={value}>{value}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <button
                        onClick={() => addMapping(holdName)}
                        disabled={!selectedField || !selectedValue}
                        className="w-full px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                      >
                        + Add to Payment Hold List
                      </button>

                      {existingMapping && (
                        <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded text-xs">
                          <div className="flex items-center justify-between">
                            <span className="text-green-800">
                              Mapped to: <strong>{existingMapping.field}</strong> = <strong>{existingMapping.value}</strong>
                            </span>
                            <button
                              onClick={() => removeMapping(holdName)}
                              className="text-red-600 hover:text-red-800"
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      ) : (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-800">
            ✓ All names from your Payment Hold List were found in the AP file.
          </p>
        </div>
      )}

      {/* Accounting Period Adjustment Configuration */}
      <div className="mb-6 p-5 bg-gray-50 border border-gray-300 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-gray-900">Accounting Period Adjustment</h3>
            <p className="text-xs text-gray-600 mt-1">Conditionally update dates before a cutoff to a new date</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={adjustmentEnabled}
              onChange={(e) => setAdjustmentEnabled(e.target.checked)}
            />
            <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-gray-400 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gray-900"></div>
          </label>
        </div>

        {adjustmentEnabled && (
          <div className="space-y-4">
            {/* Cutoff Date Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cutoff Date <span className="text-gray-500">(dates before this will be modified)</span>
              </label>
              <input
                type="date"
                value={cutoffDate}
                onChange={(e) => setCutoffDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-gray-900 focus:border-gray-900"
              />
            </div>

            {/* New Date Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Date <span className="text-gray-500">(what to change old dates to)</span>
              </label>
              <input
                type="date"
                value={newDate}
                onChange={(e) => setNewDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-gray-900 focus:border-gray-900"
              />
            </div>

            {/* Apply to Tabs */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Apply to Output Tabs
              </label>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={applyToTabs.includes('ready_to_pay')}
                    onChange={() => toggleTab('ready_to_pay')}
                    className="w-4 h-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                  />
                  <span className="text-sm text-gray-700">Ready for Payment</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={applyToTabs.includes('payment_on_hold')}
                    onChange={() => toggleTab('payment_on_hold')}
                    className="w-4 h-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                  />
                  <span className="text-sm text-gray-700">Payment On Hold</span>
                </label>
              </div>
            </div>

            {/* Columns to Check */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date Columns to Check
              </label>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={columnsToCheck.includes('created_date')}
                    onChange={() => toggleColumn('created_date')}
                    className="w-4 h-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                  />
                  <span className="text-sm text-gray-700">Created Date</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={columnsToCheck.includes('modified_date')}
                    onChange={() => toggleColumn('modified_date')}
                    className="w-4 h-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                  />
                  <span className="text-sm text-gray-700">Last Modified Date</span>
                </label>
              </div>
            </div>

            {/* Summary */}
            {(applyToTabs.length > 0 || columnsToCheck.length > 0) && (
              <div className="mt-3 p-3 bg-white border border-gray-300 rounded text-sm">
                <p className="text-gray-700">
                  <strong>Summary:</strong> Will change dates <strong>before {cutoffDate}</strong> to <strong>{newDate}</strong>
                  {' '}in{' '}
                  {columnsToCheck.length > 0 ? (
                    <>
                      <strong>
                        {columnsToCheck.map(c => c === 'created_date' ? 'Created Date' : 'Last Modified Date').join(' and ')}
                      </strong>
                    </>
                  ) : (
                    <em>no columns</em>
                  )}
                  {' '}for{' '}
                  {applyToTabs.length > 0 ? (
                    <>
                      <strong>
                        {applyToTabs.map(t => t === 'ready_to_pay' ? 'Ready for Payment' : 'Payment On Hold').join(' and ')}
                      </strong>
                    </>
                  ) : (
                    <em>no tabs</em>
                  )}
                  {'. '}
                  <span className="text-gray-600">Dates on or after {cutoffDate} will remain unchanged.</span>
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleSkip}
          disabled={isProcessing}
          className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 rounded-md font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isProcessing ? 'Processing...' : 'Skip & Proceed Anyway'}
        </button>
        <button
          onClick={handleRunProcessing}
          disabled={isProcessing}
          className="flex-1 px-6 py-3 bg-gray-900 text-white rounded-md font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isProcessing ? 'Processing...' : 'Run Processing'}
        </button>
      </div>
    </div>
  )
}
