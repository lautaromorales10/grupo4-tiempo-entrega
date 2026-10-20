"""Aplicación web Flask: estimación del tiempo de entrega de una orden de e-commerce.

Ejecutar localmente:   python app.py        -> http://127.0.0.1:5000
En Render:             gunicorn app:app
"""

from datetime import datetime

from flask import Flask, jsonify, render_template, request

from utils.etiquetas import CATEGORIAS, ESTADOS, MEDIOS_PAGO, etiqueta
from utils.modelo import Geocodificador, cargar_recursos, predecir
from utils.validacion import validar_formulario

app = Flask(__name__)

# Se cargan una sola vez al iniciar la app (no en cada predicción)
MODELO, METADATA, CIUDADES = cargar_recursos()
GEO = Geocodificador(CIUDADES)

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


@app.template_filter("num")
def formato_numero(valor, decimales=1):
    """12345.6 -> '12.345,6' (formato chileno)."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


@app.template_filter("fecha")
def formato_fecha(valor):
    return f"{DIAS[valor.weekday()]} {valor.day} de {MESES[valor.month - 1]} de {valor.year}"


def opciones_formulario():
    cats = METADATA["categorias"]
    return {
        "estados": [(c, f"{c} · {etiqueta(ESTADOS, c)}") for c in cats["customer_state"]],
        "estados_vendedor": [(c, f"{c} · {etiqueta(ESTADOS, c)}") for c in cats["first_seller_state"]],
        "categorias": sorted(((c, etiqueta(CATEGORIAS, c)) for c in cats["first_product_category_en"]), key=lambda x: x[1]),
        "medios_pago": [(c, etiqueta(MEDIOS_PAGO, c)) for c in cats["payment_type_primary"]],
    }


def valores_por_defecto():
    """Ejemplo inicial del formulario: una compra típica de Río de Janeiro a un vendedor de São Paulo."""
    return {
        "fecha_compra": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "plazo_plataforma": "24", "estado_cliente": "RJ", "ciudad_cliente": "rio de janeiro",
        "estado_vendedor": "SP", "ciudad_vendedor": "sao paulo", "categoria": "bed_bath_table",
        "n_items": "1", "n_vendedores": "1", "precio_total": "89.90", "flete_total": "17.50",
        "peso_g": "900", "largo_cm": "30", "alto_cm": "10", "ancho_cm": "25", "medio_pago": "credit_card", "cuotas": "2",
    }


@app.route("/")
def inicio():
    return render_template("index.html", valores=valores_por_defecto(), errores={}, **opciones_formulario())


@app.route("/predecir", methods=["POST"])
def prediccion():
    form = {k: v for k, v in request.form.items()}
    datos, errores, avisos = validar_formulario(form, METADATA, GEO)
    if errores:
        return render_template("index.html", valores=form, errores=errores, **opciones_formulario()), 400
    resultado = predecir(MODELO, METADATA, datos)
    resumen = {
        "Fecha de compra": formato_fecha(datetime.strptime(form["fecha_compra"], "%Y-%m-%dT%H:%M")) + " · " + form["fecha_compra"][-5:] + " h",
        "Cliente": f"{form.get('ciudad_cliente') or '(sin ciudad)'} · {form['estado_cliente']}",
        "Vendedor": f"{form.get('ciudad_vendedor') or '(sin ciudad)'} · {form['estado_vendedor']}",
        "Distancia cliente-vendedor": f"{formato_numero(resultado['distancia_km'], 0)} km",
        "Categoría": etiqueta(CATEGORIAS, form["categoria"]),
        "Ítems / vendedores": f"{form['n_items']} / {form['n_vendedores']}",
        "Precio + flete": f"R$ {formato_numero(datos['total_item_price'], 2)} + R$ {formato_numero(datos['total_freight_value'], 2)}",
        "Peso y volumen": f"{formato_numero(datos['avg_product_weight_g'], 0)} g · {formato_numero(datos['avg_product_volume_cm3'], 0)} cm³",
        "Pago": f"{etiqueta(MEDIOS_PAGO, form['medio_pago'])} · {form['cuotas']} cuota(s)",
    }
    return render_template("resultado.html", r=resultado, avisos=avisos, resumen=resumen, meta=METADATA)


@app.route("/modelo")
def acerca_del_modelo():
    return render_template("modelo.html", meta=METADATA)


@app.route("/api/ciudades")
def api_ciudades():
    estado = request.args.get("estado", "")
    return jsonify(GEO.ciudades_de(estado))


@app.route("/salud")
def salud():
    return jsonify({"estado": "ok", "modelo": METADATA["modelo"]})


@app.errorhandler(404)
def no_encontrado(_):
    return render_template("error.html", mensaje="La página que buscas no existe."), 404


@app.errorhandler(500)
def error_interno(_):
    return render_template("error.html", mensaje="Ocurrió un error inesperado al procesar la solicitud."), 500


if __name__ == "__main__":
    app.run(debug=False)
