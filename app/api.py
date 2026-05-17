import os
from datetime import datetime
from flask import Flask, request, jsonify
from bd_sqlalchemy import Session, Movimiento, Usuario, TipoMovimiento, Entidad
from sqlalchemy import func, desc, extract, or_

app = Flask(__name__)


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


def _get_usuario(telegram_user_id=None, username=None):
    session = Session()
    try:
        if telegram_user_id is not None:
            return session.query(Usuario).filter_by(telegram_user_id=telegram_user_id).first()
        if username is not None:
            return session.query(Usuario).filter_by(telegram_username=username).first()
        return None
    finally:
        session.close()


def _serialize_movimiento(m):
    return {
        "id": m.id,
        "fecha": str(m.fecha) if m.fecha else None,
        "hora": m.hora,
        "monto": float(m.monto) if m.monto else None,
        "nro_comprobante": m.nro_comprobante,
        "cuenta_origen": m.cuenta_origen,
        "beneficiario": m.beneficiario,
        "es_ingreso": m.es_ingreso,
        "tipo_id": m.tipo_id,
        "tipo_nombre": m.tipo.nombre if m.tipo else None,
        "entidad_id": m.entidad_id,
        "entidad_nombre": m.entidad.nombre if m.entidad else None,
        "usuario_id": m.usuario_id,
    }


def _require_usuario():
    telegram_user_id = request.args.get("telegram_user_id", type=int)
    username = request.args.get("username")
    if not telegram_user_id and not username:
        return None, jsonify({"error": "Se requiere telegram_user_id o username"}), 400
    usuario = _get_usuario(telegram_user_id=telegram_user_id, username=username)
    if not usuario:
        return None, jsonify({"error": "Usuario no encontrado"}), 404
    return usuario, None, None


def _apply_date_filters(q, model):
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    if fecha_desde:
        q = q.filter(model.fecha >= fecha_desde)
    if fecha_hasta:
        q = q.filter(model.fecha <= fecha_hasta)
    return q


# ─── Usuarios ─────────────────────────────────────────────────


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    session = Session()
    try:
        usuarios = session.query(Usuario).order_by(Usuario.telegram_username).all()
        return jsonify([
            {
                "id": u.id,
                "telegram_user_id": u.telegram_user_id,
                "telegram_username": u.telegram_username,
                "first_name": u.first_name,
                "last_name": u.last_name,
            }
            for u in usuarios
        ])
    finally:
        session.close()


# ─── Dashboard ────────────────────────────────────────────────


@app.route("/dashboard", methods=["GET"])
def dashboard():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    now = datetime.now()
    anio, mes = now.year, now.month
    month_start = f"{anio:04d}-{mes:02d}-01"

    session = Session()
    try:
        # Resumen mensual
        row = session.query(
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == True), 0).label("total_ingresos"),
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == False), 0).label("total_egresos"),
            func.count(Movimiento.id).label("cantidad_movimientos"),
        ).filter(
            Movimiento.usuario_id == usuario.id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        ).first()
        total_ingresos = float(row.total_ingresos)
        total_egresos = float(row.total_egresos)
        resumen = {
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "balance": total_ingresos - total_egresos,
            "cantidad_movimientos": row.cantidad_movimientos,
        }

        # Por tipo (mes actual)
        tipos = session.query(
            Movimiento.tipo_id,
            TipoMovimiento.nombre.label("tipo_nombre"),
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
        ).join(
            TipoMovimiento, Movimiento.tipo_id == TipoMovimiento.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario.id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        ).group_by(Movimiento.tipo_id, TipoMovimiento.nombre).all()

        # Por entidad (mes actual)
        entidades = session.query(
            Movimiento.entidad_id,
            Entidad.nombre.label("entidad_nombre"),
            Movimiento.beneficiario,
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
        ).join(
            Entidad, Movimiento.entidad_id == Entidad.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario.id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        ).group_by(Movimiento.entidad_id, Entidad.nombre, Movimiento.beneficiario).order_by(desc("total")).all()

        # Últimos movimientos
        ultimos = session.query(Movimiento).filter(
            Movimiento.usuario_id == usuario.id,
        ).order_by(desc(Movimiento.fecha), desc(Movimiento.id)).limit(10).all()

        # Egresos vs Ingresos
        evi = session.query(
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == True), 0).label("total_ingresos"),
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == False), 0).label("total_egresos"),
        ).filter(
            Movimiento.usuario_id == usuario.id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        ).first()

        return jsonify({
            "resumen_mensual": resumen,
            "por_tipo": [
                {
                    "tipo_id": r.tipo_id,
                    "tipo_nombre": r.tipo_nombre,
                    "total": float(r.total) if r.total else 0,
                    "cantidad": r.cantidad,
                }
                for r in tipos
            ],
            "por_entidad": [
                {
                    "entidad_id": r.entidad_id,
                    "entidad_nombre": r.entidad_nombre,
                    "beneficiario": r.beneficiario,
                    "total": float(r.total) if r.total else 0,
                    "cantidad": r.cantidad,
                }
                for r in entidades
            ],
            "egresos_vs_ingresos": {
                "total_ingresos": float(evi.total_ingresos),
                "total_egresos": float(evi.total_egresos),
                "balance": float(evi.total_ingresos) - float(evi.total_egresos),
            },
            "ultimos_movimientos": [_serialize_movimiento(m) for m in ultimos],
        })
    finally:
        session.close()


