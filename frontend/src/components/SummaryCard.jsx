export default function SummaryCard({ title, value, subtitle, color = 'text-gray-900', icon }) {
  return (
    <div className="rounded-xl bg-white p-5 shadow-sm border border-gray-100">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{title}</p>
          <p className={`mt-1 text-2xl font-bold ${color}`}>
            {value !== undefined && value !== null ? value : '—'}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-gray-400">{subtitle}</p>
          )}
        </div>
        {icon && <div className="text-2xl text-gray-300">{icon}</div>}
      </div>
    </div>
  );
}
