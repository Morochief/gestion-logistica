import React from "react";
import { useParams } from "react-router-dom";

function MICDetalle() {
  const { id } = useParams();
  // Aquí puedes hacer fetch al MIC por id
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Detalle MIC #{id}</h2>
      {/* Renderiza los datos del MIC */}
    </div>
  );
}
export default MICDetalle;
