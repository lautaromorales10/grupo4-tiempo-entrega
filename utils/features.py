"""
Ingeniería de variables compartida entre el notebook y la aplicación web.

Este módulo es la única fuente de verdad sobre qué variables usa el modelo.
El notebook lo importa para entrenar y la app lo importa para predecir, de
modo que ambos aplican exactamente la misma transformación.

Todas las transformaciones de este archivo son "sin estado": no aprenden
nada de los datos (no calculan medias, medianas ni categorías). Por eso se
pueden aplicar antes del Train/Test Split sin riesgo de filtrar información
del conjunto de prueba. Lo que sí aprende de los datos (imputación,
escalamiento, codificación) está dentro del Pipeline de scikit-learn y se
ajusta solo con Train.
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Variables de entrada (lo que se conoce en el momento de la compra)
# ---------------------------------------------------------------------------
COL_FECHA_COMPRA = "order_purchase_timestamp"

ENTRADAS_NUMERICAS = [
    "customer_geo_lat",
    "customer_geo_lng",
    "first_seller_geo_lat",
    "first_seller_geo_lng",
    "estimated_delivery_days",
    "order_item_count",
    "unique_seller_count",
    "total_item_price",
    "total_freight_value",
    "avg_product_weight_g",
    "avg_product_volume_cm3",
    "payment_max_installments",
]

ENTRADAS_CATEGORICAS = [
    "customer_state",
    "first_seller_state",
    "payment_type_primary",
    "first_product_category_en",
]

ENTRADAS = [COL_FECHA_COMPRA] + ENTRADAS_NUMERICAS + ENTRADAS_CATEGORICAS

# ---------------------------------------------------------------------------
# Variables que recibe el Pipeline (entradas + variables derivadas)
# ---------------------------------------------------------------------------
DERIVADAS_NUMERICAS = [
    "distancia_km",
    "ratio_flete",
    "mismo_estado",
    "mes_compra",
    "dia_semana_compra",
    "hora_compra",
]

VARIABLES_NUMERICAS = [c for c in ENTRADAS_NUMERICAS] + DERIVADAS_NUMERICAS
VARIABLES_CATEGORICAS = list(ENTRADAS_CATEGORICAS)
VARIABLES_MODELO = VARIABLES_NUMERICAS + VARIABLES_CATEGORICAS

TARGET = "DELIVERY_TIME_DAYS"


def distancia_haversine_km(lat1, lng1, lat2, lng2):
    """Distancia en línea recta (sobre la esfera terrestre) entre dos puntos, en km."""
    radio_tierra = 6371.0
    lat1, lng1, lat2, lng2 = (np.radians(np.asarray(v, dtype=float)) for v in (lat1, lng1, lat2, lng2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2)
    return 2 * radio_tierra * np.arcsin(np.sqrt(a))


def construir_variables(df):
    """Recibe un DataFrame con las ENTRADAS y devuelve las VARIABLES_MODELO.

    - distancia_km: distancia cliente-vendedor (si falta una coordenada queda NaN
      y la imputa el Pipeline).
    - ratio_flete: proporción del flete sobre el total pagado (flete / (precio + flete)).
    - mismo_estado: 1 si cliente y vendedor están en el mismo estado.
    - mes, día de la semana (0 = lunes) y hora de la compra.
    """
    X = df.copy()
    fecha = pd.to_datetime(X[COL_FECHA_COMPRA], errors="coerce")

    X["distancia_km"] = distancia_haversine_km(
        X["customer_geo_lat"], X["customer_geo_lng"],
        X["first_seller_geo_lat"], X["first_seller_geo_lng"],
    )
    total = X["total_item_price"].astype(float) + X["total_freight_value"].astype(float)
    X["ratio_flete"] = np.where(total > 0, X["total_freight_value"].astype(float) / total, np.nan)
    X["mismo_estado"] = (X["customer_state"].astype(str) == X["first_seller_state"].astype(str)).astype(int)
    X["mes_compra"] = fecha.dt.month
    X["dia_semana_compra"] = fecha.dt.dayofweek
    X["hora_compra"] = fecha.dt.hour

    for c in VARIABLES_CATEGORICAS:
        X[c] = X[c].astype(object)

    return X[VARIABLES_MODELO]
