// frontend/src/pages/MICsGuardados.js
import React, { useState, useEffect, useCallback, useRef } from "react";
import api from "../api/api";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./MICsGuardados.css";
import ModalMICCompleto from "./ModalMICCompleto";

// ✅ CONFIGURACIÓN DE ESTADOS Y TRANSICIONES (Sincronizada con backend)
const ESTADOS_MIC = {
  PROVISORIO: {
    label: 'Provisorio',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: '📝',
    canTransitionTo: ['DEFINITIVO', 'ANULADO'],
    requiresConfirmation: false,
    allowDirectEdit: true,
    priority: 1
  },
  DEFINITIVO: {
    label: 'Definitivo', 
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: '📋',
    canTransitionTo: ['CONFIRMADO', 'EN_PROCESO', 'ANULADO'],
    requiresConfirmation: true,
    allowDirectEdit: true,
    priority: 2
  },
  CONFIRMADO: {
    label: 'Confirmado',
    color: 'bg-green-100 text-green-800 border-green-200', 
    icon: '✅',
    canTransitionTo: ['EN_PROCESO', 'FINALIZADO', 'ANULADO'],
    requiresConfirmation: true,
    allowDirectEdit: false,
    priority: 3
  },
  EN_PROCESO: {
    label: 'En Proceso',
    color: 'bg-purple-100 text-purple-800 border-purple-200',
    icon: '⚙️', 
    canTransitionTo: ['FINALIZADO', 'ANULADO'],
    requiresConfirmation: true,
    allowDirectEdit: false,
    priority: 4
  },
  FINALIZADO: {
    label: 'Finalizado',
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: '🏁',
    canTransitionTo: [],
    requiresConfirmation: false,
    allowDirectEdit: false,
    priority: 5,
    isFinal: true
  },
  ANULADO: {
    label: 'Anulado', 
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: '❌',
    canTransitionTo: [],
    requiresConfirmation: false,
    allowDirectEdit: false,
    priority: 0,
    isFinal: true
  }
};

// ✅ HOOK PROFESIONAL PARA GESTIÓN DE ESTADOS
const useEstadosMIC = () => {
  const [loadingEstado, setLoadingEstado] = useState(null);
  const [configuracionBackend, setConfiguracionBackend] = useState(null);

  // Cargar configuración del backend (opcional)
  useEffect(() => {
    const cargarConfiguracion = async () => {
      try {
        const { data } = await api.get('mic-guardados/estados-config');
        setConfiguracionBackend(data.estados);
      } catch (error) {
        console.warn('⚠️ No se pudo cargar configuración del backend, usando local');
      }
    };
    cargarConfiguracion();
  }, []);

  const puedeTransicionar = (estadoActual, estadoDestino) => {
    const config = ESTADOS_MIC[estadoActual];
    return config && config.canTransitionTo.includes(estadoDestino);
  };

  const obtenerEstadosDisponibles = (estadoActual) => {
    const config = ESTADOS_MIC[estadoActual];
    return config ? config.canTransitionTo : [];
  };

  const requiereConfirmacion = (estadoActual, estadoDestino) => {
    const config = ESTADOS_MIC[estadoDestino];
    return config && config.requiresConfirmation;
  };

  const puedeEditarDirectamente = (estadoActual) => {
    const config = ESTADOS_MIC[estadoActual];
    return config && config.allowDirectEdit;
  };

  const cambiarEstado = async (micId, estadoActual, estadoDestino, numeroCarta, onSuccess) => {
    // Validar transición
    if (!puedeTransicionar(estadoActual, estadoDestino)) {
      toast.error(`❌ No se puede cambiar de ${estadoActual} a ${estadoDestino}`);
      return false;
    }

    // Confirmación si es requerida
    if (requiereConfirmacion(estadoActual, estadoDestino)) {
      const configDestino = ESTADOS_MIC[estadoDestino];
      const mensaje = `¿Confirmar cambio de estado del MIC ${numeroCarta || micId}?\n\n${estadoActual} → ${estadoDestino}\n\n${configDestino.icon} ${configDestino.label}`;
      if (!window.confirm(mensaje)) return false;
    }

    try {
      setLoadingEstado(micId);
      
      const response = await api.put(`mic-guardados/${micId}`, {
        campo_4_estado: estadoDestino,
        ultima_actualizacion: new Date().toISOString(),
        cambio_estado_motivo: `Cambio de ${estadoActual} a ${estadoDestino}`,
        usuario_actualizacion: "Usuario Sistema", // Reemplazar con usuario real
      });

      const configDestino = ESTADOS_MIC[estadoDestino];
      toast.success(`✅ ${configDestino.icon} Estado cambiado a ${configDestino.label}`, {
        position: "top-right",
        autoClose: 3000,
      });

      onSuccess && onSuccess(response.data);
      return true;
      
    } catch (error) {
      console.error("❌ Error cambiando estado:", error);
      
      if (error.response?.status === 400) {
        // Error de validación de transición
        const errorData = error.response.data;
        toast.error(`❌ ${errorData.error}`, { autoClose: 5000 });
        
        if (errorData.transiciones_permitidas) {
          const permitidas = errorData.transiciones_permitidas.map(e => ESTADOS_MIC[e]?.label || e).join(', ');
          toast.info(`💡 Transiciones permitidas desde ${estadoActual}: ${permitidas}`, { autoClose: 7000 });
        }
      } else if (error.response?.status === 403) {
        // Error de permisos de edición
        toast.error(`🔒 ${error.response.data.error}`, { autoClose: 5000 });
      } else {
        toast.error(`❌ Error: ${error.response?.data?.error || error.message}`, { autoClose: 5000 });
      }
      
      return false;
    } finally {
      setLoadingEstado(null);
    }
  };

  return {
    cambiarEstado,
    puedeTransicionar,
    obtenerEstadosDisponibles,
    requiereConfirmacion,
    puedeEditarDirectamente,
    loadingEstado,
    ESTADOS_MIC,
    configuracionBackend
  };
};

