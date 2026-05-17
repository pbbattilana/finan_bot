import os
from threading import Thread
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
from bot_handler import process_image
from bd_sqlalchemy import Session, Movimiento, Usuario, TipoMovimiento, Entidad
from sqlalchemy import func, desc, extract
from api import run_api
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]


def _get_usuario_id(update):
    user = update.effective_user
    session = Session()
    try:
        u = session.query(Usuario).filter_by(telegram_user_id=user.id).first()
        return u.id if u else None
    finally:
        session.close()


def _format_movimiento(m):
    tipo_nombre = m.tipo.nombre if m.tipo else "—"
    return (
        f"📅 {m.fecha}  {m.hora or '--'}\n"
        f"💰 Gs. {float(m.monto):,.0f}\n"
        f"📋 {tipo_nombre}\n"
        f"🏷️ {m.beneficiario or '—'}\n"
        f"{'📈 Ingreso' if m.es_ingreso else '📉 Egreso'}"
    )


def handle_photo(update: Update, ctx: CallbackContext):
    photo = update.message.photo[-1]
    file = photo.get_file()
    path = f"downloads/{photo.file_id}.jpg"
    file.download(path)
    ctx.bot.send_message(chat_id=update.effective_chat.id,
                         text="Imagen recibida, procesando OCR…")
    process_image(path, update, ctx)


def mis_movimientos(update: Update, ctx: CallbackContext):
    usuario_id = _get_usuario_id(update)
    if not usuario_id:
        update.message.reply_text("❌ No estás registrado. Enviá un comprobante primero.")
        return

    session = Session()
    try:
        movs = session.query(Movimiento).filter(
            Movimiento.usuario_id == usuario_id
        ).order_by(desc(Movimiento.fecha), desc(Movimiento.id)).limit(10).all()

        if not movs:
            update.message.reply_text("📭 No tenés movimientos registrados.")
            return

        lines = ["📋 *Tus últimos 10 movimientos:*\n"]
        for i, m in enumerate(movs, 1):
            lines.append(f"{i}. {_format_movimiento(m)}\n")
        update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        session.close()


def resumen_mes(update: Update, ctx: CallbackContext):
    usuario_id = _get_usuario_id(update)
    if not usuario_id:
        update.message.reply_text("❌ No estás registrado. Enviá un comprobante primero.")
        return

    now = datetime.now()
    anio, mes = now.year, now.month

    session = Session()
    try:
        row = session.query(
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == True), 0).label("ingresos"),
            func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.es_ingreso == False), 0).label("egresos"),
            func.count(Movimiento.id).label("cantidad"),
        ).filter(
            Movimiento.usuario_id == usuario_id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        ).first()

        nombre_mes = now.strftime("%B").capitalize()
        ingresos = float(row.ingresos)
        egresos = float(row.egresos)
        balance = ingresos - egresos

        texto = (
            f"📊 *Resumen de {nombre_mes} {anio}*\n\n"
            f"📈 Ingresos:  Gs. {ingresos:,.0f}\n"
            f"📉 Egresos:   Gs. {egresos:,.0f}\n"
            f"⚖️ Balance:   Gs. {balance:,.0f}\n"
            f"📦 Movimientos: {row.cantidad}"
        )
        update.message.reply_text(texto, parse_mode="Markdown")
    finally:
        session.close()


def gastos_por_tipo(update: Update, ctx: CallbackContext):
    usuario_id = _get_usuario_id(update)
    if not usuario_id:
        update.message.reply_text("❌ No estás registrado. Enviá un comprobante primero.")
        return

    now = datetime.now()
    anio, mes = now.year, now.month

    session = Session()
    try:
        rows = session.query(
            TipoMovimiento.nombre.label("tipo_nombre"),
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
        ).join(
            TipoMovimiento, Movimiento.tipo_id == TipoMovimiento.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario_id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        ).group_by(TipoMovimiento.nombre).order_by(desc("total")).all()

        if not rows:
            update.message.reply_text("📭 No hay movimientos este mes.")
            return

        nombre_mes = now.strftime("%B").capitalize()
        lines = [f"📊 *Gastos por tipo - {nombre_mes} {anio}*\n"]
        for r in rows:
            lines.append(f"• {r.tipo_nombre or 'Sin tipo'}: Gs. {float(r.total):,.0f} ({r.cantidad} mov.)")
        update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        session.close()


def gastos_por_entidad(update: Update, ctx: CallbackContext):
    usuario_id = _get_usuario_id(update)
    if not usuario_id:
        update.message.reply_text("❌ No estás registrado. Enviá un comprobante primero.")
        return

    now = datetime.now()
    anio, mes = now.year, now.month

    session = Session()
    try:
        rows = session.query(
            Entidad.nombre.label("entidad_nombre"),
            Movimiento.beneficiario,
            func.sum(Movimiento.monto).label("total"),
            func.count(Movimiento.id).label("cantidad"),
        ).join(
            Entidad, Movimiento.entidad_id == Entidad.id, isouter=True
        ).filter(
            Movimiento.usuario_id == usuario_id,
            extract("year", Movimiento.fecha) == anio,
            extract("month", Movimiento.fecha) == mes,
        ).group_by(Entidad.nombre, Movimiento.beneficiario).order_by(desc("total")).limit(10).all()

        if not rows:
            update.message.reply_text("📭 No hay movimientos este mes.")
            return

        nombre_mes = now.strftime("%B").capitalize()
        lines = [f"🏢 *Top beneficiarios - {nombre_mes} {anio}*\n"]
        for r in rows:
            nombre = r.entidad_nombre or r.beneficiario or "—"
            lines.append(f"• {nombre}: Gs. {float(r.total):,.0f} ({r.cantidad} mov.)")
        update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        session.close()


updater = Updater(TOKEN, use_context=True)

# Handlers
updater.dispatcher.add_handler(CommandHandler("mis_movimientos", mis_movimientos))
updater.dispatcher.add_handler(CommandHandler("resumen_mes", resumen_mes))
updater.dispatcher.add_handler(CommandHandler("gastos_por_tipo", gastos_por_tipo))
updater.dispatcher.add_handler(CommandHandler("gastos_por_entidad", gastos_por_entidad))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

# Iniciar API HTTP en un hilo separado
Thread(target=run_api, daemon=True).start()
print("🌐 API HTTP iniciada en puerto 5000")

updater.start_polling()
print("🤖 Bot iniciado")
updater.idle()
