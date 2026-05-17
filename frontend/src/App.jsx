import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Movimientos from './pages/Movimientos';
import ResumenMensual from './pages/ResumenMensual';
import Entidades from './pages/Entidades';
import Tipos from './pages/Tipos';
import Configuracion from './pages/Configuracion';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/movimientos" element={<Movimientos />} />
        <Route path="/resumen-mensual" element={<ResumenMensual />} />
        <Route path="/entidades" element={<Entidades />} />
        <Route path="/tipos" element={<Tipos />} />
        <Route path="/configuracion" element={<Configuracion />} />
      </Routes>
    </Layout>
  );
}
