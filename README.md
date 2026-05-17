# Finan Bot

Bot de Telegram que recibe fotos de comprobantes de pago, ejecuta OCR, extrae datos financieros y guarda los movimientos en PostgreSQL asociados al usuario de Telegram.

Incluye:
- API HTTP REST
- **Frontend web** con Vite + React + TailwindCSS + Recharts
- Comandos de Telegram para consulta rápida

## Estructura del proyecto

```
├── app/                          # Backend Python
│   ├── receiver_downloader.py    # Punto de entrada: bot + API HTTP
│   ├── bot_handler.py            # Flujo OCR: preprocesa, extrae, parsea, guarda
│   ├── bd_sqlalchemy.py          # Modelos SQLAlchemy y persistencia
│   ├── api.py                    # Endpoints HTTP REST (Flask)
│   ├── migration.sql             # Migración para soporte de usuarios
│   ├── ocr_preprocessor.py       # Preprocesamiento de imagen (OpenCV)
│   ├── ocr_easyocr.py            # OCR con EasyOCR
│   ├── ocr_tesseract.py          # OCR alternativo con Tesseract
│   ├── regex.py                  # Expresiones regulares para extraer campos
│   ├── parser/                   # Parsers especializados (Ueno)
│   └── requirements.txt          # Dependencias Python
├── frontend/                     # Frontend React
│   ├── src/
│   │   ├── services/api.js       # Consumo de API centralizado
│   │   ├── components/           # Componentes reutilizables
│   │   │   ├── Layout.jsx        # Sidebar + navbar responsive
│   │   │   ├── SummaryCard.jsx   # Card para KPIs
│   │   │   ├── ChartCard.jsx     # Card contenedora de gráficos
│   │   │   ├── MovementsTable.jsx
│   │   │   ├── UserSelector.jsx  # Selector de usuario (sin auth)
│   │   │   ├── DateRangeFilter.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   └── LoadingState.jsx
│   │   └── pages/
│   │       ├── Dashboard.jsx     # KPIs + gráficos + últimos movs
│   │       ├── Movimientos.jsx   # Tabla con filtros
│   │       ├── ResumenMensual.jsx # Selector mes/año + distribución
│   │       ├── Entidades.jsx     # Ranking de entidades
│   │       ├── Tipos.jsx         # Distribución por tipo
│   │       └── Configuracion.jsx # Selección de usuario
│   ├── Dockerfile                # Multi-stage build + Nginx
│   ├── nginx.conf                # Proxy reverso a la API
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml            # Bot + DB + Frontend
├── Dockerfile                    # Bot image
└── README.md
```

## Requisitos

