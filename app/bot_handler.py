import os
from ocr_preprocessor import preprocess
from ocr_easyocr import extract_text_easy as extract_text
from regex import parse_fields
from bd_sqlalchemy import save_record

os.makedirs("downloads", exist_ok=True)

def process_image(path, update, ctx):
    pre = preprocess(path)
    text = extract_text(pre)
    print("📄 TEXTO OCR DETECTADO:")
    print(text)
    fields = parse_fields(text)
    ctx.bot.send_message(update.effective_chat.id,f"OCR detectado:\n{text[:400]}...")
    if fields['fecha'] and fields['monto']:
        save_record(fields)
        ctx.bot.send_message(update.effective_chat.id,
                             f"✔️ Pago registrado: {fields['fecha']} — {fields['monto']} — Cuenta {fields['cuenta']}")
    else:
        ctx.bot.send_message(update.effective_chat.id,
                             "❌ No se pudo extraer toda la información. Asegúrate de que la imagen sea clara.")
