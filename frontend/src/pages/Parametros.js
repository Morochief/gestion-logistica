import React, { useEffect, useState } from "react";
import api from "../api/api";
import Table from "../components/Table";
import FormModal from "../components/FormModal";

function Parametros() {
  const [parametros, setParametros] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editParametro, setEditParametro] = useState(null);

  const formFields = [
    { name: "clave", label: "Clave", required: true },
    { name: "valor", label: "Valor", required: true },
  ];

  useEffect(() => {
    fetchParametros();
  }, []);

  const fetchParametros = async () => {
    const res = await api.get("/parametros/");
    setParametros(res.data);
  };

  const handleAdd = () => {
    setEditParametro(null);
    setModalOpen(true);
  };

  const handleEdit = (param) => {
    setEditParametro(param);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Seguro que deseas eliminar este parámetro?")) {
      await api.delete(`/parametros/${id}`);
      fetchParametros();
    }
  };

  const handleSubmit = async (data) => {
    try {
      if (editParametro) {
        await api.put(`/parametros/${editParametro.id}`, data);
      } else {
        await api.post("/parametros/", data);
      }
      setModalOpen(false);
      fetchParametros();
    } catch (e) {
      alert("Error al guardar parámetro: " + (e.response?.data?.error || e.message));
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Parámetros</h2>
      <button onClick={handleAdd}>Agregar Parámetro</button>
      <Table
        columns={[
          { field: "clave", label: "Clave" },
          { field: "valor", label: "Valor" },
        ]}
        data={parametros}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <FormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        initialValues={editParametro}
        fields={formFields}
        title={editParametro ? "Editar Parámetro" : "Nuevo Parámetro"}
      />
    </div>
  );
}

export default Parametros;