// ✅ COMPONENTE PROFESIONAL DE GESTIÓN DE ESTADO
const GestorEstadoMIC = ({ mic, onEstadoCambiado, compact = false }) => {
  const { 
    cambiarEstado, 
    obtenerEstadosDisponibles, 
    loadingEstado,
    ESTADOS_MIC 
  } = useEstadosMIC();

  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const estadoActual = mic.campo_4_estado || 'PROVISORIO';
  const configEstado = ESTADOS_MIC[estadoActual];
  const estadosDisponibles = obtenerEstadosDisponibles(estadoActual);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleCambioEstado = async (nuevoEstado) => {
    const exito = await cambiarEstado(
      mic.id,
      estadoActual,
      nuevoEstado,
      mic.campo_23_numero_campo2_crt,
      onEstadoCambiado
    );
    
    if (exito) {
      setShowDropdown(false);
    }
  };

  // Obtener acción rápida más común según el estado
  const getAccionRapida = () => {
    switch (estadoActual) {
      case 'PROVISORIO':
        return { estado: 'DEFINITIVO', label: 'Confirmar', icon: '✅', color: 'bg-green-500 hover:bg-green-600' };
      case 'DEFINITIVO':
        return { estado: 'CONFIRMADO', label: 'Aprobar', icon: '👍', color: 'bg-blue-500 hover:bg-blue-600' };
      case 'CONFIRMADO':
        return { estado: 'EN_PROCESO', label: 'Procesar', icon: '⚙️', color: 'bg-purple-500 hover:bg-purple-600' };
      case 'EN_PROCESO':
        return { estado: 'FINALIZADO', label: 'Finalizar', icon: '🏁', color: 'bg-gray-500 hover:bg-gray-600' };
      default:
        return null;
    }
  };

  const accionRapida = getAccionRapida();

  if (compact) {
    // Versión compacta para tabla
    return (
      <div className="flex items-center space-x-1">
        {/* Estado actual */}
        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${configEstado?.color || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
          <span className="mr-1">{configEstado?.icon}</span>
          {configEstado?.label || estadoActual}
        </span>

        {/* Acción rápida */}
        {accionRapida && estadosDisponibles.includes(accionRapida.estado) && (
          <button
            onClick={() => handleCambioEstado(accionRapida.estado)}
            disabled={loadingEstado === mic.id}
            className={`px-2 py-1 rounded text-xs text-white font-medium transition-colors ${
              loadingEstado === mic.id ? 'bg-gray-400 cursor-not-allowed' : accionRapida.color
            }`}
            title={`Cambiar a ${ESTADOS_MIC[accionRapida.estado]?.label}`}
          >
            {loadingEstado === mic.id ? '...' : accionRapida.icon}
          </button>
        )}

        {/* Dropdown para otros estados */}
        {estadosDisponibles.length > (accionRapida ? 1 : 0) && (
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="px-2 py-1 bg-gray-500 text-white rounded text-xs hover:bg-gray-600 transition-colors"
              title="Más opciones de estado"
            >
              ▼
            </button>

            {showDropdown && (
              <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-48">
                <div className="py-1">
                  <div className="px-3 py-2 text-xs font-medium text-gray-500 border-b border-gray-100">
                    Cambiar estado
                  </div>
                  {estadosDisponibles
                    .filter(estado => !accionRapida || estado !== accionRapida.estado)
                    .map(estado => {
                      const config = ESTADOS_MIC[estado];
                      return (
                        <button
                          key={estado}
                          onClick={() => handleCambioEstado(estado)}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center space-x-2 transition-colors"
                        >
                          <span>{config?.icon}</span>
                          <div className="flex-1">
                            <span className="font-medium">{config?.label}</span>
                            {config?.requiresConfirmation && (
                              <div className="text-xs text-gray-500">Requiere confirmación</div>
                            )}
                          </div>
                        </button>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // Versión completa para modal/detalles
  return (
    <div className="estado-gestor-completo p-4 bg-gray-50 rounded-lg">
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Estado Actual
        </label>
        <div className={`inline-flex items-center px-4 py-2 rounded-lg border-2 ${configEstado?.color || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
          <span className="text-lg mr-2">{configEstado?.icon}</span>
          <span className="font-medium">{configEstado?.label || estadoActual}</span>
        </div>
      </div>

      {estadosDisponibles.length > 0 && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Transiciones Disponibles
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {estadosDisponibles.map(estado => {
              const config = ESTADOS_MIC[estado];
              const esAccionRapida = accionRapida && estado === accionRapida.estado;
              
              return (
                <button
                  key={estado}
                  onClick={() => handleCambioEstado(estado)}
                  disabled={loadingEstado === mic.id}
                  className={`p-4 border-2 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
                    esAccionRapida 
                      ? 'border-green-300 bg-green-50 hover:bg-green-100' 
                      : 'border-gray-200 bg-white hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{config?.icon}</span>
                    <div className="text-left flex-1">
                      <div className="font-medium text-sm">{config?.label}</div>
                      {config?.requiresConfirmation && (
                        <div className="text-xs text-gray-500 mt-1">
                          🔔 Requiere confirmación
                        </div>
                      )}
                      {esAccionRapida && (
                        <div className="text-xs text-green-600 mt-1 font-medium">
                          ⚡ Acción recomendada
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {estadosDisponibles.length === 0 && (
        <div className="text-sm text-gray-500 italic p-3 bg-gray-100 rounded-lg">
          {configEstado?.isFinal 
            ? `🏁 ${configEstado?.label} es un estado final. No hay más transiciones disponibles.`
            : `No hay transiciones de estado disponibles desde ${configEstado?.label || estadoActual}`
          }
        </div>
      )}

      {loadingEstado === mic.id && (
        <div className="mt-3 flex items-center justify-center text-sm text-gray-600">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
          Actualizando estado...
        </div>
      )}
    </div>
  );
};

// ========== COMPONENTE PRINCIPAL MICsGuardados ==========
export default function MICsGuardados() {
  const [mics, setMics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMic, setSelectedMic] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [perPage] = useState(15);
  const [showFilters, setShowFilters] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);

  // Estados para edición
  const [modalEdicion, setModalEdicion] = useState({
    isOpen: false,
    mic: null,
    accion: 'editar'
  });
  const [loadingAction, setLoadingAction] = useState(null);

  // Hook de estados MIC
  const { puedeEditarDirectamente, ESTADOS_MIC } = useEstadosMIC();

  // Filtros
  const [filters, setFilters] = useState({
    estado: "",
    numero_carta: "",
    fecha_desde: "",
    fecha_hasta: "",
    transportadora: "",
    placa: "",
    destino: "",
  });

  // ========= Helpers =========
  const formatearFecha = (fecha) => {
    if (!fecha) return "N/A";
    try {
      const d = new Date(fecha);
      if (isNaN(d.getTime())) return fecha;
      return d.toLocaleDateString("es-PY");
    } catch {
      return fecha;
    }
  };

  // Formatear datos numéricos para backend
  const formatearNumeroParaBackend = (valor, tipoFormato = 'decimal') => {
    if (!valor) return null;
    
    const numero = parseFloat(valor.toString().replace(',', '.'));
    if (isNaN(numero)) return null;
    
    switch (tipoFormato) {
      case 'peso':
        return Number(numero.toFixed(3));
      case 'decimal':
        return Number(numero.toFixed(2));
      case 'entero':
        return Number(Math.round(numero));
      case 'string':
        return numero.toString();
      case 'anio':
        return Math.round(numero).toString();
      default:
        return Number(numero.toFixed(2));
    }
  };

  // ========= Cargar lista =========
  const cargarMics = useCallback(
    async (page = 1, filtros = {}) => {
      setLoading(true);
      try {
        const params = { page, per_page: perPage, ...filtros };
        const { data } = await api.get("mic-guardados/", { params });

        setMics(data.mics || []);
        setCurrentPage(data.pagination?.page || 1);
        setTotalPages(data.pagination?.pages || 1);
        setTotalItems(data.pagination?.total || 0);

        if ((data.mics || []).length === 0 && Object.values(filtros).some((v) => v)) {
          toast.info("🔍 No se encontraron MICs con los filtros aplicados");
        }
      } catch (err) {
        console.error("❌ Error cargando MICs:", err);
        toast.error(`❌ Error cargando MICs: ${err.response?.data?.error || err.message}`);
      } finally {
        setLoading(false);
      }
    },
    [perPage]
  );

  // Cargar estadísticas
  const cargarEstadisticas = useCallback(async () => {
    try {
      const { data } = await api.get("mic-guardados/stats");
      setStats(data);
    } catch (err) {
      console.warn("ℹ️ Estadísticas no disponibles:", err?.response?.status || err.message);
      setStats(null);
    }
  }, []);

  useEffect(() => {
    cargarMics();
    cargarEstadisticas();
  }, [cargarMics, cargarEstadisticas]);

  // ========= Filtros =========
  const aplicarFiltros = () => {
    cargarMics(1, filters);
    setCurrentPage(1);
    setShowFilters(false);
    toast.info("🔍 Filtros aplicados");
  };

  const limpiarFiltros = () => {
    const limpia = {
      estado: "",
      numero_carta: "",
      fecha_desde: "",
      fecha_hasta: "",
      transportadora: "",
      placa: "",
      destino: "",
    };
    setFilters(limpia);
    cargarMics();
    toast.info("🧹 Filtros limpiados");
  };

  // ========== FUNCIONES DE EDICIÓN ==========
  
  const editarMIC = async (micId) => {
    const mic = mics.find(m => m.id === micId);
    
    // Validar si puede editar según el estado
    if (mic && !puedeEditarDirectamente(mic.campo_4_estado)) {
      toast.warning(`⚠️ No se puede editar un MIC en estado ${mic.campo_4_estado}. Solo se permite cambio de estado.`);
      return;
    }

    try {
      console.log(`🔄 Cargando MIC ${micId} para edición...`);
      setLoadingAction(micId);

      const { data } = await api.get(`mic-guardados/${micId}`);
      
      console.log("✅ MIC cargado para edición:", data);

      setModalEdicion({
        isOpen: true,
        mic: data,
        accion: 'editar'
      });

    } catch (error) {
      console.error("❌ Error cargando MIC para edición:", error);
      toast.error("❌ Error al cargar MIC para edición");
    } finally {
      setLoadingAction(null);
    }
  };

  const guardarCambiosMIC = async (datosModal) => {
    const mic = modalEdicion.mic;
    if (!mic) return;

    try {
      console.log(`🔄 Guardando cambios del MIC ${mic.id}...`);
      setLoadingAction(mic.id);

      // FORMATEAR DATOS NUMÉRICOS CORRECTAMENTE
      const datosFormateados = { ...datosModal };
      
      const camposNumericos = {
        'campo_32_peso_bruto': 'peso',
        'campo_27_valor_campo16': 'decimal',
        'campo_28_total': 'decimal', 
        'campo_29_seguro': 'decimal',
        'campo_37_valor_manual': 'decimal',
        'campo_14_anio': 'anio',
        'campo_31_cantidad': 'string',
        'campo_10_numero': 'string',
      };

      Object.keys(camposNumericos).forEach(campo => {
        if (datosFormateados[campo]) {
          const tipoFormato = camposNumericos[campo];
          datosFormateados[campo] = formatearNumeroParaBackend(datosFormateados[campo], tipoFormato);
        }
      });

      const camposTexto = [
        'campo_1_transporte', 'campo_2_numero', 'campo_3_transporte', 
        'campo_7_pto_seguro', 'campo_8_destino', 'campo_11_placa', 
        'campo_12_modelo_chasis', 'campo_15_placa_semi', 'campo_24_aduana', 
        'campo_25_moneda', 'campo_26_pais', 'campo_30_tipo_bultos', 
        'campo_36_factura_despacho', 'campo_38_datos_campo11_crt', 
        'campo_40_tramo', 'campo_4_estado', 'campo_5_hoja', 'campo_6_fecha'
      ];

      camposTexto.forEach(campo => {
        if (datosFormateados[campo] !== undefined && datosFormateados[campo] !== null) {
          datosFormateados[campo] = datosFormateados[campo].toString();
        }
      });

      await api.put(`mic-guardados/${mic.id}`, {
        ...datosFormateados,
        ultima_actualizacion: new Date().toISOString(),
        usuario_actualizacion: "Usuario Sistema",
      });

      toast.success(
        `✅ MIC ${mic.campo_23_numero_campo2_crt || mic.id} actualizado exitosamente!`
      );

      setModalEdicion({ isOpen: false, mic: null, accion: null });
      cargarMics(currentPage, filters);

    } catch (error) {
      console.error("❌ Error actualizando MIC:", error);
      
      if (error.response?.status === 400) {
        toast.error(`❌ ${error.response.data.error}`);
      } else if (error.response?.status === 403) {
        toast.error(`🔒 ${error.response.data.error}`);
      } else if (error.response?.status === 404) {
        toast.error("❌ MIC no encontrado");
      } else {
        toast.error(`❌ Error actualizando MIC: ${error.response?.data?.error || error.message}`);
      }
    } finally {
      setLoadingAction(null);
    }
  };

  const duplicarMIC = async (micId) => {
    if (!window.confirm("¿Crear una copia de este MIC?")) return;

    try {
      setLoadingAction(micId);
      
      const { data } = await api.post(`mic-guardados/${micId}/duplicate`);
      
      toast.success(
        `✅ MIC duplicado exitosamente!\n🆔 Nuevo ID: ${data.id}`
      );
      
      cargarMics(currentPage, filters);
      
    } catch (error) {
      console.error("❌ Error duplicando MIC:", error);
      toast.error(
        `❌ Error duplicando MIC: ${error.response?.data?.error || error.message}`
      );
    } finally {
      setLoadingAction(null);
    }
  };

  const cerrarModalEdicion = () => {
    setModalEdicion({ isOpen: false, mic: null, accion: null });
  };

  // ========= Acciones EXISTENTES =========
  const verDetalles = async (micId) => {
    try {
      const { data } = await api.get(`mic-guardados/${micId}`);
      setSelectedMic(data);
      setShowModal(true);
    } catch (err) {
      console.warn("ℹ️ Detalle por API no disponible, intento con el item de la tabla.");
      const fallback = mics.find((x) => x.id === micId);
      if (fallback) {
        setSelectedMic(fallback);
        setShowModal(true);
      } else {
        toast.error("❌ No se pudo obtener el detalle del MIC.");
      }
    }
  };

  const descargarPDF = async (micId, numeroCarta) => {
    try {
      const response = await api.get(`mic-guardados/${micId}/pdf`, {
        responseType: "blob",
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `MIC_${numeroCarta || micId}_${new Date().toISOString().split("T")[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success("📄 PDF descargado");
    } catch (err) {
      console.error("❌ Error descargando PDF:", err);
      toast.error("❌ Error descargando PDF");
    }
  };

  const anularMic = async (micId, numeroCarta) => {
    if (!window.confirm(`¿Estás seguro de anular el MIC ${numeroCarta || micId}?`)) return;
    try {
      await api.delete(`mic-guardados/${micId}`);
      toast.success("✅ MIC anulado");
      cargarMics(currentPage, filters);
    } catch (err) {
      console.error("❌ Error anulando MIC:", err);
      toast.error("❌ Error anulando MIC");
    }
  };

  const cambiarPagina = (nuevaPagina) => {
    if (nuevaPagina >= 1 && nuevaPagina <= totalPages) {
      setCurrentPage(nuevaPagina);
      cargarMics(nuevaPagina, filters);
    }
  };

  // ========= Render =========
  return (
    <div className="mics-guardados-container">
      <ToastContainer position="top-right" autoClose={4000} />

      {/* Header */}
      <div className="header-section">
        <div className="header-content">
          <div>
            <h1 className="page-title">📋 MICs Guardados</h1>
            <p className="page-subtitle">
              {totalItems} MICs registrados • Página {currentPage} de {totalPages}
            </p>
          </div>

          <div className="header-actions">
            <button onClick={() => setShowStats(!showStats)} className="btn-secondary">
              📊 {showStats ? "Ocultar" : "Ver"} Estadísticas
            </button>
            <button onClick={() => setShowFilters(!showFilters)} className="btn-primary">
              🔍 {showFilters ? "Ocultar" : "Mostrar"} Filtros
            </button>
            <button onClick={() => cargarMics(currentPage, filters)} className="btn-primary" disabled={loading}>
              🔄 Actualizar
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      {showStats && stats && (
        <div className="stats-section">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.total_mics}</div>
              <div className="stat-label">Total MICs</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.mics_hoy}</div>
              <div className="stat-label">Hoy</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.mics_semana}</div>
              <div className="stat-label">Esta semana</div>
            </div>
            {(stats.por_estado || []).map((est, idx) => (
              <div key={idx} className="stat-card">
                <div className="stat-value">{est.cantidad}</div>
                <div className="stat-label">{est.estado}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filtros */}
      {showFilters && (
        <div className="filters-section">
          <div className="filters-grid">
            <div className="filter-group">
              <label>Estado</label>
              <select
                value={filters.estado}
                onChange={(e) => setFilters({ ...filters, estado: e.target.value })}
                className="filter-input"
              >
                <option value="">Todos</option>
                {Object.entries(ESTADOS_MIC).map(([key, config]) => (
                  <option key={key} value={key}>
                    {config.icon} {config.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Nº Carta de Porte</label>
              <input
                type="text"
                value={filters.numero_carta}
                onChange={(e) => setFilters({ ...filters, numero_carta: e.target.value })}
                placeholder="Buscar por número..."
                className="filter-input"
              />
            </div>

            <div className="filter-group">
              <label>Transportadora</label>
              <input
                type="text"
                value={filters.transportadora}
                onChange={(e) => setFilters({ ...filters, transportadora: e.target.value })}
                placeholder="Buscar transportadora..."
                className="filter-input"
              />
            </div>

            <div className="filter-group">
              <label>Placa</label>
              <input
                type="text"
                value={filters.placa}
                onChange={(e) => setFilters({ ...filters, placa: e.target.value })}
                placeholder="Buscar placa..."
                className="filter-input"
              />
            </div>

            <div className="filter-group">
              <label>Destino</label>
              <input
                type="text"
                value={filters.destino}
                onChange={(e) => setFilters({ ...filters, destino: e.target.value })}
                placeholder="Buscar destino..."
                className="filter-input"
              />
            </div>

            <div className="filter-group">
              <label>Fecha Desde</label>
              <input
                type="date"
                value={filters.fecha_desde}
                onChange={(e) => setFilters({ ...filters, fecha_desde: e.target.value })}
                className="filter-input"
              />
            </div>

            <div className="filter-group">
              <label>Fecha Hasta</label>
              <input
                type="date"
                value={filters.fecha_hasta}
                onChange={(e) => setFilters({ ...filters, fecha_hasta: e.target.value })}
                className="filter-input"
              />
            </div>
          </div>

          <div className="filters-actions">
            <button onClick={aplicarFiltros} className="btn-primary">
              🔍 Aplicar Filtros
            </button>
            <button onClick={limpiarFiltros} className="btn-secondary">
              🧹 Limpiar
            </button>
          </div>
        </div>
      )}

      {/* Tabla */}
      <div className="table-section">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Cargando MICs...</p>
          </div>
        ) : mics.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h3>No hay MICs guardados</h3>
            <p>No se encontraron MICs con los criterios especificados.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="mics-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nº Carta</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Transportadora</th>
                  <th>Destino</th>
                  <th>Placa</th>
                  <th>Peso</th>
                  <th>Creado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {mics.map((mic) => (
                  <tr key={mic.id} className="table-row">
                    <td className="id-cell">#{mic.id}</td>

                    <td className="numero-cell">
                      {mic.campo_23_numero_campo2_crt || "Sin número"}
                    </td>

                    {/* ✅ NUEVA CELDA DE ESTADO PROFESIONAL */}
                    <td className="estado-cell">
                      <GestorEstadoMIC 
                        mic={mic} 
                        onEstadoCambiado={() => cargarMics(currentPage, filters)}
                        compact={true}
                      />
                    </td>

                    <td className="fecha-cell">{formatearFecha(mic.campo_6_fecha)}</td>

                    <td className="transportadora-cell" title={mic.campo_1_transporte}>
                      {mic.campo_1_transporte
                        ? mic.campo_1_transporte.length > 30
                          ? mic.campo_1_transporte.substring(0, 30) + "..."
                          : mic.campo_1_transporte
                        : "N/A"}
                    </td>

                    <td className="destino-cell">{mic.campo_8_destino || "N/A"}</td>

                    <td className="placa-cell">{mic.campo_11_placa || "N/A"}</td>

                    <td className="peso-cell">
                      {mic.campo_32_peso_bruto ? `${mic.campo_32_peso_bruto} kg` : "N/A"}
                    </td>

                    <td className="creado-cell">{formatearFecha(mic.creado_en)}</td>

                    <td className="acciones-cell">
                      <div className="acciones-group">
                        <button
                          onClick={() => verDetalles(mic.id)}
                          className="btn-action btn-view"
                          title="Ver detalles"
                        >
                          👁️
                        </button>

                        {/* ✅ BOTÓN EDITAR CON VALIDACIÓN DE ESTADO */}
                        {puedeEditarDirectamente(mic.campo_4_estado) ? (
                          <button
                            onClick={() => editarMIC(mic.id)}
                            disabled={loadingAction === mic.id}
                            className="btn-action btn-edit"
                            title="Editar MIC"
                            style={{
                              backgroundColor: loadingAction === mic.id ? '#ccc' : '#f59e0b',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              padding: '4px 8px',
                              cursor: loadingAction === mic.id ? 'not-allowed' : 'pointer'
                            }}
                          >
                            {loadingAction === mic.id ? "..." : "✏️"}
                          </button>
                        ) : (
                          <button
                            onClick={() => toast.info(`ℹ️ No se puede editar en estado ${mic.campo_4_estado}. Solo cambio de estado permitido.`)}
                            className="btn-action btn-edit-disabled"
                            title={`No editable en estado ${mic.campo_4_estado}`}
                            style={{
                              backgroundColor: '#e5e7eb',
                              color: '#6b7280',
                              border: 'none',
                              borderRadius: '4px',
                              padding: '4px 8px',
                              cursor: 'not-allowed'
                            }}
                          >
                            🔒
                          </button>
                        )}

                        <button
                          onClick={() => duplicarMIC(mic.id)}
                          disabled={loadingAction === mic.id}
                          className="btn-action btn-duplicate"
                          title="Duplicar MIC"
                          style={{
                            backgroundColor: loadingAction === mic.id ? '#ccc' : '#3b82f6',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            padding: '4px 8px',
                            cursor: loadingAction === mic.id ? 'not-allowed' : 'pointer'
                          }}
                        >
                          {loadingAction === mic.id ? "..." : "📋"}
                        </button>

                        <button
                          onClick={() =>
                            descargarPDF(mic.id, mic.campo_23_numero_campo2_crt)
                          }
                          className="btn-action btn-download"
                          title="Descargar PDF"
                        >
                          📄
                        </button>

                        {mic.campo_4_estado !== "ANULADO" && mic.campo_4_estado !== "FINALIZADO" && (
                          <button
                            onClick={() =>
                              anularMic(mic.id, mic.campo_23_numero_campo2_crt)
                            }
                            className="btn-action btn-delete"
                            title="Anular MIC"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Paginación */}
      {totalPages > 1 && (
        <div className="pagination-section">
          <div className="pagination-info">
            Mostrando {(currentPage - 1) * perPage + 1} a{" "}
            {Math.min(currentPage * perPage, totalItems)} de {totalItems} registros
          </div>

          <div className="pagination-controls">
            <button
              onClick={() => cambiarPagina(1)}
              disabled={currentPage === 1}
              className="pagination-btn"
            >
              ⏮️
            </button>
            <button
              onClick={() => cambiarPagina(currentPage - 1)}
              disabled={currentPage === 1}
              className="pagination-btn"
            >
              ⬅️
            </button>

            {[...Array(Math.min(5, totalPages))].map((_, i) => {
              const pageNum = Math.max(1, currentPage - 2) + i;
              if (pageNum <= totalPages) {
                return (
                  <button
                    key={pageNum}
                    onClick={() => cambiarPagina(pageNum)}
                    className={`pagination-btn ${
                      pageNum === currentPage ? "active" : ""
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              }
              return null;
            })}

            <button
              onClick={() => cambiarPagina(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="pagination-btn"
            >
              ➡️
            </button>
            <button
              onClick={() => cambiarPagina(totalPages)}
              disabled={currentPage === totalPages}
              className="pagination-btn"
            >
              ⏭️
            </button>
          </div>
        </div>
      )}

      {/* Modal ORIGINAL para ver detalles */}
      {showModal && selectedMic && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📋 Detalles del MIC #{selectedMic.id}</h2>
              <button onClick={() => setShowModal(false)} className="modal-close">
                ✕
              </button>
            </div>

            <div className="modal-body">
              <MICDetalles mic={selectedMic} onEstadoCambiado={() => cargarMics(currentPage, filters)} />
            </div>

            <div className="modal-footer">
              <button
                onClick={() =>
                  descargarPDF(selectedMic.id, selectedMic.campo_23_numero_campo2_crt)
                }
                className="btn-primary"
              >
                📄 Descargar PDF
              </button>
              <button onClick={() => setShowModal(false)} className="btn-secondary">
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE EDICIÓN */}
      <ModalMICCompleto
        isOpen={modalEdicion.isOpen}
        onClose={cerrarModalEdicion}
        crt={modalEdicion.mic}
        accion="editar"
        onGenerate={guardarCambiosMIC}
        loading={loadingAction === modalEdicion.mic?.id}
        modoEdicion={true}
        datosIniciales={modalEdicion.mic}
      />
    </div>
  );
}

// ✅ COMPONENTE MICDetalles ACTUALIZADO CON GESTIÓN DE ESTADO
function MICDetalles({ mic, onEstadoCambiado }) {
  const campos = [
    { key: "campo_23_numero_campo2_crt", label: "Nº Carta de Porte", importante: true },
    { key: "campo_4_estado", label: "Estado", importante: true },
    { key: "campo_6_fecha", label: "Fecha de Emisión", importante: true },
    { key: "campo_1_transporte", label: "Transportadora", multilinea: true },
    { key: "campo_2_numero", label: "Rol Contribuyente" },
    { key: "campo_7_pto_seguro", label: "Puerto Seguro" },
    { key: "campo_8_destino", label: "Destino" },
    { key: "campo_10_numero", label: "Rol Contribuyente (10)" },
    { key: "campo_11_placa", label: "Placa Camión" },
    { key: "campo_12_modelo_chasis", label: "Modelo/Chasis" },
    { key: "campo_14_anio", label: "Año" },
    { key: "campo_15_placa_semi", label: "Placa Semi" },
    { key: "campo_24_aduana", label: "Aduana" },
    { key: "campo_25_moneda", label: "Moneda" },
    { key: "campo_26_pais", label: "País Origen" },
    { key: "campo_27_valor_campo16", label: "Valor FOT" },
    { key: "campo_28_total", label: "Flete Total" },
    { key: "campo_29_seguro", label: "Seguro" },
    { key: "campo_30_tipo_bultos", label: "Tipo Bultos" },
    { key: "campo_31_cantidad", label: "Cantidad" },
    { key: "campo_32_peso_bruto", label: "Peso Bruto" },
    { key: "campo_33_datos_campo1_crt", label: "Remitente", multilinea: true },
    { key: "campo_34_datos_campo4_crt", label: "Destinatario", multilinea: true },
    { key: "campo_35_datos_campo6_crt", label: "Consignatario", multilinea: true },
    { key: "campo_36_factura_despacho", label: "Documentos Anexos" },
    { key: "campo_37_valor_manual", label: "Valor Manual" },
    { key: "campo_38_datos_campo11_crt", label: "Detalles Mercadería", multilinea: true },
    { key: "campo_40_tramo", label: "Tramo" },
  ];

  return (
    <div className="mic-detalles">
      {/* ✅ GESTOR DE ESTADO PROFESIONAL EN EL MODAL */}
      <div className="mb-6">
        <GestorEstadoMIC 
          mic={mic} 
          onEstadoCambiado={onEstadoCambiado}
          compact={false}
        />
      </div>

      <div className="detalles-grid">
        {campos.map(({ key, label, importante, multilinea }) => {
          const valor = mic[key];
          
          // No mostrar el estado aquí ya que está en el gestor
          if (key === "campo_4_estado") return null;
          
          if (!valor) return null;
          
          return (
            <div
              key={key}
              className={`detalle-item ${importante ? "importante" : ""} ${
                multilinea ? "multilinea" : ""
              }`}
            >
              <label className="detalle-label">{label}:</label>
              <div className="detalle-valor">
                {multilinea ? (
                  <pre className="valor-multilinea">{valor}</pre>
                ) : (
                  <span>{valor}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="detalles-meta">
        <p>
          <strong>Creado:</strong> {mic.creado_en}
        </p>
        {mic.crt_numero && (
          <p>
            <strong>CRT Origen:</strong> {mic.crt_numero}
          </p>
        )}
      </div>
    </div>
  );
}