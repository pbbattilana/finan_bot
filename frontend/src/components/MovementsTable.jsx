export default function MovementsTable({ movements, loading, compact }) {
  if (loading) {
    return (
      <div className="py-8 text-center text-gray-400 animate-pulse">
        Cargando movimientos…
      </div>
    );
  }

  if (!movements || movements.length === 0) {
    return (
      <div className="py-8 text-center text-gray-400">
        No hay movimientos
      </div>
    );
  }

  const format = (n) => {
    if (n === null || n === undefined) return '—';
    return `Gs. ${Number(n).toLocaleString('es-PY', { minimumFractionDigits: 0 })}`;
  };

  const dateShort = (d) => {
    if (!d) return '—';
    const parts = d.split('-');
    if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0].slice(2)}`;
    return d;
  };

  if (compact) {
    return (
      <div className="divide-y divide-gray-100">
        {movements.map((m) => (
          <div key={m.id} className="flex items-center justify-between py-2.5">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-lg">{m.es_ingreso ? '📈' : '📉'}</span>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">
                  {m.beneficiario || m.tipo_nombre || '—'}
                </p>
                <p className="text-xs text-gray-400">{dateShort(m.fecha)}</p>
              </div>
            </div>
            <span className={`text-sm font-semibold whitespace-nowrap ml-3 ${m.es_ingreso ? 'text-green-600' : 'text-red-600'}`}>
              {m.es_ingreso ? '+' : '-'}{format(m.monto)}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
            <th className="pb-2 pr-2">Fecha</th>
            <th className="pb-2 pr-2">Tipo</th>
            <th className="pb-2 pr-2">Beneficiario</th>
            <th className="pb-2 pr-2 text-right">Monto</th>
            <th className="pb-2 pr-2">Comprobante</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {movements.map((m) => (
            <tr key={m.id} className="hover:bg-gray-50">
              <td className="py-2.5 pr-2 whitespace-nowrap text-gray-600">
                {dateShort(m.fecha)} {m.hora || ''}
              </td>
              <td className="py-2.5 pr-2 whitespace-nowrap">
                <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${
                  m.es_ingreso
                    ? 'bg-green-50 text-green-700'
                    : 'bg-red-50 text-red-700'
                }`}>
                  {m.es_ingreso ? '📈' : '📉'} {m.tipo_nombre || '—'}
                </span>
              </td>
              <td className="py-2.5 pr-2 text-gray-700 max-w-[200px] truncate">
                {m.beneficiario || m.entidad_nombre || '—'}
              </td>
              <td className={`py-2.5 pr-2 text-right font-semibold whitespace-nowrap ${
                m.es_ingreso ? 'text-green-600' : 'text-red-600'
              }`}>
                {m.es_ingreso ? '+' : '-'}{format(m.monto)}
              </td>
              <td className="py-2.5 text-gray-400 text-xs">
                {m.nro_comprobante || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
