import React, { useEffect, useState } from "react";
import api from "../api/api";
import { Search, Plus, Edit3, Trash2, Users, FileText, MapPin, Building2, CreditCard, ChevronLeft, ChevronRight } from "lucide-react";

// Componente de Paginación
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const getPageNumbers = () => {
    const delta = 2;
    const range = [];
    const rangeWithDots = [];

    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }

    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...');
    } else {
      rangeWithDots.push(1);
    }

    rangeWithDots.push(...range);

    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages);
    } else if (totalPages > 1) {
      rangeWithDots.push(totalPages);
    }

    return rangeWithDots;
  };

  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center space-x-2 mt-6">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>

      {getPageNumbers().map((page, index) => (
        <button
          key={index}
          onClick={() => typeof page === 'number' && onPageChange(page)}
          disabled={page === '...'}
          className={`px-3 py-2 rounded-lg transition-all duration-300 ${
            page === currentPage
              ? 'bg-purple-600 text-white shadow-md'
              : page === '...'
              ? 'cursor-default'
              : 'border border-gray-300 hover:bg-gray-50'
          }`}
        >
          {page}
        </button>
      ))}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
      >
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
};

// Componente Table con paginación
const EnhancedTable = ({ columns, data, onEdit, onDelete, pagination, onPageChange, onSearch }) => {
  const [searchTerm, setSearchTerm] = useState("");

  const handleSearch = (value) => {
    setSearchTerm(value);
    if (onSearch) {
      onSearch(value);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
      {/* Search Header */}
      <div className="p-6 bg-gradient-to-r from-purple-50 to-violet-50 border-b border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Buscar remitentes..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
            />
          </div>
          {pagination && (
            <div className="text-sm text-gray-600 ml-4">
              Mostrando {data.length} de {pagination.total} registros
            </div>
          )}
        </div>
      </div>
      
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              {columns.map((column) => (
                <th
                  key={column.field}
                  className="px-6 py-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider"
                >
                  {column.label}
                </th>
              ))}
              <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map((item, index) => (
              <tr
                key={item.id || index}
                className="hover:bg-gradient-to-r hover:from-purple-50 hover:to-violet-50 transition-all duration-300 group"
              >
                {columns.map((column) => (
                  <td key={column.field} className="px-6 py-4 text-gray-900">
                    {column.field === 'tipo_documento' && (
                      <div className="flex items-center space-x-2">
                        <CreditCard className="w-4 h-4 text-gray-400" />
                        <div className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium uppercase">
                          {item[column.field]}
                        </div>
                      </div>
                    )}
                    {column.field === 'numero_documento' && (
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-gray-400" />
                        <span className="font-mono text-sm">{item[column.field]}</span>
                      </div>
                    )}
                    {column.field === 'nombre' && (
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4 text-gray-400" />
                        <span className="font-medium">{item[column.field]}</span>
                      </div>
                    )}
                    {column.field === 'direccion' && (
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-700 text-sm">{item[column.field]}</span>
                      </div>
                    )}
                    {column.field === 'ciudad_nombre' && (
                      <div className="flex items-center space-x-2">
                        <Building2 className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-700">{item[column.field]}</span>
                        <div className="px-2 py-1 bg-violet-100 text-violet-700 rounded-full text-xs font-medium">
                          Ciudad
                        </div>
                      </div>
                    )}
                    {!['tipo_documento', 'numero_documento', 'nombre', 'direccion', 'ciudad_nombre'].includes(column.field) && item[column.field]}
                  </td>
                ))}
                <td className="px-6 py-4">
                  <div className="flex justify-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button
                      onClick={() => onEdit(item)}
                      className="p-2 text-purple-600 hover:bg-purple-100 rounded-lg transition-all duration-300 hover:scale-110"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onDelete(item.id)}
                      className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-all duration-300 hover:scale-110"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {data.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No se encontraron remitentes</p>
          </div>
        )}
      </div>

      {/* Paginación */}
      {pagination && (
        <div className="p-6 border-t border-gray-100">
          <Pagination
            currentPage={pagination.current_page}
            totalPages={pagination.pages}
            onPageChange={onPageChange}
          />
        </div>
      )}
    </div>
  );
};

