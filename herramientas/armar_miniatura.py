# -*- coding: utf-8 -*-
"""
Braccis - miniatura para compartir
==================================
Arma la imagen que se ve cuando alguien pega el link del sitio en
WhatsApp, Instagram o Facebook. Sale en img/compartir.jpg

Correr:  python herramientas/armar_miniatura.py
"""
import os
from PIL import Image, ImageDraw, ImageEnhance

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Medida estandar para las miniaturas de las redes
ANCHO, ALTO = 1200, 630
CREMA = (250, 247, 242)

fondo = Image.open(os.path.join(RAIZ, "img/prendas/jeans-cird.jpg")).convert("RGB")

# Recorte al centro, tomando la parte de arriba donde esta la prenda
prop = ANCHO / ALTO
an, al = fondo.size
alto_corte = int(an / prop)
arriba = int(al * 0.08)
if arriba + alto_corte > al:
    arriba = max(0, al - alto_corte)
fondo = fondo.crop((0, arriba, an, arriba + alto_corte)).resize((ANCHO, ALTO), Image.LANCZOS)

# Se oscurece para que el logo se lea encima
fondo = ImageEnhance.Brightness(fondo).enhance(0.55)
velo = Image.new("RGB", (ANCHO, ALTO), (31, 27, 24))
fondo = Image.blend(fondo, velo, 0.25)

# Logo de la marca, en claro
logo = Image.open(os.path.join(RAIZ, "img/logo-claro.png")).convert("RGBA")
ancho_logo = 520
logo = logo.resize((ancho_logo, int(logo.height * ancho_logo / logo.width)), Image.LANCZOS)
fondo.paste(logo, ((ANCHO - ancho_logo) // 2, int(ALTO * 0.34)), logo)

# Una linea fina y el nombre de la coleccion
d = ImageDraw.Draw(fondo)
cx, y = ANCHO // 2, int(ALTO * 0.34) + logo.height + 46
d.line([(cx - 60, y), (cx + 60, y)], fill=CREMA, width=1)

fondo.save(os.path.join(RAIZ, "img/compartir.jpg"), "JPEG", quality=88, optimize=True)
print("img/compartir.jpg  %d x %d  %d KB" % (
    ANCHO, ALTO, os.path.getsize(os.path.join(RAIZ, "img/compartir.jpg")) // 1024))
