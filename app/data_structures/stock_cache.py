import yfinance as yf
from typing import Dict, Optional
from datetime import datetime

class CacheAcciones:
    """
    Tabla Hash (Diccionario) para cachear precios de acciones en tiempo real.
    Provee búsqueda O(1) para precios ya obtenidos anteriormente.
    """
    def __init__(self):
        # La Tabla Hash que mapea simbolo -> precio_actual
        self._cache_precios: Dict[str, float] = {}
        # Registra cuándo se actualizó cada precio por última vez
        self._ultima_actualizacion: Dict[str, datetime] = {}

    def obtener_precio(self, simbolo: str, forzar_actualizacion: bool = False) -> Optional[float]:
        """
        Obtiene el precio de un símbolo.
        Si forzar_actualizacion es True o el símbolo no está en caché, lo busca en yfinance.
        """
        simbolo = simbolo.upper()

        # Búsqueda O(1) si no necesitamos actualizar y ya está en caché
        if not forzar_actualizacion and simbolo in self._cache_precios:
            return self._cache_precios[simbolo]

        # Obtener desde yfinance
        try:
            accion = yf.Ticker(simbolo)
            # history(period="1d") es la forma más confiable de obtener el precio de cierre más reciente en yfinance
            historial = accion.history(period="1d")

            if historial.empty:
                print(f"Advertencia: no se pudo obtener datos para {simbolo}")
                return None

            precio_actual = float(historial['Close'].iloc[-1])

            # Guardar en la Tabla Hash
            self._cache_precios[simbolo] = precio_actual
            self._ultima_actualizacion[simbolo] = datetime.now()

            return precio_actual

        except Exception as e:
            print(f"Error al obtener el precio de {simbolo}: {e}")
            # Recurrir a la caché si la API falla pero tenemos datos anteriores
            return self._cache_precios.get(simbolo)

    def establecer_precio(self, simbolo: str, precio: float):
        """
        Inyecta manualmente un precio en la caché (útil para pruebas o para sobrescribir).
        """
        simbolo = simbolo.upper()
        self._cache_precios[simbolo] = precio
        self._ultima_actualizacion[simbolo] = datetime.now()

    def obtener_simbolos_en_cache(self) -> list:
        return list(self._cache_precios.keys())
