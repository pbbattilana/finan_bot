import re
from typing import Dict
from .base_parser import normalize_amount, parse_date_time, parse_nro_comprobante


def parse(data: str) -> Dict[str, object]:
    fecha, hora = parse_date_time(data)
    monto = normalize_amount(data)
    nro = parse_nro_comprobante(data)

    comercio = None
    m = re.search(r"Comercio\s*:?\s*(.+)", data, re.IGNORECASE)
    if m:
        comercio = m.group(1).strip()

    return {
        "tipo": "pago",
        "fecha": fecha,
        "hora": hora,
        "monto": monto,
        "nro_comprobante": nro,
        "comercio": comercio,
    }
