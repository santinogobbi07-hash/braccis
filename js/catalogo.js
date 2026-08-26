/* ============================================================
   Braccis - catalogo
   Dibuja la grilla de prendas, los filtros por categoria,
   el buscador y el detalle de cada prenda en un modal.
   Los datos salen de js/productos.js
   ============================================================ */

let filtroCategoria = "todas";
let ultimoFoco = null;   // a donde vuelve el foco al cerrar la ficha
let filtroTexto = "";

/* Escapa un texto antes de meterlo en el HTML.
   Las fichas se arman como texto y se insertan con innerHTML, asi que
   cualquier dato que venga de productos.js tiene que pasar por aca. Si no,
   un nombre de prenda con simbolos raros (o copiado de un PDF cualquiera)
   podria romper la pagina o meter codigo. */
function esc(valor) {
  return String(valor === null || valor === undefined ? "" : valor)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

document.addEventListener("DOMContentLoaded", function () {
  dibujarDestacados();   // solo hace algo en la portada
  iniciarCatalogo();     // solo hace algo en catalogo.html
});

/* ============================================================
   PORTADA: prendas destacadas
   ============================================================ */
function dibujarDestacados() {
  const grilla = document.querySelector("[data-destacados]");
  if (!grilla) return;

  const destacados = PRODUCTOS.filter(function (p) { return p.destacado; }).slice(0, 8);
  const aMostrar = destacados.length ? destacados : PRODUCTOS.slice(0, 8);

  grilla.innerHTML = aMostrar.map(tarjetaProducto).join("");
  activarClicksDeTarjetas(grilla);
}

/* ============================================================
   CATALOGO: filtros + grilla
   ============================================================ */
function iniciarCatalogo() {
  const grilla = document.querySelector("[data-grilla]");
  if (!grilla) return;

  dibujarFiltros();
  dibujarGrilla();

  const buscador = document.querySelector("[data-buscador]");
  if (buscador) {
    buscador.addEventListener("input", function (e) {
      filtroTexto = e.target.value.trim().toLowerCase();
      dibujarGrilla();
    });
  }

  // Si se entra con ?categoria=blusas, arrancar filtrado.
  // Si la categoria del link no existe (un link viejo, un error de tipeo),
  // se muestra el catalogo completo en vez de dejar la pagina vacia.
  const params = new URLSearchParams(window.location.search);
  const cat = params.get("categoria");
  const existe = CATEGORIAS.some(function (c) { return c.id === cat; });
  if (cat && existe) {
    filtroCategoria = cat;
    marcarChipActivo();
    dibujarGrilla();
  }
}

function dibujarFiltros() {
  const cont = document.querySelector("[data-filtros]");
  if (!cont) return;

  // Solo mostramos categorias que efectivamente tienen prendas
  const usadas = CATEGORIAS.filter(function (c) {
    return PRODUCTOS.some(function (p) { return p.categoria === c.id; });
  });

  const chips = [{ id: "todas", nombre: "Todas" }].concat(usadas);

  cont.innerHTML = chips.map(function (c) {
    const activo = c.id === filtroCategoria;
    return '<button class="chip" data-cat="' + esc(c.id) + '" aria-pressed="' + activo + '">' +
             esc(c.nombre) +
           '</button>';
  }).join("");

  cont.querySelectorAll(".chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      filtroCategoria = chip.dataset.cat;
      marcarChipActivo();
      dibujarGrilla();
    });
  });
}

function marcarChipActivo() {
  document.querySelectorAll("[data-filtros] .chip").forEach(function (chip) {
    chip.setAttribute("aria-pressed", chip.dataset.cat === filtroCategoria);
  });
}

function productosFiltrados() {
  return PRODUCTOS.filter(function (p) {
    const pasaCategoria = filtroCategoria === "todas" || p.categoria === filtroCategoria;
    const enTexto = (p.nombre + " " + p.codigo + " " + p.descripcion).toLowerCase();
    const pasaTexto = !filtroTexto || enTexto.indexOf(filtroTexto) !== -1;
    return pasaCategoria && pasaTexto;
  });
}

function dibujarGrilla() {
  const grilla = document.querySelector("[data-grilla]");
  const contador = document.querySelector("[data-contador]");
  if (!grilla) return;

  const lista = productosFiltrados();

  if (contador) {
    contador.textContent = lista.length === 1
      ? "1 prenda"
      : lista.length + " prendas";
  }

  if (!lista.length) {
    grilla.innerHTML = '<p class="vacio">No encontramos prendas con esa búsqueda.</p>';
    return;
  }

  grilla.innerHTML = lista.map(tarjetaProducto).join("");
  activarClicksDeTarjetas(grilla);
}

/* ============================================================
   Tarjeta de producto
   ============================================================ */
function tarjetaProducto(p) {
  const imagen = p.foto
    ? '<img src="' + esc(p.foto) + '" alt="' + esc(p.nombre) + '" loading="lazy">'
    : '<div class="producto__placeholder">' + esc(p.nombre.charAt(0).toUpperCase()) + '</div>';

  // Las bolitas son los circulitos recortados del catalogo. Los colores que
  // el PDF no dibuja no llevan bolita: aparecen solo en la ficha, por nombre.
  const puntos = (p.colores || []).filter(function (c) { return c.muestra; })
    .map(function (c) {
      return '<img class="punto-color" src="' + esc(c.muestra) + '" alt="' + esc(c.nombre) +
             '" title="' + esc(c.nombre) + '" loading="lazy">';
    }).join("");

  const precio = p.precio
    ? '<p class="producto__precio">' + esc(formatearPrecio(p.precio)) + '</p>'
    : "";

  const codigo = p.codigo
    ? '<p class="producto__codigo">Cód. ' + esc(p.codigo) + '</p>'
    : "";

  return '' +
    '<article class="producto aparece visible" data-id="' + esc(p.id) + '" tabindex="0">' +
      '<div class="producto__figura">' + imagen + '</div>' +
      '<h3 class="producto__nombre">' + esc(p.nombre) + '</h3>' +
      codigo +
      precio +
      '<div class="producto__colores">' + puntos + '</div>' +
    '</article>';
}

