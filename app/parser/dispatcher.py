from typing import Callable

from .ueno_pago import parse as parse_pago
from .ueno_transferencia import parse as parse_transferencia
from .ueno_servicio import parse as parse_servicio


KEYWORDS = [
    ("comprobante de transferencia", parse_transferencia),
    ("pago de servicio", parse_servicio),
    ("comprobante de pago de servicios", parse_servicio),
    ("comprobante de pago", parse_pago),
]


def get_parser(data: str) -> Callable[[str], dict]:
    """Devuelve la función parse adecuada según palabras clave."""
    texto = data.lower()
    for palabra, parser in KEYWORDS:
        if palabra in texto:
            return parser
    return parse_pago
