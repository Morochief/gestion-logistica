import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/api"; // Asumiendo que tienes tu configuración de API
import { 
  Users, Globe, Building2, UserCheck, Truck, FileText, 
  ArrowLeftRight, Coins, DollarSign, Activity, 
  BarChart3, Settings, ChevronRight, Sparkles,
  TrendingUp, Clock, Star
} from "lucide-react";

const modules = [
  { 
    name: "Usuarios", 
    icon: <Users className="w-8 h-8" />, 
    path: "/usuarios",
    color: "from-blue-500 to-blue-700",
    bgColor: "bg-blue-50",
    description: "Gestión de usuarios del sistema",
    statsKey: "usuarios"
  },
  { 
    name: "Países", 
    icon: <Globe className="w-8 h-8" />, 
    path: "/paises",
    color: "from-green-500 to-emerald-700",
    bgColor: "bg-green-50",
    description: "Administrar países",
    statsKey: "paises"
  },
  { 
    name: "Ciudades", 
    icon: <Building2 className="w-8 h-8" />, 
    path: "/ciudades",
    color: "from-teal-500 to-cyan-700",
    bgColor: "bg-teal-50",
    description: "Gestión de ciudades",
    statsKey: "ciudades"
  },
  { 
    name: "Remitentes", 
    icon: <UserCheck className="w-8 h-8" />, 
    path: "/remitentes",
    color: "from-purple-500 to-violet-700",
    bgColor: "bg-purple-50",
    description: "Administrar remitentes",
    statsKey: "remitentes"
  },
  { 
    name: "Transportadoras", 
    icon: <Truck className="w-8 h-8" />, 
    path: "/transportadoras",
    color: "from-orange-500 to-amber-700",
    bgColor: "bg-orange-50",
    description: "Gestión de transporte",
    statsKey: "transportadoras"
  },
  { 
    name: "CRT", 
    icon: <FileText className="w-8 h-8" />, 
    path: "/crt",
    color: "from-red-500 to-rose-700",
    bgColor: "bg-red-50",
    description: "Cartas de Porte y Documentos",
    statsKey: "crt"
  },
  { 
    name: "MIC", 
    icon: <ArrowLeftRight className="w-8 h-8" />, 
    path: "/mic",
    color: "from-indigo-500 to-blue-700",
    bgColor: "bg-indigo-50",
    description: "Manifiestos de Carga",
    statsKey: "mic"
  },
  { 
    name: "Monedas", 
    icon: <Coins className="w-8 h-8" />, 
    path: "/monedas",
    color: "from-yellow-500 to-amber-600",
    bgColor: "bg-yellow-50",
    description: "Tipos de moneda",
    statsKey: "monedas"
  },
  { 
    name: "Honorarios", 
    icon: <DollarSign className="w-8 h-8" />, 
    path: "/honorarios",
    color: "from-emerald-500 to-green-700",
    bgColor: "bg-emerald-50",
    description: "Gestión de pagos",
    statsKey: "honorarios"
  },
  { 
    name: "Movimientos", 
    icon: <Activity className="w-8 h-8" />, 
    path: "/movimientos",
    color: "from-pink-500 to-rose-700",
    bgColor: "bg-pink-50",
    description: "Registro de actividad",
    statsKey: "movimientos"
  },
  { 
    name: "Reportes", 
    icon: <BarChart3 className="w-8 h-8" />, 
    path: "/reportes",
    color: "from-violet-500 to-purple-700",
    bgColor: "bg-violet-50",
    description: "Análisis y reportes",
    statsKey: "reportes"
  },
  { 
    name: "Parámetros", 
    icon: <Settings className="w-8 h-8" />, 
    path: "/parametros",
    color: "from-gray-500 to-slate-700",
    bgColor: "bg-gray-50",
    description: "Configuración del sistema",
    statsKey: "parametros"
  },
];

