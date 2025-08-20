import React, { useEffect, useState } from "react";
import { Search, Plus, Edit3, Trash2, Globe, MapPin, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

// Configuración de la API
const API_BASE_URL = "http://localhost:5000/api"; // Ajusta según tu configuración

// Componente Table mejorado
const EnhancedTable = ({ columns, data, onEdit, onDelete, loading }) => {
  const [searchTerm, setSearchTerm] = useState("");
  
  const filteredData = data.filter(item =>
    Object.values(item).some(value =>
      value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
        <div className="p-12 text-center">
          <Loader2 className="w-12 h-12 text-blue-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600 text-lg">Cargando países...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
      {/* Search Header */}
      <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-100">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Buscar países..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
          />
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
            {filteredData.map((item, index) => (
              <tr
                key={item.id || index}
                className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-300 group"
              >
                {columns.map((column) => (
                  <td key={column.field} className="px-6 py-4 text-gray-900">
                    {column.field === 'codigo' && (
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                          {item[column.field]?.slice(0, 2)?.toUpperCase() || '?'}
                        </div>
                        <span className="font-medium">{item[column.field]}</span>
                      </div>
                    )}
                    {column.field === 'nombre' && (
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <span className="font-medium">{item[column.field]}</span>
                      </div>
                    )}
                    {column.field !== 'codigo' && column.field !== 'nombre' && item[column.field]}
                  </td>
                ))}
                <td className="px-6 py-4">
                  <div className="flex justify-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button
                      onClick={() => onEdit(item)}
                      className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-all duration-300 hover:scale-110"
                      title="Editar país"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onDelete(item.id)}
                      className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-all duration-300 hover:scale-110"
                      title="Eliminar país"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredData.length === 0 && !loading && (
          <div className="text-center py-12">
            <Globe className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">
              {data.length === 0 ? "No hay países registrados" : "No se encontraron países"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Componente FormModal mejorado
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

  const validateForm = () => {
    const newErrors = {};
    
    // Validar código
    if (formData.codigo) {
      if (formData.codigo.length !== 2) {
        newErrors.codigo = "El código debe tener exactamente 2 caracteres";
      } else if (!/^[A-Z]{2}$/.test(formData.codigo.toUpperCase())) {
        newErrors.codigo = "El código debe contener solo letras mayúsculas";
      }
    }
    
    // Validar nombre
    if (!formData.nombre || formData.nombre.trim().length < 2) {
      newErrors.nombre = "El nombre debe tener al menos 2 caracteres";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const dataToSubmit = {
        ...formData,
        codigo: formData.codigo?.toUpperCase()
      };
      
      await onSubmit(dataToSubmit);
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full transform transition-all duration-300 scale-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <Globe className="w-6 h-6 text-white" />
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
        <div className="p-6 space-y-4">
          {fields.map((field) => (
            <div key={field.name} className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <div className="relative">
                <input
                  type={field.type || "text"}
                  value={formData[field.name] || ""}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  readOnly={field.readOnly}
                  required={field.required}
                  maxLength={field.name === 'codigo' ? 2 : undefined}
                  className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    field.readOnly 
                      ? 'bg-gray-50 text-gray-500' 
                      : 'bg-white hover:border-blue-300'
                  } ${errors[field.name] ? 'border-red-300' : 'border-gray-200'}`}
                />
                {field.name === 'codigo' && !field.readOnly && formData[field.name] && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-600 rounded flex items-center justify-center text-white text-xs font-bold">
                      {formData[field.name]?.slice(0, 2)?.toUpperCase() || '?'}
                    </div>
                  </div>
                )}
              </div>
              {errors[field.name] && (
                <p className="text-red-500 text-sm flex items-center space-x-1">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errors[field.name]}</span>
                </p>
              )}
            </div>
          ))}

          {/* Actions */}
          <div className="flex space-x-3 pt-6">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 py-3 px-4 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-300 font-medium disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              onClick={handleSubmit}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-xl hover:from-blue-700 hover:to-indigo-800 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
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

// Componente de Notificación
const NotificationToast = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);
    
    return () => clearTimeout(timer);
  }, [onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-blue-600" />;
    }
  };

  const getColors = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  return (
    <div className={`fixed top-4 right-4 z-50 p-4 rounded-xl border ${getColors()} shadow-lg transform transition-all duration-300`}>
      <div className="flex items-center space-x-3">
        {getIcon()}
        <span className="font-medium">{message}</span>
        <button
          onClick={onClose}
          className="ml-auto text-gray-500 hover:text-gray-700"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

// Componente principal funcional
function Paises() {
  const [paises, setPaises] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editPais, setEditPais] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const formFields = [
    ...(editPais
      ? [
          {
            name: "codigo",
            label: "Código",
            readOnly: true,
            type: "text",
          },
        ]
      : []),
    { name: "nombre", label: "Nombre del País", required: true },
    ...(!editPais
      ? [{ name: "codigo", label: "Código ISO (2 letras)", required: true, maxLength: 2 }]
      : []),
  ];

  // Función para mostrar notificaciones
  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
  };

  // Función para hacer peticiones HTTP
  const apiCall = async (url, method = 'GET', data = null) => {
    try {
      const config = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (data) {
        config.body = JSON.stringify(data);
      }

      const response = await fetch(`${API_BASE_URL}${url}`, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  };

  // Cargar países desde la API
  const fetchPaises = async () => {
    setIsLoading(true);
    try {
      const response = await apiCall('/crts/data/paises');
      setPaises(response.items || []);
      showNotification(`${response.items?.length || 0} países cargados exitosamente`, 'success');
    } catch (error) {
      console.error('Error fetching países:', error);
      showNotification('Error al cargar países: ' + error.message, 'error');
      // Datos de fallback en caso de error
      setPaises([
        { id: 1, codigo: 'PY', nombre: 'Paraguay' },
        { id: 2, codigo: 'AR', nombre: 'Argentina' },
        { id: 3, codigo: 'BR', nombre: 'Brasil' },
        { id: 4, codigo: 'UY', nombre: 'Uruguay' },
        { id: 5, codigo: 'BO', nombre: 'Bolivia' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPaises();
  }, []);

  const handleAdd = () => {
    setEditPais(null);
    setModalOpen(true);
  };

  const handleEdit = (pais) => {
    setEditPais(pais);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Estás seguro de que deseas eliminar este país?")) {
      return;
    }

    try {
      await apiCall(`/paises/${id}`, 'DELETE');
      setPaises(prev => prev.filter(p => p.id !== id));
      showNotification('País eliminado exitosamente', 'success');
    } catch (error) {
      showNotification('Error al eliminar país: ' + error.message, 'error');
    }
  };

  const handleSubmit = async (data) => {
    try {
      if (editPais) {
        // Actualizar país existente
        const response = await apiCall(`/paises/${editPais.id}`, 'PUT', data);
        setPaises(prev => prev.map(p => p.id === editPais.id ? { ...p, ...data } : p));
        showNotification('País actualizado exitosamente', 'success');
      } else {
        // Crear nuevo país
        const response = await apiCall('/paises', 'POST', data);
        const newPais = { ...data, id: response.id || Date.now() };
        setPaises(prev => [...prev, newPais]);
        showNotification('País creado exitosamente', 'success');
      }
      setModalOpen(false);
    } catch (error) {
      showNotification('Error al guardar país: ' + error.message, 'error');
      throw error; // Re-throw para que el modal maneje el estado de loading
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-lg">
                <Globe className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Gestión de Países</h1>
                <p className="text-gray-600 text-lg">Administra la información de países del sistema</p>
              </div>
            </div>
            
            <button
              onClick={handleAdd}
              disabled={isLoading}
              className="group bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-indigo-800 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">Agregar País</span>
            </button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Países</p>
                  <p className="text-3xl font-bold text-gray-900">{paises.length}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <Globe className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Regiones</p>
                  <p className="text-3xl font-bold text-gray-900">5</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <MapPin className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Estado</p>
                  <p className="text-lg font-bold text-gray-900">
                    {isLoading ? 'Cargando...' : 'Conectado'}
                  </p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                  <div className={`w-3 h-3 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500 animate-pulse'}`}></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Table */}
        <EnhancedTable
          columns={[
            { field: "codigo", label: "Código" },
            { field: "nombre", label: "Nombre del País" }
          ]}
          data={paises}
          onEdit={handleEdit}
          onDelete={handleDelete}
          loading={isLoading}
        />

        {/* Modal */}
        <EnhancedFormModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onSubmit={handleSubmit}
          initialValues={editPais}
          fields={formFields}
          title={editPais ? "Editar País" : "Nuevo País"}
        />

        {/* Notification Toast */}
        {notification && (
          <NotificationToast
            message={notification.message}
            type={notification.type}
            onClose={() => setNotification(null)}
          />
        )}
      </div>
    </div>
  );
}

export default Paises;