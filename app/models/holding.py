from dataclasses import dataclass

@dataclass
class Posicion:
    """
    Activo activo del portafolio. Es un registro generado dinámicamente,
    calculado a partir de la LinkedList del historial de transacciones.
    """
    simbolo: str
    acciones: float
    costo_promedio: float
    valor_actual: float = 0.0

    def actualizar_valor(self, precio_actual: float):
        self.valor_actual = self.acciones * precio_actual
