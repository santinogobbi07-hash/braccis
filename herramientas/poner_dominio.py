# -*- coding: utf-8 -*-
"""
Braccis - completar la direccion del sitio
==========================================

Cuando alguien pega el link en WhatsApp, WhatsApp entra a la pagina y
busca la imagen de la miniatura. Para encontrarla necesita la direccion
COMPLETA (https://...), no una ruta relativa. Con ruta relativa el link
se manda sin miniatura y se ve pobre.

Este script escribe esa direccion en las tres paginas.

Como se usa
-----------
Una vez que el sitio este publicado y sepas su direccion:

    python herramientas/poner_dominio.py https://braccis.netlify.app

Se puede correr las veces que haga falta: si despues cambias a un dominio
propio, lo volves a correr con la direccion nueva.
"""

import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = ["index.html", "catalogo.html", "contacto.html"]


def main():
    if len(sys.argv) != 2:
        sys.exit("Falta la direccion del sitio.\n"
                 "Ejemplo:  python herramientas/poner_dominio.py https://braccis.netlify.app")

    base = sys.argv[1].strip().rstrip("/")
    if not base.startswith("http"):
        sys.exit("La direccion tiene que empezar con https://")

    for pagina in PAGINAS:
        ruta = os.path.join(RAIZ, pagina)
        s = io.open(ruta, encoding="utf-8").read()

        # La miniatura, con la direccion completa
        s = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
                   r'\g<1>' + base + '/img/compartir.jpg' + r'\g<2>', s)

        # La direccion de la propia pagina
        destino = base + "/" + ("" if pagina == "index.html" else pagina)
        if '<meta property="og:url"' in s:
            s = re.sub(r'(<meta property="og:url" content=")[^"]*(")',
                       r'\g<1>' + destino + r'\g<2>', s)
        else:
            s = s.replace('  <meta property="og:image"',
                          '  <meta property="og:url" content="%s">\n  <meta property="og:image"' % destino, 1)

        io.open(ruta, "w", encoding="utf-8").write(s)
        print("%-16s -> %s" % (pagina, destino))

    print("\nListo. Volve a publicar el sitio para que tome los cambios.")
    print("Para probar como se va a ver el link:")
    print("  https://developers.facebook.com/tools/debug/?q=" + base)


if __name__ == "__main__":
    main()
