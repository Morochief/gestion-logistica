import React, { useEffect, useState } from "react";
import api from "../api/api";
import Table from "../components/Table";
import FormModal from "../components/FormModal";

function Reportes() {
  const [reportes, setReportes] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editReporte, setEditReporte] = useState(null);

  const formFields = [
    { name: "tipo", label: "Tipo", required: true },
    { name: "datos", label: "Datos (texto/JSON)", required: true },
    {
      name: "generado_por",
      label: "Generado por (Usuario)",
      required: true,
      type: "select",
      options: usuarios.map((u) => ({ value: u.id, label: u.nombre_completo })),
    },
    { name: "generado_en", label: "Fecha", required: false, type: "datetime-local" },
  ];

  useEffect(() => {
    fetchUsuarios();
    fetchReportes();
    // eslint-disable-next-line
  }, []);

  const fetchUsuarios = async () => {
    const res = await api.get("/usuarios/");
    setUsuarios(res.data.items || res.data);
  };

  const fetchReportes = async () => {
    const res = await api.get("/reportes/");
    setReportes(res.data.items || res.data);
  };

  const handleAdd = () => {
    setEditReporte(null);
    setModalOpen(true);
  };

  const handleEdit = (reporte) => {
    setEditReporte(reporte);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Seguro que deseas eliminar este reporte?")) {
      await api.delete(`/reportes/${id}`);
      fetchReportes();
    }
  };

  const handleSubmit = async (data) => {
    try {
      if (editReporte) {
        // No hay endpoint para modificar en backend, solo crear/eliminar.
        alert("La edición de reportes no está soportada.");
      } else {
        await api.post("/reportes/", data);
      }
      setModalOpen(false);
      fetchReportes();
    } catch (e) {
      alert("Error al guardar reporte: " + (e.response?.data?.error || e.message));
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Reportes</h2>
      <button onClick={handleAdd}>Nuevo Reporte</button>
      <Table
        columns={[
          { field: "tipo", label: "Tipo" },
          { field: "datos", label: "Datos" },
          { field: "generado_por", label: "Usuario", render: (id) => usuarios.find(u => u.id === id)?.nombre_completo || id },
          { field: "generado_en", label: "Fecha" },
        ]}
        data={reportes}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <FormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        initialValues={editReporte}
        fields={formFields}
        title={editReporte ? "Editar Reporte" : "Nuevo Reporte"}
      />
    </div>
  );
}

export default Reportes;
