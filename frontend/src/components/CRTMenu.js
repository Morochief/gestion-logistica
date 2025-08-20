import React from "react";
import { useNavigate } from "react-router-dom";
import { FiPlus, FiSend, FiSearch, FiPrinter, FiX } from "react-icons/fi";

const CRTMenu = () => {
  const navigate = useNavigate();

  const items = [
    { icon: <FiPlus size={20} className="text-blue-700" />, text: "Nuevo CRT", action: () => navigate("/crt") },
    { icon: <FiSend size={20} className="text-blue-600" />, text: "Emitir CRT", action: () => navigate("/crt") },
    { icon: <FiSearch size={20} className="text-blue-500" />, text: "Buscar CRT", action: () => navigate("/listar-crt") },
    { icon: <FiPrinter size={20} className="text-blue-500" />, text: "Imprimir CRT", action: () => navigate("/listar-crt") },
    { icon: <FiX size={20} className="text-blue-800" />, text: "Cerrar", action: () => window.close() },
  ];

  return (
    <div className="flex flex-col gap-2 px-2 w-full">
      {items.map((item, index) => (
        <button
          key={index}
          onClick={item.action}
          className="flex items-center gap-2 p-2 rounded hover:bg-blue-200 transition w-full"
        >
          {item.icon}
          <span className="hidden group-hover:block text-blue-900 text-sm transition">{item.text}</span>
        </button>
      ))}
    </div>
  );
};

export default CRTMenu;
