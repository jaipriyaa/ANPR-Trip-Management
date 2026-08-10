import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Modal({ isOpen, onClose, title, children }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-[#122c33]/60 backdrop-blur-sm transition-opacity" 
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="relative bg-white border border-[#c8d8e4] rounded-3xl shadow-2xl shadow-[#2b6777]/20 w-full max-w-lg overflow-hidden transform transition-all z-10">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-[#c8d8e4] flex items-center justify-between bg-[#f2f2f2]/50">
          <h3 className="text-sm font-bold text-[#2b6777] tracking-tight">{title}</h3>
          <button
            onClick={onClose}
            className="text-[#2b6777] hover:text-white p-1.5 rounded-full hover:bg-[#2b6777] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 max-h-[80vh] overflow-y-auto text-[#1a3b45]">
          {children}
        </div>
      </div>
    </div>
  );
}
