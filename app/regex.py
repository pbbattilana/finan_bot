import re

def parse_fields(text):
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
        bruto = bruto.replace('C', '.').replace('O', '0').replace('o', '0')
        bruto = re.sub(r'[^\d.]', '', bruto)
        print("🧹 Monto limpio:", bruto)
        try:
            monto_val = int(float(bruto))
            print("✅ Monto final:", monto_val)
        except Exception as e:
            print("❌ Error convirtiendo monto a número:", e)

    return {
        'fecha': fecha_match.group(1) if fecha_match else None,
        'monto': monto_val,
        'cuenta': cuenta_match.group(1) if cuenta_match else None
    }