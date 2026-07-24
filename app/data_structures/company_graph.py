from typing import Dict, List, Set, Tuple

class GrafoRelacionesEmpresas:
    """
    Estructura de grafo que representa relaciones entre empresas.
    Nodos = Empresas (Símbolos)
    Aristas = Relaciones (Supplier, Customer, Competitor)

    Se usa para detectar riesgos en cascada (ej., si un proveedor tiene problemas,
    ¿qué empresas del portafolio quedan expuestas?)
    """
    def __init__(self):
        # Lista de Adyacencia: simbolo -> Lista de (Símbolo Relacionado, Tipo de Relación)
        self.lista_adyacencia: Dict[str, List[Tuple[str, str]]] = {}

    def agregar_empresa(self, simbolo: str):
        simbolo = simbolo.upper()
        if simbolo not in self.lista_adyacencia:
            self.lista_adyacencia[simbolo] = []

    def agregar_relacion(self, simbolo1: str, simbolo2: str, tipo_relacion: str):
        """
        Agrega una relación dirigida de simbolo1 a simbolo2.
        ej., simbolo1="NVDA", simbolo2="TSM", tipo_relacion="SUPPLIER"
        Significa que TSM es SUPPLIER (proveedor) de NVDA.
        """
        simbolo1 = simbolo1.upper()
        simbolo2 = simbolo2.upper()
        tipo_relacion = tipo_relacion.upper()

        self.agregar_empresa(simbolo1)
        self.agregar_empresa(simbolo2)

        # Evitar aristas duplicadas
        if not any(rel[0] == simbolo2 and rel[1] == tipo_relacion for rel in self.lista_adyacencia[simbolo1]):
            self.lista_adyacencia[simbolo1].append((simbolo2, tipo_relacion))

    def agregar_relacion_bidireccional(self, simbolo1: str, simbolo2: str, tipo_relacion: str):
        """Útil para relaciones simétricas como 'COMPETITOR'."""
        self.agregar_relacion(simbolo1, simbolo2, tipo_relacion)
        self.agregar_relacion(simbolo2, simbolo1, tipo_relacion)

    def obtener_empresas_relacionadas(self, simbolo: str) -> List[Tuple[str, str]]:
        simbolo = simbolo.upper()
        return self.lista_adyacencia.get(simbolo, [])

    def verificar_exposicion_riesgo_portafolio(self, simbolo_problematico: str, simbolos_portafolio: Set[str]) -> List[Tuple[str, str]]:
        """
        Si `simbolo_problematico` está enfrentando problemas (ej., malos resultados,
        riesgo geopolítico), ¿qué empresas de nuestro portafolio están expuestas, y cómo?

        Retorna una lista de tuplas: (Símbolo del Portafolio, Cómo está expuesto)
        """
        simbolo_problematico = simbolo_problematico.upper()
        empresas_expuestas = []

        for simbolo_p in simbolos_portafolio:
            simbolo_p = simbolo_p.upper()
            if simbolo_p == simbolo_problematico:
                continue

            # Revisa las aristas de la empresa del portafolio para ver si apuntan al símbolo problemático
            for simbolo_relacionado, tipo_rel in self.lista_adyacencia.get(simbolo_p, []):
                if simbolo_relacionado == simbolo_problematico:
                    empresas_expuestas.append((simbolo_p, tipo_rel))

        return empresas_expuestas

    def mostrar_grafo(self):
        """Imprime la estructura del grafo, útil para depuración."""
        for simbolo, aristas in self.lista_adyacencia.items():
            if not aristas:
                continue
            print(f"[{simbolo}]")
            for relacionado, tipo_rel in aristas:
                print(f"  |-- {tipo_rel} -> {relacionado}")
