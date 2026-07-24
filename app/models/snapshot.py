from dataclasses import dataclass
from typing import Optional

@dataclass
class InstantaneaFinanciera:
    """
    Datos cuantitativos históricos generados cada trimestre para seguir la
    evolución financiera de una empresa.
    """
    simbolo: str
    fecha_periodo: str  # ej. 'Q1 2024'
    precio_actual: float
    roe: Optional[float] = None
    roa: Optional[float] = None
    nivel_deuda: Optional[float] = None
    margenes: Optional[float] = None

    def __post_init__(self):
        self.simbolo = self.simbolo.upper()
