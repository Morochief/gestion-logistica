import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import Modal from "./Modal";
import MIC from "./MIC";
import ModalMICCompleto from "./ModalMICCompleto";

function ListarCRT() {
  // ========== ESTADOS EXISTENTES (MANTENIDOS) ==========
  const [crts, setCrts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingPDF, setLoadingPDF] = useState(null);
  const [loadingMIC, setLoadingMIC] = useState(null);
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [micCrtId, setMicCrtId] = useState(null);
  const navigate = useNavigate();

  // ========== NUEVOS ESTADOS PARA MEJORAS ==========
  const [usarPaginadoBackend, setUsarPaginadoBackend] = useState(false);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [filtrosAvanzados, setFiltrosAvanzados] = useState({
    estado: "",
    transportadora_id: "",
    fecha_desde: "",
    fecha_hasta: "",
  });
  const [mostrarFiltrosAvanzados, setMostrarFiltrosAvanzados] = useState(false);
  const [estados, setEstados] = useState([]);
  const [transportadoras, setTransportadoras] = useState([]);
  const [crtEditando, setCrtEditando] = useState(null);
  const [modalEditar, setModalEditar] = useState(false);
  const [modalMIC, setModalMIC] = useState({
    isOpen: false,
    crt: null,
  });

  // ========== NUEVOS ESTADOS PARA ENTIDADES Y CAMPO 15 ==========
  const [entidades, setEntidades] = useState([]);
  const [monedas, setMonedas] = useState([]);
  const [campo15Items, setCampo15Items] = useState([]);

  const itemsPerPage = 10;

  // ========== FUNCIONES AUXILIARES PARA FORMATEO NUMÉRICO ==========

  // Función para formatear entrada de números con comas decimales
  const formatearEntradaNumerica = (valor) => {
    if (!valor) return "";
    // Reemplazar punto por coma para mostrar al usuario
    return valor.toString().replace(".", ",");
  };

  // Función para parsear entrada del usuario a número válido
  const parsearEntradaNumerica = (valor) => {
    if (!valor) return "";
    // Reemplazar coma por punto para procesamiento
    const valorLimpio = valor.toString().replace(",", ".");
    const numero = parseFloat(valorLimpio);
    return isNaN(numero) ? "" : numero;
  };

  // Función mejorada para manejar entrada numérica con comas decimales naturales
  const manejarEntradaNumerica = (e, callback) => {
    let valor = e.target.value;
    
    // Permitir números, una sola coma decimal, y signos negativos al inicio
    const regex = /^-?[\d]*[,]?[\d]*$/;
    if (!regex.test(valor)) {
      return; // No actualizar si no es válido
    }

    // Asegurar que solo haya una coma decimal
    const partesDecimales = valor.split(',').length - 1;
    if (partesDecimales > 1) {
      return; // No permitir más de una coma
    }

    // Limitar decimales a 2 dígitos después de la coma
    if (valor.includes(',')) {
      const partes = valor.split(',');
      if (partes[1] && partes[1].length > 2) {
        valor = partes[0] + ',' + partes[1].substring(0, 2);
      }
    }

    callback(valor);
  };

  // Nueva función para entrada completamente natural de comas
  const manejarEntradaNaturalComa = (e, callback) => {
    let valor = e.target.value;
    
    // Permitir solo números, una coma, y signo negativo al inicio
    // Regex más permisivo que permite escribir comas en cualquier momento
    const caracteresPermitidos = /^-?[\d,]*$/;
    if (!caracteresPermitidos.test(valor)) {
      e.preventDefault();
      return;
    }

    // Contar comas - no permitir más de una
    const comas = (valor.match(/,/g) || []).length;
    if (comas > 1) {
      e.preventDefault();
      return;
    }

    // Si hay coma, limitar decimales a 2
    if (valor.includes(',')) {
      const partes = valor.split(',');
      if (partes[1] && partes[1].length > 2) {
        valor = partes[0] + ',' + partes[1].substring(0, 2);
      }
    }

    // Permitir la actualización inmediata
    callback(valor);
  };

  // ========== NUEVA FUNCIÓN PARA AUTOCOMPLETAR VALOR FLETE EXTERNO ==========
const autocompletarValorFleteExterno = (campo15Items) => {
  if (campo15Items.length === 0) return '';
  
  const primerItem = campo15Items[0];
  if (!primerItem) return '';
  
  // Priorizar valor del remitente, si no existe usar valor del destinatario
  const valor = primerItem.valor_remitente || primerItem.valor_destinatario || '';
  
  return parsearEntradaNumerica(valor);
};

  // ========== FUNCIONES EXISTENTES (MANTENIDAS) ==========
  useEffect(() => {
    const inicializar = async () => {
      await cargarDatosIniciales();
      cargarCRTs();
    };
    inicializar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // NUEVO useEffect para autocompletar valor flete externo
  useEffect(() => {
    if (campo15Items.length > 0 && modalEditar) {
      const primerValor = autocompletarValorFleteExterno(campo15Items);
      if (primerValor) {
        const campoFleteExterno = document.querySelector('input[name="valor_flete_externo"]');
        if (campoFleteExterno && !campoFleteExterno.value) {
          campoFleteExterno.value = formatearEntradaNumerica(primerValor);
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campo15Items, modalEditar]);

  // CARGAR DATOS AUXILIARES MEJORADO
  const cargarDatosIniciales = async () => {
    try {
      // Cargar estados
      const responseEstados = await axios.get(
        "http://localhost:5000/api/crts/estados"
      );
      setEstados(responseEstados.data.estados || []);

      // USAR NUEVOS ENDPOINTS
      const responseTransportadoras = await axios.get(
        "http://localhost:5000/api/crts/data/transportadoras"
      );
      setTransportadoras(responseTransportadoras.data.items || []);

      const responseEntidades = await axios.get(
        "http://localhost:5000/api/crts/data/entidades"
      );
      setEntidades(responseEntidades.data.items || []);

      const responseMonedas = await axios.get(
        "http://localhost:5000/api/crts/data/monedas"
      );
      setMonedas(responseMonedas.data.items || []);

      console.log("✅ Datos auxiliares cargados:", {
        estados: responseEstados.data.estados?.length || 0,
        transportadoras: responseTransportadoras.data.items?.length || 0,
        entidades: responseEntidades.data.items?.length || 0,
        monedas: responseMonedas.data.items?.length || 0,
      });
    } catch (error) {
      console.log("⚠️ Error cargando datos auxiliares:", error.message);
      toast.warn("Algunos datos auxiliares no se pudieron cargar");
    }
  };

  const cargarCRTs = () => {
    setLoading(true);

    // Si hay filtros avanzados activos, usar el endpoint mejorado
    if (
      usarPaginadoBackend ||
      Object.values(filtrosAvanzados).some((v) => v !== "")
    ) {
      cargarCRTsPaginado();
    } else {
      // Usar tu lógica original
      axios
        .get("http://localhost:5000/api/crts")
        .then((res) => {
          setCrts(res.data);
          setFiltered(res.data);
          setTotalItems(res.data.length);
          setTotalPages(Math.ceil(res.data.length / itemsPerPage));
          toast.success("✅ CRTs cargados");
        })
        .catch(() => {
          toast.error("❌ Error al cargar CRTs");
        })
        .finally(() => setLoading(false));
    }
  };

  // Nueva función para usar el endpoint mejorado
  const cargarCRTsPaginado = async () => {
    try {
      const params = new URLSearchParams({
        page: currentPage,
        per_page: itemsPerPage,
        q: query,
        ...Object.fromEntries(
          Object.entries(filtrosAvanzados).filter(([_, value]) => value !== "")
        ),
      });

      const response = await axios.get(
        `http://localhost:5000/api/crts/paginated?${params}`
      );
      const data = response.data;

      setCrts(data.crts || []);
      setFiltered(data.crts || []);
      setTotalItems(data.pagination.total);
      setTotalPages(data.pagination.pages);
      setCurrentPage(data.pagination.page);

      toast.success("✅ CRTs cargados con filtros avanzados");
    } catch (error) {
      console.log("Error con endpoint avanzado, usando básico");
      // Fallback a tu método original
      setUsarPaginadoBackend(false);
      cargarCRTs();
    }
  };

  // Tu búsqueda filtrada original (MANTENIDA)
  useEffect(() => {
    if (!usarPaginadoBackend) {
      const lower = query.toLowerCase();
      setFiltered(
        crts.filter(
          (c) =>
            (c.numero_crt || "").toLowerCase().includes(lower) ||
            (c.estado || "").toLowerCase().includes(lower) ||
            (c.transportadora || "").toLowerCase().includes(lower) ||
            (c.remitente || "").toLowerCase().includes(lower) ||
            (c.destinatario || "").toLowerCase().includes(lower) ||
            (c.factura_exportacion || "").toLowerCase().includes(lower)
        )
      );
      setCurrentPage(1);
    }
  }, [query, crts, usarPaginadoBackend]);

  // Recalcular paginación cuando no se usa backend
  useEffect(() => {
    if (!usarPaginadoBackend) {
      setTotalItems(filtered.length);
      setTotalPages(Math.ceil(filtered.length / itemsPerPage));
    }
  }, [filtered, usarPaginadoBackend]);

  // Tu función de imprimir PDF (MANTENIDA EXACTA)
  const imprimirPDF = async (crt_id) => {
    setLoadingPDF(crt_id);
    try {
      const res = await fetch(`http://localhost:5000/api/crts/${crt_id}/pdf`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      window.open(URL.createObjectURL(blob), "_blank");
      toast.success("📄 PDF CRT generado");
    } catch (err) {
      toast.error("❌ Error generando PDF CRT");
    } finally {
      setLoadingPDF(null);
    }
  };

  // Tu función de eliminar (MANTENIDA EXACTA)
  const eliminarCRT = async (crt_id) => {
    if (!window.confirm("¿Eliminar este CRT?")) return;
    try {
      await axios.delete(`http://localhost:5000/api/crts/${crt_id}`);
      toast.success("✅ CRT eliminado");
      cargarCRTs();
    } catch (err) {
      toast.error("❌ Error al eliminar");
    }
  };

  // FUNCIÓN emitirMIC CORREGIDA - SOLO ABRE MODAL
  const emitirMIC = async (crt) => {
    if (!crt.numero_crt) {
      toast.warn("Primero debes emitir el CRT antes de generar el MIC.");
      return;
    }

    console.log(`🚀 Abriendo modal MIC para CRT ${crt.id} - ${crt.numero_crt}`);

    // ABRIR MODAL PARA COMPLETAR DATOS
    setModalMIC({
      isOpen: true,
      crt: crt,
    });
  };

  // NUEVA FUNCIÓN PARA GENERAR PDF CON DATOS COMPLETOS
  const generarPDFMIC = async (datosModal) => {
    const crt = modalMIC.crt;
    if (!crt) return;

    console.log(
      `🎯 Generando PDF MIC con datos completados para CRT ${crt.numero_crt}`
    );
    setLoadingMIC(crt.id);

    try {
      const response = await axios.post(
        `http://localhost:5000/api/mic/generate_pdf_from_crt/${crt.id}`,
        datosModal,
        {
          responseType: "blob",
          timeout: 30000,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank");

      setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 1000);

      toast.success(`✅ PDF MIC completo generado para CRT ${crt.numero_crt}`);
      setModalMIC({ isOpen: false, crt: null });
    } catch (error) {
      console.error("❌ Error generando MIC:", error);
      toast.error(
        `❌ Error al generar MIC: ${error.message || "Error desconocido"}`
      );
    } finally {
      setLoadingMIC(null);
    }
  };

  // FUNCIÓN PARA CERRAR MODAL
  const cerrarModalMIC = () => {
    setModalMIC({ isOpen: false, crt: null });
  };

  // ========== NUEVAS FUNCIONES PARA MEJORAS ==========
  const aplicarFiltrosAvanzados = () => {
    setUsarPaginadoBackend(true);
    setCurrentPage(1);
    cargarCRTsPaginado();
  };

  const limpiarFiltros = () => {
    setQuery("");
    setFiltrosAvanzados({
      estado: "",
      transportadora_id: "",
      fecha_desde: "",
      fecha_hasta: "",
    });
    setUsarPaginadoBackend(false);
    setCurrentPage(1);
    cargarCRTs();
  };

  const duplicarCRT = async (crtId) => {
    try {
      const response = await axios.post(
        `http://localhost:5000/api/crts/${crtId}/duplicate`
      );
      toast.success(`✅ CRT duplicado: ${response.data.nuevo_numero}`);
      cargarCRTs();
    } catch (error) {
      toast.error(
        "❌ Error duplicando CRT: " +
          (error.response?.data?.error || error.message)
      );
    }
  };

  // MEJORADA: Cargar CRT para editar con campo 15
  const editarCRT = async (crtId) => {
    try {
      console.log(`🔄 Cargando CRT ${crtId} para editar...`);

      const response = await axios.get(
        `http://localhost:5000/api/crts/${crtId}`
      );
      const crtData = response.data;
      setCrtEditando(crtData);

      // CARGAR CAMPO 15 MEJORADO
      try {
        const campo15Response = await axios.get(
          `http://localhost:5000/api/crts/${crtId}/campo15`
        );
        const items = campo15Response.data.items || [];
        console.log(`✅ Campo 15 cargado: ${items.length} items`);
        setCampo15Items(items);
      } catch (error) {
        console.log(
          "⚠️ Error cargando campo 15, iniciando vacío:",
          error.message
        );
        setCampo15Items([]);
      }

      setModalEditar(true);
    } catch (error) {
      console.error("❌ Error obteniendo CRT para editar:", error);
      toast.error("❌ Error obteniendo CRT para editar");
    }
  };

  // NUEVA: Funciones para manejar campo 15 (estructura real)
  const agregarCampo15Item = () => {
    const nuevosItems = [
      ...campo15Items,
      {
        id: null, // Nuevo item
        descripcion_gasto: "",
        valor_remitente: "",
        moneda_remitente: "USD",
        valor_destinatario: "",
        moneda_destinatario: "USD",
      },
    ];
    
    setCampo15Items(nuevosItems);
    
    // Si es el primer item, mostrar ayuda
    if (nuevosItems.length === 1) {
      toast.info("💡 El primer tramo se autocopiará a 'Valor Flete Externo'", {
        autoClose: 4000,
      });
    }
  };

  const eliminarCampo15Item = (index) => {
    setCampo15Items(campo15Items.filter((_, i) => i !== index));
  };

  const actualizarCampo15Item = (index, campo, valor) => {
    const nuevosItems = [...campo15Items];
    
    // Si es un campo numérico, procesar correctamente
    if (campo === 'valor_remitente' || campo === 'valor_destinatario') {
      const valorProcesado = parsearEntradaNumerica(valor);
      nuevosItems[index] = { ...nuevosItems[index], [campo]: valorProcesado };
      
      // AUTOCOMPLETAR VALOR FLETE EXTERNO si es el primer item (índice 0)
      if (index === 0 && valorProcesado) {
        // Buscar el campo valor_flete_externo en el formulario y actualizarlo
        const campoFleteExterno = document.querySelector('input[name="valor_flete_externo"]');
        if (campoFleteExterno) {
          campoFleteExterno.value = formatearEntradaNumerica(valorProcesado);
          
          // Disparar evento para notificar el cambio
          const evento = new Event('input', { bubbles: true });
          campoFleteExterno.dispatchEvent(evento);
        }
      }
    } else {
      nuevosItems[index] = { ...nuevosItems[index], [campo]: valor };
    }
    
    setCampo15Items(nuevosItems);
  };

  // NUEVA: Calcular totales del campo 15
  const calcularTotales = () => {
    const totalRemitente = campo15Items.reduce((total, item) => {
      const valor = parseFloat(item.valor_remitente) || 0;
      return total + valor;
    }, 0);

    const totalDestinatario = campo15Items.reduce((total, item) => {
      const valor = parseFloat(item.valor_destinatario) || 0;
      return total + valor;
    }, 0);

    return { totalRemitente, totalDestinatario };
  };

  // NUEVA: Función para buscar entidad por ID y retornar nombre
  const buscarEntidadPorId = (id) => {
    const entidad = entidades.find((e) => e.id === parseInt(id));
    return entidad ? entidad.nombre : "";
  };

  // NUEVA: Función para buscar transportadora por ID
  const buscarTransportadoraPorId = (id) => {
    const transportadora = transportadoras.find((t) => t.id === parseInt(id));
    return transportadora ? transportadora.nombre : "";
  };

  // NUEVA: Función para buscar moneda por ID
  const buscarMonedaPorId = (id) => {
    const moneda = monedas.find((m) => m.id === parseInt(id));
    return moneda ? `${moneda.codigo} - ${moneda.nombre}` : "";
  };

  // MEJORADA: Guardar cambios con campo 15 y formateo numérico correcto
  const guardarCambios = async (e) => {
    e.preventDefault();
    if (!crtEditando) return;

    try {
      console.log("🔄 Guardando cambios del CRT...");

      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());

      // PROCESAR CAMPOS NUMÉRICOS CON FORMATO CORRECTO
      const camposNumericos = [
        "peso_bruto",
        "peso_neto",
        "volumen",
        "valor_incoterm",
        "valor_mercaderia",
        "declaracion_mercaderia",
        "valor_flete_externo",
        "valor_reembolso",
      ];

      camposNumericos.forEach((campo) => {
        if (data[campo]) {
          data[campo] = parsearEntradaNumerica(data[campo]);
        }
      });

      // INCLUIR CAMPO 15 EN LOS DATOS
      data.campo15_items = JSON.stringify(campo15Items);

      console.log("📊 Datos a enviar:", {
        ...data,
        campo15_items_count: campo15Items.length,
      });

      await axios.put(`http://localhost:5000/api/crts/${crtEditando.id}`, data);

      toast.success("✅ CRT actualizado exitosamente");
      setModalEditar(false);
      setCrtEditando(null);
      setCampo15Items([]);
      cargarCRTs();
    } catch (error) {
      console.error("❌ Error guardando cambios:", error);

      if (
        error.response?.status === 409 &&
        error.response?.data?.requiere_confirmacion
      ) {
        if (
          window.confirm(
            `${error.response.data.error}\n\n¿Desea continuar con la edición?`
          )
        ) {
          try {
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());

            // Procesar campos numéricos nuevamente
            const camposNumericos = [
              "peso_bruto",
              "peso_neto",
              "volumen",
              "valor_incoterm",
              "valor_mercaderia",
              "declaracion_mercaderia",
              "valor_flete_externo",
              "valor_reembolso",
            ];

            camposNumericos.forEach((campo) => {
              if (data[campo]) {
                data[campo] = parsearEntradaNumerica(data[campo]);
              }
            });

            data.permitir_edicion_en_transito = true;
            data.campo15_items = JSON.stringify(campo15Items);

            await axios.put(
              `http://localhost:5000/api/crts/${crtEditando.id}`,
              data
            );
            toast.success("✅ CRT actualizado exitosamente");
            setModalEditar(false);
            setCrtEditando(null);
            setCampo15Items([]);
            cargarCRTs();
          } catch (retryError) {
            toast.error("❌ Error actualizando CRT");
          }
        }
      } else {
        toast.error(
          "❌ Error actualizando CRT: " +
            (error.response?.data?.error || error.message)
        );
      }
    }
  };

  // Calcular items actuales
  const currentItems = usarPaginadoBackend
    ? filtered
    : filtered.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
      );

  return (
    <div className="p-4 relative">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">
          Listado CRTs
          <span className="text-sm font-normal text-gray-500 ml-2">
            ({totalItems} registros)
          </span>
        </h2>

        {/* Toggle para filtros avanzados */}
        <button
          onClick={() => setMostrarFiltrosAvanzados(!mostrarFiltrosAvanzados)}
          className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
        >
          {mostrarFiltrosAvanzados
            ? "🔼 Ocultar filtros"
            : "🔽 Filtros avanzados"}
        </button>
      </div>

      {/* Búsqueda principal */}
      <input
        type="text"
        placeholder="🔍 Buscar..."
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          if (usarPaginadoBackend) {
            // Si estamos usando backend, aplicar filtros automáticamente
            setTimeout(() => aplicarFiltrosAvanzados(), 500);
          }
        }}
        className="mb-4 p-2 border rounded w-full text-sm"
      />

      {/* Filtros avanzados */}
      {mostrarFiltrosAvanzados && (
        <div className="bg-gray-50 p-4 rounded mb-4 border">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Estado</label>
              <select
                value={filtrosAvanzados.estado}
                onChange={(e) =>
                  setFiltrosAvanzados((prev) => ({
                    ...prev,
                    estado: e.target.value,
                  }))
                }
                className="w-full p-2 border rounded text-sm"
              >
                <option value="">Todos los estados</option>
                {estados.map((estado) => (
                  <option key={estado} value={estado}>
                    {estado.replace("_", " ")}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Transportadora
              </label>
              <select
                value={filtrosAvanzados.transportadora_id}
                onChange={(e) =>
                  setFiltrosAvanzados((prev) => ({
                    ...prev,
                    transportadora_id: e.target.value,
                  }))
                }
                className="w-full p-2 border rounded text-sm"
              >
                <option value="">Todas las transportadoras</option>
                {transportadoras.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Fecha desde
              </label>
              <input
                type="date"
                value={filtrosAvanzados.fecha_desde}
                onChange={(e) =>
                  setFiltrosAvanzados((prev) => ({
                    ...prev,
                    fecha_desde: e.target.value,
                  }))
                }
                className="w-full p-2 border rounded text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Fecha hasta
              </label>
              <input
                type="date"
                value={filtrosAvanzados.fecha_hasta}
                onChange={(e) =>
                  setFiltrosAvanzados((prev) => ({
                    ...prev,
                    fecha_hasta: e.target.value,
                  }))
                }
                className="w-full p-2 border rounded text-sm"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={aplicarFiltrosAvanzados}
              className="bg-blue-500 text-white px-4 py-2 rounded text-sm hover:bg-blue-600"
            >
              🔍 Aplicar filtros
            </button>
            <button
              onClick={limpiarFiltros}
              className="bg-gray-500 text-white px-4 py-2 rounded text-sm hover:bg-gray-600"
            >
              🗑️ Limpiar
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-10">
          <div className="border-t-4 border-blue-600 rounded-full w-12 h-12 animate-spin"></div>
        </div>
      ) : (
        <>
          {/* TABLA PRINCIPAL */}
          <table className="min-w-full border text-xs">
            <thead className="bg-sky-100">
              <tr>
                <th className="border px-2 py-1">Número</th>
                <th className="border px-2 py-1">Estado</th>
                <th className="border px-2 py-1">Transportadora</th>
                <th className="border px-2 py-1">Remitente</th>
                <th className="border px-2 py-1">Destinatario</th>
                <th className="border px-2 py-1">Factura</th>
                <th className="border px-2 py-1">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {currentItems.map((crt, idx) => (
                <tr key={crt.id || idx} className="hover:bg-slate-50">
                  <td
                    className="border px-2 py-1 cursor-pointer"
                    onClick={() => navigate(`/crt/${crt.id}`)}
                  >
                    {crt.numero_crt}
                  </td>
                  <td className="border px-2 py-1">
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        crt.estado === "EMITIDO"
                          ? "bg-green-100 text-green-800"
                          : crt.estado === "BORRADOR"
                          ? "bg-yellow-100 text-yellow-800"
                          : crt.estado === "EN_TRANSITO"
                          ? "bg-blue-100 text-blue-800"
                          : crt.estado === "ENTREGADO"
                          ? "bg-purple-100 text-purple-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {crt.estado}
                    </span>
                  </td>
                  <td className="border px-2 py-1">{crt.transportadora}</td>
                  <td className="border px-2 py-1">{crt.remitente}</td>
                  <td className="border px-2 py-1">{crt.destinatario}</td>
                  <td className="border px-2 py-1">
                    {crt.factura_exportacion}
                  </td>
                  <td className="border px-2 py-1 flex space-x-1 flex-wrap">
                    <button
                      onClick={() => eliminarCRT(crt.id)}
                      className="bg-red-600 hover:bg-red-700 px-2 rounded text-white text-xs"
                      title="Eliminar CRT"
                    >
                      🗑
                    </button>

                    <button
                      onClick={() => imprimirPDF(crt.id)}
                      disabled={loadingPDF === crt.id}
                      className={`px-2 rounded text-white text-xs ${
                        loadingPDF === crt.id
                          ? "bg-gray-400 cursor-not-allowed"
                          : "bg-blue-600 hover:bg-blue-700"
                      }`}
                      title="Descargar PDF CRT"
                    >
                      {loadingPDF === crt.id ? "..." : "📄"}
                    </button>

                    {crt.estado === "EMITIDO" && (
                      <button
                        onClick={() => emitirMIC(crt)}
                        disabled={loadingMIC === crt.id}
                        className={`text-white px-2 rounded text-xs ${
                          loadingMIC === crt.id
                            ? "bg-gray-400 cursor-not-allowed"
                            : "bg-purple-600 hover:bg-purple-700"
                        }`}
                        title="Completar y generar PDF MIC"
                      >
                        {loadingMIC === crt.id ? "..." : "📋"}
                      </button>
                    )}

                    <button
                      onClick={() => editarCRT(crt.id)}
                      className="bg-orange-500 hover:bg-orange-600 text-white px-2 rounded text-xs"
                      title="Editar rápido"
                    >
                      ✏️
                    </button>

                    <button
                      onClick={() => duplicarCRT(crt.id)}
                      className="bg-green-500 hover:bg-green-600 text-white px-2 rounded text-xs"
                      title="Duplicar CRT"
                    >
                      📋
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* PAGINACIÓN */}
          <div className="flex justify-between mt-4 text-xs">
            <span>
              Mostrando{" "}
              {totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1}-
              {Math.min(currentPage * itemsPerPage, totalItems)} de {totalItems}
              {usarPaginadoBackend && (
                <span className="text-blue-600 ml-2">
                  (con filtros avanzados)
                </span>
              )}
            </span>
            <div>
              <button
                onClick={() => {
                  const newPage = Math.max(1, currentPage - 1);
                  setCurrentPage(newPage);
                  if (usarPaginadoBackend) {
                    cargarCRTsPaginado();
                  }
                }}
                disabled={currentPage === 1}
                className="px-2 py-1 border rounded mr-2 disabled:opacity-50"
              >
                ⬅ Prev
              </button>
              <span className="px-2 py-1">
                {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => {
                  const newPage = Math.min(totalPages, currentPage + 1);
                  setCurrentPage(newPage);
                  if (usarPaginadoBackend) {
                    cargarCRTsPaginado();
                  }
                }}
                disabled={currentPage === totalPages}
                className="px-2 py-1 border rounded disabled:opacity-50"
              >
                Next ➡
              </button>
            </div>
          </div>

          {/* MODAL MIC ORIGINAL */}
          <Modal open={!!micCrtId} onClose={() => setMicCrtId(null)}>
            <MIC crtId={micCrtId} onClose={() => setMicCrtId(null)} />
          </Modal>

          {/* NUEVO MODAL MIC COMPLETO */}
          <ModalMICCompleto
            isOpen={modalMIC.isOpen}
            onClose={cerrarModalMIC}
            crt={modalMIC.crt}
            onGenerate={generarPDFMIC}
            loading={loadingMIC === modalMIC.crt?.id}
          />

          {/* MODAL PARA EDICIÓN RÁPIDA CON FORMATEO NUMÉRICO MEJORADO */}
          {modalEditar && crtEditando && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 w-full max-w-6xl mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold">
                    ✏️ Editar CRT {crtEditando.numero_crt}
                  </h3>
                  <button
                    onClick={() => setModalEditar(false)}
                    className="text-gray-500 hover:text-gray-700 text-xl font-bold"
                  >
                    ×
                  </button>
                </div>

                <form onSubmit={guardarCambios}>
                  {/* INFORMACIÓN BÁSICA */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      📋 Información Básica
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Número CRT *
                        </label>
                        <input
                          type="text"
                          name="numero_crt"
                          defaultValue={crtEditando.numero_crt || ""}
                          className="w-full p-2 border rounded text-sm"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Estado *
                        </label>
                        <select
                          name="estado"
                          defaultValue={crtEditando.estado}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="BORRADOR">Borrador</option>
                          <option value="EMITIDO">Emitido</option>
                          <option value="EN_TRANSITO">En Tránsito</option>
                          <option value="ENTREGADO">Entregado</option>
                          <option value="FINALIZADO">Finalizado</option>
                          <option value="CANCELADO">Cancelado</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Fecha de Emisión
                        </label>
                        <input
                          type="date"
                          name="fecha_emision"
                          defaultValue={crtEditando.fecha_emision || ""}
                          className="w-full p-2 border rounded text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* ENTIDADES MEJORADO */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      👥 Entidades
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Remitente
                        </label>
                        <select
                          name="remitente_id"
                          defaultValue={crtEditando.remitente_id || ""}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="">Seleccionar remitente</option>
                          {entidades.map((entidad) => (
                            <option key={entidad.id} value={entidad.id}>
                              {entidad.nombre}
                            </option>
                          ))}
                        </select>
                        {crtEditando.remitente_id && (
                          <small className="text-gray-500">
                            Actual:{" "}
                            {buscarEntidadPorId(crtEditando.remitente_id) ||
                              crtEditando.remitente ||
                              "No encontrado"}
                          </small>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Destinatario
                        </label>
                        <select
                          name="destinatario_id"
                          defaultValue={crtEditando.destinatario_id || ""}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="">Seleccionar destinatario</option>
                          {entidades.map((entidad) => (
                            <option key={entidad.id} value={entidad.id}>
                              {entidad.nombre}
                            </option>
                          ))}
                        </select>
                        {crtEditando.destinatario_id && (
                          <small className="text-gray-500">
                            Actual:{" "}
                            {buscarEntidadPorId(crtEditando.destinatario_id) ||
                              crtEditando.destinatario ||
                              "No encontrado"}
                          </small>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Consignatario
                        </label>
                        <select
                          name="consignatario_id"
                          defaultValue={crtEditando.consignatario_id || ""}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="">Seleccionar consignatario</option>
                          {entidades.map((entidad) => (
                            <option key={entidad.id} value={entidad.id}>
                              {entidad.nombre}
                            </option>
                          ))}
                        </select>
                        {crtEditando.consignatario_id && (
                          <small className="text-gray-500">
                            Actual:{" "}
                            {buscarEntidadPorId(crtEditando.consignatario_id) ||
                              crtEditando.consignatario ||
                              "No encontrado"}
                          </small>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Notificar A
                        </label>
                        <select
                          name="notificar_a_id"
                          defaultValue={crtEditando.notificar_a_id || ""}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="">Seleccionar quien notificar</option>
                          {entidades.map((entidad) => (
                            <option key={entidad.id} value={entidad.id}>
                              {entidad.nombre}
                            </option>
                          ))}
                        </select>
                        {crtEditando.notificar_a_id && (
                          <small className="text-gray-500">
                            Actual:{" "}
                            {buscarEntidadPorId(crtEditando.notificar_a_id) ||
                              crtEditando.notificar_a ||
                              "No encontrado"}
                          </small>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Transportadora
                        </label>
                        <select
                          name="transportadora_id"
                          defaultValue={crtEditando.transportadora_id || ""}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="">Seleccionar transportadora</option>
                          {transportadoras.map((t) => (
                            <option key={t.id} value={t.id}>
                              {t.nombre}
                            </option>
                          ))}
                        </select>
                        {crtEditando.transportadora_id && (
                          <small className="text-gray-500">
                            Actual:{" "}
                            {buscarTransportadoraPorId(
                              crtEditando.transportadora_id
                            ) ||
                              crtEditando.transportadora ||
                              "No encontrado"}
                          </small>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Moneda
                        </label>
                        <select
                          name="moneda_id"
                          defaultValue={crtEditando.moneda_id || ""}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="">Seleccionar moneda</option>
                          {monedas.map((m) => (
                            <option key={m.id} value={m.id}>
                              {m.codigo} - {m.nombre}
                            </option>
                          ))}
                        </select>
                        {crtEditando.moneda_id && (
                          <small className="text-gray-500">
                            Actual:{" "}
                            {buscarMonedaPorId(crtEditando.moneda_id) ||
                              crtEditando.moneda ||
                              "No encontrado"}
                          </small>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* UBICACIÓN Y ENTREGA */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      📍 Ubicación y Entrega
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Lugar de Entrega
                        </label>
                        <input
                          type="text"
                          name="lugar_entrega"
                          defaultValue={crtEditando.lugar_entrega || ""}
                          className="w-full p-2 border rounded text-sm"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Fecha de Entrega
                        </label>
                        <input
                          type="date"
                          name="fecha_entrega"
                          defaultValue={crtEditando.fecha_entrega || ""}
                          className="w-full p-2 border rounded text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* MEDIDAS Y PESOS CON FORMATEO NUMÉRICO MEJORADO */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      ⚖️ Medidas y Pesos
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Peso Bruto (kg)
                        </label>
                        <input
                          type="text"
                          name="peso_bruto"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.peso_bruto || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,000"
                        />
                        <small className="text-gray-500">
                          Use coma para decimales (ej: 3904,614)
                        </small>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Peso Neto (kg)
                        </label>
                        <input
                          type="text"
                          name="peso_neto"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.peso_neto || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,000"
                        />
                        <small className="text-gray-500">
                          Use coma para decimales
                        </small>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Volumen (m³)
                        </label>
                        <input
                          type="text"
                          name="volumen"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.volumen || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,000"
                        />
                        <small className="text-gray-500">
                          Use coma para decimales
                        </small>
                      </div>
                    </div>
                  </div>

                  {/* VALORES Y INCOTERMS CON FORMATEO NUMÉRICO */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      💰 Valores y Incoterms
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Incoterm
                        </label>
                        <input
                          type="text"
                          name="incoterm"
                          defaultValue={crtEditando.incoterm || ""}
                          className="w-full p-2 border rounded text-sm"
                          placeholder="EXW, FOB, CIF, etc."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Valor Incoterm
                        </label>
                        <input
                          type="text"
                          name="valor_incoterm"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.valor_incoterm || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,00"
                        />
                        <small className="text-gray-500">
                          Use coma para decimales (ej: 1250,50)
                        </small>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Valor Mercadería
                        </label>
                        <input
                          type="text"
                          name="valor_mercaderia"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.valor_mercaderia || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,00"
                        />
                        <small className="text-gray-500">
                          Use coma para decimales
                        </small>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Declaración Mercadería
                        </label>
                        <input
                          type="text"
                          name="declaracion_mercaderia"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.declaracion_mercaderia || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,00"
                        />
                        <small className="text-gray-500">
                          Use coma para decimales
                        </small>
                      </div>
                    </div>
                  </div>

                  {/* DOCUMENTOS Y NÚMEROS */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      📄 Documentos y Números
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Factura Exportación
                        </label>
                        <input
                          type="text"
                          name="factura_exportacion"
                          defaultValue={crtEditando.factura_exportacion || ""}
                          className="w-full p-2 border rounded text-sm"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Nro. Despacho
                        </label>
                        <input
                          type="text"
                          name="nro_despacho"
                          defaultValue={crtEditando.nro_despacho || ""}
                          className="w-full p-2 border rounded text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* VALORES ADICIONALES CON FORMATEO NUMÉRICO */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      💵 Valores Adicionales
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Valor Flete Externo
                          <span className="text-orange-600 text-xs ml-2">
                            (Se autocompleta desde Campo 15 - Primer tramo)
                          </span>
                        </label>
                        <input
                          type="text"
                          name="valor_flete_externo"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.valor_flete_externo || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,00"
                        />
                        <small className="text-gray-500">
                          ⚡ Se autocompleta automáticamente con el primer valor del Campo 15
                        </small>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Valor Reembolso
                        </label>
                        <input
                          type="text"
                          name="valor_reembolso"
                          defaultValue={formatearEntradaNumerica(
                            crtEditando.valor_reembolso || ""
                          )}
                          onChange={(e) =>
                            manejarEntradaNaturalComa(e, (valor) => {
                              e.target.value = valor;
                            })
                          }
                          className="w-full p-2 border rounded text-sm"
                          placeholder="0,00"
                        />
                        <small className="text-gray-500">
                          Use coma para decimales
                        </small>
                      </div>
                    </div>
                  </div>

                  {/* CAMPO 15 - COSTOS A PAGAR CON FORMATEO NUMÉRICO PERFECTO */}
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-semibold text-gray-700 border-b pb-2">
                        💰 Campo 15 - Custos a pagar / Gastos a pagar
                      </h4>
                      <button
                        type="button"
                        onClick={agregarCampo15Item}
                        className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                      >
                        ➕ Agregar Gasto
                      </button>
                    </div>

                    {campo15Items.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full border text-sm">
                          <thead className="bg-gray-100">
                            <tr>
                              <th
                                className="border px-2 py-2 text-left"
                                rowSpan="2"
                              >
                                15 - Custos a pagar /<br />
                                Gastos a pagar
                              </th>
                              <th
                                className="border px-2 py-1 text-center"
                                colSpan="2"
                              >
                                Valor Remitente
                                <br />
                                Monto Remitente
                              </th>
                              <th
                                className="border px-2 py-1 text-center"
                                colSpan="2"
                              >
                                Valor Destinatario
                                <br />
                                Monto Destinatario
                              </th>
                              <th
                                className="border px-2 py-1 text-center"
                                rowSpan="2"
                              >
                                Acciones
                              </th>
                            </tr>
                            <tr>
                              <th className="border px-2 py-1 text-center bg-blue-50">
                                Moeda
                              </th>
                              <th className="border px-2 py-1 text-center bg-blue-50">
                                Valor
                              </th>
                              <th className="border px-2 py-1 text-center bg-green-50">
                                Moeda
                              </th>
                              <th className="border px-2 py-1 text-center bg-green-50">
                                Valor
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {campo15Items.map((item, index) => (
                              <tr key={index} className={index === 0 ? "bg-yellow-50" : ""}>
                                <td className="border px-2 py-1">
                                  <textarea
                                    value={item.descripcion_gasto}
                                    onChange={(e) =>
                                      actualizarCampo15Item(
                                        index,
                                        "descripcion_gasto",
                                        e.target.value
                                      )
                                    }
                                    className="w-full p-1 border-0 text-sm resize-none"
                                    rows="2"
                                    placeholder={
                                      index === 0
                                        ? "⭐ PRIMER TRAMO - Este valor se autocopiará a 'Valor Flete Externo'"
                                        : "Ej: Frete / Flete, Belem - Paraguai/Foz do Iguaçu"
                                    }
                                  />
                                  {index === 0 && (
                                    <small className="text-orange-600 font-medium">
                                      ⚡ Primer tramo - Se autocompleta "Valor Flete Externo"
                                    </small>
                                  )}
                                </td>

                                {/* Valor Remitente */}
                                <td className="border px-1 py-1 bg-blue-25">
                                  <select
                                    value={item.moneda_remitente}
                                    onChange={(e) =>
                                      actualizarCampo15Item(
                                        index,
                                        "moneda_remitente",
                                        e.target.value
                                      )
                                    }
                                    className="w-full p-2 border rounded text-sm"
                                  >
                                    {monedas.map((m) => (
                                      <option key={m.id} value={m.codigo}>
                                        {m.codigo}
                                      </option>
                                    ))}
                                  </select>
                                </td>
                                <td className="border px-1 py-1 bg-blue-25">
                                  <input
                                    type="text"
                                    value={formatearEntradaNumerica(
                                      item.valor_remitente
                                    )}
                                    onChange={(e) => {
                                      manejarEntradaNaturalComa(e, (valor) => {
                                        actualizarCampo15Item(index, "valor_remitente", valor);
                                      });
                                    }}
                                    className="w-full p-2 border rounded text-sm text-right"
                                    placeholder="0,00"
                                  />
                                  {index === 0 && (
                                    <small className="text-orange-600 text-xs block mt-1">
                                      → Auto a Flete Ext.
                                    </small>
                                  )}
                                </td>

                                {/* Valor Destinatario */}
                                <td className="border px-1 py-1 bg-green-25">
                                  <select
                                    value={item.moneda_destinatario}
                                    onChange={(e) =>
                                      actualizarCampo15Item(
                                        index,
                                        "moneda_destinatario",
                                        e.target.value
                                      )
                                    }
                                    className="w-full p-2 border rounded text-sm"
                                  >
                                    {monedas.map((m) => (
                                      <option key={m.id} value={m.codigo}>
                                        {m.codigo}
                                      </option>
                                    ))}
                                  </select>
                                </td>
                                <td className="border px-1 py-1 bg-green-25">
                                  <input
                                    type="text"
                                    value={formatearEntradaNumerica(
                                      item.valor_destinatario
                                    )}
                                    onChange={(e) => {
                                      manejarEntradaNaturalComa(e, (valor) => {
                                        actualizarCampo15Item(index, "valor_destinatario", valor);
                                      });
                                    }}
                                    className="w-full p-2 border rounded text-sm text-right"
                                    placeholder="0,00"
                                  />
                                  {index === 0 && (
                                    <small className="text-orange-600 text-xs block mt-1">
                                      → Auto a Flete Ext.
                                    </small>
                                  )}
                                </td>

                                <td className="border px-1 py-1 text-center">
                                  <button
                                    type="button"
                                    onClick={() => eliminarCampo15Item(index)}
                                    className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600"
                                    title="Eliminar gasto"
                                  >
                                    🗑️
                                  </button>
                                </td>
                              </tr>
                            ))}

                            {/* FILA DE TOTALES */}
                            <tr className="bg-yellow-100 font-bold">
                              <td className="border px-2 py-2">
                                <strong>Total / Total</strong>
                              </td>
                              <td className="border px-2 py-1 text-center">
                                USD
                              </td>
                              <td className="border px-2 py-1 text-right">
                                {calcularTotales().totalRemitente.toLocaleString(
                                  "es-ES",
                                  {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                  }
                                )}
                              </td>
                              <td className="border px-2 py-1 text-center">
                                USD
                              </td>
                              <td className="border px-2 py-1 text-right">
                                {calcularTotales().totalDestinatario.toLocaleString(
                                  "es-ES",
                                  {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                  }
                                )}
                              </td>
                              <td className="border px-2 py-1"></td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-4 border-2 border-dashed border-gray-300 rounded">
                        <p>📋 No hay gastos en el Campo 15</p>
                        <p className="text-sm">
                          Haz clic en "➕ Agregar Gasto" para comenzar
                        </p>
                      </div>
                    )}

                    {/* EJEMPLOS DE GASTOS COMUNES */}
                    {campo15Items.length === 0 && (
                      <div className="mt-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                        <p className="text-sm font-medium text-blue-800 mb-2">
                          💡 Ejemplos de gastos comunes:
                        </p>
                        <ul className="text-xs text-blue-700 space-y-1">
                          <li>
                            • <strong>Frete / Flete:</strong> Belem -
                            Paraguai/Foz do Iguaçu
                          </li>
                          <li>
                            • <strong>Foz do Iguaçu/Contagem-MG:</strong>{" "}
                            Transporte nacional
                          </li>
                          <li>
                            • <strong>Seguro:</strong> Seguro de mercadería
                          </li>
                          <li>
                            • <strong>Almacenaje:</strong> Depósito y
                            manipulación
                          </li>
                          <li>
                            • <strong>Aduana:</strong> Tasas y trámites
                            aduaneros
                          </li>
                        </ul>
                      </div>
                    )}

                    {/* NOTA SOBRE FORMATO NUMÉRICO */}
                    <div className="mt-2 p-2 bg-green-50 rounded border border-green-200">
                      <p className="text-xs text-green-700">
                        💡 <strong>Formato numérico:</strong> Use coma para
                        decimales (ej: 500,25). Los totales se calculan
                        automáticamente y se muestran con formato local.
                      </p>
                    </div>
                  </div>

                  {/* CAMPOS DE TEXTO LARGO */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      📝 Descripción y Observaciones
                    </h4>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Detalles de Mercadería
                        </label>
                        <textarea
                          name="detalles_mercaderia"
                          defaultValue={crtEditando.detalles_mercaderia || ""}
                          rows="3"
                          className="w-full p-2 border rounded text-sm"
                          placeholder="Descripción detallada de la mercadería..."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Transporte Sucesivos
                        </label>
                        <textarea
                          name="transporte_sucesivos"
                          defaultValue={crtEditando.transporte_sucesivos || ""}
                          rows="2"
                          className="w-full p-2 border rounded text-sm"
                          placeholder="Información sobre transportes sucesivos..."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Formalidades de Aduana
                        </label>
                        <textarea
                          name="formalidades_aduana"
                          defaultValue={crtEditando.formalidades_aduana || ""}
                          rows="2"
                          className="w-full p-2 border rounded text-sm"
                          placeholder="Instrucciones para formalidades aduaneras..."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Observaciones
                        </label>
                        <textarea
                          name="observaciones"
                          defaultValue={crtEditando.observaciones || ""}
                          rows="3"
                          className="w-full p-2 border rounded text-sm"
                          placeholder="Observaciones adicionales..."
                        />
                      </div>
                    </div>
                  </div>

                  {/* FECHA DE FIRMA */}
                  <div className="mb-6">
                    <h4 className="text-md font-semibold mb-3 text-gray-700 border-b pb-2">
                      ✍️ Fecha de Firma
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Fecha de Firma
                        </label>
                        <input
                          type="date"
                          name="fecha_firma"
                          defaultValue={crtEditando.fecha_firma || ""}
                          className="w-full p-2 border rounded text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* BOTONES DE ACCIÓN */}
                  <div className="flex gap-2 justify-end pt-4 border-t bg-gray-50 -mx-6 px-6 -mb-6 pb-6 rounded-b-lg">
                    <button
                      type="button"
                      onClick={() => setModalEditar(false)}
                      className="px-6 py-2 border border-gray-300 rounded hover:bg-gray-50 text-sm font-medium"
                    >
                      ✖️ Cancelar
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm font-medium"
                    >
                      💾 Guardar Todos los Cambios
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ListarCRT;
