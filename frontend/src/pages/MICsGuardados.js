import React, { useState, useEffect } from "react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./MICsGuardados.css";

// Componente principal
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

  // Estados para filtros
  const [filters, setFilters] = useState({
    estado: '',
    numero_carta: '',
    fecha_desde: '',
    fecha_hasta: '',
    transportadora: '',
    placa: '',
    destino: ''
  });

  // Cargar MICs
  const cargarMics = async (page = 1, filtros = {}) => {
    setLoading(true);
    try {
      console.log('🔍 Cargando MICs guardados...', { page, filtros });
      
      const params = {
        page,
        per_page: perPage,
        ...filtros
      };

      const response = await axios.get('http://localhost:5000/api/mic-guardados/', { params });
      
      setMics(response.data.mics);
      setCurrentPage(response.data.pagination.page);
      setTotalPages(response.data.pagination.pages);
      setTotalItems(response.data.pagination.total);

      console.log(`✅ ${response.data.mics.length} MICs cargados de ${response.data.pagination.total} totales`);
      
      if (response.data.mics.length === 0 && Object.values(filtros).some(v => v)) {
        toast.info("🔍 No se encontraron MICs con los filtros aplicados");
      }
    } catch (error) {
      console.error('❌ Error cargando MICs:', error);
      toast.error(`❌ Error cargando MICs: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Cargar estadísticas
  const cargarEstadisticas = async () => {
    try {
      console.log('📊 Cargando estadísticas...');
      const response = await axios.get('http://localhost:5000/api/mic-guardados/stats');
      setStats(response.data);
      console.log('✅ Estadísticas cargadas:', response.data);
    } catch (error) {
      console.error('❌ Error cargando estadísticas:', error);
      toast.error('❌ Error cargando estadísticas');
    }
  };

  // Efectos
  useEffect(() => {
    cargarMics();
    cargarEstadisticas();
  }, []);

  // Aplicar filtros
  const aplicarFiltros = () => {
    console.log('🔍 Aplicando filtros:', filters);
    cargarMics(1, filters);
    setCurrentPage(1);
    setShowFilters(false);
    toast.info("🔍 Filtros aplicados");
  };

  // Limpiar filtros
  const limpiarFiltros = () => {
    setFilters({
      estado: '',
      numero_carta: '',
      fecha_desde: '',
      fecha_hasta: '',
      transportadora: '',
      placa: '',
      destino: ''
    });
    cargarMics();
    toast.info("🧹 Filtros limpiados");
  };

  // Ver detalles de MIC
  const verDetalles = async (micId) => {
    try {
      console.log(`🔍 Cargando detalles del MIC ${micId}...`);
      const response = await axios.get(`http://localhost:5000/api/mic-guardados/${micId}`);
      setSelectedMic(response.data);
      setShowModal(true);
      console.log('✅ Detalles cargados:', response.data);
    } catch (error) {
      console.error('❌ Error cargando detalles:', error);
      toast.error('❌ Error cargando detalles del MIC');
    }
  };

  // Descargar PDF
  const descargarPDF = async (micId, numeroCarta) => {
    try {
      console.log(`📄 Descargando PDF del MIC ${micId}...`);
      const response = await axios.get(
        `http://localhost:5000/api/mic-guardados/${micId}/pdf`,
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `MIC_${numeroCarta || micId}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('📄 PDF descargado exitosamente');
      console.log('✅ PDF descargado');
    } catch (error) {
      console.error('❌ Error descargando PDF:', error);
      toast.error('❌ Error descargando PDF');
    }
  };

  // Anular MIC
  const anularMic = async (micId, numeroCarta) => {
    if (!window.confirm(`¿Estás seguro de anular el MIC ${numeroCarta}?`)) {
      return;
    }

    try {
      console.log(`🗑️ Anulando MIC ${micId}...`);
      await axios.delete(`http://localhost:5000/api/mic-guardados/${micId}`);
      toast.success('✅ MIC anulado exitosamente');
      cargarMics(currentPage, filters);
      console.log('✅ MIC anulado');
    } catch (error) {
      console.error('❌ Error anulando MIC:', error);
      toast.error('❌ Error anulando MIC');
    }
  };

  // Cambiar página
  const cambiarPagina = (nuevaPagina) => {
    if (nuevaPagina >= 1 && nuevaPagina <= totalPages) {
      setCurrentPage(nuevaPagina);
      cargarMics(nuevaPagina, filters);
    }
  };

  // Formatear fecha
  const formatearFecha = (fecha) => {
    if (!fecha) return "N/A";
    try {
      return new Date(fecha).toLocaleDateString('es-PY');
    } catch {
      return fecha;
    }
  };

  // Formatear estado con color
  const formatearEstado = (estado) => {
    const colores = {
      'PROVISORIO': 'bg-yellow-100 text-yellow-800',
      'DEFINITIVO': 'bg-green-100 text-green-800',
      'ANULADO': 'bg-red-100 text-red-800',
      'EN_PROCESO': 'bg-blue-100 text-blue-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colores[estado] || 'bg-gray-100 text-gray-800'}`}>
        {estado}
      </span>
    );
  };

  return (
    <div className="mics-guardados-container">
      <ToastContainer position="top-right" />
      
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
            <button
              onClick={() => setShowStats(!showStats)}
              className="btn-secondary"
            >
              📊 {showStats ? 'Ocultar' : 'Ver'} Estadísticas
            </button>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-primary"
            >
              🔍 {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
            </button>
            <button
              onClick={() => cargarMics(currentPage, filters)}
              className="btn-primary"
              disabled={loading}
            >
              🔄 Actualizar
            </button>
          </div>
        </div>
      </div>

      {/* Estadísticas */}
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
            {stats.por_estado.map((est, idx) => (
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
                onChange={(e) => setFilters({...filters, estado: e.target.value})}
                className="filter-input"
              >
                <option value="">Todos</option>
                <option value="PROVISORIO">PROVISORIO</option>
                <option value="DEFINITIVO">DEFINITIVO</option>
                <option value="ANULADO">ANULADO</option>
                <option value="EN_PROCESO">EN_PROCESO</option>
              </select>
            </div>
            
            <div className="filter-group">
              <label>Nº Carta de Porte</label>
              <input
                type="text"
                value={filters.numero_carta}
                onChange={(e) => setFilters({...filters, numero_carta: e.target.value})}
                placeholder="Buscar por número..."
                className="filter-input"
              />
            </div>
            
            <div className="filter-group">
              <label>Transportadora</label>
              <input
                type="text"
                value={filters.transportadora}
                onChange={(e) => setFilters({...filters, transportadora: e.target.value})}
                placeholder="Buscar transportadora..."
                className="filter-input"
              />
            </div>
            
            <div className="filter-group">
              <label>Placa</label>
              <input
                type="text"
                value={filters.placa}
                onChange={(e) => setFilters({...filters, placa: e.target.value})}
                placeholder="Buscar placa..."
                className="filter-input"
              />
            </div>
            
            <div className="filter-group">
              <label>Destino</label>
              <input
                type="text"
                value={filters.destino}
                onChange={(e) => setFilters({...filters, destino: e.target.value})}
                placeholder="Buscar destino..."
                className="filter-input"
              />
            </div>
            
            <div className="filter-group">
              <label>Fecha Desde</label>
              <input
                type="date"
                value={filters.fecha_desde}
                onChange={(e) => setFilters({...filters, fecha_desde: e.target.value})}
                className="filter-input"
              />
            </div>
            
            <div className="filter-group">
              <label>Fecha Hasta</label>
              <input
                type="date"
                value={filters.fecha_hasta}
                onChange={(e) => setFilters({...filters, fecha_hasta: e.target.value})}
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

      {/* Tabla de MICs */}
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
                      {mic.numero_carta_porte || "Sin número"}
                    </td>
                    <td className="estado-cell">
                      {formatearEstado(mic.estado)}
                    </td>
                    <td className="fecha-cell">
                      {formatearFecha(mic.fecha_emision)}
                    </td>
                    <td className="transportadora-cell" title={mic.transportadora}>
                      {mic.transportadora ? 
                        (mic.transportadora.length > 30 ? 
                          mic.transportadora.substring(0, 30) + "..." : 
                          mic.transportadora
                        ) : "N/A"
                      }
                    </td>
                    <td className="destino-cell">
                      {mic.destino || "N/A"}
                    </td>
                    <td className="placa-cell">
                      {mic.placa_camion || "N/A"}
                    </td>
                    <td className="peso-cell">
                      {mic.peso_bruto ? `${mic.peso_bruto} kg` : "N/A"}
                    </td>
                    <td className="creado-cell">
                      {formatearFecha(mic.creado_en)}
                    </td>
                    <td className="acciones-cell">
                      <div className="acciones-group">
                        <button
                          onClick={() => verDetalles(mic.id)}
                          className="btn-action btn-view"
                          title="Ver detalles"
                        >
                          👁️
                        </button>
                        <button
                          onClick={() => descargarPDF(mic.id, mic.numero_carta_porte)}
                          className="btn-action btn-download"
                          title="Descargar PDF"
                        >
                          📄
                        </button>
                        {mic.estado !== 'ANULADO' && (
                          <button
                            onClick={() => anularMic(mic.id, mic.numero_carta_porte)}
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
            Mostrando {((currentPage - 1) * perPage) + 1} a {Math.min(currentPage * perPage, totalItems)} de {totalItems} registros
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
                    className={`pagination-btn ${pageNum === currentPage ? 'active' : ''}`}
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

      {/* Modal de detalles */}
      {showModal && selectedMic && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📋 Detalles del MIC #{selectedMic.id}</h2>
              <button
                onClick={() => setShowModal(false)}
                className="modal-close"
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <MICDetalles mic={selectedMic} />
            </div>
            
            <div className="modal-footer">
              <button
                onClick={() => descargarPDF(selectedMic.id, selectedMic.campo_23_numero_campo2_crt)}
                className="btn-primary"
              >
                📄 Descargar PDF
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="btn-secondary"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Componente para mostrar detalles del MIC
function MICDetalles({ mic }) {
  const campos = [
    { key: 'campo_23_numero_campo2_crt', label: 'Nº Carta de Porte', importante: true },
    { key: 'campo_4_estado', label: 'Estado', importante: true },
    { key: 'campo_6_fecha', label: 'Fecha de Emisión', importante: true },
    { key: 'campo_1_transporte', label: 'Transportadora', multilinea: true },
    { key: 'campo_2_numero', label: 'Rol Contribuyente' },
    { key: 'campo_7_pto_seguro', label: 'Puerto Seguro' },
    { key: 'campo_8_destino', label: 'Destino' },
    { key: 'campo_10_numero', label: 'Rol Contribuyente (10)' },
    { key: 'campo_11_placa', label: 'Placa Camión' },
    { key: 'campo_12_modelo_chasis', label: 'Modelo/Chasis' },
    { key: 'campo_14_anio', label: 'Año' },
    { key: 'campo_15_placa_semi', label: 'Placa Semi' },
    { key: 'campo_24_aduana', label: 'Aduana' },
    { key: 'campo_25_moneda', label: 'Moneda' },
    { key: 'campo_26_pais', label: 'País Origen' },
    { key: 'campo_27_valor_campo16', label: 'Valor FOT' },
    { key: 'campo_28_total', label: 'Flete Total' },
    { key: 'campo_29_seguro', label: 'Seguro' },
    { key: 'campo_30_tipo_bultos', label: 'Tipo Bultos' },
    { key: 'campo_31_cantidad', label: 'Cantidad' },
    { key: 'campo_32_peso_bruto', label: 'Peso Bruto' },
    { key: 'campo_33_datos_campo1_crt', label: 'Remitente', multilinea: true },
    { key: 'campo_34_datos_campo4_crt', label: 'Destinatario', multilinea: true },
    { key: 'campo_35_datos_campo6_crt', label: 'Consignatario', multilinea: true },
    { key: 'campo_36_factura_despacho', label: 'Documentos Anexos' },
    { key: 'campo_37_valor_manual', label: 'Valor Manual' },
    { key: 'campo_38_datos_campo11_crt', label: 'Detalles Mercadería', multilinea: true },
    { key: 'campo_40_tramo', label: 'Tramo' },
  ];

  return (
    <div className="mic-detalles">
      <div className="detalles-grid">
        {campos.map(({ key, label, importante, multilinea }) => {
          const valor = mic[key];
          if (!valor) return null;

          return (
            <div key={key} className={`detalle-item ${importante ? 'importante' : ''} ${multilinea ? 'multilinea' : ''}`}>
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
        <p><strong>Creado:</strong> {mic.creado_en}</p>
        {mic.crt_numero && (
          <p><strong>CRT Origen:</strong> {mic.crt_numero}</p>
        )}
      </div>
    </div>
  );
}