function activarClicksDeTarjetas(contenedor) {
  contenedor.querySelectorAll(".producto").forEach(function (tarjeta) {
    tarjeta.addEventListener("click", function () {
      abrirModal(tarjeta.dataset.id);
    });
    tarjeta.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        abrirModal(tarjeta.dataset.id);
      }
    });
  });
}

/* ============================================================
   Modal con el detalle de la prenda
   ============================================================ */
function abrirModal(id) {
  const p = PRODUCTOS.find(function (x) { return x.id === id; });
  const modal = document.querySelector("[data-modal]");
  if (!p || !modal) return;

  const imagen = p.foto
    ? '<img src="' + esc(p.foto) + '" alt="' + esc(p.nombre) + '" data-foto-grande>'
    : '<div class="producto__placeholder">' + esc(p.nombre.charAt(0).toUpperCase()) + '</div>';

  // Tira de miniaturas: la principal mas las fotos de los otros colores
  const galeria = [p.foto].concat(p.galeria || []).filter(Boolean);
  const miniaturas = galeria.length > 1
    ? '<div class="miniaturas">' + galeria.map(function (src, i) {
        return '<button class="miniatura" data-src="' + esc(src) + '"' +
               (i === 0 ? ' aria-current="true"' : '') +
               ' aria-label="Ver foto ' + (i + 1) + '">' +
                 '<img src="' + esc(src) + '" alt="" loading="lazy">' +
               '</button>';
      }).join("") + '</div>'
    : "";

  const filas = [];

  if (p.codigo) filas.push(fichaFila("Código", esc(p.codigo)));
  if (p.tela)   filas.push(fichaFila("Tela", esc(p.tela)));

  if (p.talles && p.talles.length) {
    const talles = p.talles.map(function (t) {
      return '<span class="talle">' + esc(t) + '</span>';
    }).join("");
    filas.push(fichaFila("Talles", '<div class="talles">' + talles + '</div>'));
  }

  if (p.colores && p.colores.length) {
    const colores = p.colores.map(function (c) {
      const bolita = c.muestra
        ? '<img class="punto-color" src="' + esc(c.muestra) + '" alt="" loading="lazy">'
        : "";
      return '<span class="color-item">' + bolita + esc(c.nombre) + '</span>';
    }).join("");
    filas.push(fichaFila("Colores", '<div class="colores-lista">' + colores + '</div>'));
  }

  const precio = p.precio
    ? '<p style="font-size:1.25rem;margin-top:10px">' + esc(formatearPrecio(p.precio)) + '</p>'
    : "";

  const descripcion = p.descripcion
    ? '<p class="bajada" style="margin-top:14px">' + esc(p.descripcion) + '</p>'
    : "";

  const consulta = "¡Hola! Me interesa la prenda " + p.nombre +
                   (p.codigo ? " (cód. " + p.codigo + ")" : "") + ". ¿Me pasan más info?";

  modal.querySelector("[data-modal-contenido]").innerHTML = '' +
    '<button class="modal__cerrar" data-cerrar aria-label="Cerrar">&times;</button>' +
    '<div class="modal__media">' +
      '<div class="modal__figura">' + imagen + '</div>' +
      miniaturas +
    '</div>' +
    '<div class="modal__info">' +
      '<h2 class="modal__nombre">' + esc(p.nombre) + '</h2>' +
      precio +
      descripcion +
      '<div class="ficha">' + filas.join("") + '</div>' +
      '<a class="btn btn--wsp" style="margin-top:26px" href="' + esc(linkWhatsapp(consulta)) + '" target="_blank" rel="noopener">Consultar por WhatsApp</a>' +
    '</div>';

  modal.classList.add("abierto");
  document.body.style.overflow = "hidden";

  // Se recuerda desde donde se abrio para devolver el foco al cerrar:
  // si no, quien navega con teclado vuelve al principio de la pagina
  ultimoFoco = document.activeElement;

  const cerrar = modal.querySelector("[data-cerrar]");
  cerrar.addEventListener("click", cerrarModal);
  cerrar.focus();

  activarMiniaturas(modal);
}

/* Al tocar una miniatura, cambia la foto grande de la ficha */
function activarMiniaturas(modal) {
  const grande = modal.querySelector("[data-foto-grande]");
  const botones = modal.querySelectorAll(".miniatura");
  if (!grande || !botones.length) return;

  botones.forEach(function (boton) {
    boton.addEventListener("click", function () {
      grande.src = boton.dataset.src;
      botones.forEach(function (b) { b.removeAttribute("aria-current"); });
      boton.setAttribute("aria-current", "true");
    });
  });
}

function fichaFila(clave, valor) {
  return '<div class="ficha__fila">' +
           '<span class="ficha__clave">' + esc(clave) + '</span>' +
           '<span>' + valor + '</span>' +
         '</div>';
}

function cerrarModal() {
  const modal = document.querySelector("[data-modal]");
  if (!modal || !modal.classList.contains("abierto")) return;
  modal.classList.remove("abierto");
  document.body.style.overflow = "";
  if (ultimoFoco && document.contains(ultimoFoco)) ultimoFoco.focus();
  ultimoFoco = null;
}

// Cerrar con click en el fondo o con Escape
document.addEventListener("click", function (e) {
  const modal = document.querySelector("[data-modal]");
  if (modal && e.target === modal) cerrarModal();
});
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") cerrarModal();
});
