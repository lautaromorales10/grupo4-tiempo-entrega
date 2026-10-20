"""Carga del modelo entrenado y generación de predicciones."""

import json
from datetime import timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from utils.features import ENTRADAS, distancia_haversine_km

RAIZ = Path(__file__).resolve().parent.parent
RUTA_MODELO = RAIZ / "models" / "modelo_final.joblib"
RUTA_METADATA = RAIZ / "models" / "metadata.json"
RUTA_CIUDADES = RAIZ / "data" / "ciudades.csv"


def cargar_recursos():
    """Carga el Pipeline entrenado (el mismo del notebook), sus metadatos y la tabla de ciudades."""
    modelo = joblib.load(RUTA_MODELO)
    with open(RUTA_METADATA, encoding="utf-8") as f:
        metadata = json.load(f)
    ciudades = pd.read_csv(RUTA_CIUDADES)
    return modelo, metadata, ciudades


class Geocodificador:
    """Convierte (estado, ciudad) en coordenadas usando la tabla data/ciudades.csv.

    Si la ciudad no está en la tabla, usa el centro aproximado del estado (mediana de sus ciudades).
    """

    def __init__(self, ciudades):
        self.tabla = ciudades.copy()
        self.tabla["clave"] = self.tabla["ciudad"].str.strip().str.lower()
        self.centros = self.tabla.groupby("estado")[["lat", "lng"]].median()

    def ciudades_de(self, estado):
        sub = self.tabla[self.tabla["estado"] == estado].sort_values("ordenes", ascending=False)
        return sub["ciudad"].tolist()

    def ubicar(self, estado, ciudad):
        """Devuelve (lat, lng, origen) donde origen es 'ciudad' o 'estado'."""
        clave = (ciudad or "").strip().lower()
        fila = self.tabla[(self.tabla["estado"] == estado) & (self.tabla["clave"] == clave)]
        if clave and len(fila):
            return float(fila["lat"].iloc[0]), float(fila["lng"].iloc[0]), "ciudad"
        if estado in self.centros.index:
            c = self.centros.loc[estado]
            return float(c["lat"]), float(c["lng"]), "estado"
        return np.nan, np.nan, "desconocido"


def predecir(modelo, metadata, datos):
    """Recibe un diccionario con las ENTRADAS del modelo y devuelve el resultado listo para mostrar."""
    fila = pd.DataFrame([{c: datos.get(c) for c in ENTRADAS}])
    dias = float(modelo.predict(fila)[0])
    dias = max(dias, 0.5)  # protección: un tiempo de entrega no puede ser negativo

    q_inf = metadata["rango_probable"]["q_inf"]
    q_sup = metadata["rango_probable"]["q_sup"]
    fecha_compra = pd.to_datetime(datos["order_purchase_timestamp"])
    distancia = float(distancia_haversine_km(datos["customer_geo_lat"], datos["customer_geo_lng"],
                                             datos["first_seller_geo_lat"], datos["first_seller_geo_lng"]))
    return {
        "dias": dias,
        "dias_min": dias * q_inf,
        "dias_max": dias * q_sup,
        "fecha_estimada": fecha_compra + timedelta(days=dias),
        "fecha_min": fecha_compra + timedelta(days=dias * q_inf),
        "fecha_max": fecha_compra + timedelta(days=dias * q_sup),
        "dias_plataforma": float(datos["estimated_delivery_days"]),
        "distancia_km": distancia,
    }
