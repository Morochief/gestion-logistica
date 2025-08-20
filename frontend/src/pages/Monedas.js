import React, { useState, useEffect } from "react";
// import axios from "axios"; // Simulado para el ejemplo
import { Search, Plus, Coins, DollarSign, Hash, Type, AlertCircle, CheckCircle, Edit3, Trash2 } from "lucide-react";

// Simulación de axios para el ejemplo
const axios = {
  get: async (url) => {
    // Simulando datos de ejemplo
    return {
      data: [
        { id: 1, codigo: 'USD', nombre: 'Dólar Estadounidense', simbolo: '$' },
        { id: 2, codigo: 'EUR', nombre: 'Euro', simbolo: '€' },
        { id: 3, codigo: 'PYG', nombre: 'Guaraní Paraguayo', simbolo: '₲' },
      ]
    };
  },
  post: async (url, data) => ({ data: { id: Date.now(), ...data } }),
  put: async (url, data) => ({ data }),
  delete: async (url) => ({ data: { message: 'Deleted' } })
};

// Componente para mostrar monedas en cards
const MonedaCard = ({ moneda, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-amber-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-bold text-lg">{moneda.simbolo}</span>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">{moneda.nombre}</h3>
            <p className="text-gray-600 text-sm">{moneda.codigo}</p>
          </div>
        </div>
        
        <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <button
            onClick={() => onEdit(moneda)}
            className="p-2 text-yellow-600 hover:bg-yellow-100 rounded-lg transition-all duration-300 hover:scale-110"
          >
            <Edit3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(moneda.id)}
            className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-all duration-300 hover:scale-110"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center space-x-2 text-sm">
          <Hash className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Código:</span>
          <span className="font-mono bg-gray-100 px-2 py-1 rounded text-gray-800">{moneda.codigo}</span>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <DollarSign className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Símbolo:</span>
          <span className="font-bold text-yellow-600 text-lg">{moneda.simbolo}</span>
        </div>
      </div>
    </div>
  );
};

