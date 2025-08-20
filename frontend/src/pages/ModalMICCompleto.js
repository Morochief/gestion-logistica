import React, { useState, useEffect } from 'react';
import { X, Save, FileText, Truck, MapPin, Package, DollarSign, Calendar, Building } from 'lucide-react';

const ModalMICCompleto = ({ 
  isOpen, 
  onClose, 
  crt, 
  onGenerate,
  loading = false 
}) => {
  const [formData, setFormData] = useState({
    // SECCIÓN 1: Información del Transporte
    campo_2_numero: '',
    campo_3_transporte: '',
    campo_7_pto_seguro: '',
    campo_8_destino: '',
    
    // SECCIÓN 2: Datos del Vehículo
    campo_10_numero: '',
    campo_11_placa: '',
    campo_12_modelo_chasis: '',
    campo_14_anio: '',
    campo_15_placa_semi: '',
    
    // SECCIÓN 3: Información Aduanera
    campo_24_aduana: '',
    campo_26_pais: '520-PARAGUAY',
    
    // SECCIÓN 4: Valores y Montos (editables)
    campo_27_valor_campo16: '',
    campo_28_total: '',
    campo_29_seguro: '',
    
    // SECCIÓN 5: Mercadería
    campo_30_tipo_bultos: '',
    campo_31_cantidad: '',
    campo_32_peso_bruto: '',
    campo_37_valor_manual: '',
    
    // SECCIÓN 6: Documentos y Referencias
    campo_36_factura_despacho: '',
    campo_40_tramo: '',
    
    // SECCIÓN 7: Campos de Solo Lectura (pre-llenados)
    campo_4_estado: 'PROVISORIO',
    campo_5_hoja: '1 / 1',
    campo_6_fecha: new Date().toISOString().split('T')[0],
    campo_13_siempre_45: '45 TON',
    campo_25_moneda: '',
  });

  // Prellenar datos del CRT cuando se abre el modal
  useEffect(() => {
    if (isOpen && crt) {
      setFormData(prev => ({
        ...prev,
        campo_8_destino: crt.lugar_entrega || '',
        campo_25_moneda: crt.moneda || '',
        campo_27_valor_campo16: crt.declaracion_mercaderia || '',
        campo_32_peso_bruto: crt.peso_bruto || '',
        campo_36_factura_despacho: `${crt.factura_exportacion || ''} ${crt.nro_despacho || ''}`.trim(),
      }));
    }
  }, [isOpen, crt]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = () => {
    onGenerate(formData);
  };

  const resetForm = () => {
    setFormData({
      campo_2_numero: '',
      campo_3_transporte: '',
      campo_7_pto_seguro: '',
      campo_8_destino: crt?.lugar_entrega || '',
      campo_10_numero: '',
      campo_11_placa: '',
      campo_12_modelo_chasis: '',
      campo_14_anio: '',
      campo_15_placa_semi: '',
      campo_24_aduana: '',
      campo_26_pais: '520-PARAGUAY',
      campo_27_valor_campo16: crt?.declaracion_mercaderia || '',
      campo_28_total: '',
      campo_29_seguro: '',
      campo_30_tipo_bultos: '',
      campo_31_cantidad: '',
      campo_32_peso_bruto: crt?.peso_bruto || '',
      campo_37_valor_manual: '',
      campo_36_factura_despacho: `${crt?.factura_exportacion || ''} ${crt?.nro_despacho || ''}`.trim(),
      campo_40_tramo: '',
      campo_4_estado: 'PROVISORIO',
      campo_5_hoja: '1 / 1',
      campo_6_fecha: new Date().toISOString().split('T')[0],
      campo_13_siempre_45: '45 TON',
      campo_25_moneda: crt?.moneda || '',
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[95vh] overflow-hidden flex flex-col">
        {/* HEADER */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <FileText className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Completar Datos MIC</h2>
              <p className="text-blue-100">CRT: {crt?.numero_crt || 'N/A'}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors p-2 hover:bg-white/10 rounded-lg"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* CONTENT */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-8">
            
            {/* SECCIÓN 1: INFORMACIÓN DEL TRANSPORTE */}
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-6 border-l-4 border-blue-500">
              <div className="flex items-center mb-4">
                <Truck className="w-6 h-6 text-blue-600 mr-3" />
                <h3 className="text-lg font-semibold text-blue-800">Información del Transporte</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 2 - Rol de contribuyente
                  </label>
                  <input
                    type="text"
                    value={formData.campo_2_numero}
                    onChange={(e) => handleInputChange('campo_2_numero', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Rol del Contribuyente"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 3 - Tipo Transporte
                  </label>
                  <select
                    value={formData.campo_3_transporte}
                    onChange={(e) => handleInputChange('campo_3_transporte', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  >
                    <option value="">Seleccionar tipo</option>
                    <option value="TERRESTRE">TERRESTRE</option>
                    <option value="MARÍTIMO">MARÍTIMO</option>
                    <option value="AÉREO">AÉREO</option>
                    <option value="MULTIMODAL">MULTIMODAL</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 7 - Puerto Seguro
                  </label>
                  <input
                    type="text"
                    value={formData.campo_7_pto_seguro}
                    onChange={(e) => handleInputChange('campo_7_pto_seguro', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Puerto o punto seguro"
                  />
                </div>
              </div>
            </div>

            {/* SECCIÓN 2: DATOS DEL VEHÍCULO */}
            <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-6 border-l-4 border-green-500">
              <div className="flex items-center mb-4">
                <Package className="w-6 h-6 text-green-600 mr-3" />
                <h3 className="text-lg font-semibold text-green-800">Datos del Vehículo</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 10 - Número Interno
                  </label>
                  <input
                    type="text"
                    value={formData.campo_10_numero}
                    onChange={(e) => handleInputChange('campo_10_numero', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                    placeholder="Número interno del vehículo"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 11 - Placa Principal *
                  </label>
                  <input
                    type="text"
                    value={formData.campo_11_placa}
                    onChange={(e) => handleInputChange('campo_11_placa', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                    placeholder="ABC-1234"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 12 - Modelo/Chasis
                  </label>
                  <input
                    type="text"
                    value={formData.campo_12_modelo_chasis}
                    onChange={(e) => handleInputChange('campo_12_modelo_chasis', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                    placeholder="Modelo y número de chasis"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 14 - Año del Vehículo
                  </label>
                  <input
                    type="number"
                    min="1980"
                    max="2030"
                    value={formData.campo_14_anio}
                    onChange={(e) => handleInputChange('campo_14_anio', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                    placeholder="2024"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 15 - Placa Semirremolque
                  </label>
                  <input
                    type="text"
                    value={formData.campo_15_placa_semi}
                    onChange={(e) => handleInputChange('campo_15_placa_semi', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                    placeholder="XYZ-5678"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 13 - Capacidad (Solo lectura)
                  </label>
                  <input
                    type="text"
                    value={formData.campo_13_siempre_45}
                    readOnly
                    className="w-full p-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>
              </div>
            </div>

            {/* SECCIÓN 3: INFORMACIÓN ADUANERA */}
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-6 border-l-4 border-purple-500">
              <div className="flex items-center mb-4">
                <Building className="w-6 h-6 text-purple-600 mr-3" />
                <h3 className="text-lg font-semibold text-purple-800">Información Aduanera</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 24 - Aduana
                  </label>
                  <select
                    value={formData.campo_24_aduana}
                    onChange={(e) => handleInputChange('campo_24_aduana', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                  >
                    <option value="">Seleccionar aduana</option>
                    <option value="ASUNCIÓN">ASUNCIÓN</option>
                    <option value="CIUDAD DEL ESTE">CIUDAD DEL ESTE</option>
                    <option value="ENCARNACIÓN">ENCARNACIÓN</option>
                    <option value="PEDRO JUAN CABALLERO">PEDRO JUAN CABALLERO</option>
                    <option value="PUERTO FALCÓN">PUERTO FALCÓN</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 26 - País (Solo lectura)
                  </label>
                  <input
                    type="text"
                    value={formData.campo_26_pais}
                    readOnly
                    className="w-full p-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>
              </div>
            </div>

            {/* SECCIÓN 4: VALORES Y MONTOS */}
            <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-6 border-l-4 border-yellow-500">
              <div className="flex items-center mb-4">
                <DollarSign className="w-6 h-6 text-yellow-600 mr-3" />
                <h3 className="text-lg font-semibold text-yellow-800">Valores y Montos</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 27 - Valor Declarado
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.campo_27_valor_campo16}
                    onChange={(e) => handleInputChange('campo_27_valor_campo16', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors"
                    placeholder="0.00"
                  />
                  <small className="text-gray-500">Del CRT Campo 16</small>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 28 - Total Flete
                  </label>
                  <input
                    type="text"
                    value={formData.campo_28_total}
                    onChange={(e) => handleInputChange('campo_28_total', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors"
                    placeholder="1.500,00"
                  />
                  <small className="text-gray-500">Calculado automáticamente</small>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 29 - Seguro
                  </label>
                  <input
                    type="text"
                    value={formData.campo_29_seguro}
                    onChange={(e) => handleInputChange('campo_29_seguro', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors"
                    placeholder="150,00"
                  />
                  <small className="text-gray-500">Calculado automáticamente</small>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 25 - Moneda (Solo lectura)
                  </label>
                  <input
                    type="text"
                    value={formData.campo_25_moneda}
                    readOnly
                    className="w-full p-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 37 - Valor Manual
                  </label>
                  <input
                    type="text"
                    value={formData.campo_37_valor_manual}
                    onChange={(e) => handleInputChange('campo_37_valor_manual', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition-colors"
                    placeholder="Valor adicional"
                  />
                </div>
              </div>
            </div>

            {/* SECCIÓN 5: MERCADERÍA */}
            <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-6 border-l-4 border-orange-500">
              <div className="flex items-center mb-4">
                <Package className="w-6 h-6 text-orange-600 mr-3" />
                <h3 className="text-lg font-semibold text-orange-800">Información de Mercadería</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 30 - Tipo de Bultos
                  </label>
                  <select
                    value={formData.campo_30_tipo_bultos}
                    onChange={(e) => handleInputChange('campo_30_tipo_bultos', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                  >
                    <option value="">Seleccionar tipo</option>
                    <option value="CAJAS">CAJAS</option>
                    <option value="PALLETS">PALLETS</option>
                    <option value="BOLSAS">BOLSAS</option>
                    <option value="CONTENEDORES">CONTENEDORES</option>
                    <option value="TAMBORES">TAMBORES</option>
                    <option value="OTROS">OTROS</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 31 - Cantidad
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.campo_31_cantidad}
                    onChange={(e) => handleInputChange('campo_31_cantidad', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                    placeholder="0"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 32 - Peso Bruto (kg)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={formData.campo_32_peso_bruto}
                    onChange={(e) => handleInputChange('campo_32_peso_bruto', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                    placeholder="0.000"
                  />
                  <small className="text-gray-500">Del CRT</small>
                </div>
              </div>
            </div>

            {/* SECCIÓN 6: INFORMACIÓN ADICIONAL */}
            <div className="bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-lg p-6 border-l-4 border-indigo-500">
              <div className="flex items-center mb-4">
                <MapPin className="w-6 h-6 text-indigo-600 mr-3" />
                <h3 className="text-lg font-semibold text-indigo-800">Información Adicional</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 8 - Destino
                  </label>
                  <input
                    type="text"
                    value={formData.campo_8_destino}
                    onChange={(e) => handleInputChange('campo_8_destino', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                    placeholder="Ciudad/Puerto de destino"
                  />
                  <small className="text-gray-500">Del CRT lugar de entrega</small>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 40 - Tramo
                  </label>
                  <input
                    type="text"
                    value={formData.campo_40_tramo}
                    onChange={(e) => handleInputChange('campo_40_tramo', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                    placeholder="Descripción del tramo"
                  />
                </div>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campo 36 - Factura y Despacho
                </label>
                <textarea
                  rows="2"
                  value={formData.campo_36_factura_despacho}
                  onChange={(e) => handleInputChange('campo_36_factura_despacho', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors resize-none"
                  placeholder="Información de facturas y números de despacho"
                />
                <small className="text-gray-500">Del CRT factura y despacho</small>
              </div>
            </div>

            {/* CAMPOS DE SOLO LECTURA */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6 border-l-4 border-gray-400">
              <div className="flex items-center mb-4">
                <Calendar className="w-6 h-6 text-gray-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-700">Información Automática</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 4 - Estado
                  </label>
                  <input
                    type="text"
                    value={formData.campo_4_estado}
                    readOnly
                    className="w-full p-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 5 - Hoja
                  </label>
                  <input
                    type="text"
                    value={formData.campo_5_hoja}
                    readOnly
                    className="w-full p-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campo 6 - Fecha
                  </label>
                  <input
                    type="date"
                    value={formData.campo_6_fecha}
                    onChange={(e) => handleInputChange('campo_6_fecha', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-gray-500 transition-colors"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FOOTER */}
        <div className="bg-gray-50 border-t p-6 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              type="button"
              onClick={resetForm}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              🔄 Resetear Formulario
            </button>
            <span className="text-sm text-gray-500">
              * Campos marcados son obligatorios
            </span>
          </div>
          
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
            >
              Cancelar
            </button>
            
            <button
              onClick={handleSubmit}
              disabled={loading || !formData.campo_11_placa}
              className={`px-6 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors ${
                loading || !formData.campo_11_placa
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white'
              }`}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Generando PDF...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Generar PDF MIC</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModalMICCompleto;