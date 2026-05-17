import { NavLink } from 'react-router-dom';
import UserSelector from './UserSelector';

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/movimientos', label: 'Movimientos', icon: '💳' },
  { to: '/resumen-mensual', label: 'Resumen', icon: '📅' },
  { to: '/entidades', label: 'Entidades', icon: '🏢' },
  { to: '/tipos', label: 'Tipos', icon: '📂' },
  { to: '/configuracion', label: 'Config', icon: '⚙️' },
];

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <NavLink to="/dashboard" className="flex items-center gap-2 font-bold text-indigo-700">
            <span className="text-xl">💰</span>
            <span className="hidden sm:inline">Finan Bot</span>
          </NavLink>
          <div className="flex items-center gap-2">
            <UserSelector />
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-6xl flex-1">
        <aside className="hidden md:flex w-56 flex-col gap-1 border-r border-gray-100 p-4">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </aside>

        <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-gray-200 bg-white md:hidden">
          <div className="flex justify-around py-1.5">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex flex-col items-center gap-0.5 px-2 py-1 text-xs font-medium ${
                    isActive ? 'text-indigo-700' : 'text-gray-400'
                  }`
                }
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        </nav>

        <main className="flex-1 p-4 pb-20 md:pb-4">{children}</main>
      </div>
    </div>
  );
}
