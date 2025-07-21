"""Parsers de comprobantes del banco Ueno."""

from .dispatcher import get_parser
from .ueno_pago import parse as parse_pago
from .ueno_transferencia import parse as parse_transferencia
from .ueno_servicio import parse as parse_servicio

__all__ = [
    "get_parser",
    "parse_pago",
    "parse_transferencia",
    "parse_servicio",
]
