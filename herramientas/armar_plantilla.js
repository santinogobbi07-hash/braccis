// Braccis - arma la plantilla del Google Sheets con las prendas actuales.
// Correr:  node herramientas/armar_plantilla.js
// Sale:    herramientas/plantilla-productos.csv  (se importa en Google Sheets)
const fs = require("fs");
const path = require("path");
const raiz = path.join(__dirname, "..");

// productos.js es un archivo del navegador: se ejecuta aparte para leer los datos
const codigo = fs.readFileSync(path.join(raiz, "js/productos.js"), "utf8");
const { CATEGORIAS, PRODUCTOS } = new Function(codigo + "; return { CATEGORIAS, PRODUCTOS };")();

function celda(v) {
  const t = String(v == null ? "" : v);
  return /[",\n\r]/.test(t) ? '"' + t.replace(/"/g, '""') + '"' : t;
}
const nombreCategoria = id => (CATEGORIAS.find(c => c.id === id) || {}).nombre || id;

const titulos = ["id (no tocar)", "codigo", "nombre", "categoria", "precio",
                 "foto", "visible", "talles", "descripcion"];
const filas = PRODUCTOS.map(p => [
  p.id, p.codigo, p.nombre, nombreCategoria(p.categoria), p.precio || "",
  path.basename(p.foto || ""), "si", (p.talles || []).join(", "), p.descripcion,
]);

const csv = [titulos].concat(filas).map(f => f.map(celda).join(",")).join("\r\n") + "\r\n";
const salida = path.join(__dirname, "plantilla-productos.csv");
fs.writeFileSync(salida, "\uFEFF" + csv, "utf8");
console.log("Listo: herramientas/plantilla-productos.csv (" + filas.length + " prendas)");
