# Braccis — sitio web

Sitio estático (HTML + CSS + JavaScript, sin frameworks ni build).
Se abre haciendo doble clic en `index.html` y se publica gratis.

---

## Estructura

```
Braccis/
├── index.html          Portada
├── catalogo.html       Catálogo con filtros y buscador
├── contacto.html       Formulario y datos de contacto
├── css/
│   └── styles.css      Todos los estilos
├── js/
│   ├── config.js       ← DATOS DE LA EMPRESA (editar acá)
│   ├── productos.js    ← LAS PRENDAS (editar acá)
│   ├── catalogo.js     Motor del catálogo (no hace falta tocarlo)
│   ├── contacto.js     Formulario (no hace falta tocarlo)
│   └── main.js         Menú, animaciones (no hace falta tocarlo)
├── img/
│   └── prendas/        Fotos de las prendas (salieron de los PDF)
├── catalogos/          Los PDF originales (ver nota al publicar)
└── herramientas/
    └── generar_catalogo.py   Lee los PDF y regenera el catálogo
```

**De todo esto, solo hay dos archivos que se tocan seguido:
`js/config.js` y `js/productos.js`.**

Las 53 prendas y sus fotos ya están cargadas, sacadas de los cuatro
catálogos PDF (JEANS, CAP REMERAS, HILO y CAMISAS).

---

## 1. Cargar los datos de la empresa

Abrí `js/config.js` y completá lo que está entre comillas.
Con eso se actualiza el header, el footer, la página de contacto
y todos los botones de WhatsApp de una sola vez.

El único dato con truco es el WhatsApp: va **solo números, con código
de país y sin el 15**.

| Número real        | Cómo se escribe   |
|--------------------|-------------------|
| (011) 15-5555-1234 | `5491155551234`   |
| (0341) 15-666-7777 | `5493416667777`   |

---

## 2. Cargar prendas

Todas las prendas están en `js/productos.js`, una por renglón.
Para cargar una nueva, copiá un renglón existente y cambiá los textos:

```js
{
  id: "delfina",                  // único, sin espacios ni acentos
  nombre: "Remera Delfina",
  codigo: "382072",
  categoria: "remeras",           // tiene que existir en CATEGORIAS
  precio: 18500,                  // o null si no se muestra precio
  descripcion: "Remera de algodón peinado, corte holgado.",
  tela: "100% algodón",
  talles: ["S", "M", "L", "XL"],
  colores: [
    { nombre: "Crudo", hex: "#f2ece3" },
    { nombre: "Negro", hex: "#1f1b18" }
  ],
  foto: "img/prendas/delfina.jpg",
  destacado: true                 // true = aparece en la portada
}
```

Detalles que conviene saber:

- Los campos que quedan vacíos (`""` o `[]`) simplemente **no se muestran**,
  no rompen nada. Se puede cargar de a poco.
- Si `foto` queda en `""`, se ve un placeholder rayado con la inicial.
- `destacado: true` la sube a la portada. Poné hasta 8.
- Para agregar una categoría nueva, sumala arriba de todo en `CATEGORIAS`
  y usá ese `id` en las prendas.

### Fotos

Guardalas en `img/prendas/` con nombre simple y sin acentos
(`sunflower.jpg`, `jeans-kady.jpg`). Recomendado: **formato vertical 3:4**
(ej. 900×1200 px), JPG de menos de 300 KB para que el sitio cargue rápido.

---

## 2 bis. Cargar una colección nueva desde un PDF

Cuando llegue un catálogo nuevo no hace falta cargar todo a mano:

1. Copiá el PDF a `catalogos/`.
2. Abrí `herramientas/generar_catalogo.py` y agregá una línea por prenda
   en la lista `PRENDAS`, con el número de página del PDF donde está.
3. Corré:

```bash
python herramientas/generar_catalogo.py
```

El script saca la foto de cada página, la recorta a 900×1200, la guarda
en `img/prendas/` y reescribe `js/productos.js` entero.

Una sola vez, antes de la primera corrida:

```bash
pip install pymupdf pillow
```

**Ojo:** el script *pisa* `js/productos.js`. Si cargaste precios a mano
en ese archivo, pasalos al script antes de volver a correrlo.

---

## 3. Formulario de contacto

Viene funcionando de entrada sin necesidad de servidor: al enviarlo,
**arma el mensaje y lo abre en WhatsApp**.

Si preferís recibir los mensajes por mail:

