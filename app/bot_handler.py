import os
from ocr_preprocessor import preprocess
from ocr_easyocr import extract_text_easy as extract_text
from regex import parse_fields
from parser import get_parser
from bd_sqlalchemy import save_record

os.makedirs("downloads", exist_ok=True)

def process_image(path, update, ctx):
    pre = preprocess(path)
    text = extract_text(pre)
    print("📄 TEXTO OCR DETECTADO:")
    print(text)
    parser_fn = get_parser(text)
    fields = parser_fn(text)
    if not fields.get('fecha') or not fields.get('monto'):
        fields = parse_fields(text)

    ctx.bot.send_message(update.effective_chat.id, f"OCR detectado:\n{text[:400]}...")

    if fields.get('fecha') and fields.get('monto'):
        save_record(fields)
        resumen = f"{fields.get('fecha')} — {fields.get('monto')}"
        if 'tipo' in fields:
            resumen += f" — {fields['tipo']}"
        ctx.bot.send_message(update.effective_chat.id, f"✔️ Movimiento registrado: {resumen}")
    else:
        ctx.bot.send_message(update.effective_chat.id,
                             "❌ No se pudo extraer toda la información. Asegúrate de que la imagen sea clara.")
