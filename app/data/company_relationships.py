from app.data_structures.company_graph import GrafoRelacionesEmpresas
from app.data.ticker_industries import SUBINDUSTRIA_POR_SIMBOLO

# Relaciones proveedor/cliente reales y públicamente documentadas, en varios
# sectores (semiconductores, hardware, autos, aeroespacial, retail, energía, medios...).
# Cada tupla es (simbolo_expuesto, simbolo_relacionado, tipo_relacion), y se lee como
# "simbolo_relacionado es un `tipo_relacion` para simbolo_expuesto" — ej.
# ("AAPL", "QCOM", "SUPPLIER") significa que Apple depende de Qualcomm como proveedor.
# La arista espejo (el expuesto es cliente/proveedor del relacionado) se agrega
# automáticamente en construir_grafo_relaciones_empresas().
RELACIONES_PROVEEDOR_CLIENTE = [
    # Semiconductores -> hardware y nube (cadena de suministro de chips)
    ("AAPL", "QCOM", "SUPPLIER"),
    ("AAPL", "SWKS", "SUPPLIER"),
    ("AAPL", "TXN", "SUPPLIER"),
    ("DELL", "NVDA", "SUPPLIER"),
    ("HPQ", "NVDA", "SUPPLIER"),
    ("HPE", "NVDA", "SUPPLIER"),
    ("MSFT", "NVDA", "SUPPLIER"),
    ("AMZN", "NVDA", "SUPPLIER"),
    ("GOOGL", "NVDA", "SUPPLIER"),
    ("META", "NVDA", "SUPPLIER"),
    ("INTC", "AMAT", "SUPPLIER"),
    ("INTC", "LRCX", "SUPPLIER"),
    ("INTC", "KLAC", "SUPPLIER"),

    # Operadoras que distribuyen dispositivos Apple (canal de ventas/clientes de Apple)
    ("AAPL", "T", "CUSTOMER"),
    ("AAPL", "VZ", "CUSTOMER"),
    ("AAPL", "TMUS", "CUSTOMER"),

    # Autos y autopartes
    ("GM", "APTV", "SUPPLIER"),
    ("F", "APTV", "SUPPLIER"),
    ("TSLA", "ON", "SUPPLIER"),

    # Aeroespacial y aerolíneas
    ("BA", "GE", "SUPPLIER"),
    ("BA", "RTX", "SUPPLIER"),
    ("DAL", "BA", "SUPPLIER"),
    ("UAL", "BA", "SUPPLIER"),
    ("LUV", "BA", "SUPPLIER"),

    # Retail -> bienes de consumo (el minorista depende de la marca como proveedor)
    ("WMT", "PG", "SUPPLIER"),
    ("TGT", "PG", "SUPPLIER"),
    ("WMT", "KO", "SUPPLIER"),
    ("WMT", "PEP", "SUPPLIER"),
    ("LOW", "MAS", "SUPPLIER"),

    # Petroleras -> servicios petroleros
    ("XOM", "SLB", "SUPPLIER"),
    ("CVX", "HAL", "SUPPLIER"),

    # Distribución de salud
    ("CVS", "MCK", "SUPPLIER"),

    # Clientes de infraestructura en la nube
    ("NFLX", "AMZN", "SUPPLIER"),
]

# Rivalidades conocidas que cruzan las líneas formales de sub-industria GICS y que,
# por lo tanto, no quedarían capturadas por la agrupación automática de competidores.
COMPETIDORES_ENTRE_SECTORES = [
    ("AAPL", "GOOGL"),
    ("AMZN", "WMT"),
    ("NFLX", "DIS"),
    ("MSFT", "GOOGL"),
    ("MSFT", "AMZN"),
    ("META", "GOOGL"),
]


def construir_grafo_relaciones_empresas() -> GrafoRelacionesEmpresas:
    """
    Construye el GrafoRelacionesEmpresas completo para el universo del S&P 500:
      1. Aristas COMPETITOR (bidireccionales) entre cada par de empresas que
         comparten sub-industria GICS (ej. todas las de Semiconductors).
      2. Aristas SUPPLIER/CUSTOMER a partir de la lista curada
         RELACIONES_PROVEEDOR_CLIENTE, con la relación inversa agregada automáticamente.
      3. Aristas COMPETITOR para rivalidades conocidas entre sectores.
    """
    grafo = GrafoRelacionesEmpresas()

    grupos = {}
    for simbolo, sub_industria in SUBINDUSTRIA_POR_SIMBOLO.items():
        grupos.setdefault(sub_industria, []).append(simbolo)

    for simbolos in grupos.values():
        for i, simbolo1 in enumerate(simbolos):
            for simbolo2 in simbolos[i + 1:]:
                grafo.agregar_relacion_bidireccional(simbolo1, simbolo2, "COMPETITOR")

    inversa = {"SUPPLIER": "CUSTOMER", "CUSTOMER": "SUPPLIER"}
    for expuesto, relacionado, tipo_rel in RELACIONES_PROVEEDOR_CLIENTE:
        grafo.agregar_relacion(expuesto, relacionado, tipo_rel)
        grafo.agregar_relacion(relacionado, expuesto, inversa[tipo_rel])

    for simbolo1, simbolo2 in COMPETIDORES_ENTRE_SECTORES:
        grafo.agregar_relacion_bidireccional(simbolo1, simbolo2, "COMPETITOR")

    return grafo
