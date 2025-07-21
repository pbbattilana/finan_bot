import re
import unicodedata

def parse_fields(text):
    """Extrae fecha, monto y cuenta de un texto OCR.

    Ejemplos de conversión de monto:
    - "Gs. 195C"   -> 195000
    - "Gs 195.000" -> 195000
    - "Gs 10O50"   -> 10050
    """
    text = unicodedata.normalize("NFKC", text)
    print("🔍 Texto recibido para parsear:\n", text)

    # Buscar fecha
    fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    print("🗓️ Fecha encontrada:", fecha_match.group(1) if fecha_match else "❌ No encontrada")

    # Buscar número de comprobante (cuenta)
    cuenta_match = re.search(r'comprobante:?\s*(\d+)', text, re.IGNORECASE)
    print("💳 Cuenta encontrada:", cuenta_match.group(1) if cuenta_match else "❌ No encontrada")

    # Buscar monto bruto (captura inicial)
    monto_match = re.search(r'\b(?:G[s5]|6S)[^\d]*([\dOCoC.,]+)', text, re.IGNORECASE)
    print("💰 Monto bruto encontrado:", monto_match.group(1) if monto_match else "❌ No encontrado")

    monto_val = None
    if monto_match:
        bruto = monto_match.group(1)
        print("🛠️ Monto antes de limpiar:", bruto)
        # Mapear posibles errores de OCR a dígitos y miles
        limpio = bruto.replace('O', '0').replace('o', '0')
        # 'C' suele aparecer en lugar de '.000'
        limpio = limpio.replace('C', '000')
        # Eliminar separadores de miles
        limpio = limpio.replace('.', '').replace(',', '')
        limpio = re.sub(r'\D', '', limpio)
        print("🧹 Monto limpio:", limpio)
        try:
            monto_val = int(limpio)
            print("✅ Monto final:", monto_val)
        except Exception as e:
            print("❌ Error convirtiendo monto a número:", e)

    return {
        'fecha': fecha_match.group(1) if fecha_match else None,
        'monto': monto_val,
        'cuenta': cuenta_match.group(1) if cuenta_match else None
    }