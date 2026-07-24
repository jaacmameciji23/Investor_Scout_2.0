from datetime import datetime
from app.models.user import Usuario
from app.models.portfolio import Portafolio
from app.models.company import Empresa
from app.data_structures.stock_cache import CacheAcciones
from app.data_structures.portfolio_tree import NodoRaizPortafolio, NodoSector, NodoEmpresa
from app.data_structures.company_graph import GrafoRelacionesEmpresas
import time

def ejecutar_simulacion():
    print("--- Investor Scout: Simulación Inicial M.V.P ---")

    # 1. Crear un Usuario
    usuario = Usuario(
        id_usuario=1,
        nombre="Joger",
        apellido="Munoz",
        correo="joger@investorscout.com",
        hash_contrasena="***",
    )

    print(f"\nUsuario creado: {usuario.nombre} {usuario.apellido}")

    # 2. Crear el Perfil cualitativo de la Empresa (no cambia con frecuencia)
    empresa_aapl = Empresa(
        simbolo="AAPL",
        nombre="Apple Inc.",
        sector="Technology",
        industria="Consumer Electronics",
        ventaja_competitiva="Lealtad de marca, ecosistema cerrado",
        modelo_negocio="Hardware premium integrado con servicios de alto margen",
        etapa_empresa="Value"
    )
    print(f"\nPerfil de Empresa: {empresa_aapl.nombre} | Sector: {empresa_aapl.sector} | Ventaja: {empresa_aapl.ventaja_competitiva}")

    # 3. Crear la estructura del Portafolio
    portafolio = Portafolio(
        id_portafolio=1,
        id_usuario=usuario.id_usuario,
        nombre="Portafolio de Value Investing",
        saldo_efectivo=10000.0
    )
    usuario.portafolios.append(portafolio)
    print(f"\nPortafolio inicializado: '{portafolio.nombre}' con Efectivo: ${portafolio.saldo_efectivo:.2f}")

    # 4. Simular el Registro Inmutable de Transacciones mediante la LinkedList
    print("\nEjecutando Transacciones...")

    portafolio.agregar_transaccion(simbolo="AAPL", tipo_transaccion="BUY", acciones=10, precio=150.0, fecha=datetime.now())
    print(f" -> BUY 10 AAPL @ $150.0")

    portafolio.agregar_transaccion(simbolo="NVDA", tipo_transaccion="BUY", acciones=5, precio=400.0, fecha=datetime.now())
    print(f" -> BUY 5 NVDA @ $400.0")

    portafolio.agregar_transaccion(simbolo="AAPL", tipo_transaccion="SELL", acciones=5, precio=180.0, fecha=datetime.now())
    print(f" -> SELL 5 AAPL @ $180.0")

    # 5. Mostrar el estado calculado implícitamente por la Linked List
    print("\n--- Posiciones Actuales (Calculadas desde el Registro de Transacciones) ---")
    for simbolo, posicion in portafolio.posiciones.items():
        print(f"Posición: {posicion.simbolo} | Acciones: {posicion.acciones} | Costo Promedio: ${posicion.costo_promedio:.2f}")

    print(f"\nSaldo de Efectivo Restante: ${portafolio.saldo_efectivo:.2f}")

def probar_cache_acciones():
    print("\n--- Probando la Tabla Hash CacheAcciones ---")
    cache = CacheAcciones()

    print("1. Obteniendo AAPL desde la API (se espera demora...)")
    inicio = time.time()
    precio = cache.obtener_precio("AAPL")
    if precio:
        print(f" -> Precio AAPL: ${precio:.2f} (Tomó {time.time() - inicio:.4f}s)")

    print("\n2. Obteniendo AAPL nuevamente desde la caché (búsqueda O(1)...)")
    inicio = time.time()
    precio_en_cache = cache.obtener_precio("AAPL")
    if precio_en_cache:
        print(f" -> Precio AAPL: ${precio_en_cache:.2f} (Tomó {time.time() - inicio:.4f}s)")

    print("\n3. Obteniendo MSFT con forzar_actualizacion=True (se espera demora...)")
    inicio = time.time()
    precio_msft = cache.obtener_precio("MSFT", forzar_actualizacion=True)
    if precio_msft:
        print(f" -> Precio MSFT: ${precio_msft:.2f} (Tomó {time.time() - inicio:.4f}s)")

    print("\n4. Obteniendo ADBE con forzar_actualizacion=True (se espera demora...)")
    inicio = time.time()
    precio_adbe = cache.obtener_precio("ADBE", forzar_actualizacion=True)
    if precio_adbe:
        print(f" -> Precio ADBE: ${precio_adbe:.2f} (Tomó {time.time() - inicio:.4f}s)")

    print(f"\nTodos los símbolos en caché: {cache.obtener_simbolos_en_cache()}")

