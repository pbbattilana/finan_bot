import re
from typing import Dict
from .base_parser import normalize_amount, parse_date_time, parse_nro_comprobante


def parse(data: str) -> Dict[str, object]:
    fecha, hora = parse_date_time(data)
    monto = normalize_amount(data)
    nro = parse_nro_comprobante(data)

    remitente = None
    m = re.search(r"Remitente\s*:?\s*(.+)", data, re.IGNORECASE)
    if m:
        remitente = m.group(1).strip()

    destinatario = None
    m = re.search(r"Destinatario\s*:?\s*(.+)", data, re.IGNORECASE)
    if m:
        destinatario = m.group(1).strip()

    entidad = None
    m = re.search(r"Entidad\s*destino\s*:?\s*(.+)", data, re.IGNORECASE)
    if m:
        entidad = m.group(1).strip()

    return {
        "tipo": "transferencia",
        "fecha": fecha,
        "hora": hora,
        "monto": monto,
        "nro_comprobante": nro,
        "cuenta_origen": remitente,
        "beneficiario": destinatario,
        "entidad": entidad,
    }