# ─── Movimientos ──────────────────────────────────────────────


@app.route("/movimientos", methods=["GET"])
def listar_movimientos():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    session = Session()
    try:
        q = session.query(Movimiento).filter(
            Movimiento.usuario_id == usuario.id
        )

        # Filters
        q = _apply_date_filters(q, Movimiento)

        tipo_id = request.args.get("tipo_id", type=int)
        if tipo_id is not None:
            q = q.filter(Movimiento.tipo_id == tipo_id)

        beneficiario = request.args.get("beneficiario")
        if beneficiario:
            q = q.filter(Movimiento.beneficiario.ilike(f"%{beneficiario}%"))

        busqueda = request.args.get("busqueda")
        if busqueda:
            q = q.filter(or_(
                Movimiento.beneficiario.ilike(f"%{busqueda}%"),
                Movimiento.nro_comprobante.ilike(f"%{busqueda}%"),
                Movimiento.cuenta_origen.ilike(f"%{busqueda}%"),
            ))

        es_ingreso = request.args.get("es_ingreso")
        if es_ingreso is not None:
            val = es_ingreso.lower() in ("true", "1", "si", "yes")
            q = q.filter(Movimiento.es_ingreso == val)

        q = q.order_by(desc(Movimiento.fecha), desc(Movimiento.id))

        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        q = q.limit(limit).offset(offset)

        movs = q.all()
        return jsonify([_serialize_movimiento(m) for m in movs])
    finally:
        session.close()


@app.route("/movimientos/top-gastos", methods=["GET"])
def top_gastos():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    session = Session()
    try:
        q = session.query(Movimiento).filter(
            Movimiento.usuario_id == usuario.id,
            Movimiento.es_ingreso == False,
        )
        q = _apply_date_filters(q, Movimiento)

        limit = request.args.get("limit", 10, type=int)
        rows = q.order_by(desc(Movimiento.monto)).limit(limit).all()

        return jsonify([_serialize_movimiento(m) for m in rows])
    finally:
        session.close()


# ─── Resumen mensual ──────────────────────────────────────────


@app.route("/movimientos/resumen-mensual", methods=["GET"])
def resumen_mensual():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    anio = request.args.get("anio", type=int)
    mes = request.args.get("mes", type=int)
    if not anio or not mes:
        return jsonify({"error": "Se requiere anio y mes"}), 400

    session = Session()
    try:
        q = session.query(
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == True), 0).label("total_ingresos"),
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == False), 0).label("total_egresos"),
            func.count(Movimiento.id).label("cantidad_movimientos"),
        ).filter(
            Movimiento.usuario_id == usuario.id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        )
        row = q.first()
        total_ingresos = float(row.total_ingresos)
        total_egresos = float(row.total_egresos)
        return jsonify({
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "balance": total_ingresos - total_egresos,
            "cantidad_movimientos": row.cantidad_movimientos,
        })
    finally:
        session.close()


# ─── Por tipo ─────────────────────────────────────────────────


@app.route("/movimientos/por-tipo", methods=["GET"])
def movimientos_por_tipo():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    session = Session()
    try:
        q = session.query(
            Movimiento.tipo_id,
            TipoMovimiento.nombre.label("tipo_nombre"),
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
        ).join(
            TipoMovimiento, Movimiento.tipo_id == TipoMovimiento.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario.id
        )

        q = _apply_date_filters(q, Movimiento)

        rows = q.group_by(Movimiento.tipo_id, TipoMovimiento.nombre).all()
        return jsonify([
            {
                "tipo_id": r.tipo_id,
                "tipo_nombre": r.tipo_nombre,
                "total": float(r.total) if r.total else 0,
                "cantidad": r.cantidad,
            }
            for r in rows
        ])
    finally:
        session.close()


