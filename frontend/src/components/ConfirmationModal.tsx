// frontend/src/components/ConfirmationModal.tsx
import React from 'react';

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  items?: string[];
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
  type?: 'warning' | 'info' | 'error';
}

export default function ConfirmationModal({
  isOpen,
  title,
  message,
  items = [],
  onConfirm,
  onCancel,
  confirmText = 'OK',
  cancelText = 'Cancel',
  type = 'warning'
}: ConfirmationModalProps) {
  if (!isOpen) return null;

  const getColors = () => {
    switch (type) {
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-300',
          icon: '⚠️',
          iconBg: 'bg-yellow-100',
          confirmBtn: 'bg-blue-600 hover:bg-blue-700',
          cancelBtn: 'bg-gray-300 hover:bg-gray-400'
        };
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-300',
          icon: '❌',
          iconBg: 'bg-red-100',
          confirmBtn: 'bg-red-600 hover:bg-red-700',
          cancelBtn: 'bg-gray-300 hover:bg-gray-400'
        };
      case 'info':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-300',
          icon: 'ℹ️',
          iconBg: 'bg-blue-100',
          confirmBtn: 'bg-blue-600 hover:bg-blue-700',
          cancelBtn: 'bg-gray-300 hover:bg-gray-400'
        };
    }
  };

  const colors = getColors();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-md w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className={`${colors.bg} border-b-2 ${colors.border} p-6 rounded-t-lg`}>
          <div className="flex items-center gap-3">
            <div className={`${colors.iconBg} w-12 h-12 rounded-full flex items-center justify-center text-2xl flex-shrink-0`}>
              {colors.icon}
            </div>
            <h3 className="text-xl font-bold text-gray-900">{title}</h3>
          </div>
        </div>

        {/* Content - Scrollable */}
        <div className="p-6 overflow-y-auto flex-1">
          <p className="text-gray-700 mb-4 whitespace-pre-line">{message}</p>

          {items && items.length > 0 && (
            <div className={`${colors.bg} border ${colors.border} rounded p-4 mb-4`}>
              <div className="space-y-2">
                {items.map((item, idx) => (
                  <div key={idx} className="text-gray-800 font-medium">
                    • {item}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer - Buttons */}
        <div className="border-t border-gray-200 p-4 flex gap-3 justify-end bg-gray-50 rounded-b-lg">
          <button
            onClick={onCancel}
            className={`px-6 py-2 ${colors.cancelBtn} text-gray-800 font-medium rounded transition-colors`}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`px-6 py-2 ${colors.confirmBtn} text-white font-medium rounded transition-colors`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
