import { useState, useEffect } from 'react';
import { getUsuarios } from '../services/api';

export default function UserSelector() {
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('finan_user');
    if (stored) setUser(JSON.parse(stored));
  }, []);

  useEffect(() => {
    getUsuarios()
      .then(setUsers)
      .catch(() => {});
  }, []);

  function select(u) {
    const obj = {
      telegram_user_id: u.telegram_user_id,
      username: u.telegram_username,
      display: u.telegram_username
        ? `@${u.telegram_username}`
        : `ID ${u.telegram_user_id}`,
    };
    localStorage.setItem('finan_user', JSON.stringify(obj));
    setUser(obj);
    setOpen(false);
    window.location.reload();
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
      >
        <span className="text-base">👤</span>
        <span>{user?.display || 'Sin usuario'}</span>
        <svg className={`h-4 w-4 transition ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="absolute right-0 z-50 mt-1 w-64 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
          <p className="px-3 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Usuarios disponibles
          </p>
          {users.length === 0 && (
            <p className="px-3 py-2 text-sm text-gray-400">No hay usuarios</p>
          )}
          {users.map((u) => (
            <button
              key={u.id}
              onClick={() => select(u)}
              className={`w-full px-3 py-2 text-left text-sm hover:bg-indigo-50 ${
                user?.telegram_user_id === u.telegram_user_id
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-700'
              }`}
            >
              <span className="font-medium">
                {u.telegram_username ? `@${u.telegram_username}` : `ID ${u.telegram_user_id}`}
              </span>
              <span className="ml-2 text-xs text-gray-400">
                {u.first_name || ''} {u.last_name || ''}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
