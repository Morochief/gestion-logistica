import React, { useEffect, useState } from "react";
import { Search, Plus, Edit3, Trash2, Building2, MapPin, Flag, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

// Configuración de la API
const API_BASE_URL = "http://localhost:5000/api"; // Ajusta según tu configuración

// Componente Table mejorado para ciudades
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
          <Loader2 className="w-12 h-12 text-emerald-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600 text-lg">Cargando ciudades...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
      {/* Search Header */}
      <div className="p-6 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-gray-100">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Buscar ciudades..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-300"
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
                className="hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 transition-all duration-300 group"
              >
                {columns.map((column) => (
                  <td key={column.field} className="px-6 py-4 text-gray-900">
                    {column.field === 'id' && (
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                          {item[column.field]}
                        </div>
                        <span className="font-medium">{item[column.field]}</span>
                      </div>
                    )}
                    {column.field === 'nombre' && (
                      <div className="flex items-center space-x-2">
                        <Building2 className="w-4 h-4 text-gray-400" />
                        <span className="font-medium">{item[column.field]}</span>
                      </div>
                    )}
                    {column.field === 'pais' && (
                      <div className="flex items-center space-x-2">
                        <Flag className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-700">{item[column.field]}</span>
                        <div className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">
                          País
                        </div>
                      </div>
                    )}
                    {!['id', 'nombre', 'pais'].includes(column.field) && item[column.field]}
                  </td>
                ))}
                <td className="px-6 py-4">
                  <div className="flex justify-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button
                      onClick={() => onEdit(item)}
                      className="p-2 text-emerald-600 hover:bg-emerald-100 rounded-lg transition-all duration-300 hover:scale-110"
                      title="Editar ciudad"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onDelete(item.id)}
                      className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-all duration-300 hover:scale-110"
                      title="Eliminar ciudad"
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
            <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">
              {data.length === 0 ? "No hay ciudades registradas" : "No se encontraron ciudades"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Componente FormModal mejorado para ciudades
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
    
    // Validar nombre
    if (!formData.nombre || formData.nombre.trim().length < 2) {
      newErrors.nombre = "El nombre debe tener al menos 2 caracteres";
    }
    
    // Validar país
    if (!formData.pais_id) {
      newErrors.pais_id = "Debe seleccionar un país";
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
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full transform transition-all duration-300 scale-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
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
                {field.type === 'select' ? (
                  <select
                    value={formData[field.name] || ""}
                    onChange={(e) => handleChange(field.name, parseInt(e.target.value) || e.target.value)}
                    required={field.required}
                    className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white hover:border-emerald-300 ${
                      errors[field.name] ? 'border-red-300' : 'border-gray-200'
                    }`}
                  >
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
                    className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-emerald-500 focus:border-transparent ${
                      field.readOnly 
                        ? 'bg-gray-50 text-gray-500' 
                        : 'bg-white hover:border-emerald-300'
                    } ${errors[field.name] ? 'border-red-300' : 'border-gray-200'}`}
                  />
                )}
                
                {field.name === 'nombre' && (
                  <Building2 className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                )}
                {field.name === 'pais_id' && field.type !== 'select' && (
                  <Flag className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
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
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-700 text-white rounded-xl hover:from-emerald-700 hover:to-teal-800 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
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
        return <AlertCircle className="w-5 h-5 text-emerald-600" />;
    }
  };

  const getColors = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-emerald-50 border-emerald-200 text-emerald-800';
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
function Ciudades() {
  const [ciudades, setCiudades] = useState([]);
  const [paises, setPaises] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editCiudad, setEditCiudad] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const formFields = [
    ...(editCiudad
      ? [
          {
            name: "id",
            label: "Código",
            readOnly: true,
            type: "text",
          },
        ]
      : []),
    { name: "nombre", label: "Nombre de la Ciudad", required: true },
    {
      name: "pais_id",
      label: "País",
      required: true,
      type: "select",
      options: [
        { value: "", label: "---Seleccionar País---" },
        ...paises.map((p) => ({ value: p.id, label: p.nombre })),
      ],
    },
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
    try {
      const response = await apiCall('/crts/data/paises');
      setPaises(response.items || []);
    } catch (error) {
      console.error('Error fetching países:', error);
      showNotification('Error al cargar países: ' + error.message, 'error');
      // Datos de fallback
      setPaises([
        { id: 1, nombre: 'Paraguay' },
        { id: 2, nombre: 'Argentina' },
        { id: 3, nombre: 'Brasil' },
        { id: 4, nombre: 'Uruguay' },
        { id: 5, nombre: 'Bolivia' },
      ]);
    }
  };

  // Cargar ciudades desde la API
  const fetchCiudades = async () => {
    setIsLoading(true);
    try {
      const response = await apiCall('/crts/data/ciudades');
      setCiudades(response.items || []);
      showNotification(`${response.items?.length || 0} ciudades cargadas exitosamente`, 'success');
    } catch (error) {
      console.error('Error fetching ciudades:', error);
      showNotification('Error al cargar ciudades: ' + error.message, 'error');
      // Datos de fallback
      setCiudades([
        { id: 1, nombre: 'Asunción', pais_id: 1, pais: 'Paraguay' },
        { id: 2, nombre: 'Ciudad del Este', pais_id: 1, pais: 'Paraguay' },
        { id: 3, nombre: 'Buenos Aires', pais_id: 2, pais: 'Argentina' },
        { id: 4, nombre: 'São Paulo', pais_id: 3, pais: 'Brasil' },
        { id: 5, nombre: 'Montevideo', pais_id: 4, pais: 'Uruguay' },
        { id: 6, nombre: 'La Paz', pais_id: 5, pais: 'Bolivia' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await fetchPaises(); // Cargar países primero
      await fetchCiudades(); // Luego cargar ciudades
    };
    loadData();
  }, []);

  const handleAdd = () => {
    setEditCiudad(null);
    setModalOpen(true);
  };

  const handleEdit = (ciudad) => {
    setEditCiudad(ciudad);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Estás seguro de que deseas eliminar esta ciudad?")) {
      return;
    }

    try {
      await apiCall(`/ciudades/${id}`, 'DELETE');
      setCiudades(prev => prev.filter(c => c.id !== id));
      showNotification('Ciudad eliminada exitosamente', 'success');
    } catch (error) {
      showNotification('Error al eliminar ciudad: ' + error.message, 'error');
    }
  };

  const handleSubmit = async (data) => {
    try {
      const paisSelected = paises.find(p => p.id === data.pais_id);
      
      if (editCiudad) {
        // Actualizar ciudad existente
        const response = await apiCall(`/ciudades/${editCiudad.id}`, 'PUT', data);
        setCiudades(prev => prev.map(c => 
          c.id === editCiudad.id 
            ? { ...c, ...data, pais: paisSelected?.nombre || '' }
            : c
        ));
        showNotification('Ciudad actualizada exitosamente', 'success');
      } else {
        // Crear nueva ciudad
        const response = await apiCall('/ciudades', 'POST', data);
        const newCiudad = { 
          ...data, 
          id: response.id || Date.now(), 
          pais: paisSelected?.nombre || '' 
        };
        setCiudades(prev => [...prev, newCiudad]);
        showNotification('Ciudad creada exitosamente', 'success');
      }
      setModalOpen(false);
    } catch (error) {
      showNotification('Error al guardar ciudad: ' + error.message, 'error');
      throw error; // Re-throw para que el modal maneje el estado de loading
    }
  };

  // Calcular estadísticas
  const totalCiudades = ciudades.length;
  const paisesConCiudades = [...new Set(ciudades.map(c => c.pais_id))].length;
  const ciudadMasReciente = ciudades[ciudades.length - 1]?.nombre || 'N/A';

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-600 to-teal-700 rounded-2xl flex items-center justify-center shadow-lg">
                <Building2 className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Gestión de Ciudades</h1>
                <p className="text-gray-600 text-lg">Administra las ciudades por país del sistema</p>
              </div>
            </div>
            
            <button
              onClick={handleAdd}
              disabled={isLoading}
              className="group bg-gradient-to-r from-emerald-600 to-teal-700 text-white px-6 py-3 rounded-xl hover:from-emerald-700 hover:to-teal-800 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">Agregar Ciudad</span>
            </button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Ciudades</p>
                  <p className="text-3xl font-bold text-gray-900">{totalCiudades}</p>
                </div>
                <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-emerald-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Países con Ciudades</p>
                  <p className="text-3xl font-bold text-gray-900">{paisesConCiudades}</p>
                </div>
                <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center">
                  <Flag className="w-6 h-6 text-teal-600" />
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
                <div className="w-12 h-12 bg-cyan-100 rounded-xl flex items-center justify-center">
                  <div className={`w-3 h-3 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500 animate-pulse'}`}></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Table */}
        <EnhancedTable
          columns={[
            { field: "id", label: "Código" },
            { field: "nombre", label: "Ciudad" },
            { field: "pais", label: "País" },
          ]}
          data={ciudades}
          onEdit={handleEdit}
          onDelete={handleDelete}
          loading={isLoading}
        />

        {/* Modal */}
        <EnhancedFormModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onSubmit={handleSubmit}
          initialValues={editCiudad}
          fields={formFields}
          title={editCiudad ? "Editar Ciudad" : "Nueva Ciudad"}
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

export default Ciudades;