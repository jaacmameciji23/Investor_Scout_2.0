from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
from app.data_structures.transaction_ll import ListaEnlazadaTransacciones
from app.data_structures.transaction_node import NodoTransaccion
from app.models.holding import Posicion

@dataclass
class Portafolio:
    id_portafolio: int
    id_usuario: int
    nombre: str
    saldo_efectivo: float
    registro_transacciones: ListaEnlazadaTransacciones = field(default_factory=ListaEnlazadaTransacciones)
    posiciones: Dict[str, Posicion] = field(default_factory=dict)

    def agregar_transaccion(self, simbolo: str, tipo_transaccion: str, acciones: float, precio: float, fecha: datetime):
        """
        Agrega la transacción a la Lista Inmutable y luego recalcula las posiciones de inmediato.
        """
        nodo = NodoTransaccion(simbolo, tipo_transaccion, acciones, precio, fecha)
        self.registro_transacciones.agregar(nodo)

        # Al comprar se descuenta del efectivo. Al vender se suma al efectivo.
        if nodo.tipo_transaccion == 'BUY':
            if self.saldo_efectivo < (acciones * precio):
                raise ValueError("Efectivo insuficiente para realizar la compra (BUY).")
            self.saldo_efectivo -= (acciones * precio)
        elif nodo.tipo_transaccion == 'SELL':
            self.saldo_efectivo += (acciones * precio)

        # Para mantener una estructura estateless, reconstruimos por completo
        # el diccionario de posiciones a partir del registro:
        self._recalcular_posiciones()

    def _recalcular_posiciones(self):
        """
        El núcleo de la arquitectura. El verdadero estado de las posiciones del
        portafolio se deriva ÚNICAMENTE de reproducir el registro de transacciones
        del nodo 1 al N.
        """
        posiciones_temp: Dict[str, Posicion] = {}

        for tx in self.registro_transacciones:
            simbolo = tx.simbolo

            if simbolo not in posiciones_temp:
                if tx.tipo_transaccion == 'SELL':
                    raise ValueError(f"Error en el registro: SELL antes de BUY para {simbolo}")
                posiciones_temp[simbolo] = Posicion(simbolo=simbolo, acciones=tx.acciones, costo_promedio=tx.precio)
            else:
                posicion = posiciones_temp[simbolo]
                if tx.tipo_transaccion == 'BUY':
                    # Calcular el nuevo costo promedio
                    valor_total_antes = posicion.acciones * posicion.costo_promedio
                    valor_nuevo = tx.acciones * tx.precio
                    posicion.acciones += tx.acciones
                    posicion.costo_promedio = (valor_total_antes + valor_nuevo) / posicion.acciones
                elif tx.tipo_transaccion == 'SELL':
                    posicion.acciones -= tx.acciones
                    if posicion.acciones < 0:
                        raise ValueError(f"Error en el registro: venta en corto no soportada. Las acciones de {simbolo} bajaron de 0")
                    elif posicion.acciones == 0:
                        posicion.costo_promedio = 0.0

        # Eliminar posiciones con 0 acciones para mantener el diccionario limpio
        self.posiciones = {k: v for k, v in posiciones_temp.items() if v.acciones > 0}

    def obtener_valor_total(self) -> float:
        """
        Calcula valor = efectivo + (suma del valor_actual de todas las posiciones).
        Asume que posicion.valor_actual se actualiza externamente por un servicio de precios.
        """
        valor_posiciones = sum(p.valor_actual for p in self.posiciones.values())
        return self.saldo_efectivo + valor_posiciones
