export default function EmptyState({ message = 'Sin datos para mostrar' }) {
  return (
    <div className="flex items-center justify-center py-16">
      <p className="text-gray-400 text-lg">{message}</p>
    </div>
  );
}
