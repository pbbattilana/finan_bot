import { useState, useEffect, useCallback } from 'react';
import { getTiposResumen } from '../services/api';
import DateRangeFilter from '../components/DateRangeFilter';
import ChartCard from '../components/ChartCard';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
  BarChart, Bar, XAxis, YAxis,
} from 'recharts';

const COLORS = ['#6366f1', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

function formatMoney(n) {
  if (n === null || n === undefined) return '—';
  return `Gs. ${Number(n).toLocaleString('es-PY', { minimumFractionDigits: 0 })}`;
}

export default function Tipos() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ fecha_desde: '', fecha_hasta: '' });

  const fetchData = useCallback(async () => {
    const stored = localStorage.getItem('finan_user');
    if (!stored) {
      setError('Configurá un usuario primero');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await getTiposResumen(filters);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const pieData = (data?.tipos || []).map((t) => ({
    name: t.tipo_nombre || 'Sin tipo',
    value: t.total,
  }));

  const barData = (data?.tipos || []).map((t) => ({
    name: t.tipo_nombre || 'Sin tipo',
    total: t.total,
    cantidad: t.cantidad,
  }));

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-gray-800">Tipos de Movimiento</h1>
      </div>

      <DateRangeFilter
        fechaDesde={filters.fecha_desde}
        fechaHasta={filters.fecha_hasta}
        onChange={(f) => setFilters(f)}
      />

      {error && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}

      {loading ? (
        <LoadingState message="Cargando…" />
      ) : !data ? (
        <EmptyState message="No hay datos" />
      ) : (
        <>
          <div className="rounded-xl bg-white p-5 shadow-sm border border-gray-100">
            <p className="text-sm text-gray-500">
              Total de egresos en el período:{' '}
              <span className="font-bold text-red-600">{formatMoney(data.total_egresos)}</span>
            </p>
          </div>

          {data.tipos?.length === 0 ? (
            <EmptyState message="No hay egresos en el período seleccionado" />
          ) : (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {/* Donut */}
              <ChartCard title="Distribución por tipo">
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {pieData.map((_, idx) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => formatMoney(v)} />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Tabla */}
              <ChartCard title="Detalle por tipo">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-100 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        <th className="pb-2 pr-2">Tipo</th>
                        <th className="pb-2 pr-2 text-right">Total</th>
                        <th className="pb-2 pr-2 text-right">Cant.</th>
                        <th className="pb-2 text-right">%</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {data.tipos.map((t, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="py-2 pr-2 font-medium text-gray-800">
                            {t.tipo_nombre || 'Sin tipo'}
                          </td>
                          <td className="py-2 pr-2 text-right font-semibold text-red-600">
                            {formatMoney(t.total)}
                          </td>
                          <td className="py-2 pr-2 text-right text-gray-600">
                            {t.cantidad}
                          </td>
                          <td className="py-2 text-right text-gray-400">
                            {t.porcentaje}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ChartCard>
            </div>
          )}
        </>
      )}
    </div>
  );
}
