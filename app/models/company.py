from dataclasses import dataclass
from typing import Optional

@dataclass
class Empresa:
    """
    Datos cualitativos estáticos/poco frecuentes sobre una empresa específica.
    """
    simbolo: str
    nombre: str
    sector: str
    industria: str
    ventaja_competitiva: Optional[str] = None
    modelo_negocio: Optional[str] = None
    etapa_empresa: Optional[str] = None  # ej. Growth, Value, Cyclical

    def __post_init__(self):
        self.simbolo = self.simbolo.upper()
