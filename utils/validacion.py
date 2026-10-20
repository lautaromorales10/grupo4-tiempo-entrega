"""Validación de los datos del formulario y conversión a las entradas del modelo."""

from datetime import datetime

# Límites de validez (rechazan valores imposibles o claramente erróneos).
# Son más amplios que el rango de entrenamiento; si un valor válido queda fuera
# de lo que el modelo vio en Train, se muestra un aviso en vez de un error.
LIMITES = {
    "plazo_plataforma": (1, 120, "El plazo informado por la plataforma"),
    "n_items": (1, 30, "La cantidad de ítems"),
    "n_vendedores": (1, 10, "La cantidad de vendedores"),
    "precio_total": (0.5, 20000, "El precio total"),
    "flete_total": (0, 2000, "El flete total"),
    "peso_g": (1, 100000, "El peso"),
    "largo_cm": (1, 250, "El largo"),
    "alto_cm": (1, 250, "El alto"),
    "ancho_cm": (1, 250, "El ancho"),
    "cuotas": (1, 24, "El número de cuotas"),
}
ENTEROS = {"n_items", "n_vendedores", "cuotas"}

CAMPOS = ["fecha_compra", "plazo_plataforma", "estado_cliente", "ciudad_cliente", "estado_vendedor", "ciudad_vendedor",
          "categoria", "n_items", "n_vendedores", "precio_total", "flete_total", "peso_g", "largo_cm", "alto_cm",
          "ancho_cm", "medio_pago", "cuotas"]

# Nombre de la entrada del modelo -> texto para los avisos de rango
NOMBRES_RANGO = {
    "estimated_delivery_days": "plazo de la plataforma (días)",
    "order_item_count": "cantidad de ítems",
    "unique_seller_count": "cantidad de vendedores",
    "total_item_price": "precio total (R$)",
    "total_freight_value": "flete total (R$)",
    "avg_product_weight_g": "peso (g)",
    "avg_product_volume_cm3": "volumen (cm³)",
    "payment_max_installments": "cuotas",
}


def _numero(texto):
    return float(str(texto).strip().replace(",", "."))


def validar_formulario(form, metadata, geo):
    """Devuelve (datos_modelo, errores, avisos).

    - datos_modelo: diccionario con las ENTRADAS del modelo (None si hay errores).
    - errores: {campo: mensaje} que impiden predecir.
    - avisos: lista de mensajes informativos (la predicción se hace igual).
    """
    errores, avisos, valores = {}, [], {}
    cats = metadata["categorias"]

    # Campos obligatorios
    for campo in CAMPOS:
        if campo.startswith("ciudad_"):
            continue  # la ciudad es opcional (si falta se usa el centro del estado)
        if not str(form.get(campo, "")).strip():
            errores[campo] = "Este campo es obligatorio."

    # Fecha de compra
    if "fecha_compra" not in errores:
        try:
            fecha = datetime.strptime(form["fecha_compra"].strip(), "%Y-%m-%dT%H:%M")
            if not 2000 <= fecha.year <= 2100:
                errores["fecha_compra"] = "Ingrese una fecha entre los años 2000 y 2100."
            valores["fecha_compra"] = fecha
        except ValueError:
            errores["fecha_compra"] = "Formato de fecha inválido."

    # Numéricos
    for campo, (minimo, maximo, nombre) in LIMITES.items():
        if campo in errores:
            continue
        try:
            v = _numero(form[campo])
        except (ValueError, TypeError):
            errores[campo] = "Debe ser un número."
            continue
        if campo in ENTEROS and v != int(v):
            errores[campo] = "Debe ser un número entero."
            continue
        if not minimo <= v <= maximo:
            errores[campo] = f"{nombre} debe estar entre {minimo:g} y {maximo:g}.".replace(".", ",").rstrip(",") + "."
            continue
        valores[campo] = int(v) if campo in ENTEROS else v

    if "n_items" in valores and "n_vendedores" in valores and valores["n_vendedores"] > valores["n_items"]:
        errores["n_vendedores"] = "No puede haber más vendedores que ítems."

    # Categóricas: deben ser valores conocidos por el modelo
    for campo, entrada in [("estado_cliente", "customer_state"), ("estado_vendedor", "first_seller_state"),
                           ("categoria", "first_product_category_en"), ("medio_pago", "payment_type_primary")]:
        if campo in errores:
            continue
        v = form[campo].strip()
        if v not in cats[entrada]:
            errores[campo] = "Seleccione una opción de la lista."
        else:
            valores[campo] = v

    if errores:
        return None, errores, avisos

    # Coordenadas a partir de la ciudad (o del centro del estado)
    lat_c, lng_c, origen_c = geo.ubicar(valores["estado_cliente"], form.get("ciudad_cliente"))
    lat_v, lng_v, origen_v = geo.ubicar(valores["estado_vendedor"], form.get("ciudad_vendedor"))
    for origen, quien, ciudad in [(origen_c, "cliente", form.get("ciudad_cliente")), (origen_v, "vendedor", form.get("ciudad_vendedor"))]:
        if origen == "estado":
            detalle = f"«{ciudad.strip()}» no está en la base de ciudades" if (ciudad or "").strip() else "no se indicó ciudad"
            avisos.append(f"Ubicación del {quien}: {detalle}; se usó el centro aproximado del estado.")

    datos = {
        "order_purchase_timestamp": valores["fecha_compra"].strftime("%Y-%m-%d %H:%M:%S"),
        "customer_geo_lat": lat_c, "customer_geo_lng": lng_c,
        "first_seller_geo_lat": lat_v, "first_seller_geo_lng": lng_v,
        "estimated_delivery_days": valores["plazo_plataforma"],
        "order_item_count": valores["n_items"],
        "unique_seller_count": valores["n_vendedores"],
        "total_item_price": valores["precio_total"],
        "total_freight_value": valores["flete_total"],
        "avg_product_weight_g": valores["peso_g"],
        "avg_product_volume_cm3": valores["largo_cm"] * valores["alto_cm"] * valores["ancho_cm"],
        "payment_max_installments": valores["cuotas"],
        "customer_state": valores["estado_cliente"],
        "first_seller_state": valores["estado_vendedor"],
        "payment_type_primary": valores["medio_pago"],
        "first_product_category_en": valores["categoria"],
    }

    # Avisos de extrapolación: valores válidos, pero fuera de lo observado en Train
    for entrada, nombre in NOMBRES_RANGO.items():
        lo, hi = metadata["rangos_train"][entrada]
        if not lo <= datos[entrada] <= hi:
            avisos.append(f"El valor de {nombre} ({datos[entrada]:,.0f}) está fuera del rango visto en el entrenamiento "
                          f"({lo:,.0f} a {hi:,.0f}); la predicción puede ser menos confiable.")
    return datos, errores, avisos
