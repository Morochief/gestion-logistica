import React, { useState, useEffect } from "react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./MIC.css";

// Configuración de la API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Opciones para selects (las mismas del componente original)
const OPCIONES_AUDANA = [
  "BRASIL - MULTILOG - FOZ DO IGUAZU 508 - 030"
];
const OPCIONES_BULTOS = [
  "CAJA", "PALLET", "A GRANEL"
];
const OPCIONES_TRAMOS = [
  "ORIGEN: PTO SEGURO FLUVIAL-VILLETA;SALIDA: CIUDAD DEL ESTE-CIUDAD DEL ESTE;DESTINO: BRASIL-CACADOR-MULTILOG - FOZ DO IGUAZU;DESTINO ENTRADA: BRASIL-CACADOR-MULTILOG - FOZ DO IGUAZU;",
  "ORIGEN: CAMPESTRE S.A.-CIUDAD DEL ESTE;SALIDA: CIUDAD DEL ESTE-CIUDAD DEL ESTE;DESTINO: BRASIL-ITAJAI-MULTILOG - FOZ DO IGUAZU;DESTINO ENTRADA: BRASIL-ITAJAI-MULTILOG - FOZ DO IGUAZU;",
  "ORIGEN: CAMPESTRE S.A.-CIUDAD DEL ESTE;SALIDA: CIUDAD DEL ESTE-CIUDAD DEL ESTE;DESTINO: BRASIL-NAVEGANTES-MULTILOG DIONISIO CERQUEIRA - SC BRASIL;DESTINO ENTRADA: BRASIL-NAVEGANTES-MULTILOG - FOZ DO IGUAZU",
  "ORIGEN: CAMPESTRE S.A.-CIUDAD DEL ESTE;SALIDA: CIUDAD DEL ESTE-CIUDAD DEL ESTE;DESTINO: BRASIL-SAO JOSE-MULTILOG - FOZ DO IGUAZU;DESTINO ENTRADA: BRASIL-SAO JOSE-MULTILOG - FOZ DO IGUAZU;"
];
const OPCIONES_7 = [
  "CAMPESTRE S.A. - CIUDAD DEL ESTE - PARAGUAY",
  "TER. DE CARGAS KM.12 CIUDAD DEL ESTE"
];

const CAMPOS_MANUALES = [
  1, 5, 6, 8, 13, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27,
  28, 29, 32, 33, 34, 35, 36, 38, 39, 41
];

const CAMPOS_16_22 = [16, 17, 18, 19, 20, 21, 22];

// Estado inicial
const initialState = {
  campo_2_numero: "",
  campo_3_transporte: "",
  campo_4_estado: "PROVISORIO",
  campo_7_pto_seguro: "",
  campo_9_datos_transporte: "",
  campo_10_numero: "",
  campo_11_placa: "",
  campo_12_modelo_chasis: "",
  campo_12_chasis: "",
  campo_14_anio: "",
  campo_15_placa_semi: "",
  campo_24_aduana: "",
  campo_30_tipo_bultos: "",
  campo_31_cantidad: "",
  campo_37_valor_manual: "",
  campo_40_tramo: "",
  ...Object.fromEntries(CAMPOS_MANUALES.map(n => [`campo_${n}`, ""]))
};

