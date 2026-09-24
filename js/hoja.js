/* ============================================================
   Braccis - datos desde Google Sheets
   ------------------------------------------------------------
   Lee el Google Sheets publicado como CSV y lo mezcla con las
   prendas de js/productos.js. El sitio se dibuja primero con los
   datos locales y se actualiza cuando llega el Sheet: si Google
   tarda o falla, el visitante igual ve el catalogo.

   Pestaña "Productos" (una fila por prenda):
     id | codigo | nombre | categoria | precio | foto | visible | talles | descripcion
     - "id" identifica la prenda. Si no existe en productos.js, es nueva.
     - Celda vacia = se deja el dato que ya estaba.
     - visible = "no" oculta la prenda.

   Pestaña "Ajustes" (clave | valor):
     video_portada | portada.mp4   (archivo de la carpeta video/ o link https)

   El Sheet es publico y cualquiera con permiso de edicion lo cambia:
   todo lo que viene de ahi se valida aca y se escapa al mostrarse.
   ============================================================ */

const AJUSTES = {};
const ESPERA_MAXIMA_MS = 6000;

/* Convierte el texto de un CSV en una lista de filas.
   Respeta comillas ("Remera, basica"), comillas dobles escapadas ("") y
   saltos de linea de Windows. */
function leerCSV(texto) {
  const filas = [];
  let fila = [];
  let celda = "";
  let entreComillas = false;
  texto = String(texto || "").replace(/^﻿/, "");

  for (let i = 0; i < texto.length; i++) {
    const c = texto[i];
    if (entreComillas) {
      if (c === '"' && texto[i + 1] === '"') { celda += '"'; i++; }
      else if (c === '"') entreComillas = false;
      else celda += c;
    } else if (c === '"') {
      entreComillas = true;
    } else if (c === ",") {
      fila.push(celda); celda = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && texto[i + 1] === "\n") i++;
      fila.push(celda); celda = "";
      filas.push(fila); fila = [];
    } else {
      celda += c;
    }
  }
  if (celda !== "" || fila.length) { fila.push(celda); filas.push(fila); }

  // Se descartan las filas totalmente vacias
  return filas.filter(function (f) { return f.some(function (x) { return x.trim() !== ""; }); });
}

/* Pasa las filas a objetos usando la primera fila como titulos.
   "id (no tocar)" se lee como "id": solo cuenta la primera palabra. */
