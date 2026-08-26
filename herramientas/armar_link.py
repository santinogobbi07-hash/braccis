# -*- coding: utf-8 -*-
"""
Braccis - armador de la version de un solo archivo
==================================================

Junta las tres paginas del sitio en un unico HTML, con los estilos, el
codigo y TODAS las fotos metidas adentro. Sirve para tener un link que se
pueda mandar sin depender de que las imagenes esten en otro lado.

Correr:   python herramientas/armar_link.py

Sale:     braccis-una-pagina.html
"""

import base64
import io
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Falta Pillow. Corre:  pip install pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "braccis-una-pagina.html")

# Las fotos se achican: en pantalla nunca se ven a mas de 400 px de ancho,
# asi que 760 de alto alcanza de sobra y el archivo pesa la mitad.
ALTO_FOTO = 760
CALIDAD = 74
LADO_MUESTRA = 60


def leer(ruta):
    return io.open(os.path.join(RAIZ, ruta), encoding="utf-8").read()


def a_data_uri(ruta, alto, calidad):
    """Convierte una imagen del disco en texto para incrustar en el HTML."""
    img = Image.open(os.path.join(RAIZ, ruta)).convert("RGB")
    img.thumbnail((int(alto * 0.8), alto), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=calidad, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def logo_data_uri(ruta):
    """El logo va en PNG porque necesita el fondo transparente."""
    img = Image.open(os.path.join(RAIZ, ruta)).convert("RGBA")
    img.thumbnail((520, 120), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def cuerpo_de(pagina):
    """El contenido propio de una pagina, sin el encabezado ni el pie."""
    html = leer(pagina)
    desde = html.index("</header>") + len("</header>")
    hasta = html.index("<!-- ============ FOOTER ============ -->")
    return html[desde:hasta].strip()


def main():
    print("Preparando las imagenes...")

    # --- Fotos de prendas y muestras de color ---
    imagenes = {}
    for carpeta, alto, cal in (("img/prendas", ALTO_FOTO, CALIDAD),
                               ("img/colores", LADO_MUESTRA, 80)):
        for archivo in sorted(os.listdir(os.path.join(RAIZ, carpeta))):
            ruta = carpeta + "/" + archivo
            imagenes[ruta] = a_data_uri(ruta, alto, cal)
    print("  %d imagenes incrustadas" % len(imagenes))

    # --- Estilos ---
    css = leer("css/styles.css")
    css = css.replace('url("../img/prendas/jeans-cird.jpg")',
                      'url("%s")' % imagenes["img/prendas/jeans-cird.jpg"])
    # Las vistas se muestran de a una
    css += """

/* --- Version de un solo archivo: las tres paginas conviven --- */
.vista { display: none; }
.vista.activa { display: block; }
"""

    # --- Codigo: se reemplazan las rutas por las imagenes incrustadas ---
    productos = leer("js/productos.js")
    for ruta, uri in imagenes.items():
        productos = productos.replace('"%s"' % ruta, '"%s"' % uri)
    sobrantes = re.findall(r'"img/[^"]+"', productos)
    if sobrantes:
        print("  AVISO: quedaron rutas sin incrustar:", set(sobrantes))

    js = "\n".join([leer("js/config.js"), productos, leer("js/catalogo.js"),
                    leer("js/main.js"), leer("js/contacto.js")])

    # El cambio de vista reemplaza a la navegacion entre archivos
    js += """

/* ============================================================
   Cambio de vista: en el sitio real cada seccion es un archivo
   aparte; aca conviven en la misma pagina.
   ============================================================ */
function mostrarVista(nombre, categoria) {
  document.querySelectorAll(".vista").forEach(function (v) {
    v.classList.toggle("activa", v.id === "vista-" + nombre);
  });
  document.querySelectorAll(".nav__link").forEach(function (a) {
    if (a.dataset.vista === nombre) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  if (categoria) {
    filtroCategoria = categoria;
    marcarChipActivo();
    dibujarGrilla();
  }
  window.scrollTo(0, 0);
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-vista]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      e.preventDefault();
      mostrarVista(el.dataset.vista, el.dataset.cat);
      const nav = document.querySelector(".nav");
      const btn = document.querySelector(".hamburguesa");
      if (nav) nav.classList.remove("abierta");
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  });
  document.querySelectorAll("[data-ir-nosotros]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      e.preventDefault();
      mostrarVista("inicio");
      const s = document.getElementById("nosotros");
      if (s) s.scrollIntoView({ behavior: "smooth" });
    });
  });
  mostrarVista("inicio");
});
"""

    # --- Encabezado y pie, una sola vez ---
    logo = logo_data_uri("img/logo.png")
    logo_claro = logo_data_uri("img/logo-claro.png")

    nav = """
      <nav class="nav">
        <ul class="nav__lista">
          <li><a class="nav__link" href="#" data-vista="inicio">Inicio</a></li>
          <li><a class="nav__link" href="#" data-vista="catalogo">Catálogo</a></li>
          <li><a class="nav__link" href="#" data-ir-nosotros>Nosotros</a></li>
          <li><a class="nav__link" href="#" data-vista="contacto">Contacto</a></li>
        </ul>
      </nav>"""

    header = """
  <header class="header">
    <div class="contenedor header__inner">
      <a href="#" class="logo" data-vista="inicio"><img src="%s" alt="Braccis"></a>
%s
      <button class="hamburguesa" aria-label="Abrir menú" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>""" % (logo, nav)

    footer = """
  <footer class="footer">
    <div class="contenedor">
      <div class="footer__grid">
        <div>
          <p class="logo"><img src="%s" alt="Braccis"></p>
          <p style="margin-top:14px;max-width:36ch;color:rgba(250,247,242,.7)" data-empresa="descripcionCorta"></p>
        </div>
        <div>
          <p class="footer__titulo">Navegación</p>
          <ul class="footer__lista">
            <li><a href="#" data-vista="inicio">Inicio</a></li>
            <li><a href="#" data-vista="catalogo">Catálogo</a></li>
            <li><a href="#" data-ir-nosotros>Nosotros</a></li>
            <li><a href="#" data-vista="contacto">Contacto</a></li>
          </ul>
        </div>
        <div>
          <p class="footer__titulo">Contacto</p>
          <ul class="footer__lista">
            <li><a data-empresa="email" href="#"></a></li>
            <li><a data-empresa="telefonoVisible" href="#"></a></li>
            <li><a data-empresa="instagramUsuario" href="#" target="_blank" rel="noopener"></a></li>
            <li data-empresa="direccion"></li>
          </ul>
        </div>
      </div>
      <div class="footer__abajo">
        <span>&copy; <span data-anio></span> Braccis. Todos los derechos reservados.</span>
        <span>Primavera–Verano 2027</span>
      </div>
    </div>
  </footer>""" % logo_claro

    icono_wsp = ('<svg width="28" height="28" viewBox="0 0 24 24" fill="#fff" aria-hidden="true">'
                 '<path d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 '
                 '1.16-.17.2-.35.22-.64.07-.3-.15-1.25-.46-2.38-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 '
                 '0-.52.07-.79.37-.27.3-1.04 1.01-1.04 2.47s1.06 2.87 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.3 '
                 '1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.75-.72 2-1.41.25-.69.25-1.28.17-1.41-.07-.13-.27-.2-.57-.35zM12.05 '
                 '21.5h-.01a9.42 9.42 0 0 1-4.8-1.32l-.34-.2-3.57.94.95-3.48-.22-.36a9.4 9.4 0 0 '
                 '1-1.44-5.02c0-5.2 4.23-9.43 9.44-9.43a9.37 9.37 0 0 1 6.67 2.77 9.35 9.35 0 0 1 2.76 '
                 '6.67c0 5.2-4.23 9.43-9.44 9.43zM20.14 3.85A11.28 11.28 0 0 0 12.05.5C5.8.5.72 5.58.72 '
                 '11.82c0 2 .52 3.95 1.52 5.67L.62 23.5l6.15-1.61a11.3 11.3 0 0 0 5.28 1.34h.01c6.24 0 '
                 '11.32-5.08 11.32-11.32 0-3.03-1.18-5.87-3.24-8.01z"/></svg>')

    # --- Contenido de cada vista ---
    vistas = ""
    for nombre, pagina in (("inicio", "index.html"),
                           ("catalogo", "catalogo.html"),
                           ("contacto", "contacto.html")):
        cuerpo = cuerpo_de(pagina)
        # Los links entre paginas pasan a ser cambios de vista
        cuerpo = re.sub(r'href="catalogo\.html\?categoria=([a-z]+)"',
                        r'href="#" data-vista="catalogo" data-cat="\1"', cuerpo)
        cuerpo = cuerpo.replace('href="catalogo.html"', 'href="#" data-vista="catalogo"')
        cuerpo = cuerpo.replace('href="contacto.html"', 'href="#" data-vista="contacto"')
        cuerpo = cuerpo.replace('href="index.html#nosotros"', 'href="#" data-ir-nosotros')
        cuerpo = cuerpo.replace('href="index.html"', 'href="#" data-vista="inicio"')
        # El pie y el boton flotante ya estan una sola vez, afuera
        cuerpo = re.sub(r'<a class="wsp-flotante".*?</a>', "", cuerpo, flags=re.S)
        cuerpo = re.sub(r'<div class="modal" data-modal>.*?</div>\s*</div>', "", cuerpo, flags=re.S)
        vistas += '\n  <div class="vista" id="vista-%s">\n%s\n  </div>\n' % (nombre, cuerpo)

    partes = [
        "<title>Braccis</title>",
        '<meta name="description" content="Catálogo Primavera–Verano 2027 de Braccis: 53 prendas con talles, colores y fotos.">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">',
        "<style>\n" + css + "\n</style>",
        header,
        vistas,
        footer,
        '<a class="wsp-flotante" data-wsp href="#" aria-label="Escribinos por WhatsApp">%s</a>' % icono_wsp,
        '<div class="modal" data-modal><div class="modal__caja" data-modal-contenido></div></div>',
        "<script>\n" + js + "\n</script>",
    ]

    # --- Todo a ASCII ---
    # Un archivo suelto no controla como lo sirve el servidor. Si el
    # servidor no dice que es UTF-8, los acentos se rompen ("acompaÃ±an").
    # Escribiendo las tildes y enes como codigos, el archivo anda igual
    # sin importar como lo sirvan.
    def a_entidades(texto):
        return "".join(c if ord(c) < 128 else "&#%d;" % ord(c) for c in texto)

    def a_escapes_js(texto):
        return "".join(c if ord(c) < 128 else "\\u%04x" % ord(c) for c in texto)

    sin_ascii_css = [c for c in css if ord(c) >= 128]
    if sin_ascii_css:
        print("  AVISO: el CSS tiene caracteres especiales:", set(sin_ascii_css))

    partes = [a_entidades(p) for p in partes[:-1]] + \
             ["<script>\n" + a_escapes_js(js) + "\n</script>"]

    html = "\n".join(partes)
    if any(ord(c) >= 128 for c in html):
        print("  AVISO: quedaron caracteres no ASCII en el archivo")
    io.open(SALIDA, "w", encoding="ascii").write(html)
    print("\nListo: %s" % os.path.basename(SALIDA))
    print("Pesa %.1f MB" % (os.path.getsize(SALIDA) / 1024 / 1024))


if __name__ == "__main__":
    main()
