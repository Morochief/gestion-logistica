import React, { useEffect, useState } from "react";
import api from "../api/api";
import Table from "../components/Table";
import FormModal from "../components/FormModal";

function Honorarios() {
  const [honorarios, setHonorarios] = useState([]);
  const [transportadoras, setTransportadoras] = useState([]);
  const [monedas, setMonedas] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editHonorario, setEditHonorario] = useState(null);

  useEffect(() => {
    fetchTransportadoras();
    fetchMonedas();
    fetchHonorarios();
    // eslint-disable-next-line
  }, []);

  const fetchTransportadoras = async () => {
    const res = await api.get("/transportadoras/");
    setTransportadoras(res.data.items || res.data);
  };

  const fetchMonedas = async () => {
    const res = await api.get("/monedas/");
    setMonedas(res.data.items || res.data);
  };

  const fetchHonorarios = async () => {
    const res = await api.get("/honorarios/");
    setHonorarios(res.data);
  };

  const handleAdd = () => {
    setEditHonorario(null);
    setModalOpen(true);
  };

  const handleEdit = (honorario) => {
    setEditHonorario(honorario);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Seguro que deseas eliminar este honorario?")) {
      await api.delete(`/honorarios/${id}`);
      fetchHonorarios();
    }
  };

  const handleSubmit = async (data) => {
    if (!data.transportadora_id || !data.moneda_id) {
      alert("Debes seleccionar transportadora y moneda.");
      return;
    }
    try {
      if (editHonorario) {
        await api.put(`/honorarios/${editHonorario.id}`, data);
      } else {
        await api.post("/honorarios/", data);
      }
      setModalOpen(false);
      fetchHonorarios();
    } catch (e) {
      alert("Error al guardar honorario: " + (e.response?.data?.error || e.message));
    }
  };

  const formFields = [
    ...(editHonorario
      ? [
          {
            name: "codigo",
            label: "Código",
            readOnly: true,
            type: "text",
          },
        ]
      : []),
    {
      name: "transportadora_id",
      label: "Transportadora",
      required: true,
      type: "select",
      options: [
        { value: "", label: "---Seleccionar Transportadora---" },
        ...transportadoras.map((t) => ({ value: t.id, label: t.nombre })),
      ],
    },
    { name: "monto", label: "Monto", required: true, type: "number" },
    {
      name: "moneda_id",
      label: "Moneda",
      required: true,
      type: "select",
      options: [
        { value: "", label: "---Seleccionar Moneda---" },
        ...monedas.map((m) => ({ value: m.id, label: m.nombre })),
      ],
    },
  ];

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Honorarios</h2>
      <button onClick={handleAdd}>Agregar Honorario</button>
      <Table
        columns={[
          { field: "codigo", label: "Código" },
          { field: "transportadora_nombre", label: "Transportadora" },
          { field: "monto", label: "Monto" },
          { field: "moneda_nombre", label: "Moneda" },
        ]}
        data={honorarios}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <FormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        initialValues={editHonorario}
        fields={formFields}
        title={editHonorario ? "Editar Honorario" : "Nuevo Honorario"}
      />
    </div>
  );
}

export default Honorarios;