function filasAObjetos(filas) {
  if (!filas.length) return [];
  const titulos = filas[0].map(function (t) {
    return t.trim().toLowerCase().split(/[\s(]/)[0];
  });
  return filas.slice(1).map(function (f) {
    const o = {};
    titulos.forEach(function (t, i) { o[t] = (f[i] || "").trim(); });
    return o;
  });
}

/* Precio en formato argentino -> numero.
   Acepta 18500, 18.500, $ 18.500, 18.500,50 y 18500.50. */
function aNumero(texto) {
  let t = String(texto || "").replace(/[^\d.,]/g, "");
  if (!t) return null;
  if (t.indexOf(",") !== -1) {
    t = t.replace(/\./g, "").replace(",", ".");        // 18.500,50
  } else if (/^\d{1,3}(\.\d{3})+$/.test(t)) {
    t = t.replace(/\./g, "");                           // 18.500
  }
  const n = Number(t);
  return isFinite(n) && n > 0 ? n : null;
}

/* Solo se aceptan nombres de archivo simples (sin carpetas ni links):
   asi nadie puede apuntar la foto a cualquier lado desde el Sheet. */
function archivoValido(nombre, extensiones) {
  const re = new RegExp("^[\\w\\-. ]+\\.(" + extensiones + ")$", "i");
  return re.test(nombre) && nombre.indexOf("..") === -1;
}

function categoriaDe(texto) {
  const t = texto.trim().toLowerCase();
  const c = CATEGORIAS.find(function (x) {
    return x.id === t || x.nombre.toLowerCase() === t;
  });
  return c ? c.id : "";
}

/* Mezcla una fila del Sheet con la prenda correspondiente */
function aplicarFila(f) {
  if (!f.id) return;
  let p = PRODUCTOS.find(function (x) { return x.id === f.id; });
  const nueva = !p;

  if (nueva) {
    // Una prenda nueva necesita al menos nombre y foto para mostrarse bien
    if (!f.nombre || !f.foto) return;
    p = { id: f.id, nombre: "", codigo: "", categoria: "", precio: null,
          descripcion: "", tela: "", talles: [], colores: [], foto: "",
          galeria: [], destacado: false, desdeHoja: true };
    PRODUCTOS.push(p);
  }

  if (f.nombre) p.nombre = f.nombre;
  if (f.codigo) p.codigo = f.codigo;
  if (f.descripcion) p.descripcion = f.descripcion;
  if (f.categoria && categoriaDe(f.categoria)) p.categoria = categoriaDe(f.categoria);

  const precio = aNumero(f.precio);
  if (precio !== null) p.precio = precio;

  if (f.foto && archivoValido(f.foto, "jpe?g|png|webp")) {
    p.foto = "img/prendas/" + f.foto;
  } else if (nueva) {
    PRODUCTOS.pop();          // sin una foto valida, la prenda nueva no entra
    return;
  }

  if (f.talles) {
    p.talles = f.talles.split(/[,;]/).map(function (t) { return t.trim(); }).filter(Boolean);
  }

  p.oculto = /^(no|n|0|false|oculto)$/i.test(f.visible || "");
}

/* Descarga un CSV con tiempo maximo de espera */
function traerCSV(url) {
  const control = typeof AbortController !== "undefined" ? new AbortController() : null;
  const reloj = setTimeout(function () { if (control) control.abort(); }, ESPERA_MAXIMA_MS);
  return fetch(url, { signal: control ? control.signal : undefined, cache: "no-store" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    })
    .finally(function () { clearTimeout(reloj); });
}

function cargarHoja() {
  const pedidos = [];

  if (EMPRESA.sheetProductos) {
    pedidos.push(traerCSV(EMPRESA.sheetProductos).then(function (texto) {
      filasAObjetos(leerCSV(texto)).forEach(aplicarFila);
    }).catch(function () { /* sin Sheet: quedan los datos locales */ }));
  }

  if (EMPRESA.sheetAjustes) {
    pedidos.push(traerCSV(EMPRESA.sheetAjustes).then(function (texto) {
      leerCSV(texto).slice(1).forEach(function (f) {
        const clave = (f[0] || "").trim().toLowerCase();
        if (clave) AJUSTES[clave] = (f[1] || "").trim();
      });
    }).catch(function () {}));
  }

  Promise.all(pedidos).then(function () {
    if (pedidos.length && typeof redibujarCatalogo === "function") redibujarCatalogo();
    document.dispatchEvent(new CustomEvent("braccis:hoja-lista", { detail: AJUSTES }));
  });
}

/* ------------------------------------------------------------
   Video de portada (solo existe en index.html)
   ------------------------------------------------------------ */
function ponerVideoPortada(valor) {
  const video = document.querySelector(".hero__video");
  if (!video || !valor) return;

  // Respeta a quien pidio menos movimiento o esta ahorrando datos
  const menosMovimiento = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ahorroDatos = navigator.connection && navigator.connection.saveData;
  if (menosMovimiento || ahorroDatos) return;

  let src = "";
  if (/^https:\/\/\S+$/i.test(valor)) src = valor;
  else if (archivoValido(valor, "mp4|webm")) src = "video/" + valor;
  if (!src) return;

  // El video arranca transparente (no oculto: Chrome pausa los videos que
  // no estan a la vista) y aparece recien cuando de verdad se reproduce.
  // Si falla, queda la foto de siempre.
  const hero = video.closest(".hero");
  function fallo() {
    hero.classList.remove("hero--con-video");
    video.removeAttribute("src");
  }
  video.muted = true;               // sin sonido: si no, el navegador no lo reproduce solo
  video.addEventListener("playing", function () {
    hero.classList.add("hero--con-video");
  }, { once: true });
  video.addEventListener("error", fallo, { once: true });
  video.src = src;
  const intento = video.play();
  if (intento && intento.catch) intento.catch(fallo);
}

document.addEventListener("braccis:hoja-lista", function (e) {
  ponerVideoPortada((e.detail || {}).video_portada);
});

document.addEventListener("DOMContentLoaded", cargarHoja);
