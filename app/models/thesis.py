from dataclasses import dataclass

@dataclass
class Tesis:
    """
    Tesis cualitativa generada por IA que representa la lógica detrás de una inversión.
    """
    simbolo: str
    aspectos_clave: str
    condiciones_vigilancia: str
    puntos_dolor: str
    estrategia_salida: str

    def __post_init__(self):
        self.simbolo = self.simbolo.upper()
