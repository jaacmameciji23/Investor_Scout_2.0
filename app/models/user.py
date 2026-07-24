from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class Usuario:
    id_usuario: int
    nombre: str
    apellido: str
    correo: str
    hash_contrasena: str
    portafolios: List[Any] = field(default_factory=list)  # Lista de objetos Portafolio

    def obtener_patrimonio_total(self) -> float:
        """
        Recorre todos los portafolios y suma su valor total calculado.
        """
        patrimonio = 0.0
        for p in self.portafolios:
            patrimonio += p.obtener_valor_total()
        return patrimonio