// Componente FormModal
const EnhancedFormModal = ({ open, onClose, onSubmit, initialValues, fields, title }) => {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setFormData(initialValues || {});
      setErrors({});
    }
  }, [open, initialValues]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full transform transition-all duration-300 scale-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-violet-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">{title}</h3>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-all duration-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Form */}
        <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
          {fields.map((field) => (
            <div key={field.name} className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <div className="relative">
                {field.type === 'select' ? (
                  <select
                    value={formData[field.name] || ""}
                    onChange={(e) => handleChange(field.name, e.target.value)}
                    required={field.required}
                    className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white hover:border-purple-300 ${
                      errors[field.name] ? 'border-red-300' : 'border-gray-200'
                    }`}
                  >
                    <option value="">---Seleccionar Ciudad---</option>
                    {field.options?.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={field.type || "text"}
                    value={formData[field.name] || ""}
                    onChange={(e) => handleChange(field.name, e.target.value)}
                    readOnly={field.readOnly}
                    required={field.required}
                    placeholder={field.placeholder}
                    className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                      field.readOnly 
                        ? 'bg-gray-50 text-gray-500' 
                        : 'bg-white hover:border-purple-300'
                    } ${errors[field.name] ? 'border-red-300' : 'border-gray-200'}`}
                  />
                )}
              </div>
              {errors[field.name] && (
                <p className="text-red-500 text-sm">{errors[field.name]}</p>
              )}
            </div>
          ))}

          {/* Actions */}
          <div className="flex space-x-3 pt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 px-4 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-300 font-medium"
            >
              Cancelar
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-purple-600 to-violet-700 text-white rounded-xl hover:from-purple-700 hover:to-violet-800 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Guardando...</span>
                </>
              ) : (
                <span>{initialValues ? 'Actualizar' : 'Crear'}</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Componente principal
function Remitentes() {
  const [remitentes, setRemitentes] = useState([]);
  const [ciudades, setCiudades] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editRemitente, setEditRemitente] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current_page: 1,
    pages: 1,
    total: 0
  });
  const [currentSearch, setCurrentSearch] = useState("");

  const formFields = [
    ...(editRemitente
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
      name: "tipo_documento",
      label: "Tipo de Documento",
      required: true,
      type: "text",
      placeholder: "Ej: RUC, CNPJ, RUT",
    },
    {
      name: "numero_documento",
      label: "Número de Documento",
      required: true,
      type: "text",
      placeholder: "Ej: 80084948-5",
    },
    { name: "nombre", label: "Nombre del Remitente", required: true },
    { name: "direccion", label: "Dirección Completa", required: true },
    {
      name: "ciudad_id",
      label: "Ciudad",
      required: true,
      type: "select",
      options: ciudades.map((c) => ({ value: c.id, label: c.nombre })),
    },
  ];

  useEffect(() => {
    fetchCiudades();
    fetchRemitentes(1, "");
  }, []);

  const fetchCiudades = async () => {
    try {
      const res = await api.get("/ciudades/");
      setCiudades(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error('Error fetching ciudades:', error);
    }
  };

  const fetchRemitentes = async (page = 1, search = "") => {
    setIsLoading(true);
    try {
      const queryParams = new URLSearchParams({
        page: page.toString(),
        per_page: '50' // Aumentar para mostrar más registros
      });
      
      if (search) {
        queryParams.set('q', search);
      }
      
      const res = await api.get(`/remitentes/?${queryParams}`);
      setRemitentes(Array.isArray(res.data.items) ? res.data.items : []);
      setPagination({
        current_page: res.data.current_page,
        pages: res.data.pages,
        total: res.data.total
      });
    } catch (error) {
      console.error('Error fetching remitentes:', error);
      // En caso de error, mostrar mensaje al usuario
      setRemitentes([]);
      setPagination({ current_page: 1, pages: 1, total: 0 });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePageChange = (page) => {
    fetchRemitentes(page, currentSearch);
  };

  const handleSearch = (searchTerm) => {
    setCurrentSearch(searchTerm);
    // Debounce la búsqueda
    const timeoutId = setTimeout(() => {
      fetchRemitentes(1, searchTerm);
    }, 500);

    return () => clearTimeout(timeoutId);
  };

  const handleAdd = () => {
    setEditRemitente(null);
    setModalOpen(true);
  };

  const handleEdit = (remitente) => {
    setEditRemitente(remitente);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Estás seguro de que deseas eliminar este remitente?")) {
      try {
        await api.delete(`/remitentes/${id}`);
        alert("Remitente eliminado correctamente.");
        fetchRemitentes(pagination.current_page, currentSearch);
      } catch (e) {
        alert("Error al eliminar: " + (e.response?.data?.error || e.message));
      }
    }
  };

  const handleSubmit = async (data) => {
    if (!data.ciudad_id) {
      alert("Debes seleccionar una ciudad.");
      return;
    }
    if (!data.tipo_documento || !data.numero_documento) {
      alert("Debes cargar tipo y número de documento.");
      return;
    }
    
    try {
      if (editRemitente) {
        await api.put(`/remitentes/${editRemitente.id}`, data);
      } else {
        await api.post("/remitentes/", data);
      }
      setModalOpen(false);
      fetchRemitentes(pagination.current_page, currentSearch);
    } catch (e) {
      alert("Error al guardar remitente: " + (e.response?.data?.error || e.message));
    }
  };

  // Calcular estadísticas
  const totalRemitentes = pagination.total;
  const tiposDocumento = [...new Set(remitentes.map(r => r.tipo_documento))].length;
  const ciudadesConRemitentes = [...new Set(remitentes.map(r => r.ciudad_id))].length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-violet-700 rounded-2xl flex items-center justify-center shadow-lg">
                <Users className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Gestión de Remitentes</h1>
                <p className="text-gray-600 text-lg">Administra los remitentes y sus documentos de identificación</p>
              </div>
            </div>
            
            <button
              onClick={handleAdd}
              className="group bg-gradient-to-r from-purple-600 to-violet-700 text-white px-6 py-3 rounded-xl hover:from-purple-700 hover:to-violet-800 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">Agregar Remitente</span>
            </button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Remitentes</p>
                  <p className="text-3xl font-bold text-gray-900">{totalRemitentes}</p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Tipos de Documento</p>
                  <p className="text-3xl font-bold text-gray-900">{tiposDocumento}</p>
                </div>
                <div className="w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center">
                  <CreditCard className="w-6 h-6 text-violet-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Ciudades con Remitentes</p>
                  <p className="text-3xl font-bold text-gray-900">{ciudadesConRemitentes}</p>
                </div>
                <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-indigo-600" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Cargando remitentes...</p>
          </div>
        ) : (
          <EnhancedTable
            columns={[
              { field: "tipo_documento", label: "Tipo Doc." },
              { field: "numero_documento", label: "Nro. Doc." },
              { field: "nombre", label: "Nombre" },
              { field: "direccion", label: "Dirección" },
              { field: "ciudad_nombre", label: "Ciudad" },
            ]}
            data={Array.isArray(remitentes) ? remitentes : []}
            onEdit={handleEdit}
            onDelete={handleDelete}
            pagination={pagination}
            onPageChange={handlePageChange}
            onSearch={handleSearch}
          />
        )}

        {/* Modal */}
        <EnhancedFormModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onSubmit={handleSubmit}
          initialValues={editRemitente}
          fields={formFields}
          title={editRemitente ? "Editar Remitente" : "Nuevo Remitente"}
        />
      </div>
    </div>
  );
}

export default Remitentes;