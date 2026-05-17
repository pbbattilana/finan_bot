import { useState, useEffect } from 'react';
import { getUsuarios } from '../services/api';
import SummaryCard from '../components/SummaryCard';
import EmptyState from '../components/EmptyState';

export default function Configuracion() {
  const [activeUser, setActiveUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [telegramUserId, setTelegramUserId] = useState('');
  const [username, setUsername] = useState('');

  useEffect(() => {
    const stored = localStorage.getItem('finan_user');
    if (stored) setActiveUser(JSON.parse(stored));
    getUsuarios().then(setUsers).catch(() => {});
  }, []);

  function saveManual() {
    const obj = {};
    if (telegramUserId) obj.telegram_user_id = parseInt(telegramUserId, 10);
    if (username) obj.username = username;
    if (!Object.keys(obj).length) return;
    obj.display = obj.username
      ? `@${obj.username}`
      : `ID ${obj.telegram_user_id}`;
    localStorage.setItem('finan_user', JSON.stringify(obj));
    setActiveUser(obj);
    window.location.reload();
  }

  function selectUser(u) {
    const obj = {
      telegram_user_id: u.telegram_user_id,
      username: u.telegram_username,
      display: u.telegram_username
        ? `@${u.telegram_username}`
        : `ID ${u.telegram_user_id}`,
    };
    localStorage.setItem('finan_user', JSON.stringify(obj));
    setActiveUser(obj);
    window.location.reload();
  }

  function clearUser() {
    localStorage.removeItem('finan_user');
    setActiveUser(null);
    window.location.reload();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-800">Configuración</h1>

      <div className="rounded-xl bg-white p-5 shadow-sm border border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          Usuario activo
        </h2>
        {activeUser ? (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-medium text-indigo-700">
                {activeUser.display}
              </p>
              {activeUser.telegram_user_id && (
                <p className="text-xs text-gray-400">
                  ID: {activeUser.telegram_user_id}
                </p>
              )}
            </div>
            <button
              onClick={clearUser}
              className="rounded-lg bg-red-50 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-100"
            >
              Limpiar
            </button>
          </div>
        ) : (
          <p className="text-sm text-gray-400">
            No hay usuario configurado. Seleccioná uno abajo o ingresá manualmente.
          </p>
        )}
      </div>

      <div className="rounded-xl bg-white p-5 shadow-sm border border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          Ingresar manualmente
        </h2>
        <div className="flex flex-wrap gap-3">
          <input
            type="number"
            placeholder="telegram_user_id"
            value={telegramUserId}
            onChange={(e) => setTelegramUserId(e.target.value)}
            className="flex-1 min-w-[200px] rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <input
            type="text"
            placeholder="username (sin @)"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="flex-1 min-w-[200px] rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <button
            onClick={saveManual}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Guardar
          </button>
        </div>
      </div>

      <div className="rounded-xl bg-white p-5 shadow-sm border border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          Usuarios registrados
        </h2>
        {users.length === 0 ? (
          <EmptyState message="No hay usuarios registrados. Enviá un comprobante al bot primero." />
        ) : (
          <div className="divide-y divide-gray-50">
            {users.map((u) => (
              <button
                key={u.id}
                onClick={() => selectUser(u)}
                className={`flex w-full items-center justify-between py-2.5 text-left hover:bg-gray-50 px-2 rounded-lg ${
                  activeUser?.telegram_user_id === u.telegram_user_id
                    ? 'bg-indigo-50'
                    : ''
                }`}
              >
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    {u.telegram_username
                      ? `@${u.telegram_username}`
                      : `ID ${u.telegram_user_id}`}
                  </p>
                  <p className="text-xs text-gray-400">
                    {u.first_name || ''} {u.last_name || ''}
                  </p>
                </div>
                <span className="text-xs text-gray-400">
                  ID: {u.telegram_user_id}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
