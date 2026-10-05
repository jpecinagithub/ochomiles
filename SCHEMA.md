# OCHOMILES — esquema de datos

Proyecto: mapa navegable en relieve de las 14 cimas de más de 8000 m
(Himalaya y Karakórum), al estilo de `tresmiles-pirineo`.
Web estática: `index.html` + `datos-base.js` + `datos-picos.js`.
Sin build. Despliegue en Vercel / GitHub Pages.

## Archivos

- `index.html` — la aplicación (mapa, índice de cimas, fichas, visor 3D).
  Lee `window.OCHO` (de `datos-base.js`) y `window.OCHO_PATCH` (de `datos-picos.js`).
  `datos-picos.js` se carga con `defer` después de pintar el mapa base.
- `datos-base.js` — `window.OCHO = {...}` relieve base, cobertura, curvas de nivel,
  vectores, cimas, fotos, zonas.
- `datos-picos.js` — `window.OCHO_PATCH = { "<peak-id>": {...}, ... }`
  recortes DEM de alta resolución alrededor de cada cima (para zoom y visor 3D).

## Codificación

Todo binario va en base64 estándar dentro de strings JS.

### `enc_ints(list[int])` — enteros con signo
1. Delta: `d[0]=a[0], d[i]=a[i]-a[i-1]`.
2. Zigzag 32 bit: `z = (d << 1) ^ (d >> 31)` (en Python: `(d<<1) ^ (d>>31)` con
   desplazamiento aritmético; equivalente a `(d*2) ^ -(d<0)`… usar fórmula
   `(d << 1) ^ (d >> 31)` con ints de Python funciona si se enmascara a 32 bits:
   `z = ((d << 1) ^ (d >> 31)) & 0xFFFFFFFF`).
3. LEB128 sin signo por valor, concatenados.
4. base64.

JS decode: base64 → bytes → LEB128 → zigzag inversa `d = (z>>>1) ^ -(z&1)` →
cumsum.

### `enc_u8(bytes)` — bytes tal cual en base64.

### `enc_lines(list[list[(lon,lat)]])` — polilíneas
- Unidades: microgrados enteros (`int(round(deg*1e6))`).
- Secuencia: por cada polilínea: `varint(npts)`,
  luego por cada punto: `varint(zigzag(dx)), varint(zigzag(dy))`
  con deltas respecto al punto anterior (el primero, delta respecto a (0,0)).
- Todo codificado como en `enc_ints` (una sola lista de ints → b64).
- JS: decodificar a ints, recorrer: `n=ints[k++]`, puntos acumulando dx,dy,
  dividir por 1e6.

## `window.OCHO`

```js
window.OCHO = {
  meta: { v: 1, built: "2026-10-05", lang: ["es","en"],
          sources: ["Copernicus DEM GLO-30 ...", "Natural Earth ...",
                    "OpenStreetMap contributors (ODbL)",
                    "Wikimedia Commons (ver ficha de cada foto)"] },
  grid: { lon0, lat0, lon1, lat1, w, h },
  // grid: celda (i,j), i=0..w-1 oeste→este, j=0..h-1 NORTE→sur.
  // lon(i) = lon0 + (i+0.5)*(lon1-lon0)/w ; lat(j) = lat1 - (j+0.5)*(lat1-lat0)/h
  dem: "<enc_ints de h*w altitudes en metros, row-major j*w+i>",
  lc:  "<enc_u8 de h*w clases 1..5>",
  // lc: 1 nieve/hielo, 2 roca, 3 prado alpino, 4 bosque, 5 valles bajos.
  //     (0 reservado para agua; no se usa en la versión procedural)
  contours: [ { e: 1000, d: "<enc_lines>" }, ... ],  // e en metros, orden ascendente
  rivers:  [ { n: "Karnali", d: "<enc_lines>" }, ... ],
  lakes:   [ { n: "...", d: "<enc_lines>" }, ... ],  // polígonos cerrados como líneas
  borders: [ { d: "<enc_lines>" } ],                  // fronteras internacionales
  towns:   [ { n: "Namche Bazaar", lat, lon, k: 1 }, ... ], // k: 1 pueblo, 2 ciudad
  peaks: [
    { id: "everest",
      n:   { es: "Everest", en: "Mount Everest" },
      aka: ["Chomolungma", "Sagarmatha"],
      a: 8848.86, prom: 8848.86,
      lat: 27.9881, lon: 86.9250,
      zone: "mahalangur",
      ctr: { es: "Nepal / China (Tíbet)", en: "Nepal / China (Tibet)" },
      rng: { es: "Mahalangur Himal", en: "Mahalangur Himal" },
      fa:  { y: 1953, by: { es: "E. Hillary y T. Norgay", en: "E. Hillary & T. Norgay" } },
      route: { es: "Vía del Collado Sur…", en: "South Col route…" },
      photo: 0,                       // índice en photos
      bc:  { n: { es: "Campo base sur", en: "South Base Camp" }, lat: 28.0026, lon: 86.8528 }
    }, ...
  ],
  zones: [ { id: "karakorum", n: { es: "Karakórum", en: "Karakoram" } }, ... ],
  photos: [ { u: "<url imagen>", t: "<url miniatura>",
              by: "Autor", lic: "CC BY-SA 4.0", src: "<url página del archivo>" } ]
}
```

- `peaks` ordenados por altitud descendente.
- `photo` puede ser `null` → la app muestra un monograma.
- Las URLs de fotos son de `upload.wikimedia.org` (hotlink permitido).

## `window.OCHO_PATCH`

```js
window.OCHO_PATCH = {
  "everest": { lon0, lat0, lon1, lat1, w, h, dem: "<enc_ints h*w metros>" },
  ...
}
```
Misma convención de celdas que `grid`. Recorte ~0.35°×0.35° centrado en la cima,
resolución objetivo ~70–150 m/píxel.

## Notas para la app

- El mapa dibuja el relieve desde `dem`+`lc` (sombreado NW + rampa hipsométrica).
- Las curvas de nivel son vectores (no hay que calcular marching squares en cliente).
- Los picos se proyectan con la fórmula de `grid` (proyección equirectangular).
- `datos-picos.js` puede no existir al inicio: la app debe funcionar solo con
  `datos-base.js` y mejorar el zoom / activar el visor 3D cuando llegue el otro.

## `window.OCHO_ROUTES` (datos-rutas.js, opcional)

```js
window.OCHO_ROUTES = {
  "everest": {
    "line": "<enc_lines: una polilínea del campo base a la cima>",
    "camps": [ {"n":{"es":"Campo 1","en":"Camp 1"},"lat":..,"lon":..,"a":6065}, ... ],
    "events": [ {"y":1996, "t":{"es":"…","en":"…"}}, {"t":{"es":"…","en":"…"}}, ... ]
  }, ...
}
```
Vías y campamentos **aproximados** (la ficha lo advierte). `y` es opcional.
