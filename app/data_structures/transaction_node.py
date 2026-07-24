from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class NodoTransaccion:
    """
    Un nodo inmutable en la LinkedList del historial de transacciones.
    Las transacciones son de tipo 'BUY' o 'SELL'.
    """
    simbolo: str
    tipo_transaccion: str  # 'BUY' o 'SELL'
    acciones: float
    precio: float
    fecha: datetime
    siguiente: Optional['NodoTransaccion'] = None

    def __post_init__(self):
        self.simbolo = self.simbolo.upper()
        self.tipo_transaccion = self.tipo_transaccion.upper()
