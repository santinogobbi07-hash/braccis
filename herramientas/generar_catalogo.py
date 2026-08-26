# -*- coding: utf-8 -*-
"""
Braccis - generador del catalogo
================================

Lee los PDF de catalogo, saca la foto de cada prenda y reescribe
js/productos.js con los datos de abajo.

Como se usa
-----------
1. Copiar los PDF nuevos a la carpeta catalogos/
2. Actualizar la lista PRENDAS de este archivo (una linea por prenda)
3. Correr:   python herramientas/generar_catalogo.py

Requiere una sola vez:   pip install pymupdf pillow

OJO: esto PISA js/productos.js. Si editaste ese archivo a mano
(precios, descripciones), pasa esos cambios aca primero.
"""

import io
import os
import sys
from collections import deque

try:
    import pymupdf
    from PIL import Image
except ImportError:
    sys.exit("Falta instalar las librerias. Corre:  pip install pymupdf pillow")

# ---------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_FOTOS = os.path.join(RAIZ, "img", "prendas")
SALIDA_JS = os.path.join(RAIZ, "js", "productos.js")

# Donde estan los PDF. Primero busca en catalogos/, si no en Descargas.
CATALOGOS = {
    "jeans":   ["catalogos/JEANS.pdf",   r"C:\Users\Usuario\Downloads\JEANS (3).pdf"],
    "remeras": ["catalogos/REMERAS.pdf", r"C:\Users\Usuario\Downloads\CAP REMERAS .pdf"],
    "hilo":    ["catalogos/HILO.pdf",    r"C:\Users\Usuario\Downloads\HILO.pdf"],
    "camisas": ["catalogos/CAMISAS.pdf", r"C:\Users\Usuario\Downloads\CAMISAS (2).pdf"],
}

# La plantilla de fondo se repite en todas las paginas: hay que ignorarla
FONDO = (950, 1342)

# --- Como se separan las fotos de verdad de los circulitos de color ---
#
# Cada pagina del catalogo tiene, ademas de las fotos, los circulitos que
# muestran los colores disponibles. Y aca esta la trampa: esos circulitos NO
# son imagenes chiquitas. Son fotos grandes (a veces la foto de OTRA prenda)
# colocadas en grande y recortadas a un circulo de pocos milimetros.
#
# Por eso no alcanza con mirar el tamano del archivo ni el espacio que ocupan:
# hay que fijarse en lo que se ve. El truco es renderizar la pagina y medir
# que porcentaje de la zona quedo del color crema del fondo. Un circulito tapa
# casi toda su zona con crema; una foto de verdad, no.
#
# Medido sobre 10 paginas de los 4 catalogos:
#     fotos reales ....... entre 13% y 53% de crema
#     circulitos ......... entre 62% y 87% de crema
DPI_CONTROL = 130
MAX_CREMA = 0.58          # de aca para arriba, es un circulito
MIN_AREA_DIBUJADA = 5000  # en puntos cuadrados, para descartar cositas sueltas

# ---------------------------------------------------------------
# Categorias que se muestran como filtros en el catalogo
# ---------------------------------------------------------------
CATEGORIAS = [
    ("remeras", "Remeras"),
    ("camisas", "Camisas"),
    ("blusas",  "Blusas"),
    ("tejidos", "Tejidos"),
    ("jeans",   "Jeans"),
]

# ---------------------------------------------------------------
# Muestras de color
# ---------------------------------------------------------------
# NO hay una tabla de colores inventada. La muestra que se ve en la web
# es el circulito recortado del propio PDF, tal cual lo dibuja el catalogo:
#   - en la capsula de remeras son fotos de la tela
#   - en camisas y poleras son la prenda puesta, en ese color
#
# Cuando el catalogo no dibuja circulito (le pasa a casi toda la capsula
# de hilo, que lista los colores solo por escrito), no se muestra ninguna
# bolita: va el nombre del color y nada mas. Antes que inventar un color,
# preferimos no mostrar nada.
NOMBRES_DE_COLOR = {
    "BLANCO", "CRUDO", "NEGRO", "BEIGE", "ARENA", "CAMEL", "CHOCOLATE",
    "PARDO", "GRIS", "VERDE", "VERDE M", "ESMERALDA", "AZUL", "CELESTE",
    "BORDO", "MOSTAZA", "MOZTAZA",
}
EQUIVALENCIAS = {"MOZTAZA": "MOSTAZA"}
CARPETA_COLORES = os.path.join(RAIZ, "img", "colores")
DPI_COLORES = 300
ANCHO_ANALISIS = 150      # a cuanto se reduce la zona para buscar el disco
LADO_MUESTRA = 72         # tamano del PNG que se guarda