// Modal para crear/editar moneda
const MonedaModal = ({ open, onClose, onSubmit, initialValues, title }) => {
  const [formData, setFormData] = useState({ codigo: '', nombre: '', simbolo: '' });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setFormData(initialValues || { codigo: '', nombre: '', simbolo: '' });
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
    const newErrors = {};
    if (!formData.codigo) newErrors.codigo = 'El código es obligatorio';
    if (!formData.nombre) newErrors.nombre = 'El nombre es obligatorio';
    if (!formData.simbolo) newErrors.simbolo = 'El símbolo es obligatorio';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full transform transition-all duration-300 scale-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-yellow-500 to-amber-600 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <Coins className="w-6 h-6 text-white" />
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
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              Código <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={formData.codigo}
                onChange={(e) => handleChange('codigo', e.target.value.toUpperCase())}
                placeholder="USD, EUR, PYG..."
                className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent ${
                  errors.codigo ? 'border-red-300' : 'border-gray-200'
                }`}
              />
              <Hash className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
            {errors.codigo && <p className="text-red-500 text-sm">{errors.codigo}</p>}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              Nombre <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={formData.nombre}
                onChange={(e) => handleChange('nombre', e.target.value)}
                placeholder="Dólar Estadounidense, Euro..."
                className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent ${
                  errors.nombre ? 'border-red-300' : 'border-gray-200'
                }`}
              />
              <Type className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
            {errors.nombre && <p className="text-red-500 text-sm">{errors.nombre}</p>}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              Símbolo <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={formData.simbolo}
                onChange={(e) => handleChange('simbolo', e.target.value)}
                placeholder="$, €, ₲..."
                className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent ${
                  errors.simbolo ? 'border-red-300' : 'border-gray-200'
                }`}
              />
              <DollarSign className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
            {errors.simbolo && <p className="text-red-500 text-sm">{errors.simbolo}</p>}
          </div>

          {/* Preview */}
          {formData.codigo || formData.nombre || formData.simbolo ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <h4 className="text-sm font-semibold text-yellow-800 mb-2">Vista previa:</h4>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-amber-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">{formData.simbolo || '?'}</span>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{formData.nombre || 'Nombre de la moneda'}</p>
                  <p className="text-sm text-gray-600">{formData.codigo || 'CÓDIGO'}</p>
                </div>
              </div>
            </div>
          ) : null}

          {/* Actions */}
          <div className="flex space-x-3 pt-4">
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
              className="flex-1 py-3 px-4 bg-gradient-to-r from-yellow-500 to-amber-600 text-white rounded-xl hover:from-yellow-600 hover:to-amber-700 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
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
const Monedas = () => {
  const [monedas, setMonedas] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editMoneda, setEditMoneda] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchMonedas();
  }, []);

  const fetchMonedas = async () => {
    setIsLoading(true);
    try {
      const res = await axios.get("http://localhost:5000/api/monedas/");
      setMonedas(res.data);
      setMensaje("");
    } catch (error) {
      setMensaje("Error cargando monedas");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editMoneda) {
        await axios.put(`http://localhost:5000/api/monedas/${editMoneda.id}`, formData);
        setMensaje("Moneda actualizada correctamente");
      } else {
        await axios.post("http://localhost:5000/api/monedas/", formData);
        setMensaje("Moneda agregada correctamente");
      }
      setModalOpen(false);
      setEditMoneda(null);
      fetchMonedas();
    } catch (error) {
      setMensaje("Error al guardar la moneda");
    }
  };

  const handleEdit = (moneda) => {
    setEditMoneda(moneda);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Estás seguro de que deseas eliminar esta moneda?")) {
      try {
        await axios.delete(`http://localhost:5000/api/monedas/${id}`);
        setMensaje("Moneda eliminada correctamente");
        fetchMonedas();
      } catch (error) {
        setMensaje("Error al eliminar la moneda");
      }
    }
  };

  const handleAdd = () => {
    setEditMoneda(null);
    setModalOpen(true);
  };

  const filteredMonedas = monedas.filter(moneda =>
    moneda.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    moneda.codigo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    moneda.simbolo.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-amber-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Coins className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Gestión de Monedas</h1>
                <p className="text-gray-600 text-lg">Administra las monedas del sistema</p>
              </div>
            </div>
            
            <button
              onClick={handleAdd}
              className="group bg-gradient-to-r from-yellow-500 to-amber-600 text-white px-6 py-3 rounded-xl hover:from-yellow-600 hover:to-amber-700 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">Agregar Moneda</span>
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Monedas</p>
                  <p className="text-3xl font-bold text-gray-900">{monedas.length}</p>
                </div>
                <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                  <Coins className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Símbolos Únicos</p>
                  <p className="text-3xl font-bold text-gray-900">{new Set(monedas.map(m => m.simbolo)).size}</p>
                </div>
                <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-amber-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Última Actualización</p>
                  <p className="text-lg font-bold text-gray-900">Hoy</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Search */}
          <div className="mb-6">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar monedas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition-all duration-300 bg-white"
              />
            </div>
          </div>

          {/* Mensaje */}
          {mensaje && (
            <div className={`mb-6 p-4 rounded-xl border flex items-center space-x-3 ${
              mensaje.includes('Error') || mensaje.includes('error')
                ? 'bg-red-50 border-red-200 text-red-700'
                : 'bg-green-50 border-green-200 text-green-700'
            }`}>
              {mensaje.includes('Error') || mensaje.includes('error') ? (
                <AlertCircle className="w-5 h-5" />
              ) : (
                <CheckCircle className="w-5 h-5" />
              )}
              <span className="font-medium">{mensaje}</span>
            </div>
          )}
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <div className="w-12 h-12 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Cargando monedas...</p>
          </div>
        ) : filteredMonedas.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <Coins className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {searchTerm ? 'No se encontraron monedas' : 'No hay monedas registradas'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchTerm 
                ? 'Intenta con otros términos de búsqueda'
                : 'Comienza agregando tu primera moneda al sistema'
              }
            </p>
            {!searchTerm && (
              <button
                onClick={handleAdd}
                className="bg-gradient-to-r from-yellow-500 to-amber-600 text-white px-6 py-3 rounded-xl hover:from-yellow-600 hover:to-amber-700 transition-all duration-300 font-medium"
              >
                Agregar Primera Moneda
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMonedas.map((moneda) => (
              <MonedaCard
                key={moneda.id}
                moneda={moneda}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}

        {/* Modal */}
        <MonedaModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onSubmit={handleSubmit}
          initialValues={editMoneda}
          title={editMoneda ? "Editar Moneda" : "Nueva Moneda"}
        />
      </div>
    </div>
  );
};

export default Monedas;