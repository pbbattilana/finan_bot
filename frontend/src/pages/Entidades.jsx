import { useState, useEffect, useCallback } from 'react';
import { getEntidadesRanking } from '../services/api';
import DateRangeFilter from '../components/DateRangeFilter';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';

function formatMoney(n) {
  if (n === null || n === undefined) return '—';
  return `Gs. ${Number(n).toLocaleString('es-PY', { minimumFractionDigits: 0 })}`;
}

export default function Entidades() {
  const [data, setData] = useState([]);
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
      const result = await getEntidadesRanking(filters);
      setData(result || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-gray-800">Entidades / Comercios</h1>
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
        <LoadingState message="Cargando ranking…" />
      ) : data.length === 0 ? (
        <EmptyState message="No hay entidades registradas en el período seleccionado" />
      ) : (
        <div className="overflow-x-auto rounded-xl bg-white shadow-sm border border-gray-100">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <th className="p-3">#</th>
                <th className="p-3">Entidad / Beneficiario</th>
                <th className="p-3 text-right">Total</th>
                <th className="p-3 text-right">Movimientos</th>
                <th className="p-3 text-right">Última vez</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {data.map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="p-3 text-gray-400 font-mono">{idx + 1}</td>
                  <td className="p-3 font-medium text-gray-800">
                    {item.entidad_nombre || item.beneficiario || '—'}
                  </td>
                  <td className="p-3 text-right font-semibold text-red-600">
                    {formatMoney(item.total)}
                  </td>
                  <td className="p-3 text-right text-gray-600">{item.cantidad}</td>
                  <td className="p-3 text-right text-gray-400 text-xs">
                    {item.ultima_fecha || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