@app.route("/tipos/resumen", methods=["GET"])
def tipos_resumen():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    session = Session()
    try:
        # Total de egresos para calcular porcentaje
        q_total = session.query(
            func.coalesce(func.sum(Movimiento.monto), 0).label("total_egresos")
        ).filter(
            Movimiento.usuario_id == usuario.id,
            Movimiento.es_ingreso == False,
        )
        q_total = _apply_date_filters(q_total, Movimiento)
        total_egresos = float(q_total.first().total_egresos)

        q = session.query(
            Movimiento.tipo_id,
            TipoMovimiento.nombre.label("tipo_nombre"),
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
        ).join(
            TipoMovimiento, Movimiento.tipo_id == TipoMovimiento.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario.id,
            Movimiento.es_ingreso == False,
        )

        q = _apply_date_filters(q, Movimiento)

        rows = q.group_by(Movimiento.tipo_id, TipoMovimiento.nombre).all()
        result = []
        for r in rows:
            total = float(r.total) if r.total else 0
            pct = round((total / total_egresos * 100), 2) if total_egresos > 0 else 0
            result.append({
                "tipo_id": r.tipo_id,
                "tipo_nombre": r.tipo_nombre,
                "total": total,
                "cantidad": r.cantidad,
                "porcentaje": pct,
            })

        return jsonify({
            "total_egresos": total_egresos,
            "tipos": result,
        })
    finally:
        session.close()


# ─── Por entidad ──────────────────────────────────────────────


@app.route("/movimientos/por-entidad", methods=["GET"])
def movimientos_por_entidad():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    session = Session()
    try:
        q = session.query(
            Movimiento.entidad_id,
            Entidad.nombre.label("entidad_nombre"),
            Movimiento.beneficiario,
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
            func.max(Movimiento.fecha).label("ultima_fecha"),
        ).join(
            Entidad, Movimiento.entidad_id == Entidad.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario.id,
        )

        q = _apply_date_filters(q, Movimiento)

        rows = q.group_by(
            Movimiento.entidad_id, Entidad.nombre, Movimiento.beneficiario
        ).order_by(desc("total")).all()

        return jsonify([
            {
                "entidad_id": r.entidad_id,
                "entidad_nombre": r.entidad_nombre,
                "beneficiario": r.beneficiario,
                "total": float(r.total) if r.total else 0,
                "cantidad": r.cantidad,
                "ultima_fecha": str(r.ultima_fecha) if r.ultima_fecha else None,
            }
            for r in rows
        ])
    finally:
        session.close()


@app.route("/entidades/ranking", methods=["GET"])
def entidades_ranking():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    session = Session()
    try:
        q = session.query(
            Movimiento.entidad_id,
            Entidad.nombre.label("entidad_nombre"),
            Movimiento.beneficiario,
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
            func.max(Movimiento.fecha).label("ultima_fecha"),
        ).join(
            Entidad, Movimiento.entidad_id == Entidad.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario.id,
        )

        q = _apply_date_filters(q, Movimiento)

        limit = request.args.get("limit", 20, type=int)
        rows = q.group_by(
            Movimiento.entidad_id, Entidad.nombre, Movimiento.beneficiario
        ).order_by(desc("total")).limit(limit).all()

        return jsonify([
            {
                "entidad_id": r.entidad_id,
                "entidad_nombre": r.entidad_nombre,
                "beneficiario": r.beneficiario,
                "total": float(r.total) if r.total else 0,
                "cantidad": r.cantidad,
                "ultima_fecha": str(r.ultima_fecha) if r.ultima_fecha else None,
            }
            for r in rows
        ])
    finally:
        session.close()


# ─── Egresos vs Ingresos ──────────────────────────────────────


@app.route("/movimientos/egresos-vs-ingresos", methods=["GET"])
def egresos_vs_ingresos():
    usuario, error, status = _require_usuario()
    if error:
        return error, status

    session = Session()
    try:
        q = session.query(
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == True), 0).label("total_ingresos"),
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == False), 0).label("total_egresos"),
        ).filter(
            Movimiento.usuario_id == usuario.id
        )

        q = _apply_date_filters(q, Movimiento)

        row = q.first()
        total_ingresos = float(row.total_ingresos)
        total_egresos = float(row.total_egresos)
        return jsonify({
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "balance": total_ingresos - total_egresos,
        })
    finally:
        session.close()


# ─── Health ───────────────────────────────────────────────────


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


def run_api():
    port = int(os.getenv("API_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, threaded=True)
