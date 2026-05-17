import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

function getUserParams() {
  const stored = localStorage.getItem('finan_user');
  if (!stored) return {};
  const user = JSON.parse(stored);
  if (user.telegram_user_id) return { telegram_user_id: user.telegram_user_id };
  if (user.username) return { username: user.username };
  return {};
}

function handleError(error) {
  if (error.response) {
    const msg = error.response.data?.error || 'Error del servidor';
    throw new Error(msg);
  }
  if (error.request) throw new Error('No se pudo conectar con el servidor');
  throw error;
}

export async function getUsuarios() {
  try {
    const { data } = await api.get('/usuarios');
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getDashboard() {
  try {
    const params = getUserParams();
    if (!Object.keys(params).length) throw new Error('Configurá un usuario primero');
    const { data } = await api.get('/dashboard', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getMovimientos({
  fecha_desde,
  fecha_hasta,
  tipo_id,
  beneficiario,
  busqueda,
  es_ingreso,
  limit = 50,
  offset = 0,
} = {}) {
  try {
    const params = { ...getUserParams(), limit, offset };
    if (fecha_desde) params.fecha_desde = fecha_desde;
    if (fecha_hasta) params.fecha_hasta = fecha_hasta;
    if (tipo_id !== undefined && tipo_id !== '') params.tipo_id = tipo_id;
    if (beneficiario) params.beneficiario = beneficiario;
    if (busqueda) params.busqueda = busqueda;
    if (es_ingreso !== undefined && es_ingreso !== '') params.es_ingreso = es_ingreso;
    const { data } = await api.get('/movimientos', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getResumenMensual(anio, mes) {
  try {
    const params = { ...getUserParams(), anio, mes };
    const { data } = await api.get('/movimientos/resumen-mensual', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getPorTipo({ fecha_desde, fecha_hasta } = {}) {
  try {
    const params = getUserParams();
    if (fecha_desde) params.fecha_desde = fecha_desde;
    if (fecha_hasta) params.fecha_hasta = fecha_hasta;
    const { data } = await api.get('/movimientos/por-tipo', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getPorEntidad({ fecha_desde, fecha_hasta } = {}) {
  try {
    const params = getUserParams();
    if (fecha_desde) params.fecha_desde = fecha_desde;
    if (fecha_hasta) params.fecha_hasta = fecha_hasta;
    const { data } = await api.get('/movimientos/por-entidad', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getEgresosVsIngresos({ fecha_desde, fecha_hasta } = {}) {
  try {
    const params = getUserParams();
    if (fecha_desde) params.fecha_desde = fecha_desde;
    if (fecha_hasta) params.fecha_hasta = fecha_hasta;
    const { data } = await api.get('/movimientos/egresos-vs-ingresos', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getTopGastos({ fecha_desde, fecha_hasta, limit = 10 } = {}) {
  try {
    const params = { ...getUserParams(), limit };
    if (fecha_desde) params.fecha_desde = fecha_desde;
    if (fecha_hasta) params.fecha_hasta = fecha_hasta;
    const { data } = await api.get('/movimientos/top-gastos', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getEntidadesRanking({ fecha_desde, fecha_hasta, limit = 20 } = {}) {
  try {
    const params = { ...getUserParams(), limit };
    if (fecha_desde) params.fecha_desde = fecha_desde;
    if (fecha_hasta) params.fecha_hasta = fecha_hasta;
    const { data } = await api.get('/entidades/ranking', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}

export async function getTiposResumen({ fecha_desde, fecha_hasta } = {}) {
  try {
    const params = getUserParams();
    if (fecha_desde) params.fecha_desde = fecha_desde;
    if (fecha_hasta) params.fecha_hasta = fecha_hasta;
    const { data } = await api.get('/tipos/resumen', { params });
    return data;
  } catch (e) {
    handleError(e);
  }
}
