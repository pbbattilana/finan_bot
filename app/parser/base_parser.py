import re
from datetime import datetime
from typing import Optional, Tuple


def normalize_amount(text: str) -> Optional[int]:
    """Extrae y normaliza montos en guaraníes de un bloque de texto."""
    monto_match = re.search(r"\b(?:G[s5]|6S|C[s5]|CS)[^\d]*([\dOCoC.,]+)", text, re.IGNORECASE)
    if not monto_match:
        return None
    bruto = monto_match.group(1)
    limpio = bruto.replace('O', '0').replace('o', '0')
    limpio = limpio.replace('C', '000').replace('c', '000')
    limpio = limpio.replace('S', '5').replace('s', '5')
    limpio = limpio.replace('.', '').replace(',', '')
    limpio = re.sub(r"\D", "", limpio)
    if not limpio:
        return None
    try:
        return int(limpio)
    except Exception:
        return None


def parse_date_time(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Devuelve fecha YYYY-MM-DD y hora HH:MM si están presentes."""
    dt_match = re.search(
        r"(\d{2}/\d{2}/\d{4})\s*(?:a\s*las)?\s*(\d{1,2}[.:]\d{2})",
        text,
        re.IGNORECASE | re.S,
    )
    fecha = hora = None
    if dt_match:
        fecha_raw = dt_match.group(1)
        hora_raw = dt_match.group(2).replace(".", ":").replace(" ", "")
        try:
            fecha = datetime.strptime(fecha_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            fecha = None
        parts = hora_raw.split(":")
        if len(parts) == 2:
            try:
                hora = f"{int(parts[0]):02d}:{int(parts[1]):02d}"
            except Exception:
                hora = None
    return fecha, hora


def parse_nro_comprobante(text: str) -> Optional[str]:
    match = re.search(r"comprobante\s*:?\s*(\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None
