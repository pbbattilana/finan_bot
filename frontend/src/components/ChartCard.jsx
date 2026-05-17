export default function ChartCard({ title, children, className = '' }) {
  return (
    <div className={`rounded-xl bg-white p-5 shadow-sm border border-gray-100 ${className}`}>
      <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>
      {children}
    </div>
  );
}
