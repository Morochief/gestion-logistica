import React, { useEffect, useState } from "react";
import api from "../api/api";
import { Search, Plus, Edit3, Trash2, Truck, Phone, MapPin, Building2, CreditCard, FileText, DollarSign, Eye } from "lucide-react";

// Componente Table mejorado para transportadoras
const EnhancedTable = ({ columns, data, onEdit, onDelete }) => {
  const [searchTerm, setSearchTerm] = useState("");
  
  const filteredData = data.filter(item =>
    Object.values(item).some(value =>
      value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
      {/* Search Header */}
      <div className="p-6 bg-gradient-to-r from-orange-50 to-amber-50 border-b border-gray-100">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Buscar transportadoras..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-300"
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
                className="hover:bg-gradient-to-r hover:from-orange-50 hover:to-amber-50 transition-all duration-300 group"
              >
                {columns.map((column) => (
                  <td key={column.field} className="px-6 py-4 text-gray-900 text-sm">
                    {column.render ? (
                      column.render(item[column.field], item)
                    ) : (
                      <>
                        {column.field === 'codigo' && (
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-amber-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                              {item[column.field]?.slice(0, 2) || '?'}
                            </div>
                            <span className="font-medium">{item[column.field]}</span>
                          </div>
                        )}
                        {column.field === 'codigo_interno' && (
                          <div className="flex items-center space-x-2">
                            <FileText className="w-4 h-4 text-gray-400" />
                            <span className="font-mono text-sm">{item[column.field] || '-'}</span>
                          </div>
                        )}
                        {column.field === 'nombre' && (
                          <div className="flex items-center space-x-2">
                            <Truck className="w-4 h-4 text-gray-400" />
                            <span className="font-medium">{item[column.field]}</span>
                          </div>
                        )}
                        {column.field === 'direccion' && (
                          <div className="flex items-center space-x-2">
                            <MapPin className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-700 text-sm">{item[column.field] || '-'}</span>
                          </div>
                        )}
                        {column.field === 'tipo_documento' && (
                          <div className="flex items-center space-x-2">
                            <CreditCard className="w-4 h-4 text-gray-400" />
                            {item[column.field] ? (
                              <div className="px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium uppercase">
                                {item[column.field]}
                              </div>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </div>
                        )}
                        {column.field === 'numero_documento' && (
                          <div className="flex items-center space-x-2">
                            <FileText className="w-4 h-4 text-gray-400" />
                            <span className="font-mono text-sm">{item[column.field] || '-'}</span>
                          </div>
                        )}
                        {column.field === 'telefono' && (
                          <div className="flex items-center space-x-2">
                            <Phone className="w-4 h-4 text-gray-400" />
                            <span className="font-mono text-sm">{item[column.field] || '-'}</span>
                          </div>
                        )}
                        {!['codigo', 'codigo_interno', 'nombre', 'direccion', 'tipo_documento', 'numero_documento', 'telefono'].includes(column.field) && item[column.field]}
                      </>
                    )}
                  </td>
                ))}
                <td className="px-6 py-4">
                  <div className="flex justify-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button
                      onClick={() => onEdit(item)}
                      className="p-2 text-orange-600 hover:bg-orange-100 rounded-lg transition-all duration-300 hover:scale-110"
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
        
        {filteredData.length === 0 && (
          <div className="text-center py-12">
            <Truck className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No se encontraron transportadoras</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Componente FormModal mejorado para transportadoras
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
        <div className="bg-gradient-to-r from-orange-600 to-amber-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <Truck className="w-6 h-6 text-white" />
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
                    className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white hover:border-orange-300 ${
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
                    className={`w-full px-4 py-3 border rounded-xl transition-all duration-300 focus:ring-2 focus:ring-orange-500 focus:border-transparent ${
                      field.readOnly 
                        ? 'bg-gray-50 text-gray-500' 
                        : 'bg-white hover:border-orange-300'
                    } ${errors[field.name] ? 'border-red-300' : 'border-gray-200'}`}
                  />
                )}
                
                {/* Iconos contextuales */}
                {field.name === 'codigo' && <FileText className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
                {field.name === 'codigo_interno' && <FileText className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
                {field.name === 'nombre' && <Truck className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
                {field.name === 'direccion' && <MapPin className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
                {field.name === 'ciudad_id' && <Building2 className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
                {field.name === 'tipo_documento' && <CreditCard className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
                {field.name === 'numero_documento' && <FileText className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
                {field.name === 'telefono' && <Phone className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
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
              className="flex-1 py-3 px-4 bg-gradient-to-r from-orange-600 to-amber-700 text-white rounded-xl hover:from-orange-700 hover:to-amber-800 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
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

// Modal de Honorarios mejorado
const HonorariosModal = ({ open, onClose, transportadora, honorarios }) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full transform transition-all duration-300 scale-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Honorarios de {transportadora?.nombre}</h3>
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

        {/* Content */}
        <div className="p-6">
          {honorarios.length > 0 ? (
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {honorarios.map((h) => (
                <div key={h.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">{h.fecha}</span>
                    <span className="text-lg font-bold text-green-600">{h.monto}</span>
                  </div>
                  <p className="text-gray-800">{h.descripcion}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <DollarSign className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No hay honorarios registrados</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end pt-6">
            <button
              onClick={onClose}
              className="py-3 px-6 bg-gradient-to-r from-green-600 to-emerald-700 text-white rounded-xl hover:from-green-700 hover:to-emerald-800 transition-all duration-300 font-medium"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Componente principal mejorado
function Transportadoras() {
  const [transportadoras, setTransportadoras] = useState([]);
  const [ciudades, setCiudades] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTrans, setEditTrans] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const [honorariosModalOpen, setHonorariosModalOpen] = useState(false);
  const [selectedHonorarios, setSelectedHonorarios] = useState([]);
  const [selectedTransportadora, setSelectedTransportadora] = useState(null);

  const formFields = [
    { name: "codigo", label: "Código", required: true },
    { name: "codigo_interno", label: "Código Interno", required: false },
    { name: "nombre", label: "Nombre", required: true },
    { name: "direccion", label: "Dirección", required: false },
    {
      name: "ciudad_id",
      label: "Ciudad",
      required: true,
      type: "select",
      options: ciudades.map((c) => ({ value: c.id, label: c.nombre })),
    },
    { name: "tipo_documento", label: "Tipo de Documento", required: false },
    { name: "numero_documento", label: "Número de Documento", required: false },
    { name: "telefono", label: "Teléfono", required: false },
  ];

  useEffect(() => {
    fetchCiudades();
    fetchTransportadoras();
  }, []);

  const fetchCiudades = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/ciudades/");
      setCiudades(res.data);
      setIsLoading(false);
    } catch (error) {
      setIsLoading(false);
      console.error('Error fetching ciudades:', error);
    }
  };

  const fetchTransportadoras = async () => {
    try {
      const res = await api.get("/transportadoras/");
      const data = res.data.items || res.data;
      
      // DEBUG: Ver estructura de datos
      console.log("Datos de transportadoras:", data);
      if (data.length > 0) {
        console.log("Primera transportadora:", data[0]);
        console.log("Honorarios de primera:", data[0].honorarios);
      }
      
      setTransportadoras(data);
    } catch (error) {
      console.error('Error fetching transportadoras:', error);
    }
  };

  const handleAdd = () => {
    setEditTrans(null);
    setModalOpen(true);
  };

  const handleEdit = (trans) => {
    setEditTrans(trans);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Seguro que deseas eliminar esta transportadora?")) {
      await api.delete(`/transportadoras/${id}`);
      fetchTransportadoras();
    }
  };

  const handleSubmit = async (data) => {
    try {
      if (editTrans) {
        await api.put(`/transportadoras/${editTrans.id}`, data);
      } else {
        await api.post("/transportadoras/", data);
      }
      setModalOpen(false);
      fetchTransportadoras();
    } catch (e) {
      alert("Error al guardar transportadora: " + (e.response?.data?.error || e.message));
    }
  };

  // Función para agregar honorarios de prueba (comentada para evitar warning ESLint)
  // const agregarHonorariosPrueba = async (transportadoraId) => {
  //   try {
  //     const honorariosPrueba = [
  //       { fecha: '2024-01-15', descripcion: 'Flete enero', monto: '500.000' },
  //       { fecha: '2024-02-15', descripcion: 'Flete febrero', monto: '750.000' },
  //       { fecha: '2024-03-15', descripcion: 'Flete marzo', monto: '650.000' }
  //     ];
  //
  //     for (const honorario of honorariosPrueba) {
  //       await api.post('/honorarios/', {
  //         ...honorario,
  //         transportadora_id: transportadoraId
  //       });
  //     }
  //
  //     // Recargar datos
  //     fetchTransportadoras();
  //     alert('Honorarios de prueba agregados correctamente');
  //   } catch (error) {
  //     console.error('Error agregando honorarios:', error);
  //   }
  // };

  // Función para abrir el modal de honorarios
  const openHonorariosModal = (transportadora) => {
    console.log("Abriendo modal para transportadora:", transportadora);
    console.log("Honorarios encontrados:", transportadora.honorarios);
    console.log("Es array?", Array.isArray(transportadora.honorarios));
    
    setSelectedHonorarios(Array.isArray(transportadora.honorarios) ? transportadora.honorarios : []);
    setSelectedTransportadora(transportadora);
    setHonorariosModalOpen(true);
  };

  // Calcular estadísticas
  const totalTransportadoras = transportadoras.length;
  const ciudadesConTransportadoras = [...new Set(transportadoras.map(t => t.ciudad_id))].length;
  const totalHonorarios = transportadoras.reduce((acc, t) => acc + (Array.isArray(t.honorarios) ? t.honorarios.length : 0), 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-600 to-amber-700 rounded-2xl flex items-center justify-center shadow-lg">
                <Truck className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Gestión de Transportadoras</h1>
                <p className="text-gray-600 text-lg">Administra las empresas de transporte y sus honorarios</p>
              </div>
            </div>
            
            <button
              onClick={handleAdd}
              className="group bg-gradient-to-r from-orange-600 to-amber-700 text-white px-6 py-3 rounded-xl hover:from-orange-700 hover:to-amber-800 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">Agregar Transportadora</span>
            </button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Transportadoras</p>
                  <p className="text-3xl font-bold text-gray-900">{totalTransportadoras}</p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                  <Truck className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Ciudades Cubiertas</p>
                  <p className="text-3xl font-bold text-gray-900">{ciudadesConTransportadoras}</p>
                </div>
                <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-amber-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Honorarios</p>
                  <p className="text-3xl font-bold text-gray-900">{totalHonorarios}</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <div className="w-12 h-12 border-4 border-orange-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Cargando transportadoras...</p>
          </div>
        ) : (
          <EnhancedTable
            columns={[
              { field: "codigo", label: "Código" },
              { field: "codigo_interno", label: "Código Interno" },
              { field: "nombre", label: "Nombre" },
              { field: "direccion", label: "Dirección" },
              {
                field: "ciudad_id",
                label: "Ciudad",
                render: (id) => {
                  const ciudad = ciudades.find(c => c.id === id);
                  return (
                    <div className="flex items-center space-x-2">
                      <Building2 className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-700">{ciudad?.nombre || id}</span>
                      <div className="px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
                        Ciudad
                      </div>
                    </div>
                  );
                }
              },
              { field: "tipo_documento", label: "Tipo Documento" },
              { field: "numero_documento", label: "Número Documento" },
              { field: "telefono", label: "Teléfono" },
              {
                field: "honorarios",
                label: "Honorarios",
                render: (h, row) => {
                  // Usar contador dinámico basado en los honorarios reales del sistema
                  return (
                    <button
                      onClick={() => openHonorariosModal(row)}
                      className="flex items-center space-x-2 text-green-600 hover:text-green-700 hover:bg-green-50 px-3 py-1 rounded-lg transition-all duration-300"
                    >
                      <DollarSign className="w-4 h-4" />
                      <span className="font-medium">Ver honorarios</span>
                      <Eye className="w-4 h-4" />
                    </button>
                  );
                }
              },
            ]}
            data={transportadoras}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}

        {/* Modal Principal */}
        <EnhancedFormModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onSubmit={handleSubmit}
          initialValues={editTrans}
          fields={formFields}
          title={editTrans ? "Editar Transportadora" : "Nueva Transportadora"}
        />

        {/* Modal de Honorarios */}
        <HonorariosModal
          open={honorariosModalOpen}
          onClose={() => setHonorariosModalOpen(false)}
          transportadora={selectedTransportadora}
          honorarios={selectedHonorarios}
        />
      </div>
    </div>
  );
}

export default Transportadoras;