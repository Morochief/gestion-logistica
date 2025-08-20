import React, { useEffect, useState } from "react";
import api from "../api/api";
import Table from "../components/Table";
import FormModal from "../components/FormModal";

function Usuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [paginacion, setPaginacion] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [formFields] = useState([
    { name: "nombre_completo", label: "Nombre Completo", required: true },
    { name: "usuario", label: "Usuario", required: true },
    { name: "rol", label: "Rol", required: false },
    { name: "estado", label: "Estado", required: false },
    { name: "clave", label: "Contraseña", type: "password", required: false },
  ]);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchUsuarios(page);
  }, [page]);

  const fetchUsuarios = async (page) => {
    const res = await api.get(`/usuarios/?page=${page}`);
    setUsuarios(res.data.items);
    setPaginacion({
      total: res.data.total,
      pages: res.data.pages,
      current: res.data.current_page,
    });
  };

  const handleAdd = () => {
    setEditUser(null);
    setModalOpen(true);
  };

  const handleEdit = (user) => {
    setEditUser(user);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Seguro que deseas eliminar este usuario?")) {
      await api.delete(`/usuarios/${id}`);
      fetchUsuarios(page);
    }
  };

  const handleSubmit = async (data) => {
    try {
      if (editUser) {
        await api.put(`/usuarios/${editUser.id}`, data);
      } else {
        await api.post("/usuarios/", data);
      }
      setModalOpen(false);
      fetchUsuarios(page);
    } catch (e) {
      alert("Error al guardar usuario: " + (e.response?.data?.error || e.message));
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Usuarios</h2>
      <button onClick={handleAdd}>Agregar Usuario</button>
      <Table
        columns={[
          { field: "nombre_completo", label: "Nombre Completo" },
          { field: "usuario", label: "Usuario" },
          { field: "rol", label: "Rol" },
          { field: "estado", label: "Estado" },
          { field: "creado_en", label: "Creado" },
        ]}
        data={usuarios}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <div style={{ marginTop: 16 }}>
        Página: {paginacion.current || 1} de {paginacion.pages || 1}
        <button
          onClick={() => setPage(Math.max(1, (paginacion.current || 1) - 1))}
          disabled={paginacion.current <= 1}
          style={{ marginLeft: 8 }}
        >
          Anterior
        </button>
        <button
          onClick={() => setPage(Math.min((paginacion.pages || 1), (paginacion.current || 1) + 1))}
          disabled={paginacion.current >= paginacion.pages}
          style={{ marginLeft: 8 }}
        >
          Siguiente
        </button>
      </div>
      <FormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        initialValues={editUser}
        fields={formFields}
        title={editUser ? "Editar Usuario" : "Nuevo Usuario"}
      />
    </div>
  );
}

export default Usuarios;