# Talles usados seguido, para no repetirlos en cada linea
S_XL = ["S", "M", "L", "XL"]
UNICO = ["Único"]
JEAN = ["26", "28", "30", "32", "34", "36"]

# ---------------------------------------------------------------
# LAS PRENDAS
# (catalogo, pagina del PDF, id, nombre, codigo, categoria,
#  talles, colores, descripcion)
# ---------------------------------------------------------------
PRENDAS = [
    # ---------------- JEANS ----------------
    ("jeans", 2,  "jeans-repro",      "Jeans Chupín Repro",       "27V4101", "jeans", JEAN, [], "Jeans chupín de tiro medio, elastizado."),
    ("jeans", 3,  "jeans-gain",       "Jeans Gain Black Oxford",  "A26I4087", "jeans", JEAN, [], "Jeans oxford semielastizado."),
    ("jeans", 4,  "jeans-cird",       "Jeans Oxford Cird",        "27V4105", "jeans", JEAN, [], "Jeans oxford de tiro medio, elastizado."),
    ("jeans", 5,  "jeans-tampa",      "Jeans Tampa Recto",        "A26I4034", "jeans", JEAN, [], "Jeans recto de tiro medio, elastizado."),
    ("jeans", 6,  "jeans-kady",       "Jeans Recto Kady",         "27V4106", "jeans", JEAN, [], "Jeans recto de tiro medio, elastizado."),
    ("jeans", 7,  "jeans-black-moon", "Jeans Black Moon Chupín",  "A26I4086", "jeans", JEAN, [], "Jeans chupín elastizado."),
    ("jeans", 8,  "jeans-sunny",      "Jeans Sunny",              "27V4103", "jeans", ["24", "28", "30", "32", "34"], [], "Jeans wide leg de tiro medio con apliques frontales."),
    ("jeans", 9,  "jeans-glam",       "Jeans Recto Glam",         "27V4104", "jeans", JEAN, [], "Jeans recto elastizado, tiro medio con apliques laterales."),
    ("jeans", 10, "jeans-black-night","Jeans Recto Black Night",  "27V4102", "jeans", JEAN, [], "Jeans recto elastizado, tiro medio con apliques frontales."),
    ("jeans", 11, "jeans-seiano",     "Jeans Wide Leg Seiano",    "A26I4078", "jeans", ["24", "26", "28", "30", "32", "34"], [], "Jeans wide leg de tiro medio, elastizado."),

    # ---------------- REMERAS ----------------
    ("remeras", 2,  "sunflower",  "Remera Sunflower",   "27V2210", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello redondo con estampa."),
    ("remeras", 3,  "roking",     "Remera Roking",      "27V2209", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello redondo con estampa."),
    ("remeras", 4,  "libel",      "Remera Libel",       "27V2208", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello redondo con estampa."),
    ("remeras", 5,  "infinity",   "Remera Infinity",    "27V2207", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello V con estampa."),
    ("remeras", 6,  "hummers",    "Remera Hummers",     "27V2206", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello V con estampa."),
    ("remeras", 7,  "somos",      "Remera Somos",       "27V2205", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello redondo con estampa."),
    ("remeras", 8,  "vive",       "Remera Vive",        "27V2204", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello redondo con estampa."),
    ("remeras", 9,  "cat-love",   "Remera Cat Love",    "27V2203", "remeras", S_XL, ["BLANCO", "NEGRO", "MOSTAZA", "GRIS", "VERDE"], "Remera de algodón, cuello redondo con estampa."),
    ("remeras", 10, "gio",        "Polera Gio",         "A26I2128", "remeras", S_XL, ["ARENA", "VERDE", "NEGRO", "CRUDO"], "Polera de morley."),
    ("remeras", 11, "moon-flower","Remera Moon Flower", "A26I2141", "remeras", S_XL, ["BLANCO", "CAMEL", "NEGRO"], "Remera de algodón, cuello redondo con estampa y detalle de corte en los laterales."),
    ("remeras", 12, "moon",       "Remera Moon",        "A26I2143", "remeras", S_XL, ["BLANCO", "AZUL", "NEGRO"], "Remera de algodón, cuello redondo con estampa y detalle de corte en los laterales."),
    ("remeras", 13, "trendy",     "Remera Trendy",      "A26I2161", "remeras", S_XL, ["NEGRO", "BLANCO"], "Remera de algodón, cuello redondo básica."),
    ("remeras", 14, "victoria",   "Remera Victoria",    "A26I2000", "remeras", S_XL, ["NEGRO", "BLANCO"], "Remera cuello V, 100% algodón."),
    ("remeras", 15, "perfectly",  "Remera Perfectly",   "A26I2142", "remeras", S_XL, ["BLANCO", "GRIS", "CHOCOLATE"], "Remera de algodón, cuello redondo con estampa y detalle de corte en los laterales."),
    ("remeras", 16, "karma",      "Remera Karma",       "A26I2153", "remeras", S_XL, ["BLANCO", "NEGRO"], "Remera de jersey, cuello redondo con estampa al frente."),
    ("remeras", 17, "be-you",     "Remera Be You",      "A26I2154", "remeras", S_XL, ["CRUDO", "NEGRO"], "Remera de jersey, cuello redondo con estampa al frente."),
    ("remeras", 18, "lirium",     "Remera Lirium",      "A26I2168", "remeras", S_XL, ["NEGRO", "BLANCO", "VERDE"], "Remera de algodón, cuello redondo con estampa."),
    ("remeras", 19, "jaguar",     "Remera Jaguar",      "A26I2167", "remeras", S_XL, ["VERDE M", "BLANCO", "MOSTAZA"], "Remera de algodón, cuello redondo con estampa."),

    # ---------------- TEJIDOS ----------------
    ("hilo", 2,  "idalia",   "Remera Tejida Idalia",   "27V00429", "tejidos", UNICO, ["BEIGE", "NEGRO", "CHOCOLATE"], "Remera tejida de talle único."),
    ("hilo", 3,  "sweater-esmeralda", "Sweater",       "A26I183",  "tejidos", UNICO, ["NEGRO", "CRUDO", "CHOCOLATE", "ESMERALDA"], "Sweater tejido de talle único."),
    ("hilo", 4,  "cowl-neck","Buzo Cowl Neck Rústico", "A26I6013", "tejidos", S_XL,  ["VERDE", "BEIGE"], "Buzo rústico con cuello cowl neck."),
    ("hilo", 5,  "chery",    "Remera Tejida Chery",    "27V00420", "tejidos", UNICO, ["BEIGE", "NEGRO", "CAMEL"], "Remera tejida de talle único."),
    ("hilo", 6,  "celina",   "Remera Tejida Celina",   "27V00408", "tejidos", UNICO, ["BEIGE", "NEGRO", "CHOCOLATE"], "Remera tejida de talle único."),
    ("hilo", 7,  "julieta",  "Remera Julieta",         "27V00408", "tejidos", UNICO, ["BEIGE", "NEGRO"], "Remera tejida de talle único."),
    ("hilo", 8,  "calista",  "Remera Tejida Calista",  "27V00428", "tejidos", UNICO, ["CRUDO", "BEIGE", "NEGRO"], "Remera tejida de talle único."),
    ("hilo", 9,  "africa",   "Sweater África",         "27V00177", "tejidos", UNICO, ["AZUL", "BEIGE", "GRIS"], "Sweater tejido de talle único."),
    ("hilo", 10, "beca",     "Musculosa Tejida Beca",  "27V00393", "tejidos", UNICO, ["BORDO", "BEIGE", "NEGRO", "CHOCOLATE", "BLANCO"], "Musculosa tejida de talle único."),
    ("hilo", 11, "marion",   "Remera Tejida Marion",   "27V00392", "tejidos", UNICO, ["CRUDO", "BEIGE", "NEGRO", "CHOCOLATE"], "Remera tejida de talle único."),
    ("hilo", 12, "analia",   "Remera Tejida Analía",   "27V00391", "tejidos", UNICO, ["CRUDO", "BEIGE", "NEGRO"], "Remera tejida de talle único."),
    ("hilo", 13, "nicky",    "Remera Tejida Nicky",    "27V00432", "tejidos", UNICO, ["CHOCOLATE", "CELESTE", "NEGRO"], "Remera tejida de talle único."),
    ("hilo", 14, "cassie",   "Remera Tejida Cassie",   "27V00394", "tejidos", UNICO, ["CAMEL", "BLANCO", "NEGRO"], "Remera tejida de talle único."),
    ("hilo", 15, "barbara",  "Remera Tejida Bárbara",  "27V00423", "tejidos", UNICO, ["CRUDO", "NEGRO", "CAMEL"], "Remera tejida de talle único."),
    ("hilo", 16, "kaia",     "Remera Tejida Kaia",     "27V00395", "tejidos", UNICO, ["BEIGE", "CHOCOLATE", "GRIS", "NEGRO"], "Remera tejida de talle único."),
    ("hilo", 17, "chantal",  "Remera Tejida Chantal",  "27V00424", "tejidos", UNICO, ["BLANCO", "NEGRO", "CHOCOLATE"], "Remera tejida de talle único."),
    ("hilo", 18, "cruella",  "Tejido Cruella",         "27V00427", "tejidos", UNICO, ["BEIGE", "NEGRO", "GRIS"], "Prenda tejida de talle único."),
    ("hilo", 19, "lauren",   "Chaleco Tejido Lauren",  "27V00430", "tejidos", UNICO, ["CHOCOLATE", "NEGRO", "CRUDO"], "Chaleco tejido de talle único."),
    ("hilo", 20, "galit",    "Vestido Galit",          "27V0086",  "tejidos", UNICO, ["CRUDO", "NEGRO", "CHOCOLATE"], "Vestido tejido de talle único."),

    # ---------------- CAMISAS Y BLUSAS ----------------
    ("camisas", 2, "era",     "Remera Era",     "A26I2123", "remeras", S_XL, ["NEGRO"], "Remera de foil, cuello redondo."),
    ("camisas", 3, "nidia",   "Blusa Nidia",    "27V00356", "blusas",  S_XL, ["NEGRO"], "Blusa de cuello redondo."),
    ("camisas", 4, "ons",     "Camisa Ons",     "27V1022",  "camisas", S_XL, ["PARDO", "CRUDO", "BEIGE"], "Camisa de lino."),
    ("camisas", 6, "plumety", "Blusa Plumety",  "27V1020",  "blusas",  S_XL, ["BLANCO", "NEGRO"], "Blusa de plumetí con manga japonesa."),
    ("camisas", 7, "dante",   "Camisa Dante",   "27V1021",  "camisas", S_XL, ["BLANCO", "NEGRO", "PARDO"], "Camisa de fibrana con apliques en cuello y puño."),
    ("camisas", 8, "dall",    "Camisa Dall",    "27V1023",  "camisas", S_XL, ["BLANCO", "NEGRO", "PARDO"], "Camisa de fibrana."),
]

# Prendas que van en la portada
DESTACADOS = {"jeans-seiano", "sunflower", "gio", "idalia", "ons", "plumety", "galit", "cowl-neck"}


# ---------------------------------------------------------------
def abrir_catalogo(clave):
    """Abre el PDF, probando primero catalogos/ y despues Descargas."""
    for ruta in CATALOGOS[clave]:
        completa = ruta if os.path.isabs(ruta) else os.path.join(RAIZ, ruta)
        if os.path.exists(completa):
            return pymupdf.open(completa)
    raise FileNotFoundError("No encontre el PDF de " + clave)


# Fondo sobre el que se apoyan las prendas recortadas (mismo crema del sitio)
FONDO_CREMA = (242, 236, 227)


def guardar(doc, img, destino, alto=1200):
    """Convierte una imagen del PDF a JPG y la deja en img/prendas/.

    Muchas fotos de los catalogos son recortes con fondo transparente. En el
    PDF la transparencia viaja aparte, en una imagen de mascara ("smask"), asi
    que hay que pegarlas sobre un fondo. Si no se hace, quedan sobre negro y
    con el borde manchado.
    """
    foto = Image.open(io.BytesIO(img["image"])).convert("RGB")

    if img.get("smask"):
        mascara = doc.extract_image(img["smask"])
        alfa = Image.open(io.BytesIO(mascara["image"])).convert("L")
        if alfa.size != foto.size:
            alfa = alfa.resize(foto.size, Image.LANCZOS)
        fondo = Image.new("RGB", foto.size, FONDO_CREMA)
        fondo.paste(foto, (0, 0), alfa)
        foto = fondo

    foto.thumbnail((int(alto * 0.75), alto), Image.LANCZOS)
    foto.save(destino, "JPEG", quality=82, optimize=True)


def _objetos(mask, an, al):
    """Recorre los objetos conectados de una zona (para separar el disco
    del texto de la etiqueta, de las lineas y de las fotos)."""
    visto = bytearray(an * al)
    for inicio in range(an * al):
        if mask[inicio] and not visto[inicio]:
            cola = deque([inicio])
            visto[inicio] = 1
            celdas = []
            while cola:
                i = cola.popleft()
                celdas.append(i)
                x, y = i % an, i // an
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < an and 0 <= ny < al:
                        j = ny * an + nx
                        if mask[j] and not visto[j]:
                            visto[j] = 1
                            cola.append(j)
            yield celdas


def buscar_disco(render, span, escala_pagina):
    """Ubica el circulito de color que va a la izquierda de una etiqueta.

    Devuelve la caja del disco dentro del render, o None si no hay
    ninguno (el catalogo no siempre los dibuja).
    """
    x0, y0, x1, y1 = span["bbox"]
    alto_letra = y1 - y0
    centro_y = (y0 + y1) / 2

    vx0 = max(0.0, x0 - alto_letra * 5.0)
    vx1 = x0 - alto_letra * 0.05
    vy0 = max(0.0, centro_y - alto_letra * 2.6)
    vy1 = centro_y + alto_letra * 2.6
    caja = tuple(int(v * escala_pagina) for v in (vx0, vy0, vx1, vy1))
    if caja[2] - caja[0] < 16 or caja[3] - caja[1] < 16:
        return None

    zona = render.crop(caja)
    escala = min(1.0, ANCHO_ANALISIS / zona.width)
    chica = zona.resize((max(8, int(zona.width * escala)),
                         max(8, int(zona.height * escala))))
    an, al = chica.size
    px = list(chica.getdata())

    # El color del papel se mide en el borde de la zona, que siempre es fondo.
    # Asi tambien aparecen los discos claros, que casi no contrastan.
    borde = ([px[i] for i in range(an)] +
             [px[(al - 1) * an + i] for i in range(an)] +
             [px[y * an] for y in range(al)] +
             [px[y * an + an - 1] for y in range(al)])
    fondo = tuple(sorted(p[c] for p in borde)[len(borde) // 2] for c in range(3))
    mask = bytearray(
        1 if any(abs(p[c] - fondo[c]) > 9 for c in range(3)) else 0
        for p in px
    )

    diam_min = alto_letra * 1.0 * escala_pagina * escala
    diam_max = alto_letra * 3.2 * escala_pagina * escala

    mejor = None
    for celdas in _objetos(mask, an, al):
        xs = [c % an for c in celdas]
        ys = [c // an for c in celdas]
        bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
        if bx0 <= 0 or by0 <= 0 or bx1 >= an - 1 or by1 >= al - 1:
            continue                                   # se sale: no es el disco
        ancho, altura = bx1 - bx0 + 1, by1 - by0 + 1
        if not (0.72 <= ancho / altura <= 1.40):
            continue                                   # no es redondo
        if not (diam_min <= ancho <= diam_max):
            continue                                   # tamano que no cierra
        if len(celdas) / (ancho * altura) < 0.62:
            continue                                   # un disco es macizo
        if mejor is None or bx1 > mejor[2]:            # el mas pegado al nombre
            mejor = (bx0, by0, bx1, by1)

    if not mejor:
        return None

    f = 1 / escala
    bx0, by0, bx1, by1 = mejor
    return (caja[0] + int(bx0 * f), caja[1] + int(by0 * f),
            caja[0] + int((bx1 + 1) * f), caja[1] + int((by1 + 1) * f))


def sacar_muestras(doc, nro_pagina, ident):
    """Recorta del PDF el circulito de cada color de la pagina.

    Devuelve {NOMBRE_DEL_COLOR: "img/colores/archivo.png"} solo para los
    colores que el catalogo dibuja. Los demas quedan afuera a proposito.
    """
    pagina = doc[nro_pagina - 1]
    escala = DPI_COLORES / 72
    pixmap = pagina.get_pixmap(dpi=DPI_COLORES)
    render = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGB")

    encontrados = {}
    for bloque in pagina.get_text("dict")["blocks"]:
        for linea in bloque.get("lines", []):
            for span in linea.get("spans", []):
                nombre = span["text"].strip().upper()
                if nombre not in NOMBRES_DE_COLOR:
                    continue
                # El catalogo escribe "MOZTAZA" con Z; nosotros lo mostramos
                # bien escrito, asi que hay que emparejarlos
                nombre = EQUIVALENCIAS.get(nombre, nombre)
                if nombre in encontrados:
                    continue
                caja = buscar_disco(render, span, escala)
                if not caja:
                    continue
                archivo = "%s-%s.png" % (ident, nombre.lower().replace(" ", "-"))
                disco = render.crop(caja).resize((LADO_MUESTRA, LADO_MUESTRA),
                                                 Image.LANCZOS)
                disco.save(os.path.join(CARPETA_COLORES, archivo), optimize=True)
                encontrados[nombre] = "img/colores/" + archivo
    return encontrados


def porcentaje_crema(trozo):
    """Que parte del recorte quedo del color crema del fondo del catalogo."""
    chico = trozo.copy()
    chico.thumbnail((90, 90))
    pixeles = list(chico.convert("RGB").getdata())
    cremosos = sum(
        1 for r, g, b in pixeles
        if r > 225 and g > 220 and b > 210 and abs(r - b) < 32
    )
    return cremosos / len(pixeles)


def sacar_fotos(doc, nro_pagina, ident):
    """Saca de una pagina la foto principal y las secundarias.

    Devuelve (nombre_principal, [nombres_secundarios]).
    Se queda solo con las imagenes que realmente se ven como foto; descarta
    la plantilla de fondo y los circulitos de color (ver nota de arriba).
    """
    pagina = doc[nro_pagina - 1]
    ancho, alto = pagina.rect.width, pagina.rect.height
    escala = DPI_CONTROL / 72

    # Se renderiza la pagina una sola vez para poder mirar el resultado real
    pixmap = pagina.get_pixmap(dpi=DPI_CONTROL)
    render = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGB")

    # Cada imagen puede estar colocada varias veces: nos quedamos con la mayor
    colocaciones = {}
    for info in pagina.get_image_info(xrefs=True):
        xref = info["xref"]
        if not xref:
            continue
        x0, y0, x1, y1 = info["bbox"]
        area = (x1 - x0) * (y1 - y0)
        if area > colocaciones.get(xref, (0, None))[0]:
            colocaciones[xref] = (area, (x0, y0, x1, y1))

    candidatas = []
    for xref, (area, caja) in colocaciones.items():
        img = doc.extract_image(xref)
        if (img["width"], img["height"]) == FONDO:
            continue                       # plantilla de fondo
        if area < MIN_AREA_DIBUJADA:
            continue

        # Recorte de la pagina renderizada, sin salirse de la hoja
        x0, y0 = max(0, caja[0]), max(0, caja[1])
        x1, y1 = min(ancho, caja[2]), min(alto, caja[3])
        if x1 - x0 < 15 or y1 - y0 < 15:
            continue

        trozo = render.crop((int(x0 * escala), int(y0 * escala),
                             int(x1 * escala), int(y1 * escala)))
        if porcentaje_crema(trozo) >= MAX_CREMA:
            continue                       # es un circulito de color

        img["_area"] = area
        candidatas.append(img)

    if not candidatas:
        return None, []

    candidatas.sort(key=lambda i: i["_area"], reverse=True)
    principal, resto = candidatas[0], candidatas[1:]

    archivo = ident + ".jpg"
    guardar(doc, principal, os.path.join(CARPETA_FOTOS, archivo))

    secundarias = []
    for img in resto:
        nombre = "%s-%d.jpg" % (ident, len(secundarias) + 2)
        guardar(doc, img, os.path.join(CARPETA_FOTOS, nombre), alto=1000)
        secundarias.append(nombre)

    return archivo, secundarias


def texto_js(valor):
    """Escapa un texto para meterlo entre comillas en JavaScript."""
    return valor.replace("\\", "\\\\").replace('"', '\\"')


def main():
    os.makedirs(CARPETA_FOTOS, exist_ok=True)
    os.makedirs(CARPETA_COLORES, exist_ok=True)
    documentos = {}
    lineas = []
    sin_foto = []
    sin_muestra = []

    for clave, pagina, ident, nombre, codigo, categoria, talles, colores, desc in PRENDAS:
        if clave not in documentos:
            documentos[clave] = abrir_catalogo(clave)

        archivo, secundarias = sacar_fotos(documentos[clave], pagina, ident)
        if not archivo:
            sin_foto.append(ident)

        muestras = sacar_muestras(documentos[clave], pagina, ident)
        sin_muestra.extend(
            "%s/%s" % (ident, c) for c in colores if c not in muestras
        )
        lista_colores = ", ".join(
            ('{ nombre: "%s", muestra: "%s" }' % (c.title(), muestras[c]))
            if c in muestras else ('{ nombre: "%s" }' % c.title())
            for c in colores
        )
        lista_talles = ", ".join('"%s"' % t for t in talles)
        lista_galeria = ", ".join('"img/prendas/%s"' % n for n in secundarias)

        lineas.append(
            '  { id: "%s", nombre: "%s", codigo: "%s", categoria: "%s", precio: null, '
            'descripcion: "%s", tela: "", talles: [%s], colores: [%s], '
            'foto: "%s", galeria: [%s], destacado: %s }'
            % (
                ident,
                texto_js(nombre),
                codigo,
                categoria,
                texto_js(desc),
                lista_talles,
                lista_colores,
                "img/prendas/" + archivo if archivo else "",
                lista_galeria,
                "true" if ident in DESTACADOS else "false",
            )
        )

    for doc in documentos.values():
        doc.close()

    cats = ",\n".join(
        '  { id: "%s", nombre: "%s" }' % (i, n) for i, n in CATEGORIAS
    )

    contenido = (
        "/* ============================================================\n"
        "   Braccis - base de datos de prendas\n"
        "   ------------------------------------------------------------\n"
        "   GENERADO AUTOMATICAMENTE por herramientas/generar_catalogo.py\n"
        "   a partir de los PDF de catalogo.\n"
        "\n"
        "   Se puede editar a mano sin problema (por ejemplo para cargar\n"
        "   precios o cambiar una descripcion), pero tene en cuenta que si\n"
        "   volves a correr el script se pisa todo. Lo mas seguro es\n"
        "   cargar los cambios en el script y regenerar.\n"
        "   ============================================================ */\n\n"
        "const CATEGORIAS = [\n" + cats + "\n];\n\n"
        "const PRODUCTOS = [\n" + ",\n".join(lineas) + "\n];\n"
    )

    with open(SALIDA_JS, "w", encoding="utf-8") as f:
        f.write(contenido)

    print("Listo: %d prendas -> js/productos.js" % len(PRENDAS))
    print("Fotos guardadas en img/prendas/")
    if sin_foto:
        print("SIN FOTO (revisar a mano): " + ", ".join(sin_foto))
    print("Muestras de color recortadas del PDF: %d" %
          len(os.listdir(CARPETA_COLORES)))
    if sin_muestra:
        print("Colores que el catalogo no dibuja (van solo con el nombre): %d"
              % len(sin_muestra))


if __name__ == "__main__":
    main()
