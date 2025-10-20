// frontend/src/components/ValidationPanel.tsx
import React from 'react';

interface ValidationError {
  code: string;
  message: string;
  where: string;
}

interface ValidationWarning {
  code: string;
  message: string;
  where: string;
}

interface ValidationPanelProps {
  validation: {
    errors: ValidationError[];
    warnings: ValidationWarning[];
  };
  templateVars: Record<string, any>;
  onFix?: (fieldName: string) => void;
}

export default function ValidationPanel({ validation, templateVars, onFix }: ValidationPanelProps) {
  const getFieldStatus = (fieldName: string): 'error' | 'warning' | 'success' | 'empty' => {
    const hasError = validation.errors.some(e => e.where === fieldName);
    const hasWarning = validation.warnings.some(w => w.where === fieldName);
    const value = templateVars[fieldName];
    const hasValue = value && (typeof value !== 'number' || value !== 0);

    if (hasError) return 'error';
    if (hasWarning) return 'warning';
    if (hasValue) return 'success';
    return 'empty';
  };

  const statusConfig = {
    error: {
      style: 'border-red-500 bg-red-50',
      icon: '❌',
      textColor: 'text-red-700'
    },
    warning: {
      style: 'border-yellow-500 bg-yellow-50',
      icon: '⚠️',
      textColor: 'text-yellow-700'
    },
    success: {
      style: 'border-green-500 bg-green-50',
      icon: '✓',
      textColor: 'text-green-700'
    },
    empty: {
      style: 'border-gray-300 bg-gray-50',
      icon: '○',
      textColor: 'text-gray-600'
    }
  };

  const fields = [
    { name: 'supplier_serial_no', label: 'Supplier Serial No', required: true },
    { name: 'contract_number', label: 'Contract Number', required: true },
    { name: 'contract_item', label: 'Contract Item', required: true },
    { name: 'product_description', label: 'Product Description', required: true },
    { name: 'quantity', label: 'Quantity', required: true },
    { name: 'shipment_no', label: 'Shipment Number', required: true },
    { name: 'date', label: 'Date', required: true },
    { name: 'acquirer', label: 'Acquirer', required: false },
    { name: 'delivery_address', label: 'Delivery Address', required: false },
    { name: 'partial_delivery_number', label: 'Partial Delivery Number', required: false },
    { name: 'final_delivery_number', label: 'Final Delivery Number', required: false },
    { name: 'undelivered_quantity', label: 'Undelivered Quantity', required: false },
    { name: 'remarks', label: 'Remarks', required: false },
  ];

  const errorCount = validation.errors.length;
  const warningCount = validation.warnings.length;
  const successCount = fields.filter(f => getFieldStatus(f.name) === 'success').length;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Validation Status</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
          <div className="text-3xl font-bold text-red-600">{errorCount}</div>
          <div className="text-sm text-red-800 font-medium">Blocking Errors</div>
        </div>
        <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
          <div className="text-3xl font-bold text-yellow-600">{warningCount}</div>
          <div className="text-sm text-yellow-800 font-medium">Warnings</div>
        </div>
        <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
          <div className="text-3xl font-bold text-green-600">{successCount}</div>
          <div className="text-sm text-green-800 font-medium">Valid Fields</div>
        </div>
      </div>

      {/* Overall Status */}
      {errorCount > 0 ? (
        <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded text-red-800">
          <strong>Cannot proceed:</strong> Fix {errorCount} error{errorCount > 1 ? 's' : ''} before generating document.
        </div>
      ) : warningCount > 0 ? (
        <div className="mb-4 p-3 bg-yellow-100 border border-yellow-300 rounded text-yellow-800">
          <strong>Ready with warnings:</strong> Document can be generated but review {warningCount} warning{warningCount > 1 ? 's' : ''}.
        </div>
      ) : (
        <div className="mb-4 p-3 bg-green-100 border border-green-300 rounded text-green-800">
          <strong>All checks passed:</strong> Ready to generate document.
        </div>
      )}

      {/* Field-by-field Status */}
      <div className="space-y-2">
        <h3 className="font-semibold text-sm text-gray-600 mb-2">Field Status:</h3>
        {fields.map(field => {
          const status = getFieldStatus(field.name);
          const config = statusConfig[status];
          const fieldErrors = validation.errors.filter(e => e.where === field.name);
          const fieldWarnings = validation.warnings.filter(w => w.where === field.name);
          const value = templateVars[field.name];

          return (
            <div key={field.name} className={`p-3 border-l-4 rounded ${config.style}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2 flex-1">
                  <span className="text-lg">{config.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium">
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </div>
                    {value && (
                      <div className="text-sm text-gray-600 mt-1">
                        {(() => {
                          const strValue = String(value);
                          // Don't truncate addresses and acquirer - show full text
                          if (field.name === 'delivery_address' || field.name === 'acquirer') {
                            return strValue;
                          }
                          // Truncate other long fields at 50 chars
                          return strValue.length > 50 ? strValue.slice(0, 50) + '...' : strValue;
                        })()}
                      </div>
                    )}
                  </div>
                </div>
                {onFix && (status === 'error' || status === 'warning') && (
                  <button
                    onClick={() => onFix(field.name)}
                    className="text-blue-600 text-sm hover:underline ml-2"
                  >
                    Fix
                  </button>
                )}
              </div>
              
              {fieldErrors.map((err, idx) => (
                <div key={idx} className={`mt-2 text-sm ${config.textColor} flex items-start gap-1`}>
                  <span className="font-bold">Error:</span>
                  <span>{err.message}</span>
                </div>
              ))}
              
              {fieldWarnings.map((warn, idx) => (
                <div key={idx} className={`mt-2 text-sm ${config.textColor} flex items-start gap-1`}>
                  <span className="font-bold">Warning:</span>
                  <span>{warn.message}</span>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}