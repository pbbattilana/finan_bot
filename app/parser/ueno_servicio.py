import re
from typing import Dict
from .base_parser import normalize_amount, parse_date_time, parse_nro_comprobante


def parse(data: str) -> Dict[str, object]:
    fecha, hora = parse_date_time(data)
    monto = normalize_amount(data)
    nro = parse_nro_comprobante(data)

    cuenta = None
    m = re.search(r"Cuenta\s+origen\s*:?\s*(\S+)", data, re.IGNORECASE)
    if m:
        cuenta = m.group(1).strip()

    entidad = None
    m = re.search(r"Entidad\s*:?\s*(.+)", data, re.IGNORECASE)
    if m:
        entidad = m.group(1).strip()

    operacion = None
    m = re.search(r"Operaci\w+n\s*:?\s*(.+)", data, re.IGNORECASE)
    if m:
        operacion = m.group(1).strip()

    return {
        "tipo": "servicio",
        "fecha": fecha,
        "hora": hora,
        "monto": monto,
        "nro_comprobante": nro,
        "cuenta_origen": cuenta,
        "entidad": entidad,
        "beneficiario": operacion,
    }
