/* ============================================================
   Braccis - boton de arrepentimiento
   ------------------------------------------------------------
   Arma la solicitud y la abre en WhatsApp, igual que el
   formulario de contacto.

   OJO: la Resolucion 424/2020 obliga a Braccis a contestar cada
   solicitud dentro de las 24 horas con un numero de tramite.
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("[data-form-arrepentimiento]");
  if (!form) return;

  const estado = form.querySelector("[data-form-estado]");
  const fecha = form.querySelector("#arr-fecha");

  // No se puede elegir una fecha futura
  const hoy = new Date();
  fecha.max = hoy.getFullYear() + "-" +
    String(hoy.getMonth() + 1).padStart(2, "0") + "-" +
    String(hoy.getDate()).padStart(2, "0");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const datos = Object.fromEntries(new FormData(form).entries());

    // Si el campo trampa vino completo, lo mando un robot: se descarta
    if (datos["apellido-2"]) return;

    const digitos = (datos.telefono || "").replace(/\D/g, "");
    if (digitos.length < 8 || digitos.length > 15) {
      estado.textContent = "Escribí un teléfono válido, con código de área. Ej: 11 5555-1234";
      form.querySelector("#arr-telefono").focus();
      return;
    }

    const mensaje =
      "Hola, quiero arrepentirme de mi compra (Botón de arrepentimiento)." +
      "\nNombre: " + datos.nombre +
      "\nTeléfono: " + datos.telefono +
      (datos.email ? "\nEmail: " + datos.email : "") +
      "\nFecha de compra o entrega: " + fechaLegible(datos.fecha) +
      "\nPrendas: " + datos.prendas;

    window.open(linkWhatsapp(mensaje), "_blank", "noopener");
    estado.textContent = "Te abrimos WhatsApp con la solicitud lista. Mandala y dentro de las 24 horas te respondemos con un número de trámite.";
  });
});

// "2026-09-29" -> "29/09/2026"
function fechaLegible(valor) {
  const partes = (valor || "").split("-");
  return partes.length === 3 ? partes[2] + "/" + partes[1] + "/" + partes[0] : valor;
}
