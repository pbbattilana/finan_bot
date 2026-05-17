import { useState, useEffect } from 'react';
import { getResumenMensual, getPorTipo, getPorEntidad, getTopGastos } from '../services/api';
import SummaryCard from '../components/SummaryCard';
import ChartCard from '../components/ChartCard';
import MovementsTable from '../components/MovementsTable';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis,
} from 'recharts';

const COLORS = ['#6366f1', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

function formatMoney(n) {
  if (n === null || n === undefined) return '—';
  return `Gs. ${Number(n).toLocaleString('es-PY', { minimumFractionDigits: 0 })}`;
}

const MONTHS = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

const now = new Date();

export default function ResumenMensual() {
  const [anio, setAnio] = useState(now.getFullYear());
  const [mes, setMes] = useState(now.getMonth() + 1);
  const [resumen, setResumen] = useState(null);
  const [tipos, setTipos] = useState([]);
  const [entidades, setEntidades] = useState([]);
  const [topGastos, setTopGastos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem('finan_user');
    if (!stored) {
      setError('Configurá un usuario primero');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    const dateStr = `${anio}-${String(mes).padStart(2, '0')}-01`;
    Promise.all([
      getResumenMensual(anio, mes),
      getPorTipo({ fecha_desde: dateStr, fecha_hasta: dateStr }),
      getPorEntidad({ fecha_desde: dateStr, fecha_hasta: dateStr }),
      getTopGastos({ fecha_desde: dateStr, fecha_hasta: dateStr, limit: 10 }),
    ])
      .then(([r, t, e, g]) => {
        setResumen(r);
        setTipos(t || []);
        setEntidades(e || []);
        setTopGastos(g || []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [anio, mes]);

  if (error) {
    return (
      <div className="py-16 text-center">
        <p className="text-red-500 font-medium">{error}</p>
        {error.includes('Configurá') && (
          <p className="mt-2 text-sm text-gray-400">
            Andá a /configuracion para seleccionar tu usuario.
          </p>
        )}
      </div>
    );
  }

  const pieData = tipos.filter((t) => t.total > 0).map((t) => ({
    name: t.tipo_nombre || 'Sin tipo',
    value: t.total,
  }));

  const entData = entidades.slice(0, 10).map((e) => ({
    name: (e.entidad_nombre || e.beneficiario || '—').slice(0, 14),
    total: e.total,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-gray-800">Resumen Mensual</h1>
        <div className="flex gap-2">
          <select
            value={mes}
            onChange={(e) => setMes(parseInt(e.target.value))}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm"
          >
            {MONTHS.map((name, idx) => (
              <option key={idx + 1} value={idx + 1}>{name}</option>
            ))}
          </select>
          <input
            type="number"
            value={anio}
            onChange={(e) => setAnio(parseInt(e.target.value))}
            className="w-20 rounded-lg border border-gray-200 px-3 py-1.5 text-sm"
            min={2020}
            max={2030}
          />
        </div>
      </div>

      {loading ? (
        <LoadingState message="Cargando resumen…" />
      ) : (
        <>
          {/* KPIs */}
          {resumen && (
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <SummaryCard title="Ingresos" value={formatMoney(resumen.total_ingresos)} color="text-green-600" icon="📈" />
              <SummaryCard title="Egresos" value={formatMoney(resumen.total_egresos)} color="text-red-600" icon="📉" />
              <SummaryCard
                title="Balance"
                value={formatMoney(resumen.balance)}
                color={(resumen.balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}
                icon="⚖️"
              />
              <SummaryCard title="Movimientos" value={resumen.cantidad_movimientos} color="text-indigo-600" icon="📦" />
            </div>
          )}

          {pieData.length === 0 && entData.length === 0 && topGastos.length === 0 ? (
            <EmptyState message="No hay movimientos en este período" />
          ) : (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {/* Distribución por tipo */}
              {pieData.length > 0 && (
                <ChartCard title="Distribución por tipo">
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        dataKey="value"
                        label={({ name }) => name}
                      >
                        {pieData.map((_, idx) => (
                          <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v) => formatMoney(v)} />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartCard>
              )}

              {/* Distribución por entidad */}
              {entData.length > 0 && (
                <ChartCard title="Distribución por entidad">
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={entData} layout="vertical">
                      <XAxis type="number" tick={{ fontSize: 11 }} />
                      <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={90} />
                      <Tooltip formatter={(v) => formatMoney(v)} />
                      <Bar dataKey="total" radius={[0, 6, 6, 0]} fill="#6366f1" />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              )}

              {/* Top 10 gastos */}
              {topGastos.length > 0 && (
                <ChartCard title="Top 10 gastos del mes">
                  <MovementsTable movements={topGastos} compact />
                </ChartCard>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
