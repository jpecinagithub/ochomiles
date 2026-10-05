# OCHOMILES — Las 14 cimas de más de 8000 m

Mapa navegable en relieve de las 14 montañas que superan los 8000 metros de
altitud (Himalaya y Karakórum). Cada cima tiene una ficha con foto, altitud,
prominencia, cordillera, país, primera ascensión y vía normal, además de su
campo base y un modelo 3D que se puede girar.

Inspirado en [tresmiles-pirineo](https://github.com/rforcano/tresmiles-pirineo).

## Ver el mapa

Despliega este repositorio en Vercel (o cualquier hosting estático).

## Archivos

- `index.html`: la aplicación (mapa en relieve, índice de cimas, fichas y visor 3D).
- `datos-base.js`: relieve, cobertura del suelo, curvas de nivel, ríos, lagos,
  fronteras, pueblos, cimas, zonas y fotos.
- `datos-picos.js`: recortes de relieve de alta resolución alrededor de cada
  cima (se cargan después de mostrar el mapa; alimentan el zoom profundo y el
  visor 3D).
- `SCHEMA.md`: formato exacto de los datos (para desarrolladores).
- `sample/`: datos sintéticos de muestra para desarrollar sin el DEM real.
- `tools/`: `enc.py` (codificadores), `make_sample.py`, `fetch_photos.py`.

Es una web estática: sin build. Las tipografías se cargan desde Google Fonts,
el visor 3D usa three.js desde jsDelivr y Vercel Analytics se activa solo en
despliegues de Vercel.

## Datos y licencias

- Relieve: AWS Terrain Tiles (Terrarium; datos SRTM de la NASA).
- Ríos, lagos y fronteras: Natural Earth (dominio público).
- Pueblos: © colaboradores de OpenStreetMap (ODbL).
- Fotos: Wikimedia Commons. El autor y la licencia de cada foto aparecen en su ficha.
- Lista de cimas y altitudes: Wikipedia.
- Visor 3D: three.js (licencia MIT). Tipografías Barlow, Barlow Condensed y
  Cormorant Garamond (SIL Open Font License).

Las vías de acceso son orientativas. Antes de salir, consulta una guía
actualizada y el estado de la montaña.
