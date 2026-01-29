'use client'

import { useState, useEffect } from 'react'
import { InspectResponse, saveMapping, runProcessing, MappingPayload } from '@/lib/api'

interface ConfirmStepProps {
  runId: string
  inspectData: InspectResponse
  onNext: () => void
  onSkip: () => void
}

interface NameMapping {
  holdName: string
  apName: string
}

interface RowLevelOverride {
  match_field: string
  match_value: string
  force_on_hold: boolean
}

export default function ConfirmStep({ runId, inspectData, onNext, onSkip }: ConfirmStepProps) {
  const [nameMappings, setNameMappings] = useState<NameMapping[]>([])
  const [rowLevelHolds, setRowLevelHolds] = useState<RowLevelOverride[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [userDecision, setUserDecision] = useState<'pending' | 'manual' | 'proceed'>('pending')

  // Column mappings state
  const [accountNameColumn, setAccountNameColumn] = useState<string>('')
  const [createdDateColumn, setCreatedDateColumn] = useState<string>('')
  const [modifiedDateColumn, setModifiedDateColumn] = useState<string>('')

  // Extract unmatched hold names and available AP names from inspect data
  const unmatchedHoldNames = inspectData.unmatched_payments || []
  const availableApNames = inspectData.available_ap_names || []
  
  const hasUnmatched = unmatchedHoldNames.length > 0
  const hasMappings = nameMappings.length > 0
  const hasRowHolds = rowLevelHolds.length > 0
  const notFoundCount = unmatchedHoldNames.length

  // Get available columns from preview data
  const availableColumns: string[] = []
  if (inspectData.preview_rows && inspectData.preview_rows.length > 0) {
    availableColumns.push(...Object.keys(inspectData.preview_rows[0]))
  }

  // Set defaults from detected column mappings
  useEffect(() => {
    if (inspectData.column_mappings?.account_name) {
      setAccountNameColumn(inspectData.column_mappings.account_name)
    }
    if (inspectData.column_mappings?.created_date) {
      setCreatedDateColumn(inspectData.column_mappings.created_date)
    }
    if (inspectData.column_mappings?.modified_date) {
      setModifiedDateColumn(inspectData.column_mappings.modified_date)
    }
  }, [inspectData])

  // Detect available identifier columns from preview data
  const availableIdentifierColumns: string[] = []
  if (inspectData.preview_rows && inspectData.preview_rows.length > 0) {
    const firstRow = inspectData.preview_rows[0]
    const columnNames = Object.keys(firstRow).map(k => k.toLowerCase())
    
    if (columnNames.some(col => col.includes('case') && col.includes('number'))) {
      const caseCol = Object.keys(firstRow).find(k => k.toLowerCase().includes('case') && k.toLowerCase().includes('number'))
      if (caseCol) availableIdentifierColumns.push(caseCol)
    }
    if (columnNames.some(col => col.includes('confirmation') && col.includes('number'))) {
      const confCol = Object.keys(firstRow).find(k => k.toLowerCase().includes('confirmation') && k.toLowerCase().includes('number'))
      if (confCol) availableIdentifierColumns.push(confCol)
    }
    if (columnNames.some(col => col.includes('invoice') && col.includes('number'))) {
      const invCol = Object.keys(firstRow).find(k => k.toLowerCase().includes('invoice') && k.toLowerCase().includes('number'))
      if (invCol) availableIdentifierColumns.push(invCol)
    }
  }

  const addMapping = (holdName: string, apName: string) => {
    setNameMappings(prev => {
      // Remove existing mapping for this hold name if any
      const filtered = prev.filter(m => m.holdName !== holdName)
      return [...filtered, { holdName, apName }]
    })
  }

  const removeMapping = (holdName: string) => {
    setNameMappings(prev => prev.filter(m => m.holdName !== holdName))
  }

  const addRowLevelHold = (matchField: string, matchValue: string) => {
    const newHold: RowLevelOverride = {
      match_field: matchField,
      match_value: matchValue,
      force_on_hold: true
    }
    setRowLevelHolds(prev => [...prev, newHold])
  }

  const removeRowLevelHold = (index: number) => {
    setRowLevelHolds(prev => prev.filter((_, idx) => idx !== index))
  }

  const handleProcess = async () => {
    if (!accountNameColumn) {
      alert('Please select an Account Name column')
      return
    }

    setIsProcessing(true)
    
    try {
      // Build override_hold_name_to_ap_name from manual mappings
      const override_hold_name_to_ap_name = nameMappings.reduce((acc, m) => {
        acc[m.holdName] = m.apName
        return acc
      }, {} as Record<string, string>)
      
      // Build override_row_level_holds array
      const override_row_level_holds = rowLevelHolds
      
      // Build the complete mapping payload
      const mappingPayload: MappingPayload = {
        account_name_column: accountNameColumn,
        overrides: {
          hold_name_to_ap_name: override_hold_name_to_ap_name,
          row_level_holds: override_row_level_holds
        }
      }

      // Add optional date column mappings if provided
      if (createdDateColumn) {
        mappingPayload.created_date_column = createdDateColumn
      }
      if (modifiedDateColumn) {
        mappingPayload.modified_date_column = modifiedDateColumn
      }
      
      // Save mapping configuration to backend
      await saveMapping(runId, mappingPayload)
      
      // Run the processing
      await runProcessing(runId)
      
      // Move to download step
      onNext()
    } catch (error) {
      console.error('Processing failed:', error)
      alert(error instanceof Error ? error.message : 'Processing failed')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">
        Confirm / Manual Match
      </h2>

      {/* Counts Summary */}
      {inspectData.counts && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Summary</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Total Payments:</span>
              <span className="ml-2 font-medium text-gray-800">
                {inspectData.counts.total_payments}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Matched:</span>
              <span className="ml-2 font-medium text-green-600">
                {inspectData.counts.matched}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Unmatched:</span>
              <span className="ml-2 font-medium text-orange-600">
                {inspectData.counts.unmatched}
              </span>
            </div>
            <div>
              <span className="text-gray-600">On Hold:</span>
              <span className="ml-2 font-medium text-red-600">
                {inspectData.counts.holds}
              </span>
            </div>
            {inspectData.counts.unique_ap_accounts !== undefined && (
              <div>
                <span className="text-gray-600">Unique AP Accounts:</span>
                <span className="ml-2 font-medium text-gray-800">
                  {inspectData.counts.unique_ap_accounts}
                </span>
              </div>
            )}
            {inspectData.counts.total_hold_names !== undefined && (
              <div>
                <span className="text-gray-600">Hold List Names:</span>
                <span className="ml-2 font-medium text-gray-800">
                  {inspectData.counts.total_hold_names}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Detected Column Mappings */}
      {inspectData.column_mappings && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-sm font-semibold text-blue-800 mb-3">
            Detected Column Mappings (Suggested)
          </h3>
          <div className="space-y-2 text-sm">
            {inspectData.column_mappings.account_name && (
              <div className="flex items-center gap-2">
                <span className="text-blue-700 font-medium">Account Name:</span>
                <code className="bg-white px-2 py-1 rounded text-blue-900 border border-blue-300">
                  {inspectData.column_mappings.account_name}
                </code>
              </div>
            )}
            {inspectData.column_mappings.created_date && (
              <div className="flex items-center gap-2">
                <span className="text-blue-700 font-medium">Created Date:</span>
                <code className="bg-white px-2 py-1 rounded text-blue-900 border border-blue-300">
                  {inspectData.column_mappings.created_date}
                </code>
              </div>
            )}
            {inspectData.column_mappings.modified_date && (
              <div className="flex items-center gap-2">
                <span className="text-blue-700 font-medium">Modified Date:</span>
                <code className="bg-white px-2 py-1 rounded text-blue-900 border border-blue-300">
                  {inspectData.column_mappings.modified_date}
                </code>
              </div>
            )}
          </div>
          <p className="text-xs text-blue-600 mt-3 italic">
            You can adjust these mappings below if needed.
          </p>
        </div>
      )}

      {/* Column Mapping Configuration */}
      <div className="mb-6 p-4 bg-white rounded-lg border border-gray-300">
        <h3 className="text-sm font-semibold text-gray-800 mb-3">
          Confirm Column Mappings
        </h3>
        <p className="text-xs text-gray-600 mb-4">
          Select which columns contain the required data. These are pre-filled with detected values.
        </p>
        
        <div className="space-y-4">
          {/* Account Name Column (Required) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account Name Column <span className="text-red-500">*</span>
            </label>
            <select
              value={accountNameColumn}
              onChange={(e) => setAccountNameColumn(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Select account name column --</option>
              {availableColumns.map((col, idx) => (
                <option key={idx} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>

          {/* Created Date Column (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Created Date Column <span className="text-gray-400 text-xs">(Optional)</span>
            </label>
            <select
              value={createdDateColumn}
              onChange={(e) => setCreatedDateColumn(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- None --</option>
              {availableColumns.map((col, idx) => (
                <option key={idx} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>

          {/* Modified Date Column (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Modified Date Column <span className="text-gray-400 text-xs">(Optional)</span>
            </label>
            <select
              value={modifiedDateColumn}
              onChange={(e) => setModifiedDateColumn(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- None --</option>
              {availableColumns.map((col, idx) => (
                <option key={idx} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>
        </div>

        {!accountNameColumn && (
          <p className="mt-3 text-xs text-red-600">
            ⚠️ Account Name column is required to proceed
          </p>
        )}
      </div>

      {/* Data Preview */}
      {inspectData.preview_rows && inspectData.preview_rows.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Data Preview (First {inspectData.preview_rows.length} rows)
          </h3>
          <div className="overflow-x-auto border border-gray-200 rounded-lg">
            <table className="min-w-full divide-y divide-gray-200 text-xs">
              <thead className="bg-gray-50">
                <tr>
                  {Object.keys(inspectData.preview_rows[0]).map((key) => (
                    <th
                      key={key}
                      className="px-3 py-2 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {inspectData.preview_rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    {Object.values(row).map((value: any, cellIdx) => (
                      <td
                        key={cellIdx}
                        className="px-3 py-2 whitespace-nowrap text-gray-800"
                      >
                        {value !== null && value !== undefined
                          ? String(value)
                          : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Warnings */}
      {inspectData.warnings && inspectData.warnings.length > 0 && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5"
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
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-yellow-800 mb-2">
                Warnings
              </h3>
              <ul className="text-sm text-yellow-700 space-y-1">
                {inspectData.warnings.map((warning, idx) => (
                  <li key={idx}>• {warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Hold Names Not Found Warning */}
      {hasUnmatched && userDecision === 'pending' && (
        <div className="mb-6 p-5 bg-orange-50 border-2 border-orange-300 rounded-lg">
          <div className="flex items-start gap-3 mb-4">
            <svg
              className="w-6 h-6 text-orange-600 flex-shrink-0"
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
            <div className="flex-1">
              <h3 className="text-base font-semibold text-orange-900 mb-2">
                {notFoundCount} Hold Name{notFoundCount > 1 ? 's' : ''} Not Found in Uploaded AP File
              </h3>
              <p className="text-sm text-orange-800 mb-3">
                The following names from the payment hold list were not found in the AP data:
              </p>
              
              <div className="bg-white border border-orange-300 rounded p-3 mb-4 max-h-40 overflow-y-auto">
                <ul className="space-y-1">
                  {unmatchedHoldNames.map((name: string, idx: number) => (
                    <li key={idx} className="text-sm text-gray-800">
                      • {name}
                    </li>
                  ))}
                </ul>
              </div>

              <p className="text-sm text-orange-800 mb-4">
                What would you like to do?
              </p>

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => setUserDecision('manual')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium transition-colors text-sm"
                >
                  Manual Match
                </button>
                <button
                  onClick={() => setUserDecision('proceed')}
                  className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 font-medium transition-colors text-sm"
                >
                  Proceed Anyway
                </button>
                <button
                  onClick={() => setUserDecision('proceed')}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 font-medium transition-colors text-sm"
                >
                  Skip
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manual Matching Section (shown after user clicks "Manual Match") */}
      {hasUnmatched && userDecision === 'manual' && (
        <div className="mb-6">
          <div className="p-4 bg-orange-50 border border-orange-200 rounded-md mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-orange-800">
                Manual Matching Mode
              </h3>
              <div className="flex gap-2">
                <span className="text-xs font-semibold text-orange-700 bg-white px-2 py-1 rounded border border-orange-300">
                  {nameMappings.length} of {notFoundCount} mapped
                </span>
                {hasRowHolds && (
                  <span className="text-xs font-semibold text-purple-700 bg-white px-2 py-1 rounded border border-purple-300">
                    {rowLevelHolds.length} forced hold{rowLevelHolds.length > 1 ? 's' : ''}
                  </span>
                )}
              </div>
            </div>
            <p className="text-sm text-orange-700 mb-3">
              Map hold list names to AP account names. {notFoundCount} name{notFoundCount > 1 ? 's need' : ' needs'} matching.
            </p>
            
            <div className="space-y-2">
              {unmatchedHoldNames.map((name: string, idx: number) => {
                const mapping = nameMappings.find(m => m.holdName === name)
                return (
                  <div key={idx} className="bg-white p-2 rounded border border-orange-300 flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800">{name}</span>
                    {mapping ? (
                      <span className="text-xs text-green-600 font-medium">
                        ✓ Mapped to: {mapping.apName}
                      </span>
                    ) : (
                      <span className="text-xs text-orange-600">Not mapped</span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Manual Mapping Interface */}
      {userDecision === 'manual' && (
        <div className="mb-6">
          {/* Vendor Name Mapping */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-md mb-4">
            <h3 className="text-base font-semibold text-blue-900 mb-2">
              Manual Match (Vendor Name)
            </h3>
            <p className="text-sm text-blue-700 mb-4">
              Map hold list vendor names to AP account names. This creates override mappings without editing raw data.
            </p>
            
            <ManualMatchVendorName
              unmatchedHoldNames={unmatchedHoldNames}
              availableApNames={availableApNames}
              existingMappings={nameMappings}
              onAddMapping={addMapping}
              onRemoveMapping={removeMapping}
            />
          </div>

          {/* Row-Level Hold by Identifier */}
          {availableIdentifierColumns.length > 0 && (
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-md mb-4">
              <h3 className="text-base font-semibold text-purple-900 mb-2">
                Manual Match (By Identifier)
              </h3>
              <p className="text-sm text-purple-700 mb-2">
                Force specific rows to be marked as "Payment On Hold" by identifier.
              </p>
              <p className="text-xs text-purple-600 mb-4 italic">
                Note: This will mark matching rows as Payment On Hold.
              </p>
              
              <ManualMatchByIdentifier
                availableIdentifierColumns={availableIdentifierColumns}
                existingHolds={rowLevelHolds}
                onAddHold={addRowLevelHold}
                onRemoveHold={removeRowLevelHold}
              />
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={() => setUserDecision('pending')}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm"
            >
              ← Back to Options
            </button>
            <button
              onClick={() => setUserDecision('proceed')}
              className="flex-1 px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm font-medium"
            >
              {(hasMappings || hasRowHolds)
                ? `Done - Proceed with ${nameMappings.length + rowLevelHolds.length} Override${nameMappings.length + rowLevelHolds.length > 1 ? 's' : ''}`
                : 'Done - Proceed Anyway'
              }
            </button>
          </div>
        </div>
      )}

      {/* Action Buttons - Only show when ready to proceed */}
      {(!hasUnmatched || userDecision !== 'pending') && (
        <>
          {accountNameColumn && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Ready to process:</span> This will save your mappings and run the processing workflow.
              </p>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={handleProcess}
              disabled={isProcessing || !accountNameColumn}
              className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors flex items-center justify-center gap-2 ${
                isProcessing || !accountNameColumn
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isProcessing ? (
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
                  Processing & Running...
                </>
              ) : (
                <>
                  Run Processing
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
                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </>
              )}
            </button>
          </div>

          {!accountNameColumn && (
            <p className="mt-3 text-xs text-center text-red-600 font-medium">
              ⚠️ Please select an Account Name column above to proceed
            </p>
          )}

          {accountNameColumn && hasUnmatched && userDecision === 'proceed' && !hasMappings && !hasRowHolds && (
            <p className="mt-3 text-xs text-center text-orange-600 font-medium">
              ⚠️ Processing without mappings - {notFoundCount} hold name{notFoundCount > 1 ? 's' : ''} will remain unmatched
            </p>
          )}

          {accountNameColumn && (hasMappings || hasRowHolds) && (
            <div className="mt-3 text-xs text-center space-y-1">
              {hasMappings && (
                <p className="text-green-600 font-medium">
                  ✓ {nameMappings.length} vendor name mapping{nameMappings.length > 1 ? 's' : ''} will be applied
                </p>
              )}
              {hasRowHolds && (
                <p className="text-purple-600 font-medium">
                  ✓ {rowLevelHolds.length} forced hold rule{rowLevelHolds.length > 1 ? 's' : ''} will be applied
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// Manual Match Vendor Name Component
interface ManualMatchVendorNameProps {
  unmatchedHoldNames: string[]
  availableApNames: string[]
  existingMappings: NameMapping[]
  onAddMapping: (holdName: string, apName: string) => void
  onRemoveMapping: (holdName: string) => void
}

function ManualMatchVendorName({
  unmatchedHoldNames,
  availableApNames,
  existingMappings,
  onAddMapping,
  onRemoveMapping,
}: ManualMatchVendorNameProps) {
  const [selectedHoldName, setSelectedHoldName] = useState('')
  const [selectedApName, setSelectedApName] = useState('')

  const handleAdd = () => {
    if (selectedHoldName && selectedApName) {
      onAddMapping(selectedHoldName, selectedApName)
      setSelectedHoldName('')
      setSelectedApName('')
    }
  }

  // Get unmatched names that haven't been mapped yet
  const unmappedHoldNames = unmatchedHoldNames.filter(
    name => !existingMappings.find(m => m.holdName === name)
  )

  return (
    <div>
      {/* Add Mapping Form */}
      <div className="bg-white border border-blue-300 rounded-md p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
          {/* Left Dropdown */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Left: Hold Vendor Name (Not Found)
            </label>
            <select
              value={selectedHoldName}
              onChange={(e) => setSelectedHoldName(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Select hold name --</option>
              {unmappedHoldNames.map((name, idx) => (
                <option key={idx} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          {/* Right Dropdown */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Right: AP Account Name
            </label>
            <select
              value={selectedApName}
              onChange={(e) => setSelectedApName(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={!selectedHoldName}
            >
              <option value="">-- Select AP account name --</option>
              {availableApNames.map((name: string, idx: number) => (
                <option key={idx} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleAdd}
          disabled={!selectedHoldName || !selectedApName}
          className={`w-full py-2 px-4 text-sm rounded-md font-medium transition-colors ${
            selectedHoldName && selectedApName
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Add Mapping
        </button>
      </div>

      {/* Mappings Table */}
      {existingMappings.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">
            Mappings Added ({existingMappings.length})
          </h4>
          <div className="bg-white border border-gray-300 rounded-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase">
                    Hold Vendor Name
                  </th>
                  <th className="px-4 py-2 text-center text-xs font-semibold text-gray-700">
                    →
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase">
                    AP Account Name
                  </th>
                  <th className="px-4 py-2 text-center text-xs font-semibold text-gray-700 uppercase">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {existingMappings.map((mapping, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {mapping.holdName}
                    </td>
                    <td className="px-4 py-3 text-center text-gray-400">
                      →
                    </td>
                    <td className="px-4 py-3 text-sm text-blue-700 font-medium">
                      {mapping.apName}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => onRemoveMapping(mapping.holdName)}
                        className="text-red-600 hover:text-red-800 transition-colors"
                        title="Remove mapping"
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
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {existingMappings.length === 0 && (
        <div className="text-center py-6 bg-gray-50 border-2 border-dashed border-gray-300 rounded-md">
          <p className="text-sm text-gray-500">
            No mappings added yet. Use the form above to create mappings.
          </p>
        </div>
      )}
    </div>
  )
}

// Manual Match By Identifier Component
interface ManualMatchByIdentifierProps {
  availableIdentifierColumns: string[]
  existingHolds: RowLevelOverride[]
  onAddHold: (matchField: string, matchValue: string) => void
  onRemoveHold: (index: number) => void
}

function ManualMatchByIdentifier({
  availableIdentifierColumns,
  existingHolds,
  onAddHold,
  onRemoveHold,
}: ManualMatchByIdentifierProps) {
  const [selectedField, setSelectedField] = useState('')
  const [identifierValue, setIdentifierValue] = useState('')

  const handleAdd = () => {
    if (selectedField && identifierValue.trim()) {
      onAddHold(selectedField, identifierValue.trim())
      setIdentifierValue('')
    }
  }

  return (
    <div>
      {/* Add Hold Rule Form */}
      <div className="bg-white border border-purple-300 rounded-md p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
          {/* Identifier Field Dropdown */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Identifier Field
            </label>
            <select
              value={selectedField}
              onChange={(e) => setSelectedField(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">-- Select identifier field --</option>
              {availableIdentifierColumns.map((col, idx) => (
                <option key={idx} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>

          {/* Identifier Value Input */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Identifier Value
            </label>
            <input
              type="text"
              value={identifierValue}
              onChange={(e) => setIdentifierValue(e.target.value)}
              placeholder="Enter value..."
              disabled={!selectedField}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>
        </div>

        <button
          onClick={handleAdd}
          disabled={!selectedField || !identifierValue.trim()}
          className={`w-full py-2 px-4 text-sm rounded-md font-medium transition-colors ${
            selectedField && identifierValue.trim()
              ? 'bg-purple-600 text-white hover:bg-purple-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Add Forced Hold Rule
        </button>
      </div>

      {/* Hold Rules Table */}
      {existingHolds.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">
            Forced Hold Rules ({existingHolds.length})
          </h4>
          <div className="bg-white border border-gray-300 rounded-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase">
                    Identifier Field
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase">
                    Identifier Value
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase">
                    Action
                  </th>
                  <th className="px-4 py-2 text-center text-xs font-semibold text-gray-700 uppercase">
                    Remove
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {existingHolds.map((hold, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {hold.match_field}
                    </td>
                    <td className="px-4 py-3 text-sm text-purple-700 font-medium">
                      {hold.match_value}
                    </td>
                    <td className="px-4 py-3 text-sm text-red-600">
                      Force On Hold
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => onRemoveHold(idx)}
                        className="text-red-600 hover:text-red-800 transition-colors"
                        title="Remove hold rule"
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
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {existingHolds.length === 0 && (
        <div className="text-center py-6 bg-gray-50 border-2 border-dashed border-gray-300 rounded-md">
          <p className="text-sm text-gray-500">
            No forced hold rules added yet. Use the form above to add rules.
          </p>
        </div>
      )}
    </div>
  )
}