export default function MIC({ crtId, crtNumero, onClose, modo = "generar" }) {
  const [mic, setMic] = useState(initialState);
  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [cargandoCRT, setCargandoCRT] = useState(false);
  const [camposAutocompletados, setCamposAutocompletados] = useState([]);
  const [datosCRT, setDatosCRT] = useState(null);

  // ✅ CARGAR DATOS DEL CRT AL MONTAR EL COMPONENTE
  useEffect(() => {
    cargarDatosCRT();
  }, [crtId, crtNumero]);

  const handleChange = e => {
    setMic({ ...mic, [e.target.name]: e.target.value });
  };

  // Validación (misma del componente original)
  const validar = () => {
    let err = [];
    if (!mic.campo_2_numero) err.push("Campo 2 obligatorio");
    if (!mic.campo_10_numero) err.push("Campo 10 obligatorio");
    if (!mic.campo_11_placa) err.push("Campo 11 obligatorio");
    if (!mic.campo_12_modelo_chasis) err.push("Campo 12 obligatorio");
    if (!mic.campo_14_anio) err.push("Campo 14 obligatorio");
    if (!mic.campo_15_placa_semi) err.push("Campo 15 obligatorio");
    if (!mic.campo_24_aduana) err.push("Campo 24 obligatorio");
    if (!mic.campo_30_tipo_bultos) err.push("Campo 30 obligatorio");
    if (!mic.campo_31_cantidad) err.push("Campo 31_cantidad obligatorio");
    if (!mic.campo_40_tramo) err.push("Campo 40 obligatorio");
    if (!mic.campo_7_pto_seguro) err.push("Campo 7 obligatorio");
    return err;
  };

  // ✅ FUNCIÓN ACTUALIZADA: Guardar MIC en base de datos usando la nueva ruta
  const guardarMic = async () => {
    const errores = validar();
    if (errores.length) {
      toast.error(errores.join(", "));
      return;
    }

    setGuardando(true);
    
    // Auto-completar campos 16-22 con "******"
    const micToSave = { ...mic };
    CAMPOS_16_22.forEach(n => {
      if (!micToSave[`campo_${n}`] || micToSave[`campo_${n}`].trim() === "") {
        micToSave[`campo_${n}`] = "******";
      }
    });

    try {
      console.log('💾 Guardando MIC en base de datos...');
      
      let endpoint, payload;
      
      if (crtId) {
        // ✅ USAR NUEVA RUTA DE INTEGRACIÓN
        endpoint = `${API_BASE_URL}/api/mic/crear_desde_crt/${crtId}`;
        payload = micToSave;
      } else {
        // Crear manual
        endpoint = `${API_BASE_URL}/api/mic/`;
        payload = { ...micToSave, crt_id: null };
      }

      const response = await axios.post(endpoint, payload);
      
      toast.success(`💾 MIC guardado exitosamente con ID: ${response.data.id}`);
      console.log('✅ MIC guardado:', response.data);
      
      // Mostrar opción de descargar PDF
      if (window.confirm("¿Deseas descargar el PDF del MIC guardado?")) {
        await descargarPDFGuardado(response.data.id);
      }
      
      if (onClose) onClose();
      
    } catch (error) {
      console.error('❌ Error guardando MIC:', error);
      toast.error(`❌ Error guardando MIC: ${error.response?.data?.error || error.message}`);
    } finally {
      setGuardando(false);
    }
  };

  // ✅ FUNCIÓN MEJORADA: Generar PDF temporal usando datos integrados
  const generarPDFTemporal = async () => {
    const errores = validar();
    if (errores.length) {
      toast.error(errores.join(", "));
      return;
    }
    
    setLoading(true);

    const micToSend = { ...mic };
    CAMPOS_16_22.forEach(n => {
      if (!micToSend[`campo_${n}`] || micToSend[`campo_${n}`].trim() === "") {
        micToSend[`campo_${n}`] = "******";
      }
    });

    try {
      console.log('📄 Generando PDF temporal con integración CRT...');
      
      const endpoint = crtId 
        ? `${API_BASE_URL}/api/mic/generate_pdf_from_crt/${crtId}`
        : `${API_BASE_URL}/api/mic/generate_pdf_temporal`;
        
      const res = await axios.post(endpoint, micToSend, { responseType: "blob" });
      
      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank");
      
      toast.success("📋 PDF temporal generado exitosamente");
      
    } catch (error) {
      console.error('❌ Error generando PDF temporal:', error);
      toast.error(`❌ Error generando PDF: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ✅ FUNCIÓN: Descargar PDF de MIC guardado
  const descargarPDFGuardado = async (micId) => {
    try {
      console.log(`📄 Descargando PDF del MIC guardado ${micId}...`);
      const response = await axios.get(
        `${API_BASE_URL}/api/mic/${micId}/pdf`,
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `MIC_${mic.campo_23_numero_campo2_crt || micId}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('📄 PDF descargado exitosamente');
    } catch (error) {
      console.error('❌ Error descargando PDF:', error);
      toast.error('❌ Error descargando PDF');
    }
  };

  // ✅ FUNCIÓN: Recargar datos del CRT
  const recargarDatosCRT = async () => {
    await cargarDatosCRT();
  };

  // ✅ FUNCIÓN: Verificar qué campos están auto-completados
  const esCampoAutocompletado = (nombreCampo) => {
    return camposAutocompletados.includes(nombreCampo);
  };

  // Mismos campos principales del componente original
  const CAMPOS_PRINCIPALES = [
    "campo_2_numero", "campo_3_transporte", "campo_4_estado", "campo_7_pto_seguro",
    "campo_9_datos_transporte", "campo_10_numero", "campo_11_placa", "campo_12_modelo_chasis",
    "campo_14_anio", "campo_15_placa_semi", "campo_24_aduana", "campo_30_tipo_bultos",
    "campo_31_cantidad", "campo_37_valor_manual", "campo_38", "campo_40_tramo"
  ];

  return (
    <form className="mic-form-pro" onSubmit={(e) => e.preventDefault()}>
      <ToastContainer position="top-right" />
      
      <h2 className="mic-form-title">
        {modo === "editar" ? "✏️ Editar MIC" : "📋 Completar datos del MIC"}
        {(crtId || crtNumero) && (
          <span className="text-blue-600"> 
            (CRT: {datosCRT?.numero_crt || crtNumero || crtId})
          </span>
        )}
      </h2>

      {/* ✅ INDICADORES DE ESTADO */}
      <div className="mic-status-indicators">
        {cargandoCRT && (
          <div className="status-indicator loading">
            <span>🔄 Cargando datos del CRT...</span>
          </div>
        )}
        
        {datosCRT && !cargandoCRT && (
          <div className="status-indicator success">
            <span>✅ CRT {datosCRT.numero_crt} cargado - {camposAutocompletados.length} campos auto-completados</span>
            <button 
              type="button" 
              onClick={recargarDatosCRT}
              className="reload-btn"
              title="Recargar datos del CRT"
            >
              🔄
            </button>
          </div>
        )}
        
        {camposAutocompletados.length > 0 && (
          <div className="auto-completed-info">
            <details>
              <summary>📋 Campos auto-completados ({camposAutocompletados.length})</summary>
              <ul>
                {camposAutocompletados.map(campo => (
                  <li key={campo}>{campo.replace('campo_', 'Campo ').replace(/_/g, ' ')}</li>
                ))}
              </ul>
            </details>
          </div>
        )}
      </div>

      <div className="mic-form-grid">
        {/* CAMPO 2 */}
        <label>
          <div className="field-header">
            Campo 2 (Rol contribuyente) *
            {esCampoAutocompletado('campo_2_numero') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_2_numero" 
            value={mic.campo_2_numero} 
            onChange={handleChange} 
            required 
            className="inputPro" 
          />
        </label>

        {/* CAMPO 3 */}
        <label>
          <div className="field-header">
            Campo 3 (Transporte, dejar vacío)
            {esCampoAutocompletado('campo_3_transporte') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_3_transporte" 
            value={mic.campo_3_transporte} 
            onChange={handleChange} 
            placeholder="(vacío)" 
            className="inputPro" 
          />
        </label>

        {/* CAMPO 4 */}
        <label>
          <div className="field-header">
            Campo 4 (Estado)
            {esCampoAutocompletado('campo_4_estado') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <select name="campo_4_estado" value={mic.campo_4_estado} onChange={handleChange} className="inputPro">
            <option value="PROVISORIO">PROVISORIO</option>
            <option value="DEFINITIVO">DEFINITIVO</option>
            <option value="EN_PROCESO">EN_PROCESO</option>
          </select>
        </label>
        
        {/* CAMPO 6 */}
        <label>
          <div className="field-header">
            Campo 6 (Fecha de emisión)
            {esCampoAutocompletado('campo_6_fecha') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_6_fecha" 
            type="date" 
            value={mic.campo_6_fecha} 
            onChange={handleChange} 
            className="inputPro"
          />
          {esCampoAutocompletado('campo_6_fecha') && (
            <small className="auto-help">Auto-completado desde el CRT</small>
          )}
        </label>
        
        {/* CAMPO 7 */}
        <label>
          <div className="field-header">
            Campo 7 (Pto Seguro) *
            {esCampoAutocompletado('campo_7_pto_seguro') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <select name="campo_7_pto_seguro" value={mic.campo_7_pto_seguro} onChange={handleChange} required className="inputPro">
            <option value="">Seleccione...</option>
            {OPCIONES_7.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </label>
        
        {/* CAMPO 8 */}
        <label>
          <div className="field-header">
            Campo 8 (Ciudad y país de destino final)
            {esCampoAutocompletado('campo_8_destino') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_8_destino" 
            value={mic.campo_8_destino} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="Ciudad de destino"
          />
          {esCampoAutocompletado('campo_8_destino') && (
            <small className="auto-help">Auto-completado desde lugar_entrega del CRT</small>
          )}
        </label>

        {/* CAMPO 9 */}
        <label>
          <div className="field-header">
            Campo 9 (CAMIÓN ORIGINAL: Nombre y domicilio del propietario)
            {esCampoAutocompletado('campo_9_datos_transporte') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <textarea
            name="campo_9_datos_transporte"
            value={mic.campo_9_datos_transporte}
            onChange={handleChange}
            className="inputPro"
            rows={3}
            style={{ resize: "vertical", maxHeight: 80 }}
            placeholder="Nombre y dirección (auto-completado desde CRT)"
          />
          {esCampoAutocompletado('campo_9_datos_transporte') && (
            <small className="auto-help">Auto-completado desde transportadora del CRT</small>
          )}
        </label>

        {/* CAMPO 10 */}
        <label>
          <div className="field-header">
            Campo 10 (Rol contribuyente) *
            {esCampoAutocompletado('campo_10_numero') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_10_numero" 
            value={mic.campo_10_numero} 
            onChange={handleChange} 
            required 
            className="inputPro" 
          />
        </label>

        {/* CAMPO 11 */}
        <label>
          <div className="field-header">
            Campo 11 (Placa) *
            {esCampoAutocompletado('campo_11_placa') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_11_placa" 
            value={mic.campo_11_placa} 
            onChange={handleChange} 
            required 
            className="inputPro" 
          />
        </label>

        {/* CAMPO 12 */}
        <label>
          <div className="field-header">
            Campo 12 (Modelo/Chasis) *
            {esCampoAutocompletado('campo_12_modelo_chasis') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <input
              name="campo_12_modelo_chasis"
              value={mic.campo_12_modelo_chasis}
              onChange={(e) => {
                const marca = e.target.value;
                const chasis = mic.campo_12_chasis || "";
                const combined = chasis ? `${marca}\n${chasis}` : marca;
                setMic({ ...mic, campo_12_modelo_chasis: combined });
              }}
              required
              className="inputPro"
              placeholder="Ejemplo: SCANIA R450 6x4"
              maxLength={80}
            />
            <input
              name="campo_12_chasis"
              value={mic.campo_12_chasis || ""}
              onChange={(e) => {
                const chasis = e.target.value;
                const marca = mic.campo_12_modelo_chasis?.split('\n')[0] || "";
                const combined = chasis ? `${marca}\nChasis: ${chasis}` : marca;
                setMic({ ...mic, campo_12_chasis: chasis, campo_12_modelo_chasis: combined });
              }}
              className="inputPro"
              placeholder="Número de chasis (opcional)"
              maxLength={50}
            />
          </div>
        </label>

        {/* CAMPO 14 */}
        <label>
          <div className="field-header">
            Campo 14 (Año) *
            {esCampoAutocompletado('campo_14_anio') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input
            name="campo_14_anio"
            value={mic.campo_14_anio}
            onChange={handleChange}
            type="number"
            min="1900"
            max="2100"
            required
            className="inputPro"
            placeholder="2025"
          />
        </label>

        {/* CAMPO 15 */}
        <label>
          <div className="field-header">
            Campo 15 (Placa Semi) *
            {esCampoAutocompletado('campo_15_placa_semi') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_15_placa_semi" 
            value={mic.campo_15_placa_semi} 
            onChange={handleChange} 
            required 
            className="inputPro" 
          />
        </label>
        
        {/* CAMPO 23 */}
        <label>
          <div className="field-header">
            Campo 23 (Nº carta de porte)
            {esCampoAutocompletado('campo_23_numero_campo2_crt') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_23_numero_campo2_crt" 
            value={mic.campo_23_numero_campo2_crt} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="Número del CRT"
          />
          {esCampoAutocompletado('campo_23_numero_campo2_crt') && (
            <small className="auto-help">Auto-completado desde número_crt</small>
          )}
        </label>
        
        {/* CAMPO 24 */}
        <label>
          <div className="field-header">
            Campo 24 (Aduana) *
            {esCampoAutocompletado('campo_24_aduana') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <select name="campo_24_aduana" value={mic.campo_24_aduana} onChange={handleChange} required className="inputPro">
            <option value="">Seleccione...</option>
            {OPCIONES_AUDANA.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </label>
        
        {/* CAMPO 25 */}
        <label>
          <div className="field-header">
            Campo 25 (Moneda)
            {esCampoAutocompletado('campo_25_moneda') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <select name="campo_25_moneda" value={mic.campo_25_moneda} onChange={handleChange} className="inputPro">
            <option value="DOLAR AMERICANO">DOLAR AMERICANO</option>
            <option value="GUARANI">GUARANI</option>
            <option value="REAL">REAL</option>
            <option value="PESO ARGENTINO">PESO ARGENTINO</option>
            <option value="EURO">EURO</option>
          </select>
          {esCampoAutocompletado('campo_25_moneda') && (
            <small className="auto-help">Auto-completado desde moneda del CRT</small>
          )}
        </label>
        
        {/* CAMPO 26 */}
        <label>
          <div className="field-header">
            Campo 26 (Origen de las mercaderías)
            {esCampoAutocompletado('campo_26_pais') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_26_pais" 
            value={mic.campo_26_pais} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="520-PARAGUAY"
          />
        </label>
        
        {/* CAMPO 27 */}
        <label>
          <div className="field-header">
            Campo 27 (Valor FOT)
            {esCampoAutocompletado('campo_27_valor_campo16') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_27_valor_campo16" 
            type="number" 
            step="0.01"
            value={mic.campo_27_valor_campo16} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="0.00"
          />
          {esCampoAutocompletado('campo_27_valor_campo16') && (
            <small className="auto-help">Auto-completado desde declaracion_mercaderia del CRT</small>
          )}
        </label>

        {/* CAMPO 28 - FLETE */}
        <label>
          <div className="field-header">
            Campo 28 (Flete en U$S)
            {esCampoAutocompletado('campo_28_total') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_28_total" 
            type="number" 
            step="0.01"
            value={mic.campo_28_total} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="0.00"
          />
          {esCampoAutocompletado('campo_28_total') && (
            <small className="auto-help">Auto-calculado desde gastos del CRT (suma de no-seguros)</small>
          )}
        </label>

        {/* CAMPO 29 - SEGURO */}
        <label>
          <div className="field-header">
            Campo 29 (Seguro en U$S)
            {esCampoAutocompletado('campo_29_seguro') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_29_seguro" 
            type="number" 
            step="0.01"
            value={mic.campo_29_seguro} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="0.00"
          />
          {esCampoAutocompletado('campo_29_seguro') && (
            <small className="auto-help">Auto-calculado desde gastos del CRT (solo seguros)</small>
          )}
        </label>

        {/* CAMPO 30 */}
        <label>
          <div className="field-header">
            Campo 30 (Tipo Bultos) *
            {esCampoAutocompletado('campo_30_tipo_bultos') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <select name="campo_30_tipo_bultos" value={mic.campo_30_tipo_bultos} onChange={handleChange} required className="inputPro">
            <option value="">Seleccione...</option>
            {OPCIONES_BULTOS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </label>

        {/* CAMPO 31 */}
        <label>
          <div className="field-header">
            Campo 31 (Cantidad) *
            {esCampoAutocompletado('campo_31_cantidad') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_31_cantidad" 
            type="number" 
            value={mic.campo_31_cantidad} 
            onChange={handleChange} 
            required 
            className="inputPro" 
          />
        </label>
        
        {/* CAMPO 32 */}
        <label>
          <div className="field-header">
            Campo 32 (Peso bruto)
            {esCampoAutocompletado('campo_32_peso_bruto') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_32_peso_bruto" 
            type="number" 
            step="0.001"
            value={mic.campo_32_peso_bruto} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="0.000"
          />
          {esCampoAutocompletado('campo_32_peso_bruto') && (
            <small className="auto-help">Auto-completado desde peso_bruto del CRT</small>
          )}
        </label>
        
        {/* CAMPO 36 */}
        <label style={{ gridColumn: "span 2" }}>
          <div className="field-header">
            Campo 36 (Documentos anexos)
            {esCampoAutocompletado('campo_36_factura_despacho') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_36_factura_despacho" 
            value={mic.campo_36_factura_despacho} 
            onChange={handleChange} 
            className="inputPro"
            style={{ width: "100%" }}
            placeholder="Factura: XXX Despacho: YYY"
          />
          {esCampoAutocompletado('campo_36_factura_despacho') && (
            <small className="auto-help">Auto-completado desde factura_exportacion y nro_despacho del CRT</small>
          )}
        </label>

        {/* CAMPO 37 */}
        <label>
          <div className="field-header">
            Campo 37 (Manual)
            {esCampoAutocompletado('campo_37_valor_manual') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <input 
            name="campo_37_valor_manual" 
            value={mic.campo_37_valor_manual} 
            onChange={handleChange} 
            className="inputPro" 
          />
        </label>

        {/* CAMPO 38 */}
        <label style={{ gridColumn: "span 2" }}>
          <div className="field-header">
            Campo 38 (Detalles de Mercadería)
            {esCampoAutocompletado('campo_38') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <textarea
            name="campo_38"
            value={mic.campo_38}
            onChange={handleChange}
            className="inputPro"
            rows={4}
            style={{ resize: "vertical", maxHeight: 120, width: "100%" }}
            placeholder="Auto-completado desde el Campo 11 del CRT"
            maxLength={1500}
          />
          {esCampoAutocompletado('campo_38') && (
            <small className="auto-help">Auto-completado desde detalles_mercaderia del CRT</small>
          )}
        </label>

        {/* CAMPO 40 */}
        <label>
          <div className="field-header">
            Campo 40 (Tramo) *
            {esCampoAutocompletado('campo_40_tramo') && <span className="auto-badge">✅ Auto</span>}
          </div>
          <select name="campo_40_tramo" value={mic.campo_40_tramo} onChange={handleChange} required className="inputPro">
            <option value="">Seleccione...</option>
            {OPCIONES_TRAMOS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </label>
      </div>

      {/* Campos manuales adicionales */}
      <hr className="my-4" />
      <h3 className="font-bold text-sm mb-2">Campos adicionales manuales (opcional)</h3>
      <div className="mic-form-grid">
        {Object.entries(mic).map(([key, val]) => {
          if (!CAMPOS_PRINCIPALES.includes(key) && key !== "campo_12_chasis") {
            return (
              <label key={key}>
                <div className="field-header">
                  {key.replace("campo_", "Campo ").replace(/_/g, " ")}
                  {esCampoAutocompletado(key) && <span className="auto-badge">✅ Auto</span>}
                </div>
                <input
                  name={key}
                  value={val}
                  onChange={handleChange}
                  className="inputPro"
                  type="text"
                  autoComplete="off"
                  maxLength={200}
                  placeholder="(opcional)"
                />
              </label>
            );
          }
          return null;
        })}
      </div>

      {/* ✅ ACCIONES MEJORADAS */}
      <div className="mic-form-actions">
        <div className="action-group">
          <button
            type="button"
            onClick={guardarMic}
            disabled={guardando}
            className="mic-btn mic-btn-save"
          >
            {guardando ? "💾 Guardando..." : "💾 Guardar MIC"}
          </button>
          <button
            type="button"
            onClick={generarPDFTemporal}
            disabled={loading}
            className="mic-btn mic-btn-preview"
          >
            {loading ? "📄 Generando..." : "👁️ Vista Previa PDF"}
          </button>
        </div>
        
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="mic-btn-cancel"
          >
            Cancelar
          </button>
        )}
      </div>

      {/* ✅ INFORMACIÓN DE AYUDA MEJORADA */}
      <div className="mic-help-info">
        <div className="help-section">
          <h4>💡 Integración CRT → MIC:</h4>
          <ul>
            <li><strong>💾 Guardar MIC:</strong> Guarda el MIC en la base de datos con datos integrados del CRT</li>
            <li><strong>👁️ Vista Previa PDF:</strong> Genera un PDF temporal usando la integración automática</li>
            <li><strong>🔄 Recarga:</strong> Usa el botón de recarga para actualizar datos del CRT</li>
            <li>Los campos con <span className="auto-badge-demo">✅ Auto</span> se completan automáticamente desde el CRT</li>
            <li>Los campos marcados con * son obligatorios</li>
            <li><strong>💰 Gastos:</strong> Los campos 28 (Flete) y 29 (Seguro) se calculan automáticamente desde los gastos del CRT</li>
          </ul>
        </div>
        
        {datosCRT && (
          <div className="help-section">
            <h4>📊 Resumen de integración:</h4>
            <div className="integration-summary">
              <div className="summary-item">
                <strong>CRT:</strong> {datosCRT.numero_crt}
              </div>
              <div className="summary-item">
                <strong>Transportadora:</strong> {datosCRT.transportadora?.nombre || 'N/A'}
              </div>
              <div className="summary-item">
                <strong>Remitente:</strong> {datosCRT.remitente?.nombre || 'N/A'}
              </div>
              <div className="summary-item">
                <strong>Campos auto-completados:</strong> {camposAutocompletados.length}
              </div>
              {(datosCRT.campo_28_total || datosCRT.campo_29_seguro) && (
                <div className="summary-item">
                  <strong>Gastos procesados:</strong> 
                  {datosCRT.campo_28_total && ` Flete: ${datosCRT.campo_28_total}`}
                  {datosCRT.campo_29_seguro && ` | Seguro: ${datosCRT.campo_29_seguro}`}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </form>
  );
}
       NUEVA FUNCIÓN: Cargar datos del CRT desde el backend Python
  const cargarDatosCRT = async () => {
    if (!crtId && !crtNumero) {
      console.log('⚠️ No se proporcionó crtId ni crtNumero');
      return;
    }
    
    setCargandoCRT(true);
    
    try {
      const endpoint = `${API_BASE_URL}/api/mic/get_crt_data/${crtId || crtNumero}`;
      console.log('🔍 Cargando datos del CRT desde:', endpoint);
      
      const response = await axios.get(endpoint);
      const { datos, numero_crt, campos_autocompletados } = response.data;
      
      console.log('📦 Datos del CRT recibidos:', datos);
      console.log('✅ Campos auto-completados:', campos_autocompletados);
      
      // Actualizar estado con datos del CRT
      setMic(prev => ({
        ...prev,
        ...datos,
        // Mapear campo_38 correctamente
        campo_38: datos.campo_38 || datos.detalles_mercaderia || "",
        // Asegurar valores por defecto
        campo_4_estado: datos.campo_4_estado || "PROVISORIO",
        campo_5_hoja: datos.campo_5_hoja || "1 / 1",
        campo_13_siempre_45: datos.campo_13_siempre_45 || "45 TON",
        campo_26_pais: datos.campo_26_pais || "520-PARAGUAY"
      }));
      
      setDatosCRT(datos);
      setCamposAutocompletados(campos_autocompletados || []);
      
      toast.success(`✅ CRT ${numero_crt} cargado exitosamente - ${campos_autocompletados?.length || 0} campos auto-completados`);
      
    } catch (error) {
      console.error('❌ Error cargando datos del CRT:', error);
      const errorMsg = error.response?.status === 404 
        ? `CRT ID ${crtId || crtNumero} no encontrado`
        : `Error de conexión: ${error.response?.data?.error || error.message}`;
      toast.error(`❌ ${errorMsg}`);
    } finally {
      setCargandoCRT(false);
    }
  };

  // ✅