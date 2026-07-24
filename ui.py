from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.models.user import Usuario
from app.models.portfolio import Portafolio
from app.data_structures.stock_cache import CacheAcciones
from app.data_structures.portfolio_tree import NodoRaizPortafolio, NodoSector, NodoEmpresa
from app.data.ticker_sectors import SECTORES_POR_SIMBOLO
from app.data.company_relationships import construir_grafo_relaciones_empresas

app = Flask(__name__)
app.secret_key = 'investor-scout-cyberpunk-2077'

cache_acciones = CacheAcciones()

usuario_demo = Usuario(
    id_usuario=1,
    nombre="Scout",
    apellido="User",
    correo="scout@investorscout.com",
    hash_contrasena="***"
)

portafolio_demo = Portafolio(
    id_portafolio=1,
    id_usuario=1,
    nombre="Main Portfolio",
    saldo_efectivo=10000.0
)
usuario_demo.portafolios.append(portafolio_demo)

# Grafo que cubre todo el universo del S&P 500: aristas COMPETITOR entre empresas
# que comparten sub-industria GICS, más relaciones SUPPLIER/CUSTOMER curadas del
# mundo real y rivalidades conocidas entre sectores. Ver app/data/company_relationships.py.
grafo_empresas = construir_grafo_relaciones_empresas()
grafo_empresas.agregar_relacion("NVDA", "TSM", "SUPPLIER")
grafo_empresas.agregar_relacion("TSM", "NVDA", "CUSTOMER")
grafo_empresas.agregar_relacion("AAPL", "TSM", "SUPPLIER")
grafo_empresas.agregar_relacion("TSM", "AAPL", "CUSTOMER")


def obtener_datos_posiciones():
    portafolio = usuario_demo.portafolios[0]
    datos_posiciones = []
    for simbolo, posicion in portafolio.posiciones.items():
        precio = cache_acciones.obtener_precio(simbolo)
        if precio:
            posicion.actualizar_valor(precio)
        costo_base = posicion.acciones * posicion.costo_promedio
        ganancia_perdida = posicion.valor_actual - costo_base
        ganancia_perdida_pct = (ganancia_perdida / costo_base * 100) if costo_base > 0 else 0
        datos_posiciones.append({
            'simbolo': simbolo,
            'acciones': posicion.acciones,
            'costo_promedio': posicion.costo_promedio,
            'precio_actual': precio or 0.0,
            'valor_actual': posicion.valor_actual,
            'ganancia_perdida': ganancia_perdida,
            'ganancia_perdida_pct': ganancia_perdida_pct
        })
    return datos_posiciones


def construir_arbol_portafolio(portafolio, datos_posiciones):
    """
    Agrupa las posiciones actuales en un árbol NodoRaizPortafolio -> NodoSector -> NodoEmpresa
    para poder derivar el total (y el desglose por sector) de forma recursiva.
    """
    raiz = NodoRaizPortafolio(nombre=portafolio.nombre, saldo_efectivo=portafolio.saldo_efectivo)
    nodos_sector = {}
    for p in datos_posiciones:
        sector = SECTORES_POR_SIMBOLO.get(p['simbolo'], 'Other')
        if sector not in nodos_sector:
            nodos_sector[sector] = NodoSector(sector)
            raiz.agregar_hijo(nodos_sector[sector])
        nodos_sector[sector].agregar_hijo(
            NodoEmpresa(simbolo=p['simbolo'], acciones=p['acciones'], precio_actual=p['precio_actual'])
        )
    return raiz


@app.route('/')
def panel():
    portafolio = usuario_demo.portafolios[0]
    datos_posiciones = obtener_datos_posiciones()
    cantidad_transacciones = sum(1 for _ in portafolio.registro_transacciones)

    arbol = construir_arbol_portafolio(portafolio, datos_posiciones)
    valor_total = arbol.obtener_valor()

    desglose_sectores = []
    for nodo_sector in arbol.hijos:
        valor_sector = nodo_sector.obtener_valor()
        desglose_sectores.append({
            'nombre': nodo_sector.nombre,
            'valor': valor_sector,
            'porcentaje': (valor_sector / valor_total * 100) if valor_total > 0 else 0,
            'empresas': [c.simbolo for c in nodo_sector.hijos]
        })
    desglose_sectores.sort(key=lambda s: s['valor'], reverse=True)
    porcentaje_efectivo = (portafolio.saldo_efectivo / valor_total * 100) if valor_total > 0 else 0

    return render_template('dashboard.html',
        usuario=usuario_demo,
        portafolio=portafolio,
        posiciones=datos_posiciones,
        valor_total=valor_total,
        cantidad_transacciones=cantidad_transacciones,
        desglose_sectores=desglose_sectores,
        porcentaje_efectivo=porcentaje_efectivo
    )


