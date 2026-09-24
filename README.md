# Braccis — sitio web

**En línea:** https://santinogobbi07-hash.github.io/braccis/
**Repositorio:** https://github.com/santinogobbi07-hash/braccis

Para actualizar el sitio: guardás los cambios, y desde GitHub Desktop
hacés `Commit` y después `Push`. En un minuto se ve en línea.

> ### ⚠️ El sitio está oculto para Google, a propósito
>
> Las tres páginas tienen `<meta name="robots" content="noindex, nofollow">`
> porque esta dirección es una **muestra temporal**: si se da de baja, un
> link ya indexado seguiría apareciendo en las búsquedas durante semanas.
>
> **Cuando esta pase a ser la dirección definitiva, hay que borrar esa
> línea de `index.html`, `catalogo.html` y `contacto.html`.** Si no, el
> sitio no aparece nunca en Google.

### Cómo darlo de baja

| Qué querés | Dónde | Resultado |
|---|---|---|
| Que deje de verse el sitio | Settings → Pages → Source: `None` | El link muere, el código queda |
| Que no se vea el código | Settings → General → Change visibility | El link **también** muere (Pages gratis necesita repo público) |
| Borrar todo | Settings → Danger Zone → Delete this repository | Desaparece |

Lo que **no** se puede deshacer: si alguien ya clonó o descargó el
repositorio, esa copia queda. Y todo lo que estuvo en un commit sigue en
el historial aunque después se borre el archivo — por eso nunca hay que
subir contraseñas ni claves, ni siquiera "un ratito".

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
│   ├── hoja.js         Lee el Google Sheets y el video (no hace falta tocarlo)
│   ├── carrito.js      Carrito y pedido por WhatsApp (no hace falta tocarlo)
│   ├── contacto.js     Formulario (no hace falta tocarlo)
│   └── main.js         Menú, animaciones (no hace falta tocarlo)
├── img/
│   ├── prendas/        Fotos de las prendas (salieron de los PDF)
│   └── colores/        Muestras de color recortadas de los PDF
├── video/              Video de portada (ver LEEME.txt)
├── docs/               Catálogo PDF para descargar
├── catalogos/          Los PDF originales (ver nota al publicar)
└── herramientas/
    ├── generar_catalogo.py   Lee los PDF y regenera el catálogo
    ├── armar_plantilla.js    Arma la plantilla del Google Sheets
    └── armar_pdf.py          Arma el catálogo PDF liviano