def probar_arbol_portafolio():
    print("\n--- Probando NodoArbol del Portafolio (Valuación Recursiva) ---")

    # Crear el portafolio raíz
    raiz = NodoRaizPortafolio(nombre="Mi Portafolio de Value", saldo_efectivo=5000.0)

    # Crear los nodos de Sector
    sector_tecnologia = NodoSector("Technology")
    sector_finanzas = NodoSector("Financials")

    # Agregar sectores a la raíz
    raiz.agregar_hijo(sector_tecnologia)
    raiz.agregar_hijo(sector_finanzas)

    # Agregar nodos hoja de Empresa
    # AAPL y MSFT en Tecnología
    nodo_aapl = NodoEmpresa(simbolo="AAPL", acciones=10, precio_actual=150.0)  # $1500
    nodo_msft = NodoEmpresa(simbolo="MSFT", acciones=5, precio_actual=400.0)   # $2000
    sector_tecnologia.agregar_hijo(nodo_aapl)
    sector_tecnologia.agregar_hijo(nodo_msft)

    # JPM en Finanzas
    nodo_jpm = NodoEmpresa(simbolo="JPM", acciones=20, precio_actual=190.0)    # $3800
    sector_finanzas.agregar_hijo(nodo_jpm)

    # Calcular el Valor Total (Debería ser 5000 + 1500 + 2000 + 3800 = 12300)
    print("Jerarquía del Árbol y Valores:")
    raiz.mostrar()
    print(f"\nValor Total Calculado del Portafolio: ${raiz.obtener_valor():.2f}")

def probar_grafo_empresas():
    print("\n--- Probando GrafoRelacionesEmpresas (Exposición a Riesgo) ---")

    grafo = GrafoRelacionesEmpresas()

    # Definir relaciones (entrada manual Fase 1)
    # TSM es proveedor de NVDA y AAPL
    grafo.agregar_relacion("NVDA", "TSM", "SUPPLIER")
    grafo.agregar_relacion("AAPL", "TSM", "SUPPLIER")

    # MSFT es cliente de NVDA
    grafo.agregar_relacion("MSFT", "NVDA", "CUSTOMER")

    # NVDA y AMD son competidores
    grafo.agregar_relacion_bidireccional("NVDA", "AMD", "COMPETITOR")

    print("Estructura del Grafo:")
    grafo.mostrar_grafo()

    # Portafolio simulado
    mi_portafolio = {"NVDA", "AAPL", "MSFT"}
    print(f"\nMi Portafolio: {mi_portafolio}")

    # Escenario: TSMC (TSM) tiene problemas de manufactura
    simbolo_problematico = "TSM"
    print(f"\n[ALERTA] Se detectaron malas noticias para {simbolo_problematico}!")

    riesgos = grafo.verificar_exposicion_riesgo_portafolio(simbolo_problematico, mi_portafolio)
    if riesgos:
        print("Riesgo en cascada detectado para tu portafolio:")
        for simbolo_afectado, tipo_exposicion in riesgos:
            print(f" -> {simbolo_afectado} está en riesgo porque {simbolo_problematico} es su {tipo_exposicion}.")
    else:
        print("Tu portafolio no tiene exposición directa a esta empresa.")

if __name__ == "__main__":
    ejecutar_simulacion()
    probar_cache_acciones()
    probar_arbol_portafolio()
    probar_grafo_empresas()