@app.route('/trade', methods=['GET', 'POST'])
def operar():
    portafolio = usuario_demo.portafolios[0]
    if request.method == 'POST':
        simbolo = request.form.get('simbolo', '').strip().upper()
        accion = request.form.get('accion', '').upper()
        try:
            acciones = float(request.form.get('acciones', 0))
        except ValueError:
            flash('Cantidad de acciones inválida.', 'error')
            return redirect(url_for('operar'))

        if not simbolo or acciones <= 0:
            flash('Ingresa un símbolo válido y una cantidad de acciones.', 'error')
            return redirect(url_for('operar'))

        precio = cache_acciones.obtener_precio(simbolo)
        if not precio:
            flash(f'No se pudo obtener el precio de {simbolo}. Verifica el símbolo.', 'error')
            return redirect(url_for('operar'))

        try:
            portafolio.agregar_transaccion(
                simbolo=simbolo,
                tipo_transaccion=accion,
                acciones=acciones,
                precio=precio,
                fecha=datetime.now()
            )
            flash(f'{accion} {acciones} acciones de {simbolo} a ${precio:.2f} — ÉXITO', 'success')
        except ValueError as e:
            flash(str(e), 'error')

        return redirect(url_for('panel'))

    return render_template('trade.html', portafolio=portafolio)


@app.route('/api/price/<simbolo>')
def obtener_precio_api(simbolo):
    precio = cache_acciones.obtener_precio(simbolo.upper().strip())
    if precio:
        return jsonify({'simbolo': simbolo.upper(), 'precio': precio, 'estado': 'ok'})
    return jsonify({'simbolo': simbolo.upper(), 'precio': None, 'estado': 'no_encontrado'}), 404


@app.route('/history')
def historial():
    portafolio = usuario_demo.portafolios[0]
    transacciones = list(portafolio.registro_transacciones)
    transacciones_invertidas = list(reversed(transacciones))
    return render_template('history.html',
        transacciones=transacciones_invertidas,
        portafolio=portafolio,
        cantidad_total=len(transacciones)
    )


@app.route('/risk', methods=['GET', 'POST'])
def riesgo():
    portafolio = usuario_demo.portafolios[0]
    simbolos_portafolio = set(portafolio.posiciones.keys())
    resultado_riesgo = None
    simbolo_verificado = None
    datos_grafo = {
        'nodos': [],
        'aristas': []
    }

    # El grafo completo cubre ~500+ empresas, demasiado denso para dibujarlo como
    # un diagrama circular. Mostramos solo el subgrafo relevante para tus
    # posiciones: tus símbolos más cada empresa conectada directamente a alguno de ellos.
    aristas_relevantes = []
    for simbolo1, aristas in grafo_empresas.lista_adyacencia.items():
        for simbolo2, rel in aristas:
            if simbolo1 in simbolos_portafolio or simbolo2 in simbolos_portafolio:
                aristas_relevantes.append({'origen': simbolo1, 'destino': simbolo2, 'etiqueta': rel})

    simbolos_relevantes = set(simbolos_portafolio)
    for arista in aristas_relevantes:
        simbolos_relevantes.add(arista['origen'])
        simbolos_relevantes.add(arista['destino'])

    datos_grafo['nodos'] = [
        {'id': s, 'en_portafolio': s in simbolos_portafolio} for s in simbolos_relevantes
    ]
    datos_grafo['aristas'] = aristas_relevantes
    total_empresas = len(grafo_empresas.lista_adyacencia)

    if request.method == 'POST':
        tipo_formulario = request.form.get('tipo_formulario')

        if tipo_formulario == 'agregar_relacion':
            simbolo1 = request.form.get('simbolo1', '').upper().strip()
            simbolo2 = request.form.get('simbolo2', '').upper().strip()
            tipo_rel = request.form.get('tipo_relacion', 'SUPPLIER').upper().strip()
            bidireccional = request.form.get('bidireccional') == 'on'
            if simbolo1 and simbolo2 and tipo_rel:
                if bidireccional:
                    grafo_empresas.agregar_relacion_bidireccional(simbolo1, simbolo2, tipo_rel)
                else:
                    grafo_empresas.agregar_relacion(simbolo1, simbolo2, tipo_rel)
                flash(f'Relación agregada: {simbolo1} ↔ {simbolo2} [{tipo_rel}]', 'success')
            return redirect(url_for('riesgo'))

        if tipo_formulario == 'verificar_riesgo':
            simbolo_verificado = request.form.get('simbolo', '').upper().strip()
            riesgos = grafo_empresas.verificar_exposicion_riesgo_portafolio(simbolo_verificado, simbolos_portafolio)
            resultado_riesgo = riesgos

    return render_template('risk.html',
        portafolio=portafolio,
        datos_grafo=datos_grafo,
        resultado_riesgo=resultado_riesgo,
        simbolo_verificado=simbolo_verificado,
        simbolos_portafolio=simbolos_portafolio,
        total_empresas=total_empresas
    )


if __name__ == '__main__':
    import os
    puerto = int(os.environ.get('PORT', 5050))
    app.run(debug=False, host='0.0.0.0', port=puerto)
