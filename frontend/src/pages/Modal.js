// Modal.js
import React from "react";

export default function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-40">
      <div className="bg-white rounded shadow-lg max-w-lg w-full relative p-0">
        <button
          className="absolute top-1 right-3 text-2xl text-gray-500 hover:text-black"
          onClick={onClose}
          aria-label="Cerrar"
        >×</button>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}
