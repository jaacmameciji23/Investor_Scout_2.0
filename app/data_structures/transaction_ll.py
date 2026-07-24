from typing import Optional
from app.data_structures.transaction_node import NodoTransaccion

class ListaEnlazadaTransacciones:
    """
    LinkedList de solo-append diseñada para mantener un historial inmutable
    de todas las transacciones.
    """
    def __init__(self):
        self.cabeza: Optional[NodoTransaccion] = None
        self.cola: Optional[NodoTransaccion] = None

    def agregar(self, transaccion: NodoTransaccion):
        """
        Agrega una nueva transacción al final de la lista. Inserción O(1).
        """
        if not self.cabeza:
            self.cabeza = transaccion
            self.cola = transaccion
        else:
            self.cola.siguiente = transaccion
            self.cola = transaccion

    def __iter__(self):
        """
        Método auxiliar para recorrer los nodos de forma natural:
        (ej., [nodo for nodo in lista])
        """
        actual = self.cabeza
        while actual:
            yield actual
            actual = actual.siguiente
