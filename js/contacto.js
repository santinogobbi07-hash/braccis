/* ============================================================
   Braccis - formulario de contacto
   ------------------------------------------------------------
   Funciona de dos maneras segun EMPRESA.formEndpoint (config.js):

   1) Si formEndpoint esta VACIO (por defecto):
      el formulario arma el mensaje y lo abre en WhatsApp.
      No necesita servidor ni servicio externo. Funciona ya.

   2) Si formEndpoint tiene una URL (ej. de Formspree):
      el mensaje se envia por mail a esa direccion.
      Ver README.md para darlo de alta en 2 minutos.
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("[data-form]");
  if (!form) return;

  const estado = form.querySelector("[data-form-estado]");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const datos = Object.fromEntries(new FormData(form).entries());

    // Si el campo trampa vino completo, lo mando un robot: se descarta
    // en silencio para no darle pistas.
    if (datos["apellido-2"]) return;
    delete datos["apellido-2"];

    if (!EMPRESA.formEndpoint) {
      enviarPorWhatsapp(datos, estado);
    } else {
      enviarPorEndpoint(form, estado);
    }
  });
});

/* ---------- Modo 1: abrir WhatsApp con el mensaje armado ---------- */
function enviarPorWhatsapp(datos, estado) {
  const mensaje =
    "¡Hola! Soy " + datos.nombre + "." +
    "\nMotivo: " + datos.asunto +
    "\nEmail: " + datos.email +
    (datos.telefono ? "\nTeléfono: " + datos.telefono : "") +
    "\n\n" + datos.mensaje;

  window.open(linkWhatsapp(mensaje), "_blank", "noopener");

  if (estado) {
    estado.textContent = "Te abrimos WhatsApp con el mensaje listo para enviar.";
  }
}

/* ---------- Modo 2: enviar al servicio configurado ---------- */
function enviarPorEndpoint(form, estado) {
  const boton = form.querySelector('button[type="submit"]');
  const textoOriginal = boton.textContent;

  boton.disabled = true;
  boton.textContent = "Enviando...";
  if (estado) estado.textContent = "";

  fetch(EMPRESA.formEndpoint, {
    method: "POST",
    body: new FormData(form),
    headers: { Accept: "application/json" }
  })
    .then(function (res) {
      if (!res.ok) throw new Error("Fallo el envio");
      form.reset();
      if (estado) estado.textContent = "Listo, recibimos tu mensaje. Te respondemos a la brevedad.";
    })
    .catch(function () {
      if (estado) {
        estado.textContent = "No pudimos enviarlo. Escribinos por WhatsApp o a " + EMPRESA.email + ".";
      }
    })
    .finally(function () {
      boton.disabled = false;
      boton.textContent = textoOriginal;
    });
}
