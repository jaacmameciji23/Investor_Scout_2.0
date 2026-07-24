# Investor Scout 2.0

Aplicación de compra y venta de acciones con análisis de portafolio, desarrollada como proyecto final para la clase de Estructuras de Datos.

---

## Punto de partida — Aporte inicial del equipo

La base del proyecto fue desarrollada por **@JogerGott**, quien diseñó e implementó la arquitectura del backend en Python. Su aporte incluyó:

### Estructuras de datos implementadas

| Estructura | Archivo | Uso |
|---|---|---|
| **Lista Enlazada** | `app/data_structures/transaction_ll.py` | Registro inmutable de transacciones (append-only) |
| **Árbol Compuesto** | `app/data_structures/portfolio_tree.py` | Jerarquía portafolio → sectores → empresas |
| **Grafo Dirigido** | `app/data_structures/company_graph.py` | Relaciones entre empresas para análisis de riesgo |
| **Tabla Hash** | `app/data_structures/stock_cache.py` | Cache de precios para consultas O(1) |

### Modelos de dominio

- `User` — Usuario con portafolios asociados
- `Portfolio` — Portafolio con saldo en efectivo y log de transacciones
- `Company` — Perfil cualitativo de una empresa (sector, moat, modelo de negocio)
- `Holding` — Posición activa calculada a partir del log de transacciones
- `FinancialSnapshot` — Datos financieros trimestrales
- `Thesis` — Tesis de inversión (placeholder para integración futura con IA)

### Patrón arquitectónico destacado

El portafolio usa **Event Sourcing** mediante la Lista Enlazada: el estado real de las posiciones no se almacena directamente, sino que se recalcula reproduciendo todos los nodos de la lista de transacciones de inicio a fin.

### Integración con datos reales

Se usa la librería `yfinance` para obtener precios reales del mercado desde Yahoo Finance.

---

## Interfaz gráfica — Prototipo temprano

> ⚠️ **Nota:** Lo que se describe a continuación es únicamente una **idea inicial** de cómo podría verse la interfaz gráfica del proyecto. No representa el diseño final ni ha sido aprobada por el equipo. Su propósito es explorar posibilidades y servir como punto de discusión.

Como complemento al backend, se desarrolló un prototipo de interfaz web usando **Flask** y **Jinja2**, con una estética cyberpunk.

### Tecnologías usadas

- **Python + Flask** — Servidor web que conecta el backend con el navegador
- **Jinja2** — Motor de plantillas que inyecta datos de Python en el HTML
- **HTML + CSS** — Interfaz visual con estética cyberpunk (sin librerías externas)
- **JavaScript** — Interactividad: fetch de precios en tiempo real y visualización del grafo

### Páginas del prototipo

- **Dashboard** — Valor total del portafolio, saldo en efectivo, posiciones activas con P&L
- **Trade Terminal** — Formulario de compra/venta con precio en vivo
- **Transaction Log** — Visualización de la Lista Enlazada como línea de tiempo
- **Risk Map** — Visualización del Grafo de relaciones y detector de riesgo en cascada

### Cómo correrlo localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/jaacmameciji23/Investor_Scout_2.0.git
cd Investor_Scout_2.0
git checkout juan-trabajo

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Correr el servidor
python3 ui.py
```

Luego abrir `http://localhost:5050` en el navegador.

---

## Estado del proyecto

- [x] Estructuras de datos implementadas
- [x] Modelos de dominio definidos
- [x] Integración con precios reales (yfinance)
- [x] Prototipo de interfaz gráfica web
- [ ] Interfaz gráfica definitiva (pendiente aprobación del equipo)
- [ ] Persistencia de datos
- [ ] Autenticación de usuarios
- [ ] Integración con IA para tesis de inversión
- [ ] Tests unitarios

---

## Equipo

- **@JogerGott** — Arquitectura backend, estructuras de datos, modelos de dominio
- **@jaacmameciji23** — Prototipo de interfaz gráfica web