// Componente de partículas flotantes
const FloatingParticles = () => {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 20 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 2,
      delay: Math.random() * 2,
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute rounded-full bg-gradient-to-r from-blue-400 to-purple-400 opacity-20"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            animation: `float 6s ease-in-out infinite ${particle.delay}s`,
          }}
        />
      ))}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
      `}</style>
    </div>
  );
};

// Componente de estadísticas
const StatsCard = ({ title, value, icon, trend, color }) => (
  <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 hover:shadow-2xl transition-all duration-500 hover:scale-105">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-xl bg-gradient-to-r ${color}`}>
        {icon}
      </div>
      <div className="text-right">
        <div className="flex items-center space-x-1 text-green-500">
          <TrendingUp className="w-4 h-4" />
          <span className="text-sm font-medium">{trend}</span>
        </div>
      </div>
    </div>
    <div>
      <p className="text-gray-600 text-sm">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  </div>
);

// Componente de módulo mejorado
const ModuleCard = ({ module, index, stats }) => {
  const [isHovered, setIsHovered] = useState(false);
  const moduleStats = stats[module.statsKey] || 0;

  return (
    <Link
      to={module.path}
      className="group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 hover:shadow-2xl transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 p-6 h-full overflow-hidden">
        {/* Efecto de brillo */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
        
        {/* Contenido */}
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className={`p-4 rounded-2xl bg-gradient-to-r ${module.color} shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300`}>
              <div className="text-white">
                {module.icon}
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transform group-hover:translate-x-1 transition-all duration-300" />
          </div>
          
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-blue-600 group-hover:to-purple-600 transition-all duration-300">
              {module.name}
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              {module.description}
            </p>
            <div className="flex items-center justify-between pt-2">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${module.bgColor} text-gray-700`}>
                {moduleStats} {module.statsKey === 'honorarios' ? 'registros' : 
                 module.statsKey === 'usuarios' ? 'usuarios' :
                 module.statsKey === 'paises' ? 'países' :
                 module.statsKey === 'ciudades' ? 'ciudades' :
                 module.statsKey === 'remitentes' ? 'empresas' :
                 module.statsKey === 'transportadoras' ? 'activas' :
                 module.statsKey === 'monedas' ? 'monedas' :
                 module.statsKey === 'crt' ? 'documentos' :
                 module.statsKey === 'mic' ? 'manifiestos' :
                 'registros'}
              </span>
              {isHovered && (
                <div className="flex items-center space-x-1 text-blue-500">
                  <Sparkles className="w-4 h-4" />
                  <span className="text-xs font-medium">Acceder</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

function Dashboard() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [stats, setStats] = useState({
    usuarios: 0,
    paises: 0,
    ciudades: 0,
    remitentes: 0,
    transportadoras: 0,
    crt: 0,
    mic: 0,
    monedas: 0,
    honorarios: 0,
    movimientos: 0,
    reportes: 0,
    parametros: 0,
    totalHonorarios: 0,
    usuariosConectados: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    setIsLoading(true);
    try {
      // Llamadas paralelas a todas las APIs
      const [
        paisesRes,
        ciudadesRes,
        remitentesRes,
        transportadorasRes,
        monedasRes,
        honorariosRes,
        crtsRes
      ] = await Promise.all([
        api.get('/paises/').catch(() => ({ data: [] })),
        api.get('/ciudades/').catch(() => ({ data: [] })),
        api.get('/remitentes/').catch(() => ({ data: { items: [] } })),
        api.get('/transportadoras/').catch(() => ({ data: { items: [] } })),
        api.get('/monedas/').catch(() => ({ data: [] })),
        api.get('/honorarios/').catch(() => ({ data: [] })),
        api.get('/crts/').catch(() => ({ data: [] }))
      ]);

      // Calcular estadísticas reales
      const remitentesData = Array.isArray(remitentesRes.data.items) ? remitentesRes.data.items : [];
      const transportadorasData = Array.isArray(transportadorasRes.data.items) ? transportadorasRes.data.items : transportadorasRes.data || [];
      const honorariosData = Array.isArray(honorariosRes.data) ? honorariosRes.data : [];
      const crtsData = Array.isArray(crtsRes.data) ? crtsRes.data : [];

      // Calcular total de honorarios
      const totalHonorarios = honorariosData.reduce((acc, h) => acc + (parseFloat(h.monto) || 0), 0);

      setStats({
        paises: paisesRes.data.length || 0,
        ciudades: ciudadesRes.data.length || 0,
        remitentes: remitentesData.length,
        transportadoras: transportadorasData.length,
        monedas: monedasRes.data.length || 0,
        honorarios: honorariosData.length,
        crt: crtsData.length,
        usuarios: 0, // No tienes endpoint de usuarios aún
        mic: 0, // No tienes endpoint de MIC aún
        movimientos: 0, // No tienes endpoint de movimientos aún
        reportes: 0, // No tienes endpoint de reportes aún
        parametros: 0, // No tienes endpoint de parámetros aún
        totalHonorarios: totalHonorarios,
        usuariosConectados: 1 // Usuario actual conectado
      });
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 relative overflow-hidden">
      {/* Partículas flotantes */}
      <FloatingParticles />
      
      {/* Fondo con patrón */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%236366f1' fill-opacity='0.4'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>
      
      <div className="container mx-auto px-6 py-8 relative z-10">
        {/* Header con animación */}
        <div className="text-center mb-12 space-y-6">
          <div className="inline-flex items-center space-x-3 bg-white/60 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg border border-white/20">
            <Clock className="w-5 h-5 text-indigo-600" />
            <span className="text-sm font-medium text-gray-700">
              {currentTime.toLocaleString()}
            </span>
          </div>
          
          <div className="space-y-4">
            <h1 className="text-6xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 bg-clip-text text-transparent animate-pulse">
              Gestion de Transportes
            </h1>
            <div className="flex items-center justify-center space-x-2">
              <Star className="w-6 h-6 text-yellow-500 animate-spin" />
              <h2 className="text-2xl font-bold text-gray-800">
                Sistema de Gestión de Transportadoras
              </h2>
              <Star className="w-6 h-6 text-yellow-500 animate-spin" />
            </div>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Plataforma integral para la gestión completa de operaciones de transporte, 
              documentación y logística empresarial.
            </p>
          </div>
        </div>

        {/* Estadísticas rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <StatsCard 
            title="Total CRT + MIC"
            value={isLoading ? "..." : (stats.crt + stats.mic).toLocaleString()}
            icon={<FileText className="w-6 h-6 text-white" />}
            trend="+0%"
            color="from-blue-500 to-blue-700"
          />
          <StatsCard 
            title="Transportadoras Activas"
            value={isLoading ? "..." : stats.transportadoras.toString()}
            icon={<Truck className="w-6 h-6 text-white" />}
            trend="+0%"
            color="from-green-500 to-emerald-700"
          />
          <StatsCard 
            title="Total Honorarios"
            value={isLoading ? "..." : `${stats.totalHonorarios.toLocaleString()}`}
            icon={<DollarSign className="w-6 h-6 text-white" />}
            trend="+0%"
            color="from-yellow-500 to-amber-600"
          />
          <StatsCard 
            title="Usuarios Conectados"
            value={isLoading ? "..." : stats.usuariosConectados.toString()}
            icon={<Users className="w-6 h-6 text-white" />}
            trend="+0%"
            color="from-purple-500 to-violet-700"
          />
        </div>

        {/* Módulos principales */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-8">
            <div className="w-1 h-8 bg-gradient-to-b from-indigo-500 to-purple-600 rounded-full" />
            <h3 className="text-2xl font-bold text-gray-900">Módulos del Sistema</h3>
            <Sparkles className="w-6 h-6 text-yellow-500 animate-pulse" />
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {modules.map((module, index) => (
              <div
                key={module.name}
                style={{ 
                  animationDelay: `${index * 100}ms`,
                  animation: 'slideInUp 0.6s ease-out forwards'
                }}
                className="opacity-0"
              >
                <ModuleCard module={module} index={index} stats={stats} />
              </div>
            ))}
          </div>
        </div>

        {/* Footer con efecto */}
        <div className="text-center pt-12 pb-6">
          <div className="inline-flex items-center space-x-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-8 py-4 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105">
            <Sparkles className="w-5 h-5 animate-spin" />
            <span className="font-semibold">¡Bienvenido al futuro del transporte!</span>
            <Sparkles className="w-5 h-5 animate-spin" />
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}

export default Dashboard;