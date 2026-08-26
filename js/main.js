/* ============================================================
   Braccis - comportamiento comun a todas las paginas
   Menu movil, animaciones de entrada, ano del footer y
   volcado de los datos de EMPRESA en el HTML.
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
  menuMovil();
  volcarDatosEmpresa();
  animarAlScrollear();
  anioActual();
});

/* ---------- Menu hamburguesa ---------- */
function menuMovil() {
  const boton = document.querySelector(".hamburguesa");
  const nav = document.querySelector(".nav");
  if (!boton || !nav) return;

  boton.addEventListener("click", function () {
    const abierto = nav.classList.toggle("abierta");
    boton.setAttribute("aria-expanded", abierto ? "true" : "false");
  });

  // Al tocar un link del menu, cerrarlo
  nav.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      nav.classList.remove("abierta");
      boton.setAttribute("aria-expanded", "false");
    });
  });
}

/* ---------- Rellenar datos de contacto ----------
   Cualquier elemento con data-empresa="clave" recibe el valor
   correspondiente de EMPRESA. Los <a> ademas reciben el href.  */
function volcarDatosEmpresa() {
  if (typeof EMPRESA === "undefined") return;

  document.querySelectorAll("[data-empresa]").forEach(function (el) {
    const clave = el.dataset.empresa;
    const valor = EMPRESA[clave];

    // Si el dato esta vacio se esconde el bloque entero, para no dejar
    // una fila en blanco. Sirve para no publicar datos que no tenemos.
    if (!valor) {
      const bloque = el.closest("li, .dato");
      if (bloque) bloque.hidden = true;
      else el.hidden = true;
      return;
    }

    el.textContent = valor;

    if (el.tagName === "A") {
      if (clave === "email") el.href = "mailto:" + valor;
      // El "+" es necesario: sin el, un celular no marca bien el numero
      else if (clave === "telefonoVisible") el.href = "tel:+" + EMPRESA.whatsapp;
      else if (clave === "instagramUsuario") el.href = EMPRESA.instagram;
    }
  });

  // Todos los links de WhatsApp del sitio
  document.querySelectorAll("[data-wsp]").forEach(function (el) {
    el.href = linkWhatsapp();
    el.target = "_blank";
    el.rel = "noopener";
  });
}

/* ---------- Animacion suave al entrar en pantalla ---------- */
function animarAlScrollear() {
  const elementos = document.querySelectorAll(".aparece");
  if (!elementos.length || !("IntersectionObserver" in window)) {
    elementos.forEach(function (el) { el.classList.add("visible"); });
    return;
  }

  const observador = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (entrada) {
      if (entrada.isIntersecting) {
        entrada.target.classList.add("visible");
        observador.unobserve(entrada.target);
      }
    });
  }, { threshold: 0.12 });

  elementos.forEach(function (el) { observador.observe(el); });
}

/* ---------- Ano en el footer ---------- */
function anioActual() {
  const el = document.querySelector("[data-anio]");
  if (el) el.textContent = new Date().getFullYear();
}
