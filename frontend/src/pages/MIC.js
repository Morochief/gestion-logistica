import React, { useState, useEffect } from "react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./MIC.css";

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

  // ✅ CARGAR DATOS DEL CRT desde microservicio Go
  useEffect(() => {
    if (!crtId && !crtNumero) {
      console.log('⚠️ No se proporcionó crtId ni crtNumero');
      return;
    }
    
    const endpoint = `http://localhost:8080/api/crts/${crtId || crtNumero}`;
    
    console.log('🔍 Cargando CRT desde microservicio Go:', endpoint);
    
    axios.get(endpoint)
      .then(res => {
        const crt = res.data;
        console.log('📦 CRT recibido:', crt);
        
        setMic(prev => ({
          ...prev,
          campo_24_aduana: crt.aduana || "",
          campo_30_tipo_bultos: crt.tipo_bultos || "",
          campo_40_tramo: crt.tramo || "",
          campo_9_datos_transporte:
            ((crt.transportadora_nombre || crt.transportadora || "") +
              (crt.transportadora_direccion ? "\n" + crt.transportadora_direccion : "")) || "",
          campo_38: crt.detalles_mercaderia || "",
          campo_6_fecha: crt.fecha_emision || new Date().toISOString().split('T')[0],
          campo_8_destino: crt.lugar_entrega || "",
          campo_23_numero_campo2_crt: crt.numero_crt || "",
          campo_25_moneda: crt.moneda?.nombre || "DOLAR AMERICANO",
          campo_26_pais: "520-PARAGUAY",
          campo_27_valor_campo16: crt.declaracion_mercaderia || "",
          campo_32_peso_bruto: crt.peso_bruto || "",
          campo_36_factura_despacho: crt.factura_exportacion && crt.nro_despacho 
            ? `Factura: ${crt.factura_exportacion} Despacho: ${crt.nro_despacho}`
            : (crt.factura_exportacion ? `Factura: ${crt.factura_exportacion}` : "")
        }));
        
        toast.success(`✅ CRT ${crt.numero_crt} cargado - Campo 38 auto-completado`);
      })
      .catch(err => {
        console.error('❌ Error cargando CRT:', err);
        const errorMsg = err.response?.status === 404 
          ? `CRT ID ${crtId || crtNumero} no encontrado`
          : `Error de conexión: ${err.message}`;
        toast.error(`❌ ${errorMsg}`);
      });
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
    if (!mic.campo_31_cantidad) err.push("Campo 31 obligatorio");
    if (!mic.campo_40_tramo) err.push("Campo 40 obligatorio");
    if (!mic.campo_7_pto_seguro) err.push("Campo 7 obligatorio");
    return err;
  };

  // ✅ NUEVA FUNCIÓN: Guardar MIC en base de datos
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
      
      // Decidir endpoint según si viene de CRT o es manual
      let endpoint, payload;
      
      if (crtId) {
        // Crear desde CRT y guardar
        endpoint = `http://localhost:5000/api/mic-guardados/crear-desde-crt/${crtId}`;
        payload = micToSave;
      } else {
        // Crear manual y guardar
        endpoint = `http://localhost:5000/api/mic-guardados/`;
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

  // ✅ FUNCIÓN MEJORADA: Generar PDF temporal (sin guardar)
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
      console.log('📄 Generando PDF temporal...');
      const crtIdToUse = crtId || "temp";
      const res = await axios.post(
        `http://localhost:5000/api/mic/generate_pdf_from_crt/${crtIdToUse}`,
        micToSend,
        { responseType: "blob" }
      );
      
      const blob = new Blob([res.data], { type: "application/pdf" });
      window.open(URL.createObjectURL(blob), "_blank");
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
        `http://localhost:5000/api/mic-guardados/${micId}/pdf`,
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
        {(crtId || crtNumero) && <span className="text-blue-600"> (CRT: {crtNumero || crtId})</span>}
      </h2>

      <div className="mic-form-grid">
        {/* CAMPO 2 */}
        <label>
          Campo 2 (Rol contribuyente) *
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
          Campo 3 (Transporte, dejar vacío)
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
          Campo 4 (Estado)
          <select name="campo_4_estado" value={mic.campo_4_estado} onChange={handleChange} className="inputPro">
            <option value="PROVISORIO">PROVISORIO</option>
            <option value="DEFINITIVO">DEFINITIVO</option>
            <option value="EN_PROCESO">EN_PROCESO</option>
          </select>
        </label>
        
        {/* CAMPO 6 */}
        <label>
          Campo 6 (Fecha de emisión)
          <input 
            name="campo_6_fecha" 
            type="date" 
            value={mic.campo_6_fecha} 
            onChange={handleChange} 
            className="inputPro"
          />
          <small style={{ color: "#666", fontSize: "0.8em" }}>Auto-completado desde el CRT</small>
        </label>
        
        {/* CAMPO 7 */}
        <label>
          Campo 7 (Pto Seguro) *
          <select name="campo_7_pto_seguro" value={mic.campo_7_pto_seguro} onChange={handleChange} required className="inputPro">
            <option value="">Seleccione...</option>
            {OPCIONES_7.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </label>
        
        {/* CAMPO 8 */}
        <label>
          Campo 8 (Ciudad y país de destino final)
          <input 
            name="campo_8_destino" 
            value={mic.campo_8_destino} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="Ciudad de destino"
          />
          <small style={{ color: "#666", fontSize: "0.8em" }}>Auto-completado desde lugar_entrega del CRT</small>
        </label>

        {/* CAMPO 9 */}
        <label>
          Campo 9 (CAMIÓN ORIGINAL: Nombre y domicilio del propietario)
          <textarea
            name="campo_9_datos_transporte"
            value={mic.campo_9_datos_transporte}
            onChange={handleChange}
            className="inputPro"
            rows={3}
            style={{ resize: "vertical", maxHeight: 80 }}
            placeholder="Nombre y dirección (auto-completado desde CRT)"
          />
        </label>

        {/* CAMPO 10 */}
        <label>
          Campo 10 (Rol contribuyente) *
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
          Campo 11 (Placa) *
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
          Campo 12 (Modelo/Chasis) *
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
          Campo 14 (Año) *
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
          Campo 15 (Placa Semi) *
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
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span style={{ fontWeight: "bold" }}>Campo 23 (Nº carta de porte)</span>
            {mic.campo_23_numero_campo2_crt && <span style={{ color: "#10b981", fontSize: "0.8em" }}>✅ Auto-completado</span>}
          </div>
          <input 
            name="campo_23_numero_campo2_crt" 
            value={mic.campo_23_numero_campo2_crt} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="Número del CRT"
          />
        </label>
        
        {/* CAMPO 24 */}
        <label>
          Campo 24 (Aduana) *
          <select name="campo_24_aduana" value={mic.campo_24_aduana} onChange={handleChange} required className="inputPro">
            <option value="">Seleccione...</option>
            {OPCIONES_AUDANA.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </label>
        
        {/* CAMPO 25 */}
        <label>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span style={{ fontWeight: "bold" }}>Campo 25 (Moneda)</span>
            {mic.campo_25_moneda && <span style={{ color: "#10b981", fontSize: "0.8em" }}>✅ Auto-completado</span>}
          </div>
          <select name="campo_25_moneda" value={mic.campo_25_moneda} onChange={handleChange} className="inputPro">
            <option value="DOLAR AMERICANO">DOLAR AMERICANO</option>
            <option value="GUARANI">GUARANI</option>
            <option value="REAL">REAL</option>
            <option value="PESO ARGENTINO">PESO ARGENTINO</option>
            <option value="EURO">EURO</option>
          </select>
        </label>
        
        {/* CAMPO 26 */}
        <label>
          Campo 26 (Origen de las mercaderías)
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
          Campo 27 (Valor FOT)
          <input 
            name="campo_27_valor_campo16" 
            type="number" 
            step="0.01"
            value={mic.campo_27_valor_campo16} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="0.00"
          />
        </label>

        {/* CAMPO 30 */}
        <label>
          Campo 30 (Tipo Bultos) *
          <select name="campo_30_tipo_bultos" value={mic.campo_30_tipo_bultos} onChange={handleChange} required className="inputPro">
            <option value="">Seleccione...</option>
            {OPCIONES_BULTOS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </label>

        {/* CAMPO 31 */}
        <label>
          Campo 31 (Cantidad) *
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
          Campo 32 (Peso bruto)
          <input 
            name="campo_32_peso_bruto" 
            type="number" 
            step="0.001"
            value={mic.campo_32_peso_bruto} 
            onChange={handleChange} 
            className="inputPro"
            placeholder="0.000"
          />
        </label>
        
        {/* CAMPO 36 */}
        <label style={{ gridColumn: "span 2" }}>
          Campo 36 (Documentos anexos)
          <input 
            name="campo_36_factura_despacho" 
            value={mic.campo_36_factura_despacho} 
            onChange={handleChange} 
            className="inputPro"
            style={{ width: "100%" }}
            placeholder="Factura: XXX Despacho: YYY"
          />
        </label>

        {/* CAMPO 37 */}
        <label>
          Campo 37 (Manual)
          <input 
            name="campo_37_valor_manual" 
            value={mic.campo_37_valor_manual} 
            onChange={handleChange} 
            className="inputPro" 
          />
        </label>

        {/* CAMPO 38 */}
        <label style={{ gridColumn: "span 2" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span style={{ fontWeight: "bold" }}>Campo 38 (Detalles de Mercadería)</span>
            {mic.campo_38 && <span style={{ color: "#10b981", fontSize: "0.8em" }}>✅ Auto-completado</span>}
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
        </label>

        {/* CAMPO 40 */}
        <label>
          Campo 40 (Tramo) *
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
                {key.replace("campo_", "Campo ").replace(/_/g, " ")}
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

      {/* ✅ INFORMACIÓN DE AYUDA */}
      <div className="mic-help-info">
        <div className="help-section">
          <h4>💡 Opciones disponibles:</h4>
          <ul>
            <li><strong>💾 Guardar MIC:</strong> Guarda el MIC en la base de datos para futuras consultas</li>
            <li><strong>👁️ Vista Previa PDF:</strong> Genera un PDF temporal sin guardar en base de datos</li>
            <li>Los campos marcados con <span style={{color: "#10b981"}}>✅ Auto-completado</span> se llenan desde el CRT</li>
            <li>Los campos marcados con * son obligatorios</li>
          </ul>
        </div>
      </div>
    </form>
  );
}