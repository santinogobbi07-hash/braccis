# -*- coding: utf-8 -*-
"""
Braccis - catalogo en PDF para descargar
========================================

Junta los cuatro catalogos (jeans, remeras, hilo, camisas) en un solo
PDF liviano, para el boton "Catalogo PDF" del menu.

Los originales suman unos 140 MB: nadie los descarga desde el celular.
Este script vuelve a dibujar cada pagina como imagen comprimida y arma
un PDF nuevo de pocos megas que se ve igual en pantalla.

Correr:   python herramientas/armar_pdf.py
Sale:     docs/catalogo-braccis-pv2027.pdf

Requiere: pip install pymupdf
"""

import os
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("Falta instalar pymupdf. Corre:  pip install pymupdf")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "docs", "catalogo-braccis-pv2027.pdf")

# En el orden en que aparecen en el PDF final. Busca primero en catalogos/
# y si no estan, en Descargas (mismo criterio que generar_catalogo.py).
CATALOGOS = [
    ["catalogos/JEANS.pdf",   r"C:\Users\Usuario\Downloads\JEANS (3).pdf"],
    ["catalogos/REMERAS.pdf", r"C:\Users\Usuario\Downloads\CAP REMERAS .pdf"],
    ["catalogos/HILO.pdf",    r"C:\Users\Usuario\Downloads\HILO.pdf"],
    ["catalogos/CAMISAS.pdf", r"C:\Users\Usuario\Downloads\CAMISAS (2).pdf"],
]

# Con 110 dpi el texto se lee perfecto en pantalla y el archivo queda chico.
# Si se quiere imprimir, subir a 150 (pesa casi el doble).
DPI = 110
CALIDAD_JPG = 72


def buscar(rutas):
    for r in rutas:
        completa = r if os.path.isabs(r) else os.path.join(RAIZ, r)
        if os.path.exists(completa):
            return completa
    return None


def main():
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    final = pymupdf.open()
    paginas = 0

    for rutas in CATALOGOS:
        ruta = buscar(rutas)
        if not ruta:
            sys.exit("No encontre el PDF: " + rutas[-1])
        doc = pymupdf.open(ruta)
        for pagina in doc:
            imagen = pagina.get_pixmap(dpi=DPI)
            jpg = imagen.tobytes("jpeg", jpg_quality=CALIDAD_JPG)
            nueva = final.new_page(width=pagina.rect.width, height=pagina.rect.height)
            nueva.insert_image(nueva.rect, stream=jpg)
            paginas += 1
        print("  %-24s %d paginas" % (os.path.basename(ruta), doc.page_count))
        doc.close()

    final.set_metadata({
        "title": "Braccis - Coleccion Primavera-Verano 2027",
        "author": "Braccis",
        "subject": "Catalogo de las capsulas de jeans, remeras, hilo, y camisas y blusas",
    })
    final.save(SALIDA, garbage=4, deflate=True)
    final.close()
    print("\nListo: %s" % os.path.relpath(SALIDA, RAIZ))
    print("%d paginas, %.1f MB" % (paginas, os.path.getsize(SALIDA) / 1024 / 1024))


if __name__ == "__main__":
    main()