- Docker y Docker Compose
- Token de Bot de Telegram (de [@BotFather](https://t.me/BotFather))

## Configuración inicial

Crear archivo `.env` en la raíz:

```env
TELEGRAM_TOKEN=tu_token_aqui
POSTGRES_USER=finanuser
POSTGRES_PASSWORD=finanpass
POSTGRES_DB=finandb
POSTGRES_HOST=db
API_PORT=5000
```

## Cómo levantar todo (producción)

```bash
docker compose up --build
```

Esto levanta:
- **PostgreSQL** en puerto `5432`
- **Bot de Telegram** (interno)
- **API HTTP** en `http://localhost:5000`
- **Frontend** en `http://localhost:3000`

## Cómo levantar frontend en desarrollo

```bash
cd frontend
cp .env.example .env      # Editar VITE_API_BASE_URL si es necesario
npm install
npm run dev
```

El frontend corre en `http://localhost:5173` con proxy automático a la API en `:5000`.

### Variable de entorno

```env
# Con proxy de Vite (recomendado, no requiere CORS):
VITE_API_BASE_URL=/api
# O directo (requiere CORS en backend):
# VITE_API_BASE_URL=http://localhost:5000
```

Si usás el proxy de Vite, el `vite.config.js` ya tiene configuración para redirigir `/api` → `http://localhost:5000`.
Si el backend corre en otro puerto o dominio, ajustar el target en `vite.config.js` y/o `VITE_API_BASE_URL`.

## Migración de base de datos

Si ya tenés datos existentes, ejecutá el script de migración:

```bash
docker exec -i finan_postgres psql -U finanuser -d finandb < app/migration.sql
```

## Pantallas del frontend

### 1. Dashboard (`/dashboard`)
- KPIs: ingresos, egresos, balance, cantidad de movimientos del mes
- Gráfico de barras: ingresos vs egresos
- Gráfico de dona: gastos por tipo
- Gráfico de barras: gastos por entidad
- Últimos movimientos

### 2. Movimientos (`/movimientos`)
- Tabla completa con paginación
- Filtros: fecha desde/hasta, tipo, ingreso/egreso, búsqueda por texto
- Indicador visual con colores

### 3. Resumen mensual (`/resumen-mensual`)
- Selector de año y mes
- KPIs del período
- Distribución por tipo (dona)
- Distribución por entidad (barras)
- Top 10 gastos del mes

### 4. Entidades (`/entidades`)
- Ranking de entidades/beneficiarios
- Total gastado, cantidad de movimientos, última fecha
- Filtro por rango de fechas

### 5. Tipos (`/tipos`)
- Total de egresos del período
- Gráfico de dona con porcentajes
- Tabla detalle: tipo, total, cantidad, %

### 6. Configuración (`/configuracion`)
- Seleccionar usuario de Telegram de una lista
- Ingresar manualmente `telegram_user_id` o `username`
- Guarda en localStorage
- Botón para limpiar usuario activo

> **Sin autenticación real:** El usuario se selecciona manualmente desde el frontend y se guarda en localStorage. Cada pantalla filtra datos por ese usuario.

## Comandos de Telegram

| Comando | Descripción |
|---------|-------------|
| `/mis_movimientos` | Últimos 10 movimientos del usuario |
| `/resumen_mes` | Resumen del mes actual |
| `/gastos_por_tipo` | Gastos agrupados por tipo |
| `/gastos_por_entidad` | Top 10 beneficiarios/entidades |

## Endpoints HTTP API

| Endpoint | Descripción |
|----------|-------------|
| `GET /health` | Health check |
| `GET /usuarios` | Lista todos los usuarios registrados |
| `GET /dashboard` | Dashboard completo (resumen + gráficos + últimos movs) |
| `GET /movimientos` | Lista movimientos (filtros: fecha, tipo, texto, ingreso/egreso, paginación) |
| `GET /movimientos/resumen-mensual` | Resumen por año/mes |
| `GET /movimientos/por-tipo` | Agrupación por tipo |
| `GET /movimientos/por-entidad` | Agrupación por entidad |
| `GET /movimientos/egresos-vs-ingresos` | Comparación ingresos/egresos |
| `GET /movimientos/top-gastos` | Mayores gastos |
| `GET /entidades/ranking` | Ranking de entidades |
| `GET /tipos/resumen` | Resumen por tipo con porcentajes |

Todos los endpoints aceptan `?telegram_user_id=` o `?username=` para filtrar por usuario.

Ejemplos:

```bash
curl "http://localhost:5000/movimientos?telegram_user_id=123456&limit=5"
curl "http://localhost:5000/dashboard?username=pepe"
curl "http://localhost:5000/movimientos/resumen-mensual?telegram_user_id=123456&anio=2024&mes=3"
```

## Pruebas manuales

### 1. Enviar comprobante desde Telegram
- Enviá una foto de un comprobante al bot.
- El bot responde con el OCR y confirma el registro.

### 2. Verificar usuario creado
```bash
docker exec -it finan_postgres psql -U finanuser -d finandb -c "SELECT id, telegram_user_id, telegram_username, first_name FROM usuarios;"
```

### 3. Probar frontend
1. Abrí `http://localhost:3000` (o `http://localhost:5173` en dev)
2. Andá a `/configuracion` y seleccioná tu usuario
3. Explorá el Dashboard, Movimientos, Resumen, Entidades y Tipos

### 4. Probar comandos de Telegram
```
/mis_movimientos
/resumen_mes
/gastos_por_tipo
/gastos_por_entidad
```

## Construir para producción

```bash
# Backend (Docker)
docker compose up --build

# Frontend (standalone)
cd frontend
npm run build
# El output queda en frontend/dist/, servible con Nginx o similar
```

## Stack

**Backend:** Python 3.11, Flask, SQLAlchemy 2.0, EasyOCR, OpenCV, psycopg2

**Frontend:** Vite, React 18, React Router 6, TailwindCSS 3, Recharts 2, Axios

**Infra:** Docker Compose, PostgreSQL 15, Nginx
