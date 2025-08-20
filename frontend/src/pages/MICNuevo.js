import React from "react";
import { useLocation } from "react-router-dom";

function MICNuevo() {
  const location = useLocation();
  const micData = location.state;

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Nuevo MIC desde CRT</h2>
      <pre className="bg-gray-100 p-2 rounded">{JSON.stringify(micData, null, 2)}</pre>
      {/* Aquí puedes armar tu formulario de edición de MIC */}
    </div>
  );
}
export default MICNuevo;
