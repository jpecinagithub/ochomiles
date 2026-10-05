"""Descarga teselas de ESRI World Imagery y compone la textura satelital
de un pico para el visor 3D: tex/<peak-id>.jpg

La imagen cubre EXACTAMENTE los bounds del parche DEM (lon0,lat0,lon1,lat1),
así las UV 0-1 del PlaneGeometry encajan 1:1.

Atribución requerida: "Source: Esri, Maxar, Earthstar Geographics".
"""
import io
import json
import math
import os
import sys
import time
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..")
TEXDIR = os.path.join(ROOT, "tex")
Z = 13
TILE = 256
UA = {"User-Agent": "OCHOMILES/1.0 (educational relief map; contact: github.com/jpecinagithub/ochomiles)"}
URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


def lonlat_to_tile(lon, lat, z):
    n = 2 ** z
    xt = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    yt = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return xt, yt


def tile_to_lonlat(xt, yt, z):
    n = 2 ** z
    lon = xt / n * 360.0 - 180.0
    lat_r = math.atan(math.sinh(math.pi * (1.0 - 2.0 * yt / n)))
    return lon, math.degrees(lat_r)


def fetch_tile(z, x, y, retries=4):
    url = URL.format(z=z, y=y, x=x)
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) < 1000:
                raise ValueError("respuesta vacía")
            return data
        except Exception as e:
            if a == retries - 1:
                raise
            time.sleep(1.5 * (a + 1))
    raise RuntimeError("sin reintentos")


def build(pid):
    from PIL import Image

    s = open(os.path.join(ROOT, "datos-picos.js")).read()
    i = s.find('"%s"' % pid)
    if i < 0:
        raise SystemExit("pico no encontrado: " + pid)
    start = s.find("{", i)
    depth = 0
    for j in range(start, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                patch = json.loads(s[start:j + 1])
                break
    lon0, lat0, lon1, lat1 = patch["lon0"], patch["lat0"], patch["lon1"], patch["lat1"]
    print("%s: bounds %.4f,%.4f -> %.4f,%.4f" % (pid, lon0, lat0, lon1, lat1))

    # teselas que cubren los bounds (con 1 de margen)
    fx0, fy0 = lonlat_to_tile(lon0, lat1, Z)  # NO
    fx1, fy1 = lonlat_to_tile(lon1, lat0, Z)  # SE
    x0, x1 = int(math.floor(fx0)) - 1, int(math.floor(fx1)) + 1
    y0, y1 = int(math.floor(fy0)) - 1, int(math.floor(fy1)) + 1
    nx, ny = x1 - x0 + 1, y1 - y0 + 1
    print("teselas: x %d..%d, y %d..%d (%d en total)" % (x0, x1, y0, y1, nx * ny))

    canvas = Image.new("RGB", (nx * TILE, ny * TILE))
    n = 0
    for ty in range(y0, y1 + 1):
        for tx in range(x0, x1 + 1):
            data = fetch_tile(Z, tx, ty)
            im = Image.open(io.BytesIO(data)).convert("RGB")
            canvas.paste(im, ((tx - x0) * TILE, (ty - y0) * TILE))
            n += 1
            if n % 10 == 0:
                print("  %d/%d teselas" % (n, nx * ny))
            time.sleep(0.15)

    # recorte exacto a los bounds del parche
    # esquina NO del canvas:
    clon, clat = tile_to_lonlat(x0, y0, Z)
    # píxeles por grado en este canvas:
    # (el canvas cubre de clon..clon+nx*tile_deg lon)
    lon_per_px = 360.0 / (2 ** Z) / TILE
    # lat no es lineal en webmercator: usar la función inversa por píxel
    def px_of_lon(lon):
        return (lonlat_to_tile(lon, 0, Z)[0] - x0) * TILE

    def py_of_lat(lat):
        return (lonlat_to_tile(0, lat, Z)[1] - y0) * TILE

    px0, px1 = px_of_lon(lon0), px_of_lon(lon1)
    py0, py1 = py_of_lat(lat1), py_of_lat(lat0)  # lat1=norte=arriba
    img = canvas.crop((int(round(px0)), int(round(py0)), int(round(px1)), int(round(py1))))
    print("recorte: %dx%d" % img.size)

    os.makedirs(TEXDIR, exist_ok=True)
    out = os.path.join(TEXDIR, pid + ".jpg")
    # limitar a 1600 px de ancho para un peso razonable (~700 KB)
    if img.size[0] > 1600:
        nh = int(img.size[1] * 1600 / img.size[0])
        img = img.resize((1600, nh), Image.LANCZOS)
    img.save(out, "JPEG", quality=78, optimize=True)
    print("guardado: %s (%d KB, %dx%d)" % (out, os.path.getsize(out) // 1024, img.size[0], img.size[1]))


if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else "makalu"
    build(pid)
