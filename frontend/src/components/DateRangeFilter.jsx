export default function DateRangeFilter({ fechaDesde, fechaHasta, onChange }) {
  return (
    <div className="flex flex-wrap items-end gap-3">
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Desde</label>
        <input
          type="date"
          value={fechaDesde}
          onChange={(e) => onChange({ fecha_desde: e.target.value, fecha_hasta })}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none"
        />
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Hasta</label>
        <input
          type="date"
          value={fechaHasta}
          onChange={(e) => onChange({ fecha_desde: fechaDesde, fecha_hasta: e.target.value })}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none"
        />
      </div>
      {(fechaDesde || fechaHasta) && (
        <button
          onClick={() => onChange({ fecha_desde: '', fecha_hasta: '' })}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-50"
        >
          Limpiar
        </button>
      )}
    </div>
  );
}
