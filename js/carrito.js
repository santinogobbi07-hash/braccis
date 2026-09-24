/* ============================================================
   Braccis - carrito de compras
   ------------------------------------------------------------
   Se guarda en el navegador de quien compra (localStorage), asi no
   se pierde al pasar de pagina o al volver otro dia.

   Solo se guarda que prenda, que talle, que color y cuantas. El
   precio NO se guarda: se lee del catalogo cada vez, asi si cambia
   en el Google Sheets el carrito muestra el precio nuevo.

   El pedido termina en WhatsApp: no hay pagos ni datos en ningun
   servidor. El telefono que escribe el cliente no se guarda.
   ============================================================ */

const Carrito = (function () {
  const CLAVE = "braccis-carrito";
  let items = leer();
  let listo = false;     // true cuando ya se cargo el Google Sheets (si hay)

  /* ---------- Guardado ---------- */
  function leer() {
    try {
      const datos = JSON.parse(localStorage.getItem(CLAVE) || "[]");
      return Array.isArray(datos) ? datos.filter(function (i) {
        return i && typeof i.id === "string" && Number(i.cantidad) > 0;
      }) : [];
    } catch (e) {
      return [];          // navegador sin almacenamiento o dato roto
    }
  }
  function guardar() {
    try { localStorage.setItem(CLAVE, JSON.stringify(items)); } catch (e) {}
  }

  function producto(id) {
    return PRODUCTOS.find(function (p) { return p.id === id && !p.oculto; });
  }

  /* Items que se pueden mostrar. Antes de que llegue el Sheet no se
     borra nada: una prenda nueva del Sheet todavia no esta cargada. */
  function vigentes() {
    return items.filter(function (i) { return producto(i.id); });
  }

  /* ---------- Acciones ---------- */
  function agregar(id, talle, color) {
    const igual = items.find(function (i) {
      return i.id === id && i.talle === (talle || "") && i.color === (color || "");
    });
    if (igual) igual.cantidad += 1;
    else items.push({ id: id, talle: talle || "", color: color || "", cantidad: 1 });
    guardar();
    dibujar();
    mostrarAviso();
  }

  function cambiarCantidad(indice, delta) {
    const i = vigentes()[indice];
    if (!i) return;
    i.cantidad += delta;
    if (i.cantidad <= 0) items.splice(items.indexOf(i), 1);
    guardar();
    dibujar();
  }

  function quitar(indice) {
    const i = vigentes()[indice];
    if (!i) return;
    items.splice(items.indexOf(i), 1);
    guardar();
    dibujar();
  }

  function vaciar() {
    items = [];
    guardar();
    dibujar();
  }

  function cantidadTotal() {
    return vigentes().reduce(function (n, i) { return n + i.cantidad; }, 0);
  }

  /* ---------- Mensaje de WhatsApp ---------- */
  function detalle(i) {
    return [i.talle ? "Talle " + i.talle : "", i.color].filter(Boolean).join(" · ");
  }

  function armarMensaje(telefono) {
    let total = 0;
    let faltanPrecios = false;
    const lineas = vigentes().map(function (i) {
      const p = producto(i.id);
      const extra = detalle(i);
      let precio;
      if (p.precio) {
        total += p.precio * i.cantidad;
        precio = formatearPrecio(p.precio * i.cantidad);
      } else {
        faltanPrecios = true;
        precio = "precio a confirmar";
      }
      return i.cantidad + "x " + p.nombre + (extra ? " · " + extra : "") + " (" + precio + ")";
    });
    return "Hola, mi teléfono es " + telefono + ". " +
           "Pedido: " + lineas.join(", ") + ". " +
           "Total: " + formatearPrecio(total) +
           (faltanPrecios ? " (sin contar las prendas con precio a confirmar)" : "");
  }

  /* ---------- Panel ---------- */
  // El panel se arma desde aca para no repetir el mismo HTML en las
  // tres paginas: en cada una solo hace falta el boton del encabezado.
  function crearPanel() {
    if (document.querySelector("[data-carrito]")) return;
    const fondo = document.createElement("div");
    fondo.className = "carrito-fondo";
    fondo.setAttribute("data-carrito-fondo", "");
    fondo.hidden = true;

    const panel = document.createElement("aside");
    panel.className = "carrito";
    panel.setAttribute("data-carrito", "");
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "true");
    panel.setAttribute("aria-labelledby", "carrito-titulo");
    panel.hidden = true;
    panel.innerHTML = '' +
      '<div class="carrito__cabecera">' +
        '<h2 class="carrito__titulo" id="carrito-titulo">Tu pedido</h2>' +
        '<button type="button" class="carrito__cerrar" data-carrito-cerrar aria-label="Cerrar carrito">&times;</button>' +
      '</div>' +
      '<div class="carrito__cuerpo" data-carrito-lista></div>' +
      '<div class="carrito__pie" data-carrito-pie></div>';

    document.body.appendChild(fondo);
    document.body.appendChild(panel);

    fondo.addEventListener("click", cerrar);
    panel.querySelector("[data-carrito-cerrar]").addEventListener("click", cerrar);

    // Un solo manejador para todos los botones de la lista
    panel.addEventListener("click", function (e) {
      const b = e.target.closest("[data-accion]");
      if (!b) return;
      const n = Number(b.getAttribute("data-indice"));
      const accion = b.getAttribute("data-accion");
      if (accion === "mas") cambiarCantidad(n, 1);
      if (accion === "menos") cambiarCantidad(n, -1);
      if (accion === "quitar") quitar(n);
      if (accion === "vaciar") vaciar();
      if (accion === "volver") dibujar();
    });
  }

  let focoAnterior = null;
  function abrir() {
    const panel = document.querySelector("[data-carrito]");
    if (!panel) return;
    if (typeof cerrarModal === "function") cerrarModal();
    focoAnterior = document.activeElement;
    dibujar();
    panel.hidden = false;
    document.querySelector("[data-carrito-fondo]").hidden = false;
    document.body.style.overflow = "hidden";
    panel.querySelector("[data-carrito-cerrar]").focus();
  }
  function cerrar() {
    const panel = document.querySelector("[data-carrito]");
    if (!panel || panel.hidden) return;
    panel.hidden = true;
    document.querySelector("[data-carrito-fondo]").hidden = true;
    document.body.style.overflow = "";
    if (focoAnterior && document.contains(focoAnterior)) focoAnterior.focus();
  }

  function dibujar() {
    // Contador del encabezado
    document.querySelectorAll("[data-carrito-cantidad]").forEach(function (el) {
      el.textContent = cantidadTotal();
    });

    const lista = document.querySelector("[data-carrito-lista]");
    const pie = document.querySelector("[data-carrito-pie]");
    if (!lista || !pie) return;

    const actuales = vigentes();
    if (!actuales.length) {
      lista.innerHTML = '<p class="carrito__vacio">Todavía no agregaste prendas.</p>';
      pie.innerHTML = "";
      return;
    }

    let total = 0;
    let faltanPrecios = false;
    lista.innerHTML = actuales.map(function (i, n) {
      const p = producto(i.id);
      let precio;
      if (p.precio) {
        total += p.precio * i.cantidad;
        precio = formatearPrecio(p.precio * i.cantidad);
      } else {
        faltanPrecios = true;
        precio = "Precio a confirmar";
      }
      const foto = p.foto ? '<img src="' + esc(p.foto) + '" alt="" loading="lazy">' : "";
      return '' +
        '<div class="carrito__item">' +
          '<div class="carrito__foto">' + foto + '</div>' +
          '<div class="carrito__datos">' +
            '<p class="carrito__nombre">' + esc(p.nombre) + '</p>' +
            (detalle(i) ? '<p class="carrito__detalle">' + esc(detalle(i)) + '</p>' : "") +
            '<div class="carrito__cantidad">' +
              '<button type="button" data-accion="menos" data-indice="' + n + '" aria-label="Uno menos">−</button>' +
              '<span aria-label="Cantidad">' + i.cantidad + '</span>' +
              '<button type="button" data-accion="mas" data-indice="' + n + '" aria-label="Uno más">+</button>' +
              '<button type="button" class="carrito__quitar" data-accion="quitar" data-indice="' + n + '">Quitar</button>' +
            '</div>' +
          '</div>' +
          '<p class="carrito__precio">' + esc(precio) + '</p>' +
        '</div>';
    }).join("");

    pie.innerHTML = '' +
      '<div class="carrito__total">' +
        '<span>Total</span><span>' + esc(formatearPrecio(total) || "$ 0") + '</span>' +
      '</div>' +
      (faltanPrecios ? '<p class="carrito__nota">Hay prendas con precio a confirmar: te lo pasamos por WhatsApp.</p>' : "") +
      '<form class="carrito__form" data-carrito-form novalidate>' +
        '<div class="campo">' +
          '<label for="carrito-telefono">Tu teléfono</label>' +
          '<input type="tel" id="carrito-telefono" name="telefono" autocomplete="tel" inputmode="tel" required placeholder="Ej: 11 5555-1234">' +
        '</div>' +
        '<p class="carrito__error" data-carrito-error role="alert"></p>' +
        '<button type="submit" class="btn btn--wsp">Finalizar pedido</button>' +
      '</form>';

    pie.querySelector("[data-carrito-form]").addEventListener("submit", finalizar);
  }

  function finalizar(e) {
    e.preventDefault();
    const campo = document.getElementById("carrito-telefono");
    const error = document.querySelector("[data-carrito-error]");
    const telefono = campo.value.trim();
    const digitos = telefono.replace(/\D/g, "");
    if (digitos.length < 8 || digitos.length > 15) {
      error.textContent = "Escribí un teléfono válido, con código de área. Ej: 11 5555-1234";
      campo.focus();
      return;
    }
    error.textContent = "";

    window.open(linkWhatsapp(armarMensaje(telefono)), "_blank", "noopener");

    // No se vacia solo: si el cliente cerro WhatsApp sin mandar, no pierde el pedido
    document.querySelector("[data-carrito-pie]").innerHTML = '' +
      '<p class="carrito__nota">Te abrimos WhatsApp con el pedido listo. ¿Ya lo enviaste?</p>' +
      '<div class="carrito__acciones">' +
        '<button type="button" class="btn btn--primario" data-accion="vaciar">Sí, vaciar carrito</button>' +
        '<button type="button" class="btn btn--linea" data-accion="volver">Todavía no</button>' +
      '</div>';
  }

  function mostrarAviso() {
    const boton = document.querySelector(".carrito-boton");
    if (!boton) return;
    boton.classList.remove("carrito-boton--pulso");
    void boton.offsetWidth;            // reinicia la animacion
    boton.classList.add("carrito-boton--pulso");
  }

  /* ---------- Arranque ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    crearPanel();
    document.querySelectorAll(".carrito-boton").forEach(function (b) {
      b.addEventListener("click", abrir);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") cerrar();
    });
    dibujar();
    if (!EMPRESA.sheetProductos) listo = true;
  });

  // Cuando llegan los datos del Sheet: se redibuja con precios nuevos y se
  // limpian del guardado las prendas que ya no existen o se ocultaron.
  document.addEventListener("braccis:hoja-lista", function () {
    listo = true;
    const antes = items.length;
    items = vigentes();
    if (items.length !== antes) guardar();
    dibujar();
  });

  // Si otra pestaña cambia el carrito, esta se entera
  window.addEventListener("storage", function (e) {
    if (e.key === CLAVE) { items = leer(); dibujar(); }
  });

  return { agregar: agregar, abrir: abrir, cerrar: cerrar, vaciar: vaciar,
           armarMensaje: armarMensaje, cantidadTotal: cantidadTotal,
           estaListo: function () { return listo; } };
})();
