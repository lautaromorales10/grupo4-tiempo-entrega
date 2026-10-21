# Estimador de tiempo de entrega · E-commerce

Proyecto Semestral de **Análisis de Negocios (IND-163C)**, UTFSM 2026-02 · **Grupo 4**

| Integrante | ROL | Rol principal en el proyecto |
|---|---|---|
| Lautaro Morales | 202160640-8 | Modelamiento predictivo y despliegue de la aplicación |
| Vicente Vergara | 202160591-6 | Redacción del informe: dataset, EDA y preprocesamiento |
| Joaquín Valero | 202160609-2 | Redacción del informe: modelos, evaluación y K-Fold |
| Maximiliano Espinosa | 202160605-k | Presentación y preparación de la defensa |

## Objetivo y problema de negocio

Una plataforma de comercio electrónico quiere estimar, **en el momento en que el cliente compra**, cuántos días tardará el pedido en llegar. Una estimación precisa permite comunicar plazos realistas, planificar la logística y detectar a tiempo los pedidos con riesgo de demora.

El problema es de **regresión supervisada**: la variable objetivo es `DELIVERY_TIME_DAYS` (días entre la compra y la entrega al cliente).

## Dataset

`data/Dataset_Ordenes_Comp E-Commerce.xlsx`: 7.000 órdenes históricas anonimizadas (2016-2018) con información de la orden, los productos, el cliente, el vendedor, el pago y la logística. Cada fila es una orden. Se usan las **6.791 órdenes entregadas** (las demás no tienen target).

La dificultad central del dataset es la **fuga de información (data leakage)**: varias columnas solo se conocen después de la compra (despacho al transportista, atraso respecto de lo estimado, reseñas, etc.). El modelo usa **solo variables disponibles al momento de la compra**.

## Modelo seleccionado

**Gradient Boosting (`GradientBoostingRegressor`)**, elegido entre Elastic Net, Random Forest y Gradient Boosting (además de dos baselines).

| Hiperparámetro | Valor |
|---|---|
| `n_estimators` | 220 |
| `learning_rate` | 0,05 |
| `max_depth` | 4 |
| `min_samples_leaf` | 20 |
| `subsample` | 0,8 |

| Métrica | K-Fold (K=5, Train) | Test |
|---|---|---|
| MAE (días) | 4,62 ± 0,04 | 4,51 |
| RMSE (días) | 7,34 ± 0,61 | 6,75 |
| R² | 0,32 ± 0,04 | 0,36 |
| Sesgo (días) | −0,15 | −0,19 |

Como referencia, la estimación actual de la plataforma tiene un MAE de **12,5 días** en el mismo conjunto de prueba.

## Estructura del proyecto

```
├── app.py                  # Aplicación Flask (rutas y vistas)
├── requirements.txt        # Dependencias (app + notebook)
├── .python-version         # Versión de Python para Render
├── notebooks/
│   └── Proyecto_Grupo4_Tiempo_Entrega.ipynb   # Análisis completo: EDA → modelos → K-Fold → exportación
├── utils/
│   ├── features.py         # Ingeniería de variables (la usan el notebook Y la app)
│   ├── modelo.py           # Carga del modelo, geocodificación de ciudades y predicción
│   ├── validacion.py       # Validación de las entradas del formulario
│   └── etiquetas.py        # Nombres en español de estados, categorías y medios de pago
├── models/
│   ├── modelo_final.joblib # Pipeline completo entrenado (preprocesamiento + modelo)
│   └── metadata.json       # Métricas, hiperparámetros, rango probable y valores válidos
├── data/
│   ├── Dataset_Ordenes_Comp E-Commerce.xlsx   # Dataset original
│   └── ciudades.csv        # Coordenadas por ciudad (generado por el notebook)
├── templates/              # base.html, index.html (formulario), resultado.html, modelo.html, error.html
└── static/                 # css/style.css, js/app.js, img/icono.svg
```

