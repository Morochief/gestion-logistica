import React, { useEffect, useState } from "react";
import api from "../api/api";
import Table from "../components/Table";
import FormModal from "../components/FormModal";

function Movimientos() {
  const [movimientos, setMovimientos] = useState([]);
  const [remitentes, setRemitentes] = useState([]);
  const [transportadoras, setTransportadoras] = useState([]);
  const [monedas, setMonedas] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editMov, setEditMov] = useState(null);

  const formFields = [
    { name: "fecha", label: "Fecha", required: true, type: "date" },
    { name: "monto", label: "Monto", required: true, type: "number" },
    {
      name: "moneda_id",
      label: "Moneda",
      required: true,
      type: "select",
      options: Array.isArray(monedas) ? monedas.map((m) => ({ value: m.id, label: m.nombre })) : [],
    },
    {
      name: "remitente_id",
      label: "Remitente",
      required: true,
      type: "select",
      options: Array.isArray(remitentes) ? remitentes.map((r) => ({ value: r.id, label: r.nombre })) : [],
    },
    {
      name: "transportadora_id",
      label: "Transportadora",
      required: true,
      type: "select",
      options: Array.isArray(transportadoras) ? transportadoras.map((t) => ({ value: t.id, label: t.nombre })) : [],
    },
    {
      name: "usuario_id",
      label: "Usuario",
      required: true,
      type: "select",
      options: Array.isArray(usuarios) ? usuarios.map((u) => ({ value: u.id, label: u.nombre_completo })) : [],
    },
    { name: "tipo", label: "Tipo", required: true },
    { name: "descripcion", label: "Descripción", required: false },
    { name: "estado", label: "Estado", required: false },
  ];

  useEffect(() => {
    fetchRemitentes();
    fetchTransportadoras();
    fetchMonedas();
    fetchUsuarios();
    fetchMovimientos();
    // eslint-disable-next-line
  }, []);

  const fetchRemitentes = async () => {
    const res = await api.get("/remitentes/");
    setRemitentes(res.data.items || res.data);
  };

  const fetchTransportadoras = async () => {
    const res = await api.get("/transportadoras/");
    setTransportadoras(res.data.items || res.data);
  };

  const fetchMonedas = async () => {
    const res = await api.get("/monedas/");
    setMonedas(res.data.items || res.data);
  };

  const fetchUsuarios = async () => {
    const res = await api.get("/usuarios/");
    setUsuarios(res.data.items || res.data);
  };

  const fetchMovimientos = async () => {
    const res = await api.get("/movimientos/");
    setMovimientos(res.data.items || res.data);
  };

  const handleAdd = () => {
    setEditMov(null);
    setModalOpen(true);
  };

  const handleEdit = (mov) => {
    setEditMov(mov);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Seguro que deseas eliminar este movimiento?")) {
      await api.delete(`/movimientos/${id}`);
      fetchMovimientos();
    }
  };

  const handleSubmit = async (data) => {
    try {
      if (editMov) {
        await api.put(`/movimientos/${editMov.id}`, data);
      } else {
        await api.post("/movimientos/", data);
      }
      setModalOpen(false);
      fetchMovimientos();
    } catch (e) {
      alert("Error al guardar movimiento: " + (e.response?.data?.error || e.message));
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Movimientos</h2>
      <button onClick={handleAdd}>Agregar Movimiento</button>
      <Table
        columns={[
          { field: "fecha", label: "Fecha" },
          { field: "monto", label: "Monto" },
          { field: "moneda_id", label: "Moneda", render: (id) => monedas.find(m => m.id === id)?.nombre || id },
          { field: "remitente_id", label: "Remitente", render: (id) => remitentes.find(r => r.id === id)?.nombre || id },
          { field: "transportadora_id", label: "Transportadora", render: (id) => transportadoras.find(t => t.id === id)?.nombre || id },
          { field: "usuario_id", label: "Usuario", render: (id) => usuarios.find(u => u.id === id)?.nombre_completo || id },
          { field: "tipo", label: "Tipo" },
          { field: "descripcion", label: "Descripción" },
          { field: "estado", label: "Estado" },
        ]}
        data={movimientos}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <FormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        initialValues={editMov}
        fields={formFields}
        title={editMov ? "Editar Movimiento" : "Nuevo Movimiento"}
      />
    </div>
  );
}

export default Movimientos;
