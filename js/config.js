/* ============================================================
   Braccis - datos de la empresa
   ------------------------------------------------------------
   Cambiando estos valores se actualiza TODO el sitio de una:
   el header, el footer, los botones de WhatsApp y la pagina
   de contacto. No hay que buscar el dato en cada HTML.
   ============================================================ */

const EMPRESA = {
  nombre: "Braccis",
  // OJO: solo texto que sepamos que es cierto. Antes decia "diseñada y
  // confeccionada en Argentina", pero eso no figura en ningun catalogo:
  // si lo fabrican aca, poner esa frase de vuelta.
  descripcionCorta: "Indumentaria femenina. Colección Primavera–Verano 2027.",

  // Telefono para el link de WhatsApp: solo numeros, con codigo de pais
  // y SIN el 15. Argentina = 54 + 9 + codigo de area + numero.
  // Ej: (11) 5555-1234 se escribe "5491155551234".
  // Tomado de la ultima pagina de los catalogos PDF
  whatsapp: "5491126234369",
  whatsappTexto: "¡Hola! Quiero hacer una consulta sobre las prendas.",

  // Telefono como se muestra en pantalla
  telefonoVisible: "+54 9 11 2623-4369",

  // Vacio a proposito: el mail que habia era inventado y no se puede
  // publicar. Al quedar vacio, la fila del mail no se muestra en ningun
  // lado. Cuando tengan el real, se escribe aca y aparece solo.
  email: "",

  // OJO: falta la altura de la calle (el numero). Sin eso la direccion
  // queda incompleta para quien quiera ir.
  direccion: "San José, San Miguel (B1714), Buenos Aires",

  // Confirmados por la empresa
  horarios: "Lunes a viernes de 9 a 18 h",

  instagram: "https://instagram.com/braccisoficial",
  instagramUsuario: "@braccisoficial",
  facebook: "",

  // Direccion a donde llegan los mensajes del formulario de contacto.
  // Ver README.md, seccion "Formulario de contacto".
  formEndpoint: "",

  // Links del Google Sheets publicado como CSV (ver README.md, seccion
  // "Administrar el sitio desde Google Sheets"). Vacios = el sitio usa
  // los datos de js/productos.js, sin precios.
  //   sheetProductos: pestaña "Productos" (precios, nombres, fotos)
  //   sheetAjustes:   pestaña "Ajustes" (video de portada)
  sheetProductos: "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1-0hjIajs9ZoIuhltFO_u-W4CXn8r7SBb6Hyx3cZkMAgGb3sxOUUbvbHKmp5XgyzCHzI_eQ3K2fLD/pub?gid=287490435&single=true&output=csv",
  sheetAjustes: "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1-0hjIajs9ZoIuhltFO_u-W4CXn8r7SBb6Hyx3cZkMAgGb3sxOUUbvbHKmp5XgyzCHzI_eQ3K2fLD/pub?gid=1246368891&single=true&output=csv",

  // Venta mayorista: desde cuantas unidades de una misma prenda (o en
  // todo el carrito) se le avisa al cliente que hay precios mayoristas y
  // se le ofrece consultarlos por WhatsApp. OJO: 12 es un valor de
  // ejemplo, CONFIRMAR CON BRACCIS su minimo mayorista real.
  // En 0 no se muestra el aviso.
  mayoristaDesde: 12,

  // Link del canal de WhatsApp de Braccis. Si tiene un link, al tocar
  // "Finalizar pedido" se pregunta primero "¿Ya te sumaste a nuestro canal
  // de WhatsApp?". Vacio = no se pregunta y se va directo al pedido.
  // Tiene que empezar con https://whatsapp.com/channel/
  canalWhatsapp: "https://whatsapp.com/channel/0029VbCMaEx0Qearpf44mm47",

  // Catalogo en PDF que se descarga desde el menu
  catalogoPdf: "docs/catalogo-braccis-pv2027.pdf",

  // ---------- Datos legales (Ley 24.240 de Defensa del Consumidor) ----------
  // Los tiene que pasar Braccis. Mientras esten vacios no se muestran.
  // razonSocial: como figura en ARCA (ej. "Braccis S.R.L." o el nombre
  //              y apellido del titular si es monotributista)
  // cuit:        con guiones, ej. "30-12345678-9"
  razonSocial: "",
  cuit: "",

  // Data fiscal de ARCA (ex AFIP): el link del codigo QR del formulario
  // 960. Lo da ARCA al tramitarlo y empieza con "http://qr.afip.gob.ar/".
  // Se pega entero aca y aparece solo el cuadrito en el pie de pagina.
  dataFiscal: "",

  // Pagina oficial para hacer reclamos de consumo (obligatorio mostrarla)
  reclamos: "https://www.argentina.gob.ar/produccion/defensadelconsumidor/formulario"
};

/* --- Helpers usados por el resto del sitio --- */

// Arma el link de WhatsApp, opcionalmente con un mensaje sobre una prenda
function linkWhatsapp(mensaje) {
  const texto = mensaje || EMPRESA.whatsappTexto;
  return "https://wa.me/" + EMPRESA.whatsapp + "?text=" + encodeURIComponent(texto);
}

// Formatea un numero como precio argentino: 18500 -> "$ 18.500"
function formatearPrecio(valor) {
  if (valor === null || valor === undefined || valor === "") return "";
  const n = Number(valor);
  const decimales = n % 1 ? 2 : 0;          // 19990.5 -> "19.990,50", no "19.990,5"
  return "$ " + n.toLocaleString("es-AR", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales
  });
}
