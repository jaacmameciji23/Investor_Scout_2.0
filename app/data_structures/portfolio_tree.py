from typing import List
from abc import ABC, abstractmethod

class NodoArbol(ABC):
    """Clase base para el árbol jerárquico del Portafolio."""
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.hijos: List['NodoArbol'] = []

    def agregar_hijo(self, hijo: 'NodoArbol'):
        self.hijos.append(hijo)

    @abstractmethod
    def obtener_valor(self) -> float:
        """Calcula el valor de forma recursiva."""
        pass

    def mostrar(self, nivel: int = 0):
        """Auxiliar para imprimir la estructura del árbol."""
        sangria = "  " * nivel
        valor = self.obtener_valor()
        print(f"{sangria}- {self.nombre}: ${valor:.2f}")
        for hijo in self.hijos:
            hijo.mostrar(nivel + 1)


class NodoEmpresa(NodoArbol):
    """Nodo hoja que representa una posición real en una empresa."""
    def __init__(self, simbolo: str, acciones: float, precio_actual: float):
        super().__init__(nombre=simbolo)
        self.simbolo = simbolo
        self.acciones = acciones
        self.precio_actual = precio_actual

    def obtener_valor(self) -> float:
        return self.acciones * self.precio_actual


class NodoSector(NodoArbol):
    """Nodo intermedio que agrupa empresas por sector."""
    def obtener_valor(self) -> float:
        return sum(hijo.obtener_valor() for hijo in self.hijos)


class NodoRaizPortafolio(NodoArbol):
    """Nodo raíz de todo el árbol del portafolio."""
    def __init__(self, nombre: str, saldo_efectivo: float = 0.0):
        super().__init__(nombre)
        self.saldo_efectivo = saldo_efectivo

    def obtener_valor(self) -> float:
        # El valor del portafolio es el efectivo + el valor de todos los sectores
        return self.saldo_efectivo + sum(hijo.obtener_valor() for hijo in self.hijos)