```

**Con el Google Sheets armado, el día a día se hace desde ahí.** En el
código solo se toca `js/config.js` si cambian los datos de contacto.

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

## 1 bis. Administrar el sitio desde Google Sheets

Precios, nombres, fotos, prendas ocultas y el video de portada se manejan
desde un Google Sheets. **No hace falta tocar código.**

### Armarlo por primera vez (una sola vez, 10 minutos)

1. Entrá a [sheets.google.com](https://sheets.google.com) con la cuenta de
   la empresa → **Hoja de cálculo en blanco**. Arriba a la izquierda,
   ponele de nombre **Braccis – Catálogo**.
2. **Archivo → Importar → Subir** → elegí el archivo
   `herramientas/plantilla-productos.csv` (ya trae las 53 prendas cargadas).
   En la ventana que aparece elegí **"Reemplazar hoja actual"** → **Importar datos**.
3. Abajo, en la pestaña de la hoja, clic derecho → **Cambiar nombre** →
   escribí **Productos** (exacto, con mayúscula).
4. Abajo a la izquierda, el **+** para agregar otra pestaña. Nombrala
   **Ajustes** y escribí:

   | | A | B |
   |---|---|---|
   | 1 | clave | valor |
   | 2 | video_portada | portada.mp4 |

   (Si todavía no hay video, dejá B2 vacío.)
5. **Archivo → Compartir → Publicar en la Web**.
   - En el primer desplegable elegí **Productos**.
   - En el segundo, **Valores separados por comas (.csv)**.
   - Clic en **Publicar** → **Aceptar**. Copiá el link que aparece.
   - Abajo, en "Contenido publicado y configuración", dejá tildado
     **"Volver a publicar automáticamente cuando se hagan cambios"**.
6. Repetí el paso 5 eligiendo **Ajustes** en el primer desplegable.
   Copiá ese segundo link.
7. Pegá los dos links en `js/config.js`, en `sheetProductos` y
   `sheetAjustes`, y subí el cambio (GitHub Desktop → Commit → Push).

### Uso de todos los días

| Columna | Qué poner | Ejemplo |
|---|---|---|
| **id (no tocar)** | Nunca se cambia. Es cómo el sitio reconoce cada prenda | `somos` |
| **codigo** | El código del catálogo | `27V2205` |
| **nombre** | Como se ve en la web | `Remera Somos` |
| **categoria** | Remeras, Camisas, Blusas, Tejidos o Jeans | `Remeras` |
| **precio** | Solo el número. Acepta con o sin puntos | `18500` o `18.500` |
| **foto** | El nombre del archivo en `img/prendas/` | `somos.jpg` |
| **visible** | `si` se muestra, `no` se oculta (sin borrarla) | `no` |
| **talles** | Separados por coma | `S, M, L, XL` |
| **descripcion** | Un renglón | `Remera de algodón...` |

- **Celda vacía = queda lo que ya estaba.** Si no ponés precio, dice
  "Consultar precio".
- **Prenda nueva**: agregá una fila con un `id` nuevo (sin espacios ni
  acentos, por ejemplo `remera-luna`), y completá nombre, categoria, precio
  y foto. La foto se sube a `img/prendas/` con GitHub Desktop.
- **Los cambios tardan unos 5 minutos** en verse en la web: es la demora
  de Google al volver a publicar. Si no aparecen, esperá y recargá.
- ⚠️ **Todo lo que está en ese Sheets es público** (cualquiera con el link
  lo puede ver). No pongas costos, datos de proveedores ni nada privado.
- ⚠️ **No cambies los títulos de las columnas** ni los nombres de las
  pestañas. Si el sitio no los encuentra, muestra los datos viejos.

Si el Sheets se rompe o Google no responde, **el sitio sigue funcionando**
con los datos de `js/productos.js`, sin precios.

La plantilla se puede regenerar con `node herramientas/armar_plantilla.js`.

---

## 1 ter. Carrito, pedido por WhatsApp y catálogo PDF

- **Carrito**: en la ficha de cada prenda se elige talle (y color si tiene)
  y se agrega. El carrito queda guardado en el navegador del cliente.
- **Finalizar pedido**: pide el teléfono obligatorio y abre WhatsApp con
  el mensaje listo, dirigido al número de `js/config.js`:
  > Hola, mi teléfono es 11 5555-1234. Pedido: 1x Remera Somos · Talle M ·
  > Negro ($ 18.500), 1x Jeans Recto Kady · Talle 28 ($ 32.000). Total: $ 50.500
- **No cobra**: el pago se arregla por WhatsApp.
- **Video de portada**: ver `video/LEEME.txt`.
- **Catálogo PDF**: `docs/catalogo-braccis-pv2027.pdf`, botón en el menú
  y en la página de catálogo. Con una colección nueva se regenera con
  `python herramientas/armar_pdf.py`.

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

Hay dos caminos y los dos son gratis. **Los dos funcionan**: la diferencia
está en la seguridad y en cómo se actualiza.

### Opción A — Netlify Drop (la más segura)

1. Entrá a [app.netlify.com/drop](https://app.netlify.com/drop).
2. Arrastrá la carpeta `Braccis` entera a la ventana.
3. Listo, queda online con una URL tipo `braccis.netlify.app`.

Para actualizar, volvés a arrastrar la carpeta.

**Es la opción recomendada** porque Netlify lee el archivo `_headers`,
que activa todas las protecciones (ver la sección de Seguridad).

### Opción B — GitHub Pages

El proyecto ya está preparado como repositorio de git, listo para subir.
Desde **GitHub Desktop**:

1. `Archivo` → `Add Local Repository` → elegí `Documents\Braccis`
2. `Publish repository`
3. En github.com, entrá al repositorio → `Settings` → `Pages`
4. En *Source* elegí `Deploy from a branch`, rama `main`, carpeta `/ (root)` → `Save`
5. En un minuto queda en `https://TU-USUARIO.github.io/braccis/`

Para actualizar: guardás los cambios, `Commit` y `Push` desde GitHub Desktop.

**Dos cosas a tener en cuenta:**

- **El repositorio tiene que ser público.** GitHub Pages gratis no funciona
  con repositorios privados. El código y las fotos quedan a la vista de
  cualquiera (las fotos se publican igual en el sitio, así que no cambia
  mucho, pero conviene saberlo).
- **GitHub Pages ignora `_headers`.** Por eso las reglas de seguridad
  también están escritas dentro de cada HTML. Se pierden dos: la que
  impide meter el sitio dentro de un iframe y la que fuerza HTTPS, porque
  esas solo funcionan como cabecera del servidor.

### Dominio propio

Con cualquiera de las dos opciones se puede usar `braccis.com.ar`.
Se compra en [NIC Argentina](https://nic.ar) y se configura desde el panel
de Netlify o desde `Settings → Pages → Custom domain` en GitHub.

> **Si publicás arrastrando la carpeta, vaciá antes `catalogos/`.** Los
> cuatro PDF pesan 140 MB y el sitio entero pesa 6. Con git no hace falta:
> el `.gitignore` ya los deja afuera.

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
ni usuarios, ni contraseñas, ni pagos. Eso elimina de entrada la mayoría
de los ataques típicos: no hay nada que robar ni dónde entrar.

**Lo único que se guarda es el carrito**, en el navegador de cada persona
(`localStorage`): qué prendas, qué talle, qué color y cuántas. Nunca sale
de su compu o celular. **El teléfono que escribe para finalizar el pedido
no se guarda**: se usa para armar el mensaje de WhatsApp y nada más.
No hay cookies ni analítica.

Lo que sí se cubrió:

| Riesgo | Cómo está resuelto |
|---|---|
| Inyección de código por los datos | Todo lo que sale de `productos.js` y del Google Sheets se escapa antes de mostrarse (`esc()` en `catalogo.js`) |
| Alguien edita el Google Sheets con mala intención | Las fotos y el video solo aceptan un nombre de archivo simple (nada de carpetas ni links raros); los precios solo aceptan números; los textos se muestran como texto, nunca como código |
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
