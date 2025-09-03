import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

// Datos de ejemplo para los gráficos
const monthlyData = [
  { month: 'Ene', crts: 12, mics: 8, honorarios: 4500 },
  { month: 'Feb', crts: 19, mics: 12, honorarios: 5200 },
  { month: 'Mar', crts: 15, mics: 10, honorarios: 4800 },
  { month: 'Abr', crts: 22, mics: 15, honorarios: 6100 },
  { month: 'May', crts: 18, mics: 13, honorarios: 5500 },
  { month: 'Jun', crts: 25, mics: 18, honorarios: 7200 }
];

const entityData = [
  { name: 'Remitentes', value: 45, color: '#8884d8' },
  { name: 'Transportadoras', value: 32, color: '#82ca9d' },
  { name: 'Países', value: 12, color: '#ffc658' },
  { name: 'Ciudades', value: 28, color: '#ff7c7c' }
];

const statusData = [
  { name: 'Completados', value: 68, color: '#10b981' },
  { name: 'En Progreso', value: 22, color: '#f59e0b' },
  { name: 'Pendientes', value: 10, color: '#ef4444' }
];


export const MonthlyChart = ({ data = monthlyData }) => (
  <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      Actividad Mensual
    </h3>
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="month"
          stroke="#6b7280"
          fontSize={12}
        />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1f2937',
            border: 'none',
            borderRadius: '8px',
            color: '#f9fafb'
          }}
        />
        <Legend />
        <Area
          type="monotone"
          dataKey="crts"
          stackId="1"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.6}
          name="CRTs"
        />
        <Area
          type="monotone"
          dataKey="mics"
          stackId="2"
          stroke="#10b981"
          fill="#10b981"
          fillOpacity={0.6}
          name="MICs"
        />
      </AreaChart>
    </ResponsiveContainer>
  </div>
);

export const EntitiesChart = ({ data = entityData }) => (
  <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      Distribución de Entidades
    </h3>
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="name"
          stroke="#6b7280"
          fontSize={12}
        />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1f2937',
            border: 'none',
            borderRadius: '8px',
            color: '#f9fafb'
          }}
        />
        <Bar dataKey="value" fill="#8884d8" radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  </div>
);

export const StatusPieChart = ({ data = statusData }) => (
  <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      Estado de Procesos
    </h3>
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: '#1f2937',
            border: 'none',
            borderRadius: '8px',
            color: '#f9fafb'
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

export const RevenueChart = ({ data = monthlyData }) => (
  <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      Tendencia de Honorarios
    </h3>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="month"
          stroke="#6b7280"
          fontSize={12}
        />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1f2937',
            border: 'none',
            borderRadius: '8px',
            color: '#f9fafb'
          }}
          formatter={(value) => [`$${value.toLocaleString()}`, 'Honorarios']}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="honorarios"
          stroke="#f59e0b"
          strokeWidth={3}
          dot={{ fill: '#f59e0b', strokeWidth: 2, r: 6 }}
          activeDot={{ r: 8, stroke: '#f59e0b', strokeWidth: 2 }}
          name="Honorarios"
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

// Componente principal que combina todos los gráficos
export const DashboardCharts = () => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
    <MonthlyChart />
    <EntitiesChart />
    <StatusPieChart />
    <RevenueChart />
  </div>
);

export default DashboardCharts;