**Coherencia entre el análisis y la app:** el notebook exporta el `Pipeline` completo de scikit-learn (variables derivadas → imputación → escalamiento → dummies → modelo) en `models/modelo_final.joblib`. La app carga ese mismo archivo y le entrega los datos del formulario sin transformarlos a mano, de modo que el preprocesamiento es idéntico. Las variables derivadas (distancia, ratio de flete, mes/día/hora) están en `utils/features.py`, que importan ambos.

## Cómo funciona la aplicación

1. **Formulario** (`/`): el usuario ingresa la fecha de compra, el plazo que informa la plataforma, el estado y la ciudad del cliente y del vendedor, la categoría, la cantidad de ítems y vendedores, el precio, el flete, el peso, las dimensiones, el medio de pago y las cuotas. Incluye tres ejemplos precargados para la demostración.
2. **Validación** (`utils/validacion.py`): los campos obligatorios, los rangos válidos y las categorías conocidas se revisan en el navegador y de nuevo en el servidor. Si un valor es válido pero queda fuera del rango visto en el entrenamiento, se muestra un aviso.
3. **Ubicación**: la ciudad se convierte en coordenadas con `data/ciudades.csv`. Si no se encuentra, se usa el centro aproximado del estado y se avisa al usuario.
4. **Resultado** (`/predecir`): días estimados, fecha estimada de llegada, **rango probable del 80%** (calculado con los errores de la validación cruzada) y comparación con el plazo de la plataforma.
5. **Sobre el modelo** (`/modelo`): hiperparámetros, métricas y variables usadas.
6. `/salud` responde `{"estado": "ok"}` para verificar que el servicio está activo.

## Ejecución local

Requisitos: **Python 3.12 o superior** (recomendado 3.13; numpy 2.5 y scipy 1.18 no se instalan en versiones anteriores). Las versiones exactas de las librerías están en `requirements.txt`.

```bash
# 1. Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
python app.py
```

Abrir **http://127.0.0.1:5000** en el navegador.

Para volver a ejecutar el análisis, abrir `notebooks/Proyecto_Grupo4_Tiempo_Entrega.ipynb` con Jupyter o VS Code desde la carpeta del proyecto. Tarda unos 20-30 minutos, porque hace muchas validaciones cruzadas. Al final regenera `models/modelo_final.joblib`, `models/metadata.json` y `data/ciudades.csv`.

> **Importante:** el modelo se guardó con scikit-learn 1.9.1. Si se vuelve a entrenar con otra versión, actualizar `requirements.txt` con esa versión; si la app carga el modelo con una versión distinta, puede fallar.

## Despliegue en Render

**Modalidad seleccionada:** despliegue en la nube con GitHub + Render (la ejecución local queda documentada como respaldo).

1. Crear un repositorio vacío en GitHub y subir esta carpeta (rama `main`):
   ```bash
   git init && git add . && git commit -m "Proyecto Grupo 4"
   git branch -M main
   git remote add origin https://github.com/<usuario>/<repositorio>.git
   git push -u origin main
   ```
2. En Render: **New → Web Service** → conectar el repositorio.
3. Configuración:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
4. **Versión de Python:** el archivo `.python-version` (contenido: `3.13`) hace que Render use la última versión 3.13. Sin él, Render usaría su versión por defecto (3.14 para servicios nuevos). Si algo falla, también se puede fijar con la variable de entorno `PYTHON_VERSION` y una versión completa, por ejemplo `3.13.5`; esa variable tiene prioridad sobre el archivo.
5. Probar la URL pública desde otro dispositivo.

**URL pública:** (https://grupo4-tiempo-entrega.onrender.com/) 
**Repositorio GitHub:** (https://github.com/lautaromorales10/grupo4-tiempo-entrega)

> En el plan gratuito, Render "duerme" el servicio después de unos minutos sin visitas y tarda alrededor de un minuto en despertar. **Abrir la URL unos minutos antes de la presentación.**
