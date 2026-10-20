"""Etiquetas en español para mostrar en el formulario.

El modelo trabaja con los códigos originales del dataset (por ejemplo, "bed_bath_table").
Estas etiquetas solo cambian lo que ve el usuario; al modelo siempre se le envía el código.
"""

ESTADOS = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahía", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Río de Janeiro", "RN": "Río Grande del Norte", "RO": "Rondônia",
    "RR": "Roraima", "RS": "Río Grande del Sur", "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo",
    "TO": "Tocantins",
}

MEDIOS_PAGO = {
    "credit_card": "Tarjeta de crédito",
    "debit_card": "Tarjeta de débito",
    "boleto": "Boleto bancario (pago en efectivo)",
    "voucher": "Voucher / cupón",
}

CATEGORIAS = {
    "agro_industry_and_commerce": "Agroindustria y comercio",
    "air_conditioning": "Aire acondicionado",
    "art": "Arte",
    "arts_and_craftmanship": "Artesanía",
    "audio": "Audio",
    "auto": "Automotriz",
    "baby": "Bebés",
    "bed_bath_table": "Cama, baño y mesa",
    "books_general_interest": "Libros de interés general",
    "books_imported": "Libros importados",
    "books_technical": "Libros técnicos",
    "cds_dvds_musicals": "CD, DVD y musicales",
    "christmas_supplies": "Artículos de Navidad",
    "cine_photo": "Cine y fotografía",
    "computers": "Computadores",
    "computers_accessories": "Accesorios de computación",
    "consoles_games": "Consolas y videojuegos",
    "construction_tools_construction": "Herramientas de construcción",
    "construction_tools_lights": "Iluminación (construcción)",
    "construction_tools_safety": "Seguridad (construcción)",
    "cool_stuff": "Artículos novedosos",
    "costruction_tools_garden": "Herramientas de jardín (construcción)",
    "costruction_tools_tools": "Herramientas (construcción)",
    "diapers_and_hygiene": "Pañales e higiene",
    "drinks": "Bebidas",
    "dvds_blu_ray": "DVD y Blu-ray",
    "electronics": "Electrónica",
    "fashio_female_clothing": "Ropa de mujer",
    "fashion_bags_accessories": "Bolsos y accesorios",
    "fashion_childrens_clothes": "Ropa infantil",
    "fashion_male_clothing": "Ropa de hombre",
    "fashion_shoes": "Calzado",
    "fashion_underwear_beach": "Ropa interior y de playa",
    "fixed_telephony": "Telefonía fija",
    "food": "Alimentos",
    "food_drink": "Alimentos y bebidas",
    "furniture_bedroom": "Muebles de dormitorio",
    "furniture_decor": "Muebles y decoración",
    "furniture_living_room": "Muebles de living",
    "furniture_mattress_and_upholstery": "Colchones y tapicería",
    "garden_tools": "Herramientas de jardín",
    "health_beauty": "Salud y belleza",
    "home_appliances": "Electrodomésticos",
    "home_appliances_2": "Electrodomésticos (línea 2)",
    "home_confort": "Confort del hogar",
    "home_construction": "Construcción del hogar",
    "housewares": "Artículos para el hogar",
    "industry_commerce_and_business": "Industria, comercio y negocios",
    "kitchen_dining_laundry_garden_furniture": "Muebles de cocina, comedor, lavandería y jardín",
    "la_cuisine": "Cocina gourmet",
    "luggage_accessories": "Maletas y accesorios de viaje",
    "market_place": "Marketplace",
    "music": "Música",
    "musical_instruments": "Instrumentos musicales",
    "office_furniture": "Muebles de oficina",
    "party_supplies": "Artículos de fiesta",
    "perfumery": "Perfumería",
    "pet_shop": "Mascotas",
    "signaling_and_security": "Señalización y seguridad",
    "small_appliances": "Pequeños electrodomésticos",
    "small_appliances_home_oven_and_coffee": "Hornos y cafeteras",
    "sports_leisure": "Deportes y ocio",
    "stationery": "Papelería",
    "tablets_printing_image": "Tablets, impresión e imagen",
    "telephony": "Telefonía",
    "toys": "Juguetes",
    "watches_gifts": "Relojes y regalos",
}


def etiqueta(diccionario, codigo):
    """Devuelve la etiqueta en español; si no existe, una versión legible del código."""
    return diccionario.get(codigo, str(codigo).replace("_", " ").capitalize())