1. Entrá a [formspree.io](https://formspree.io) y creá una cuenta gratis.
2. Creá un formulario nuevo con el mail donde querés recibirlos.
3. Copiá la URL que te da (algo como `https://formspree.io/f/xxxxxxx`).
4. Pegala en `js/config.js`, en `formEndpoint`.

Con eso el formulario pasa a enviar por mail automáticamente.

---

## 4. Ver el sitio mientras se trabaja

Doble clic en `index.html` alcanza para la mayoría de los casos.

Para verlo como se va a ver publicado (con las rutas bien resueltas),
desde la carpeta del proyecto:

```bash
python -m http.server 5173
```

Y abrir `http://localhost:5173` en el navegador.

---

## 5. Publicarlo

La opción más simple y gratuita es **Netlify Drop**:

1. Entrá a [app.netlify.com/drop](https://app.netlify.com/drop).
2. Arrastrá la carpeta `Braccis` entera a la ventana.
3. Listo, queda online con una URL tipo `braccis.netlify.app`.

Para usar un dominio propio (`braccis.com.ar`), se compra en
[NIC Argentina](https://nic.ar) y se apunta desde el panel de Netlify.

Cada vez que cambies algo, volvés a arrastrar la carpeta y se actualiza.

> **Antes de arrastrar, vaciá `catalogos/`.** Los cuatro PDF pesan 140 MB
> y el sitio entero pesa 4 MB. Si están adentro, la subida tarda muchísimo
> al pedo: nadie los ve, no están linkeados desde ninguna página.
> Guardalos aparte y copialos de vuelta solo cuando corras el generador.

---

## Sobre los colores

Las bolitas de color que se ven en el catálogo **son recortes del propio PDF**,
no colores elegidos a mano. Según la cápsula, el catálogo dibuja una cosa u otra:

- **Remeras**: el circulito es una foto de la tela
- **Camisas y poleras**: el circulito es la prenda puesta, en ese color
- **Hilo**: no hay circulito. El catálogo lista los colores solo por escrito

Por eso hay prendas que muestran bolitas y otras que muestran solo el nombre
del color. **Es a propósito.** De los 140 colores del catálogo, 81 tienen
muestra dibujada y 59 no.

Cuando el PDF no trae la muestra, no se inventa: va el nombre y nada más.
Si la empresa pasa los colores reales, se pueden cargar a mano en
`js/productos.js` agregando `muestra: "..."` al color que corresponda.

---

## Sobre los textos del sitio

Casi todo lo que se lee en la web sale de los catálogos: el logo, la frase
*"Piezas que te acompañan siempre"*, *"Diseños que te acompañan, calidad que
te representa"* y el nombre de la colección (Primavera–Verano 2027, SS-27).

**Regla para no meter la pata: no inventar texto de marca.** Si hace falta
decir algo nuevo, que sea un dato verificable (cuántas prendas hay, qué
cápsulas la componen) o que lo confirme la empresa.

Hubo tres frases inventadas que ya se sacaron, porque no hay forma de saber
si son ciertas: *"diseñada y confeccionada en Argentina"*, *"trabajamos con
telas seleccionadas y series cortas"* y *"Hecho en Argentina"*. Si la empresa
confirma que fabrica en el país, se pueden poner de vuelta.

---

## Seguridad

El sitio es estático: no tiene base de datos, ni panel de administración,
ni usuarios, ni contraseñas. **No guarda ningún dato de quien lo visita**
(nada de cookies, ni localStorage, ni analítica). Eso elimina de entrada
la mayoría de los ataques típicos: no hay nada que robar ni dónde entrar.

Lo que sí se cubrió:

| Riesgo | Cómo está resuelto |
|---|---|
| Inyección de código por los datos | Todo lo que sale de `productos.js` se escapa antes de mostrarse (`esc()` en `catalogo.js`) |
| Scripts de terceros | Ninguno. Solo la tipografía de Google |
| Enlaces a otros sitios | Todos con `rel="noopener"` |
| Robots de spam en el formulario | Campo trampa invisible en `contacto.html` |
| Cabeceras del servidor | Archivo `_headers` (lo lee Netlify al publicar) |
| Contraseñas o claves en el código | No hay ninguna |
| Los PDF del catálogo | Fuera de la carpeta que se publica |

**El archivo `_headers` tiene que subirse junto al resto.** Si se publica
en un servicio que no lo lee (GitHub Pages, por ejemplo), esas protecciones
no se aplican.

Dos cosas que quedan a criterio de ustedes:

- **La tipografía se carga desde Google.** Funciona bien, pero le avisa a
  Google la IP de cada visitante. Se puede evitar descargando las fuentes
  y sirviéndolas desde el propio sitio.
- **HSTS** (la última línea de `_headers`) conviene activarlo recién cuando
  el dominio definitivo funcione bien por HTTPS.

---

## Antes de publicar

Reviso hecha el 26/08/2026. El sitio pasó estos controles:

| Control | Resultado |
|---|---|
| Enlaces y archivos referenciados | 198 imágenes, ninguna rota, ningún huérfano |
| Las 53 fichas abren | Sin fallos |
| Filtros | 19+3+2+19+10 = 53, sin prendas perdidas ni repetidas |
| Buscador | Por nombre, por código, sin distinguir mayúsculas |
| Formulario | Valida y arma el mensaje de WhatsApp |
| Menú móvil | Abre, cierra y no desborda |
| Contraste (WCAG AA) | Todos los textos por encima de 4.5:1 |
| Teclado | Se navega, se abre con Enter, cierra con Escape, el foco vuelve |
| Errores de consola | Ninguno en las tres páginas |
| Peso | 6 MB, imagen más pesada 123 KB |

**Sin esto no se puede publicar:**

- [ ] **Mail real de la empresa** en `js/config.js` (hoy hay uno inventado)
- [ ] **Dirección y horarios** en `js/config.js`, o borrar esos bloques
      de `contacto.html` si no atienden al público

**Para que quede completo:**

- [ ] Precios, si se van a mostrar (`precio` de cada prenda)
- [ ] Composición de la tela por prenda (campo `tela`, vacío por ahora)
- [ ] Foto del taller para la sección "Nosotros" (hoy usa una foto de producto)
- [ ] Si quieren contar la historia de la empresa, va en la sección "Nosotros"

**Datos raros de los catálogos, para avisarle a quien los arma:**

- [ ] *Celina* (pág. 6 de HILO) y *Julieta* (pág. 7) tienen el mismo código `27V00408`
- [ ] El sweater de la pág. 3 de HILO no tiene nombre propio
- [ ] El *Jeans Sunny* figura con talles 24-28-30-32-34, sin el 26
- [ ] Los jeans no tienen colores listados (las otras cápsulas sí)
