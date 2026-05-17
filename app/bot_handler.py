import os
from ocr_preprocessor import preprocess
from ocr_easyocr import extract_text_easy as extract_text
from regex import parse_fields
from parser import get_parser
from bd_sqlalchemy import save_record, get_or_create_user

os.makedirs("downloads", exist_ok=True)


def process_image(path, update, ctx):
    # Obtener datos del usuario de Telegram
    user = update.effective_user
    telegram_user_id = user.id
    telegram_username = user.username
    first_name = user.first_name
    last_name = user.last_name

    print(f"👤 Usuario detectado: {telegram_user_id} (@{telegram_username}) - {first_name} {last_name}")

    # Buscar o crear el usuario en la base de datos
    usuario_id = get_or_create_user(
        telegram_user_id=telegram_user_id,
        telegram_username=telegram_username,
        first_name=first_name,
        last_name=last_name,
    )
    print(f"👤 usuario_id={usuario_id} para Telegram user {telegram_user_id}")

    pre = preprocess(path)
    text = extract_text(pre)
    print("📄 TEXTO OCR DETECTADO:")
    print(text)
    parser_fn = get_parser(text)
    fields = parser_fn(text)

    # Extraer campos básicos con expresiones regulares si faltan
    fallback = parse_fields(text)
    for key, val in fallback.items():
        if not fields.get(key) and val:
            fields[key] = val

    ctx.bot.send_message(update.effective_chat.id, f"OCR detectado:\n{text[:400]}...")

    if fields.get('fecha') and fields.get('monto'):
        save_record(fields, usuario_id=usuario_id)
        resumen = f"{fields.get('fecha')} — {fields.get('monto')}"
        if 'tipo' in fields:
            resumen += f" — {fields['tipo']}"
        ctx.bot.send_message(update.effective_chat.id, f"✔️ Movimiento registrado: {resumen}")
    else:
        ctx.bot.send_message(update.effective_chat.id,
                             "❌ No se pudo extraer toda la información. Asegúrate de que la imagen sea clara.")
