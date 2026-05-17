import { useState, useEffect } from 'react';
import { getDashboard } from '../services/api';
import SummaryCard from '../components/SummaryCard';
import ChartCard from '../components/ChartCard';
import MovementsTable from '../components/MovementsTable';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';

const COLORS = ['#6366f1', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

function formatMoney(n) {
  if (n === null || n === undefined) return '—';
  return `Gs. ${Number(n).toLocaleString('es-PY', { minimumFractionDigits: 0 })}`;
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem('finan_user');
    if (!stored) {
      setError('Configurá un usuario en /configuracion primero');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getDashboard()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState message="Cargando dashboard…" />;

  if (error) {
    return (
      <div className="py-16 text-center">
        <p className="text-red-500 font-medium">{error}</p>
      </div>
    );
  }

  if (!data) return <EmptyState message="No hay datos" />;

  const { resumen_mensual, por_tipo, por_entidad, egresos_vs_ingresos, ultimos_movimientos } = data;

  const eviData = [
    { name: 'Ingresos', value: egresos_vs_ingresos?.total_ingresos || 0 },
    { name: 'Egresos', value: egresos_vs_ingresos?.total_egresos || 0 },
  ];

  const pieData = (por_tipo || []).filter((t) => t.total > 0).map((t) => ({
    name: t.tipo_nombre || 'Sin tipo',
    value: t.total,
  }));

  const entData = (por_entidad || []).slice(0, 8).map((e) => ({
    name: (e.entidad_nombre || e.beneficiario || '—').slice(0, 12),
    total: e.total,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800">Dashboard</h1>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard
          title="Ingresos"
          value={formatMoney(resumen_mensual?.total_ingresos)}
          color="text-green-600"
          icon="📈"
        />
        <SummaryCard
          title="Egresos"
          value={formatMoney(resumen_mensual?.total_egresos)}
          color="text-red-600"
          icon="📉"
        />
        <SummaryCard
          title="Balance"
          value={formatMoney(resumen_mensual?.balance)}
          color={(resumen_mensual?.balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}
          icon="⚖️"
        />
        <SummaryCard
          title="Movimientos"
          value={resumen_mensual?.cantidad_movimientos}
          color="text-indigo-600"
          icon="📦"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Ingresos vs Egresos */}
        <ChartCard title="Ingresos vs Egresos (mes actual)">
          {eviData[0].value === 0 && eviData[1].value === 0 ? (
            <EmptyState message="Sin datos este mes" />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={eviData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(v) => formatMoney(v)}
                  contentStyle={{ fontSize: 12 }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {eviData.map((_, idx) => (
                    <Cell key={idx} fill={idx === 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* Gastos por tipo */}
        <ChartCard title="Gastos por tipo (mes actual)">
          {pieData.length === 0 ? (
            <EmptyState message="Sin datos este mes" />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  dataKey="value"
                >
                  {pieData.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => formatMoney(v)} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* Por entidad */}
        <ChartCard title="Gastos por entidad (mes actual)">
          {entData.length === 0 ? (
            <EmptyState message="Sin datos este mes" />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={entData} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={80} />
                <Tooltip formatter={(v) => formatMoney(v)} />
                <Bar dataKey="total" radius={[0, 6, 6, 0]} fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>

      {/* Últimos movimientos */}
      <ChartCard title="Últimos movimientos">
        <MovementsTable movements={ultimos_movimientos} compact />
      </ChartCard>
    </div>
  );
}
