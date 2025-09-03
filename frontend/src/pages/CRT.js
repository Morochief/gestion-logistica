import React, { useEffect, useState, useRef, useCallback } from "react";
import api from "../api/api";
import Select from "react-select";
import { useNavigate, useParams } from "react-router-dom";

function hoyISO() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

function formatoFecha(fecha) {
  if (!fecha) return "";
  const [yyyy, mm, dd] = fecha.split("-");
  return `${dd}-${mm}-${yyyy}`;
}

const INCOTERMS = [
  { value: "EXW", label: "EXW" },
  { value: "FCA", label: "FCA" },
  { value: "FOB", label: "FOB" },
  { value: "CPT", label: "CPT" },
  { value: "CIP", label: "CIP" },
  { value: "DAP", label: "DAP" },
  { value: "DDP", label: "DDP" },
];

function CRT() {
  const { crtId } = useParams(); // Para detectar si venimos con ID de edición
  const [isEditing, setIsEditing] = useState(false);
  const [editingCrtId, setEditingCrtId] = useState(null);
  const [loadingEdit, setLoadingEdit] = useState(false);

  const [remitentes, setRemitentes] = useState([]);
  const [transportadoras, setTransportadoras] = useState([]);
  const [ciudades, setCiudades] = useState([]);
  const [paises, setPaises] = useState([]);
  const [monedas, setMonedas] = useState([]);
  const [ciudad7, setCiudad7] = useState(null);
  const [fecha7, setFecha7] = useState(hoyISO());
  const [monedaGasto, setMonedaGasto] = useState(null);
  const [selectedTransportadora, setSelectedTransportadora] = useState(null);
  const [monedaTouched, setMonedaTouched] = useState(false);
  const [firmaRemitente, setFirmaRemitente] = useState(null);
  const [firmaTransportador, setFirmaTransportador] = useState(null);
  const [firmaDestinatario, setFirmaDestinatario] = useState(null);
  const [showMicModal, setShowMicModal] = useState(false);
  const [crtEmitido, setCrtEmitido] = useState(null);
  const textareaRef = useRef(null);
  const navigate = useNavigate();

  const optCiudadPais = (ciudades, paises) =>
    ciudades.map((c) => {
      const pais = paises.find((p) => p.id === c.pais_id);
      return {
        value: c.id,
        label: `${c.nombre.toUpperCase()} - ${(
          pais?.nombre || ""
        ).toUpperCase()}`,
        ciudad: c.nombre,
        pais: pais?.nombre || "",
        pais_id: c.pais_id,
      };
    });

  const opt = (arr, label = "nombre") =>
    arr.map((x) => ({ ...x, value: x.id, label: x[label] }));

  const getDefaultLugarEmision = (ciudades, paises) => {
    const ciudad = ciudades.find((c) => c.nombre.toUpperCase() === "ASUNCION");
    if (ciudad) {
      const pais = paises.find(
        (p) => p.id === ciudad.pais_id && p.nombre.toUpperCase() === "PARAGUAY"
      );
      if (pais) {
        return {
          value: ciudad.id,
          label: `${ciudad.nombre.toUpperCase()} - ${pais.nombre.toUpperCase()}`,
          ciudad: ciudad.nombre,
          pais: pais.nombre,
          pais_id: pais.id,
        };
      }
    }
    return null;
  };

  const [form, setForm] = useState({
    numero_crt: "",
    fecha_emision: hoyISO(),
    estado: "EMITIDO",
    remitente_id: null,
    destinatario_id: null,
    consignatario_id: null,
    notificar_a_id: null,
    transportadora_id: null,
    ciudad_emision_id: null,
    pais_emision_id: null,
    lugar_entrega: "",
    fecha_entrega: "",
    detalles_mercaderia: "",
    peso_bruto: "",
    peso_neto: "",
    volumen: "",
    incoterm: "",
    moneda_id: null,
    valor_incoterm: "",
    valor_mercaderia: "",
    declaracion_mercaderia: "",
    valor_flete_externo: "",
    valor_reembolso: "",
    factura_exportacion: "",
    nro_despacho: "",
    transporte_sucesivos: "",
    observaciones: "",
    formalidades_aduana: "",
    fecha_firma: "",
    gastos: [],
    local_responsabilidad: "",
  });

  const [gastoActual, setGastoActual] = useState({
    tramo: "",
    valor_remitente: "",
    valor_destinatario: "",
  });

  useEffect(() => {
    if (monedas.length) {
      const exists = monedas.some(
        (m) => m.id === (monedaGasto && monedaGasto.value)
      );
      if (!monedaGasto || !exists) {
        let dolar =
          monedas.find(
            (m) => m.codigo && m.codigo.toUpperCase().includes("USD")
          ) || monedas[0];
        if (dolar)
          setMonedaGasto({
            value: dolar.id,
            label: `${dolar.codigo} - ${dolar.nombre}`,
          });
      }
    }
  }, [monedas, monedaGasto]);

  useEffect(() => {
    api.get("/remitentes/").then((r) => setRemitentes(r.data.items || r.data));
    api
      .get("/transportadoras/")
      .then((r) => setTransportadoras(r.data.items || r.data));
    api.get("/ciudades/").then((r) => setCiudades(r.data));
    api.get("/paises/").then((r) => setPaises(r.data));
    api.get("/monedas/").then((r) => setMonedas(r.data));
  }, []);

  // Función para cargar datos del CRT para editar
  const cargarDatosParaEditar = useCallback(async (id) => {
    setLoadingEdit(true);
    try {
      console.log(`🔄 Cargando CRT ${id} para editar...`);

      // Cargar datos del CRT
      const response = await api.get(`/crts/${id}`);
      const crtData = response.data;

      // Cargar campo 15 si existe
      let campo15Data = [];
      try {
        const campo15Response = await api.get(`/crts/${id}/campo15`);
        campo15Data = campo15Response.data.items || [];
      } catch (error) {
        console.log("⚠️ Campo 15 no disponible:", error.message);
      }

      // Función auxiliar para formatear números
      const formatNumber = (value, decimals = 2) => {
        if (!value || value === "") return "";
        const num = parseFloat(value);
        if (isNaN(num)) return value;
        return num.toFixed(decimals).replace(".", ",");
      };

      // Función auxiliar para formatear pesos (3 decimales)
      const formatWeight = (value) => {
        if (!value || value === "") return "";
        const num = parseFloat(value);
        if (isNaN(num)) return value;
        return num.toFixed(3).replace(".", ",");
      };

      // Función auxiliar para formatear volumen (5 decimales)
      const formatVolume = (value) => {
        if (!value || value === "") return "";
        const num = parseFloat(value);
        if (isNaN(num)) return value;
        return num.toFixed(5).replace(".", ",");
      };

      // Llenar el formulario con los datos del CRT formateados correctamente
      setForm({
        numero_crt: crtData.numero_crt || "",
        fecha_emision: crtData.fecha_emision || hoyISO(),
        estado: crtData.estado || "EMITIDO",
        remitente_id: crtData.remitente_id || null,
        destinatario_id: crtData.destinatario_id || null,
        consignatario_id: crtData.consignatario_id || null,
        notificar_a_id: crtData.notificar_a_id || null,
        transportadora_id: crtData.transportadora_id || null,
        ciudad_emision_id: crtData.ciudad_emision_id || null,
        pais_emision_id: crtData.pais_emision_id || null,
        lugar_entrega: crtData.lugar_entrega || "",
        fecha_entrega: crtData.fecha_entrega || "",
        detalles_mercaderia: crtData.detalles_mercaderia || "",
        peso_bruto: formatWeight(crtData.peso_bruto),
        peso_neto: formatWeight(crtData.peso_neto),
        volumen: formatVolume(crtData.volumen),
        incoterm: crtData.incoterm || "",
        moneda_id: crtData.moneda_id || null,
        valor_incoterm: formatNumber(crtData.valor_incoterm, 2),
        valor_mercaderia: formatNumber(crtData.valor_mercaderia, 2),
        declaracion_mercaderia: formatNumber(crtData.declaracion_mercaderia, 2),
        valor_flete_externo: formatNumber(crtData.valor_flete_externo, 2),
        valor_reembolso: formatNumber(crtData.valor_reembolso, 2),
        factura_exportacion: crtData.factura_exportacion || "",
        nro_despacho: crtData.nro_despacho || "",
        transporte_sucesivos: crtData.transporte_sucesivos || "",
        observaciones: crtData.observaciones || "",
        formalidades_aduana: crtData.formalidades_aduana || "",
        fecha_firma: crtData.fecha_firma || "",
        gastos: campo15Data,
        local_responsabilidad: "",
      });

      // Configurar transportadora seleccionada
      if (crtData.transportadora_id && transportadoras.length > 0) {
        const transportadora = transportadoras.find(t => t.id === crtData.transportadora_id);
        if (transportadora) {
          setSelectedTransportadora({
            value: transportadora.id,
            label: transportadora.nombre,
            codigo: transportadora.codigo
          });
        }
      }

      // Configurar moneda
      if (crtData.moneda_id && monedas.length > 0) {
        const moneda = monedas.find(m => m.id === crtData.moneda_id);
        if (moneda) {
          setMonedaGasto({
            value: moneda.id,
            label: `${moneda.codigo} - ${moneda.nombre}`
          });
        }
      }

      // Configurar firmas si los datos están disponibles
      if (remitentes.length > 0) {
        if (crtData.remitente_id) {
          const remitente = remitentes.find(r => r.id === crtData.remitente_id);
          if (remitente && !firmaRemitente) {
            setFirmaRemitente({ value: remitente.id, label: remitente.nombre });
          }
        }

        if (crtData.destinatario_id) {
          const destinatario = remitentes.find(r => r.id === crtData.destinatario_id);
          if (destinatario && !firmaDestinatario) {
            setFirmaDestinatario({ value: destinatario.id, label: destinatario.nombre });
          }
        }
      }

      if (crtData.transportadora_id && transportadoras.length > 0 && !firmaTransportador) {
        const transportadora = transportadoras.find(t => t.id === crtData.transportadora_id);
        if (transportadora) {
          setFirmaTransportador({ value: transportadora.id, label: transportadora.nombre });
        }
      }

      console.log(`✅ CRT ${id} cargado para editar`);
    } catch (error) {
      console.error("❌ Error cargando CRT para editar:", error);
      alert("Error al cargar los datos del CRT para editar");
      navigate("/listar-crt");
    } finally {
      setLoadingEdit(false);
    }
  }, [transportadoras, monedas, remitentes, navigate]);

  // Detectar si venimos para editar un CRT
  useEffect(() => {
    if (crtId && transportadoras.length > 0 && monedas.length > 0 && remitentes.length > 0) {
      setIsEditing(true);
      setEditingCrtId(crtId);
      cargarDatosParaEditar(crtId);
    }
  }, [crtId, transportadoras, monedas, remitentes, cargarDatosParaEditar]);

  useEffect(() => {
    if (ciudades.length > 0 && paises.length > 0) {
      const def = getDefaultLugarEmision(ciudades, paises);
      if (def) {
        setForm((f) => ({
          ...f,
          ciudad_emision_id: def.value,
          pais_emision_id: def.pais_id,
        }));
      }
    }
  }, [ciudades, paises]);

  useEffect(() => {
    if (
      form.remitente_id &&
      remitentes.length > 0 &&
      ciudades.length > 0 &&
      paises.length > 0
    ) {
      const remitente = remitentes.find((r) => r.id === form.remitente_id);
      if (remitente && remitente.ciudad_id) {
        const ciudad = ciudades.find((c) => c.id === remitente.ciudad_id);
        if (ciudad) {
          setCiudad7({
            value: ciudad.id,
            label: `${ciudad.nombre.toUpperCase()} - ${(
              paises.find((p) => p.id === ciudad.pais_id)?.nombre || ""
            ).toUpperCase()}`,
            ciudad: ciudad.nombre,
            pais: paises.find((p) => p.id === ciudad.pais_id)?.nombre || "",
            pais_id: ciudad.pais_id,
          });
        }
      }
    }
  }, [form.remitente_id, remitentes, ciudades, paises]);

  useEffect(() => {
    if (ciudad7 && fecha7) {
      setForm((f) => ({
        ...f,
        local_responsabilidad: `${ciudad7.ciudad.toUpperCase()} - ${ciudad7.pais.toUpperCase()}-${formatoFecha(
          fecha7
        )}`,
      }));
    }
  }, [ciudad7, fecha7]);

  useEffect(() => {
    if (
      form.destinatario_id &&
      remitentes.length > 0 &&
      ciudades.length > 0 &&
      paises.length > 0
    ) {
      const destinatario = remitentes.find(
        (r) => r.id === form.destinatario_id
      );
      if (destinatario && destinatario.ciudad_id) {
        const ciudad = ciudades.find((c) => c.id === destinatario.ciudad_id);
        const pais = paises.find((p) => ciudad && ciudad.pais_id === p.id);
        const lugarAuto =
          ciudad && pais
            ? `${ciudad.nombre.toUpperCase()} - ${pais.nombre.toUpperCase()}`
            : "";
        setForm((f) => {
          if (
            !f.lugar_entrega ||
            f.lugar_entrega === "" ||
            f.lugar_entrega === lugarAuto
          ) {
            return { ...f, lugar_entrega: lugarAuto };
          }
          return f;
        });
      }
    }
  }, [form.destinatario_id, remitentes, ciudades, paises]);

  // Auto-poblar firmas cuando se seleccionan entidades
  useEffect(() => {
    if (form.remitente_id && remitentes.length > 0 && !firmaRemitente) {
      const remitente = remitentes.find((r) => r.id === form.remitente_id);
      if (remitente) {
        setFirmaRemitente({ value: remitente.id, label: remitente.nombre });
      }
    }
  }, [form.remitente_id, remitentes, firmaRemitente]);

  useEffect(() => {
    if (form.transportadora_id && transportadoras.length > 0 && !firmaTransportador) {
      const transportadora = transportadoras.find((t) => t.id === form.transportadora_id);
      if (transportadora) {
        setFirmaTransportador({ value: transportadora.id, label: transportadora.nombre });
      }
    }
  }, [form.transportadora_id, transportadoras, firmaTransportador]);

  useEffect(() => {
    if (form.destinatario_id && remitentes.length > 0 && !firmaDestinatario) {
      const destinatario = remitentes.find((r) => r.id === form.destinatario_id);
      if (destinatario) {
        setFirmaDestinatario({ value: destinatario.id, label: destinatario.nombre });
      }
    }
  }, [form.destinatario_id, remitentes, firmaDestinatario]);

  const handleValorGastoInput = (e, campo) => {
    let v = e.target.value
      .replace(/[^\d.,]/g, "")
      .replace(/\.(?=.*\.)/g, "")
      .replace(/,/g, ",");
    setGastoActual((g) => ({ ...g, [campo]: v }));
  };

  const handleValorGastoBlur = (e, campo) => {
    let val = e.target.value.replace(/\./g, "").replace(",", ".");
    let num = parseFloat(val);
    setGastoActual((g) => ({
      ...g,
      [campo]: isNaN(num)
        ? ""
        : num.toLocaleString("es-ES", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
    }));
  };

  const handleMonedaGasto = (option) => {
    setMonedaGasto(option);
    setMonedaTouched(true);
  };

  const handleAddGasto = () => {
    if (!gastoActual.tramo) return;
    const normaliza = (v) =>
      typeof v === "string"
        ? parseFloat(v.replace(/\./g, "").replace(",", "."))
        : v;
    setForm((f) => ({
      ...f,
      gastos: [
        ...f.gastos,
        {
          ...gastoActual,
          valor_remitente: normaliza(gastoActual.valor_remitente),
          valor_destinatario: normaliza(gastoActual.valor_destinatario),
        },
      ],
    }));
    setGastoActual({ tramo: "", valor_remitente: "", valor_destinatario: "" });
  };

  const handleRemoveGasto = (idx) =>
    setForm((f) => ({ ...f, gastos: f.gastos.filter((_, i) => i !== idx) }));

  const totalRemitente = form.gastos.reduce(
    (acc, g) => acc + (parseFloat(g.valor_remitente) || 0),
    0
  );
  const totalDestinatario = form.gastos.reduce(
    (acc, g) => acc + (parseFloat(g.valor_destinatario) || 0),
    0
  );

  const monedaCodigo = monedaGasto
    ? monedas.find((m) => m.id === monedaGasto.value)?.codigo ||
      monedaGasto.label
    : "";

  useEffect(() => {
    if (form.gastos.length > 0) {
      const primerGasto = form.gastos[0];
      const primerValor =
        primerGasto.valor_remitente &&
        parseFloat(primerGasto.valor_remitente) > 0
          ? primerGasto.valor_remitente
          : primerGasto.valor_destinatario || "";
      setForm((f) => ({
        ...f,
        valor_flete_externo: primerValor,
      }));
    } else {
      setForm((f) => ({
        ...f,
        valor_flete_externo: "",
      }));
    }
  }, [form.gastos]);

  const handleValorIncotermChange = (e) => {
    let val = e.target.value.replace(/[^\d,]/g, "");
    val = val.replace(/(,)(?=.*,)/g, "");
    setForm((f) => ({ ...f, valor_incoterm: val }));
  };
  const handleValorIncotermBlur = (e) => {
    let raw = e.target.value.replace(/\./g, "").replace(",", ".");
    let num = parseFloat(raw);
    setForm((f) => ({
      ...f,
      valor_incoterm: isNaN(num) ? "" : num.toFixed(2).replace(".", ","),
    }));
  };

  const handlePesoInput = (e) => {
    let v = e.target.value.replace(/[^\d,]/g, "");
    v = v.replace(/(,)(?=.*,)/g, "");
    setForm((f) => ({ ...f, [e.target.name]: v }));
  };
  const handlePesoBlur = (e) => {
    let raw = e.target.value.replace(/\./g, "").replace(",", ".");
    let num = parseFloat(raw);
    setForm((f) => ({
      ...f,
      [e.target.name]: isNaN(num) ? "" : num.toFixed(3).replace(".", ","),
    }));
  };

  const handleVolumenInput = (e) => {
    let v = e.target.value.replace(/[^\d,]/g, "");
    v = v.replace(/(,)(?=.*,)/g, "");
    setForm((f) => ({ ...f, volumen: v }));
  };
  const handleVolumenBlur = (e) => {
    let raw = e.target.value.replace(/\./g, "").replace(",", ".");
    let num = parseFloat(raw);
    setForm((f) => ({
      ...f,
      volumen: isNaN(num) ? "" : num.toFixed(5).replace(".", ","),
    }));
  };

  const handleDeclaracionInput = (e) => {
    let v = e.target.value.replace(/[^\d,]/g, "");
    v = v.replace(/(,)(?=.*,)/g, "");
    setForm((f) => ({ ...f, declaracion_mercaderia: v }));
  };
  const handleDeclaracionBlur = (e) => {
    let raw = e.target.value.replace(/\./g, "").replace(",", ".");
    let num = parseFloat(raw);
    setForm((f) => ({
      ...f,
      declaracion_mercaderia: isNaN(num)
        ? ""
        : num.toFixed(2).replace(".", ","),
    }));
  };

  const handleIncoterm = (option) => {
    setForm((f) => ({ ...f, incoterm: option ? option.value : "" }));
  };

  useEffect(() => {
    if (
      selectedTransportadora &&
      selectedTransportadora.id &&
      selectedTransportadora.codigo
    ) {
      api
        .get(
          `/crts/next_number?transportadora_id=${selectedTransportadora.id}&codigo=${selectedTransportadora.codigo}`
        )
        .then((res) =>
          setForm((f) => ({ ...f, numero_crt: res.data.next_number }))
        )
        .catch(() => setForm((f) => ({ ...f, numero_crt: "" })));
    } else {
      setForm((f) => ({ ...f, numero_crt: "" }));
    }
  }, [selectedTransportadora]);

  const handleRemitente = (option) =>
    setForm((f) => ({ ...f, remitente_id: option ? option.value : null }));
  const handleDestinatario = (option) =>
    setForm((f) => ({
      ...f,
      destinatario_id: option ? option.value : null,
      consignatario_id:
        !f.consignatario_id && option ? option.value : f.consignatario_id,
      notificar_a_id:
        !f.notificar_a_id && option ? option.value : f.notificar_a_id,
    }));
  const handleConsignatario = (option) =>
    setForm((f) => ({ ...f, consignatario_id: option ? option.value : null }));
  const handleNotificarA = (option) =>
    setForm((f) => ({ ...f, notificar_a_id: option ? option.value : null }));
  const handleInput = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  const handleCiudadPais = (option) =>
    setForm((f) => ({
      ...f,
      ciudad_emision_id: option ? option.value : null,
      pais_emision_id: option ? option.pais_id : null,
    }));
  const handleSelect = (name, option) =>
    setForm((f) => ({ ...f, [name]: option ? option.value : null }));
  const handleCiudad7 = (option) => setCiudad7(option);
  const handleFecha7 = (e) => setFecha7(e.target.value);

  // Función para auto-resize del textarea
  const autoResizeTextarea = () => {
    if (textareaRef.current) {
      // Pequeño retraso para asegurar que el DOM se actualice
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto';
          textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
      }, 0);
    }
  };

  // Auto-resize cuando cambia el contenido
  useEffect(() => {
    autoResizeTextarea();
  }, [form.detalles_mercaderia]);

  const handleLugarEntregaSelect = (option) => {
    setForm((f) => ({
      ...f,
      lugar_entrega: option ? option.label : "",
    }));
  };


  const monedaObligatoria = !monedaGasto || !monedaGasto.value;
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMonedaTouched(true);

    // Validar que se haya seleccionado un remitente
    if (!form.remitente_id) {
      alert("Debe seleccionar un remitente antes de guardar el CRT.");
      return;
    }

    // Validar que se haya seleccionado un destinatario
    if (!form.destinatario_id) {
      alert("Debe seleccionar un destinatario antes de guardar el CRT.");
      return;
    }

    // Validar que se haya seleccionado una transportadora
    if (!form.transportadora_id) {
      alert("Debe seleccionar una transportadora antes de guardar el CRT.");
      return;
    }

    if (monedaObligatoria) return;

    try {
      const dataToSend = {
        ...form,
        gastos: form.gastos.map((g) => ({
          ...g,
          moneda: monedaCodigo,
        })),
        moneda_id: monedaGasto ? monedaGasto.value : null,
        firma_remitente: firmaRemitente ? firmaRemitente.label : "",
        firma_transportador: firmaTransportador ? firmaTransportador.label : "",
        firma_destinatario: firmaDestinatario ? firmaDestinatario.label : "",
      };

      if (isEditing && editingCrtId) {
        // Actualizar CRT existente
        await api.put(`/crts/${editingCrtId}`, dataToSend);
        alert("CRT actualizado correctamente");
        navigate("/listar-crt");
      } else {
        // Crear nuevo CRT
        const response = await api.post("/crts/", dataToSend);
        setCrtEmitido(response.data);
        setShowMicModal(true);
        setForm((f) => ({ ...f, gastos: [] }));
        setMonedaTouched(false);
      }
    } catch (e) {
      alert("Error al guardar CRT: " + (e.response?.data?.error || e.message));
    }
  };

  // Función para crear MIC con datos del CRT
  const handleCrearMicDesdeCrt = async () => {
    if (!crtEmitido?.id) {
      alert("No se pudo obtener el ID del CRT emitido.");
      return;
    }

    try {
      // Obtener datos del CRT para pre-cargar el MIC
      const resp = await api.get(`/mic/get_crt_data/${crtEmitido.id}`);
      if (resp.data.success) {
        // Cerrar modal y navegar a MIC con datos pre-cargados
        setShowMicModal(false);
        navigate("/mic/nuevo", { state: resp.data.datos });
      } else {
        alert("Error obteniendo datos del CRT: " + resp.data.mensaje);
      }
    } catch (err) {
      alert(
        "Error al obtener datos del CRT: " +
          (err.response?.data?.error || err.message)
      );
    }
  };

  // Función para crear MIC nuevo
  const handleCrearMicNuevo = () => {
    setShowMicModal(false);
    navigate("/mic/nuevo");
  };

  // Función para cerrar modal sin crear MIC
  const handleCerrarModal = () => {
    setShowMicModal(false);
    setCrtEmitido(null);
  };

  // Mostrar loading mientras se cargan datos para editar
  if (loadingEdit) {
    return (
      <div className="bg-slate-50 min-h-screen py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-center items-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-lg text-gray-600">Cargando datos del CRT para editar...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 min-h-screen py-4">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold mb-4 text-center text-indigo-700">
          {isEditing ? `EDITAR CRT - ${form.numero_crt || 'Cargando...'}` : 'SALIDA DE CARGAMENTO'}
        </h2>
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl shadow-lg p-6 border"
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-2">
            <div className="md:col-span-2 flex flex-col gap-2">
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  1. Nome e endereço do remetente <span className="text-red-500">*</span>
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Nombre y domicilio del remitente <span className="text-red-500">*</span>
                </span>
                <Select
                  options={opt(remitentes)}
                  value={
                    opt(remitentes).find(
                      (x) => x.value === form.remitente_id
                    ) || null
                  }
                  onChange={handleRemitente}
                  placeholder="Seleccione una opción"
                  isClearable
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  4. Nome e endereço do destinatário <span className="text-red-500">*</span>
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Nombre y domicilio del destinatario <span className="text-red-500">*</span>
                </span>
                <Select
                  options={opt(remitentes)}
                  value={
                    opt(remitentes).find(
                      (x) => x.value === form.destinatario_id
                    ) || null
                  }
                  onChange={handleDestinatario}
                  placeholder="Seleccione una opción"
                  isClearable
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  6. Nome e endereço do consignatário
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Nombre y domicilio del consignatario
                </span>
                <Select
                  options={opt(remitentes)}
                  value={
                    opt(remitentes).find(
                      (x) => x.value === form.consignatario_id
                    ) || null
                  }
                  onChange={handleConsignatario}
                  placeholder="Seleccione una opción"
                  isClearable
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  9. Notificar a:
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Notificar a
                </span>
                <Select
                  options={opt(remitentes)}
                  value={
                    opt(remitentes).find(
                      (x) => x.value === form.notificar_a_id
                    ) || null
                  }
                  onChange={handleNotificarA}
                  placeholder="Seleccione una opción"
                  isClearable
                />
              </label>
              <label className="block h-full">
                <span className="font-bold text-xs text-blue-900">
                  11. Quantidade e categoria de volumes, marcas e números, tipos
                  de mercadorias, contêineres e acessórios
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Cantidad y clase de bultos, marcas y números, tipo de
                  mercancías, contenedores y accesorios
                </span>
                <textarea
                  ref={textareaRef}
                  name="detalles_mercaderia"
                  value={form.detalles_mercaderia}
                  onChange={handleInput}
                  onInput={autoResizeTextarea}
                  className="block w-full rounded border px-2 py-1 resize-none overflow-hidden"
                  rows={1}
                  style={{
                    minHeight: "110px",
                    maxHeight: "400px"
                  }}
                  placeholder="Ingrese los detalles de la mercadería..."
                />
              </label>
            </div>
            <div className="md:col-span-2 flex flex-col gap-2">
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  2. Número
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">Número</span>
                <input
                  type="text"
                  name="numero_crt"
                  value={form.numero_crt}
                  disabled
                  className="block w-full rounded border px-2 py-1 bg-gray-200 text-gray-600 cursor-not-allowed"
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  3. Nome e endereço do transportador <span className="text-red-500">*</span>
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Nombre y domicilio del porteador <span className="text-red-500">*</span>
                </span>
                <Select
                  options={opt(transportadoras)}
                  value={
                    opt(transportadoras).find(
                      (x) => x.value === form.transportadora_id
                    ) || null
                  }
                  onChange={(opt) => {
                    handleSelect("transportadora_id", opt);
                    setSelectedTransportadora(opt);
                  }}
                  placeholder="Seleccione una opción"
                  isClearable
                  isSearchable
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  5. Local e país de emissão
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Lugar y país de emisión
                </span>
                <Select
                  options={optCiudadPais(ciudades, paises)}
                  value={
                    optCiudadPais(ciudades, paises).find(
                      (x) => x.value === form.ciudad_emision_id
                    ) || null
                  }
                  onChange={handleCiudadPais}
                  placeholder="Seleccione una opción"
                  isClearable
                  isSearchable
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  7. Local, país e data que o transportador se responsabiliza
                  pela mercadoria
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Lugar, país y fecha en que el portador se hace cargo de las
                  mercancias
                </span>
                <div className="flex flex-row gap-2 items-center">
                  <Select
                    options={optCiudadPais(ciudades, paises)}
                    value={ciudad7}
                    onChange={handleCiudad7}
                    placeholder="Ciudad y País"
                    isClearable
                    isSearchable
                    className="flex-1"
                  />
                  <input
                    type="date"
                    value={fecha7}
                    onChange={handleFecha7}
                    className="rounded border px-2 py-1 w-[140px]"
                  />
                </div>
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  8. Localidade, país e prazo de entrega
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Lugar, país y plazo de entrega
                </span>
                <Select
                  options={optCiudadPais(ciudades, paises)}
                  value={
                    optCiudadPais(ciudades, paises).find(
                      (x) => x.label === form.lugar_entrega
                    ) || null
                  }
                  onChange={handleLugarEntregaSelect}
                  placeholder="Seleccione una opción"
                  isClearable
                  isSearchable
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  10. Transporte sucessivos
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Porteadores sucesivos
                </span>
                <input
                  type="text"
                  name="transporte_sucesivos"
                  value={form.transporte_sucesivos}
                  onChange={handleInput}
                  className="block w-full rounded border px-2 py-1"
                />
              </label>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-2">
            <div>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  12 Peso Bruto em Kg. / Peso Bruto en Kg.
                </span>
                <div className="flex gap-2 mt-1">
                  <div className="flex flex-col">
                    <span className="text-[11px] font-semibold text-blue-900 mb-1">
                      PB:
                    </span>
                    <input
                      type="text"
                      name="peso_bruto"
                      value={form.peso_bruto}
                      onChange={handlePesoInput}
                      onBlur={handlePesoBlur}
                      className="block rounded border px-2 py-1 w-[120px] text-right"
                      inputMode="decimal"
                      placeholder="0,000"
                    />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[11px] font-semibold text-blue-900 mb-1">
                      PN:
                    </span>
                    <input
                      type="text"
                      name="peso_neto"
                      value={form.peso_neto}
                      onChange={handlePesoInput}
                      onBlur={handlePesoBlur}
                      className="block rounded border px-2 py-1 w-[120px] text-right"
                      inputMode="decimal"
                      placeholder="0,000"
                    />
                  </div>
                </div>
              </label>
            </div>
            <div>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  13. Volume em m³
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Volumen en m.cu
                </span>
                <input
                  type="text"
                  name="volumen"
                  value={form.volumen}
                  onChange={handleVolumenInput}
                  onBlur={handleVolumenBlur}
                  className="block w-full rounded border px-2 py-1 text-right"
                  placeholder="0,00000"
                  inputMode="decimal"
                />
              </label>
            </div>
            <div className="md:col-span-2">
              <label className="block font-bold text-xs text-blue-900 mb-1">
                14 Valor / Valor
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                <div>
                  <label className="text-xs font-semibold text-blue-800">
                    Tipo
                  </label>
                  <Select
                    options={INCOTERMS}
                    value={
                      INCOTERMS.find((opt) => opt.value === form.incoterm) ||
                      null
                    }
                    onChange={handleIncoterm}
                    placeholder="Tipo"
                    isClearable
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-blue-800">
                    Valor:
                  </label>
                  <input
                    type="text"
                    name="valor_incoterm"
                    value={form.valor_incoterm}
                    onChange={handleValorIncotermChange}
                    onBlur={handleValorIncotermBlur}
                    placeholder="0,00"
                    className="block w-full rounded border px-2 py-1 text-right"
                    inputMode="decimal"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-blue-800">
                    Seleccione la moneda: <span className="text-red-500">*</span>
                  </label>
                  <Select
                    options={opt(monedas)}
                    value={monedaGasto}
                    onChange={handleMonedaGasto}
                    placeholder="Moneda"
                    isClearable
                    className={
                      "w-full " +
                      (monedaTouched && monedaObligatoria
                        ? "border-red-500 border-2"
                        : "")
                    }
                    getOptionLabel={(opt) =>
                      opt.codigo ? `${opt.codigo} - ${opt.nombre}` : opt.label
                    }
                    getOptionValue={(opt) => opt.value}
                  />
                  {monedaTouched && monedaObligatoria && (
                    <span className="text-xs text-red-500 font-bold block mt-1">
                      Moneda obligatoria
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-4 mb-2">
            <div className="flex-1 min-w-[420px] bg-slate-50 p-2 rounded border">
              <span className="font-bold text-xs text-blue-900">
                15. Custos a Pagar / Gastos a Pagar
              </span>
              <div className="flex gap-2 mt-1 items-center">
                <input
                  placeholder="Descripción"
                  name="tramo"
                  value={gastoActual.tramo}
                  onChange={(e) =>
                    setGastoActual({ ...gastoActual, tramo: e.target.value })
                  }
                  className="rounded border px-2 py-1 w-44"
                />
                <input
                  type="text"
                  placeholder="Valor remitente"
                  name="valor_remitente"
                  value={gastoActual.valor_remitente}
                  onChange={(e) => handleValorGastoInput(e, "valor_remitente")}
                  onBlur={(e) => handleValorGastoBlur(e, "valor_remitente")}
                  className="rounded border px-2 py-1 w-32 text-right"
                  inputMode="decimal"
                />
                <input
                  type="text"
                  placeholder="Valor destinatario"
                  name="valor_destinatario"
                  value={gastoActual.valor_destinatario}
                  onChange={(e) =>
                    handleValorGastoInput(e, "valor_destinatario")
                  }
                  onBlur={(e) => handleValorGastoBlur(e, "valor_destinatario")}
                  className="rounded border px-2 py-1 w-32 text-right"
                  inputMode="decimal"
                />
                <Select
                  options={opt(monedas)}
                  value={monedaGasto}
                  onChange={handleMonedaGasto}
                  placeholder="Moneda"
                  isClearable
                  className={
                    "w-32 " +
                    (monedaTouched && monedaObligatoria
                      ? "border-red-500 border-2"
                      : "")
                  }
                  getOptionLabel={(opt) =>
                    opt.codigo ? `${opt.codigo} - ${opt.nombre}` : opt.label
                  }
                  getOptionValue={(opt) => opt.value}
                />
                <button
                  type="button"
                  onClick={handleAddGasto}
                  className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded transition"
                  title="Agregar gasto"
                >
                  +
                </button>
              </div>
              <table className="w-full border mt-2 rounded text-xs">
                <thead>
                  <tr className="bg-sky-100 text-sky-800">
                    <th className="p-2 font-semibold">Descripción</th>
                    <th className="p-2 font-semibold">Valor Remitente</th>
                    <th className="p-2 font-semibold">Valor Destinatario</th>
                    <th className="p-2 font-semibold">Moneda</th>
                    <th className="p-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {form.gastos.map((g, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="p-2">{g.tramo}</td>
                      <td className="p-2 text-right">
                        {parseFloat(g.valor_remitente || 0).toLocaleString(
                          "es-ES",
                          { minimumFractionDigits: 2 }
                        )}
                      </td>
                      <td className="p-2 text-right">
                        {parseFloat(g.valor_destinatario || 0).toLocaleString(
                          "es-ES",
                          { minimumFractionDigits: 2 }
                        )}
                      </td>
                      <td className="p-2">{monedaCodigo}</td>
                      <td className="p-2">
                        <button
                          type="button"
                          onClick={() => handleRemoveGasto(idx)}
                          className="bg-red-500 hover:bg-red-700 text-white px-2 py-1 rounded"
                          title="Quitar gasto"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="flex gap-2 items-center mt-2 font-bold">
                <span className="text-xs">Total {monedaCodigo}:</span>
                <input
                  value={totalRemitente.toLocaleString("es-ES", {
                    minimumFractionDigits: 2,
                  })}
                  className="rounded border px-2 py-1 w-28 text-right bg-gray-100"
                  disabled
                />
                <span className="text-xs">{monedaCodigo}</span>
                <input
                  value={totalDestinatario.toLocaleString("es-ES", {
                    minimumFractionDigits: 2,
                  })}
                  className="rounded border px-2 py-1 w-28 text-right bg-gray-100"
                  disabled
                />
              </div>
            </div>
            <div className="flex flex-col gap-2 w-full md:w-80">
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  16. Declaração do valor das mercadorias
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Declaración del valor de las mercaderías
                </span>
                <input
                  type="text"
                  name="declaracion_mercaderia"
                  value={form.declaracion_mercaderia}
                  onChange={handleDeclaracionInput}
                  onBlur={handleDeclaracionBlur}
                  className="block w-full rounded border px-2 py-1 text-right"
                  placeholder="0,00"
                  inputMode="decimal"
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  17. Documentos Anexos
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Documentos Anexos
                </span>
                <input
                  type="text"
                  name="factura_exportacion"
                  value={form.factura_exportacion}
                  onChange={handleInput}
                  placeholder="Factura de Exportación Nº"
                  className="block w-full rounded border px-2 py-1 mb-1"
                />
                <input
                  type="text"
                  name="nro_despacho"
                  value={form.nro_despacho}
                  onChange={handleInput}
                  placeholder="Despacho Nº"
                  className="block w-full rounded border px-2 py-1"
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  18. Instruções sobre formalidades de alfândega
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Instrucciones sobre formalidades de aduana
                </span>
                <textarea
                  name="formalidades_aduana"
                  value={form.formalidades_aduana}
                  onChange={handleInput}
                  className="block w-full rounded border px-2 py-1"
                  rows={2}
                />
              </label>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  19. Valor do frete Externo
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Monto del Flete Externo
                </span>
                <input
                  type="number"
                  step="0.01"
                  name="valor_flete_externo"
                  value={form.valor_flete_externo}
                  className="block w-full rounded border px-2 py-1 bg-gray-100"
                  disabled
                />
              </label>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-2">
            <div>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  20. Valor do Reembolso Contra Entrega
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Monto de Reembolso Contra Entrega
                </span>
                <input
                  type="number"
                  step="0.01"
                  name="valor_reembolso"
                  value={form.valor_reembolso}
                  onChange={handleInput}
                  className="block w-full rounded border px-2 py-1"
                />
              </label>
              <div className="border p-2 rounded-lg bg-blue-50 mt-4">
                <div className="font-bold text-xs text-blue-900">
                  21. Nombre y firma del remitente
                </div>
                <Select
                  options={opt(remitentes)}
                  value={firmaRemitente}
                  onChange={setFirmaRemitente}
                  placeholder="Seleccionar firma del remitente"
                  isClearable
                  className="mt-1"
                />
                <div className="text-xs text-gray-500 mt-1">
                  Fecha: {fecha7 ? formatoFecha(fecha7) : "--/--/----"}
                </div>
              </div>
              <div className="border p-2 rounded-lg bg-blue-50 mt-4">
                <div className="font-bold text-xs text-blue-900">
                  23. Nombre y firma del transportador
                </div>
                <Select
                  options={opt(transportadoras)}
                  value={firmaTransportador}
                  onChange={setFirmaTransportador}
                  placeholder="Seleccionar firma del transportador"
                  isClearable
                  className="mt-1"
                />
                <div className="text-xs text-gray-500 mt-1">
                  Fecha: {fecha7 ? formatoFecha(fecha7) : "--/--/----"}
                </div>
              </div>
            </div>
            <div>
              <label className="block">
                <span className="font-bold text-xs text-blue-900">
                  22. Declarações e observações
                </span>
                <br />
                <span className="font-bold text-xs text-blue-700">
                  Declaraciones y observaciones
                </span>
                <textarea
                  name="observaciones"
                  value={form.observaciones}
                  onChange={handleInput}
                  className="block w-full rounded border px-2 py-1 mb-1"
                  rows={2}
                />
              </label>
              <div className="border p-2 rounded-lg bg-blue-50 mt-4">
                <div className="font-bold text-xs text-blue-900">
                  24. Nombre y firma del destinatario
                </div>
                <Select
                  options={opt(remitentes)}
                  value={firmaDestinatario}
                  onChange={setFirmaDestinatario}
                  placeholder="Seleccionar firma del destinatario"
                  isClearable
                  className="mt-1"
                />
                <div className="text-xs text-gray-500 mt-1">
                  Fecha: {fecha7 ? formatoFecha(fecha7) : "--/--/----"}
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-gray-600 mb-4 text-center">
            <span className="text-red-500">*</span> Campos obligatorios
          </div>
          <div className="flex flex-col md:flex-row gap-4 justify-end mt-8">
            {isEditing && (
              <button
                type="button"
                onClick={() => navigate('/listar-crt')}
                className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-10 rounded-xl shadow-lg transition"
              >
                ← Volver a Lista
              </button>
            )}
            <button
              type="submit"
              disabled={loadingEdit}
              className="bg-indigo-700 hover:bg-indigo-800 text-white font-bold py-3 px-10 rounded-xl shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadingEdit ? 'Cargando...' : (isEditing ? 'Actualizar CRT' : 'Emitir CRT')}
            </button>
          </div>
        </form>
      </div>

      {/* Modal de confirmación para crear MIC */}
      {showMicModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="mb-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  ¡CRT Emitido Exitosamente!
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Número de CRT: <span className="font-bold text-indigo-600">{crtEmitido?.numero_crt}</span>
                </p>
                <p className="text-sm text-gray-700 mb-6">
                  ¿Desea crear un Manifiesto de Carga (MIC) con los datos de este CRT?
                </p>
              </div>

              <div className="flex flex-col gap-3">
                <button
                  onClick={handleCrearMicDesdeCrt}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Crear MIC con datos del CRT
                </button>

                <button
                  onClick={handleCrearMicNuevo}
                  className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Crear MIC nuevo
                </button>

                <button
                  onClick={handleCerrarModal}
                  className="w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded-lg transition duration-200 text-sm"
                >
                  Continuar sin crear MIC
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CRT;
