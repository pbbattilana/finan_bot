import { useState, useEffect, useCallback } from 'react';
import { getMovimientos, getPorTipo } from '../services/api';
import MovementsTable from '../components/MovementsTable';
import DateRangeFilter from '../components/DateRangeFilter';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';

export default function Movimientos() {
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    fecha_desde: '',
    fecha_hasta: '',
    tipo_id: '',
    busqueda: '',
    es_ingreso: '',
  });
  const [tipos, setTipos] = useState([]);
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const fetchMovements = useCallback(async () => {
    const stored = localStorage.getItem('finan_user');
    if (!stored) {
      setError('Configurá un usuario primero');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getMovimientos({
        ...filters,
        limit: pageSize,
        offset: page * pageSize,
      });
      setMovements(data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    fetchMovements();
  }, [fetchMovements]);

  useEffect(() => {
    getPorTipo()
      .then((data) => setTipos(data || []))
      .catch(() => {});
  }, []);

  function handleDateChange({ fecha_desde, fecha_hasta }) {
    setFilters((prev) => ({ ...prev, fecha_desde, fecha_hasta }));
    setPage(0);
  }

  function handleFilterChange(key, value) {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(0);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-gray-800">Movimientos</h1>

      {/* Filters */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-gray-100 space-y-3">
        <DateRangeFilter
          fechaDesde={filters.fecha_desde}
          fechaHasta={filters.fecha_hasta}
          onChange={handleDateChange}
        />
        <div className="flex flex-wrap gap-3">
          <select
            value={filters.tipo_id}
            onChange={(e) => handleFilterChange('tipo_id', e.target.value)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none"
          >
            <option value="">Todos los tipos</option>
            {tipos.map((t) => (
              <option key={t.tipo_id} value={t.tipo_id}>
                {t.tipo_nombre || 'Sin nombre'}
              </option>
            ))}
          </select>
          <select
            value={filters.es_ingreso}
            onChange={(e) => handleFilterChange('es_ingreso', e.target.value)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none"
          >
            <option value="">Ingreso/Egreso</option>
            <option value="true">Ingreso</option>
            <option value="false">Egreso</option>
          </select>
          <input
            type="text"
            placeholder="Buscar por texto…"
            value={filters.busqueda}
            onChange={(e) => handleFilterChange('busqueda', e.target.value)}
            className="flex-1 min-w-[200px] rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none"
          />
        </div>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <LoadingState message="Cargando movimientos…" />
        ) : (
          <MovementsTable movements={movements} />
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <button
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
          className="rounded-lg border border-gray-200 px-3 py-1.5 disabled:opacity-40 hover:bg-gray-50"
        >
          ← Anterior
        </button>
        <span>Página {page + 1}</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={movements.length < pageSize}
          className="rounded-lg border border-gray-200 px-3 py-1.5 disabled:opacity-40 hover:bg-gray-50"
        >
          Siguiente →
        </button>
      </div>
    </div>
  );
}
