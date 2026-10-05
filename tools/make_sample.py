"""Genera datos de MUESTRA (sintéticos) para desarrollar la app sin esperar al DEM real.
Salida: sample/datos-base.js y sample/datos-picos.js en el raíz del proyecto."""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from enc import enc_ints, enc_u8, enc_lines

ROOT = os.path.join(os.path.dirname(__file__), "..")
SAMPLE = os.path.join(ROOT, "sample")
os.makedirs(SAMPLE, exist_ok=True)

# Región sintética: zona del Everest
LON0, LAT0, LON1, LAT1 = 85.5, 27.0, 88.5, 29.0
W, H = 150, 100

def synth_dem():
    dem = []
    for j in range(H):
        lat = LAT1 - (j + 0.5) * (LAT1 - LAT0) / H
        for i in range(W):
            lon = LON0 + (i + 0.5) * (LON1 - LON0) / W
            # cordillera sintética NO-SE con picos gaussianos
            r = (0.9 * math.exp(-(((lon - 86.9) ** 2) / 0.35 + ((lat - 28.0) ** 2) / 0.18))
                 + 0.55 * math.exp(-(((lon - 87.1) ** 2) / 0.2 + ((lat - 27.9) ** 2) / 0.12))
                 + 0.25 * math.sin(lon * 9.0) * math.cos(lat * 7.0))
            h = int(2500 + 6500 * max(0.0, r) + 300 * math.sin(i * 0.4) * math.cos(j * 0.3))
            dem.append(h)
    return dem

def synth_lc(dem):
    cls = []
    for h in dem:
        if h > 5600: c = 1
        elif h > 4600: c = 2
        elif h > 3600: c = 3
        elif h > 2200: c = 4
        else: c = 5
        cls.append(c)
    return bytes(cls)

def synth_contours():
    # anillos sintéticos alrededor de los picos
    out = []
    for e in (3000, 4000, 5000, 6000, 7000, 8000):
        lines = []
        for cx, cy, rx, ry in ((86.925, 27.988, 0.55, 0.42),
                               (87.089, 27.890, 0.34, 0.26)):
            pts = [(cx + rx * math.cos(t), cy + ry * math.sin(t))
                   for t in [k * math.pi / 36 for k in range(37)]]
            lines.append(pts)
        out.append({"e": e, "d": enc_lines(lines)})
    return out

PEAKS = [
    dict(id="everest", n={"es": "Everest", "en": "Mount Everest"},
         aka=["Chomolungma", "Sagarmatha"], a=8848.86, prom=8848.86,
         lat=27.9881, lon=86.9250, zone="mahalangur",
         ctr={"es": "Nepal / China (Tíbet)", "en": "Nepal / China (Tibet)"},
         rng={"es": "Mahalangur Himal", "en": "Mahalangur Himal"},
         fa={"y": 1953, "by": {"es": "E. Hillary y T. Norgay", "en": "E. Hillary & T. Norgay"}},
         route={"es": "Vía normal del Collado Sur (Nepal).",
                "en": "Normal route via the South Col (Nepal)."},
         photo=None,
         bc={"n": {"es": "Campo base sur", "en": "South Base Camp"},
             "lat": 28.0026, "lon": 86.8528}),
    dict(id="lhotse", n={"es": "Lhotse", "en": "Lhotse"},
         aka=[], a=8516, prom=610,
         lat=27.9617, lon=86.9330, zone="mahalangur",
         ctr={"es": "Nepal / China (Tíbet)", "en": "Nepal / China (Tibet)"},
         rng={"es": "Mahalangur Himal", "en": "Mahalangur Himal"},
         fa={"y": 1956, "by": {"es": "E. Reiss y F. Luchsinger", "en": "E. Reiss & F. Luchsinger"}},
         route={"es": "Corredor del Lhotse desde el Collado Sur.",
                "en": "Lhotse Couloir from the South Col."},
         photo=None,
         bc={"n": {"es": "Campo base sur", "en": "South Base Camp"},
             "lat": 28.0026, "lon": 86.8528}),
    dict(id="makalu", n={"es": "Makalu", "en": "Makalu"},
         aka=[], a=8463, prom=2378,
         lat=27.8897, lon=87.0889, zone="mahalangur",
         ctr={"es": "Nepal / China (Tíbet)", "en": "Nepal / China (Tibet)"},
         rng={"es": "Mahalangur Himal", "en": "Mahalangur Himal"},
         fa={"y": 1955, "by": {"es": "L. Couzy y L. Terray", "en": "L. Couzy & L. Terray"}},
         route={"es": "Arista noroeste.", "en": "Northwest ridge."},
         photo=None,
         bc={"n": {"es": "Campo base del Makalu", "en": "Makalu Base Camp"},
             "lat": 27.8717, "lon": 87.1150}),
]

def main():
    dem = synth_dem()
    base = {
        "meta": {"v": 1, "built": "sample", "lang": ["es", "en"],
                 "sources": ["Datos sintéticos de muestra"]},
        "grid": {"lon0": LON0, "lat0": LAT0, "lon1": LON1, "lat1": LAT1, "w": W, "h": H},
        "dem": enc_ints(dem),
        "lc": enc_u8(synth_lc(dem)),
        "contours": synth_contours(),
        "rivers": [{"n": "Dudh Koshi", "d": enc_lines(
            [[(86.6 + t * 0.35, 27.6 + t * 0.5 + 0.08 * math.sin(t * 9)) for t in
              [k / 20 for k in range(21)]]])}],
        "lakes": [],
        "borders": [{"d": enc_lines(
            [[(LON0 + t * (LON1 - LON0), 28.35 + 0.12 * math.sin(t * 12)) for t in
              [k / 40 for k in range(41)]]])}],
        "towns": [
            {"n": "Namche Bazaar", "lat": 27.8069, "lon": 86.7140, "k": 1},
            {"n": "Lukla", "lat": 27.6869, "lon": 86.7297, "k": 1},
        ],
        "peaks": PEAKS,
        "zones": [{"id": "mahalangur",
                   "n": {"es": "Mahalangur Himal", "en": "Mahalangur Himal"}}],
        "photos": [],
    }
    with open(os.path.join(SAMPLE, "datos-base.js"), "w") as f:
        f.write("window.OCHO=" + json.dumps(base, ensure_ascii=False) + ";")

    patch = {}
    for p in PEAKS:
        w = h = 48
        lon0, lon1 = p["lon"] - 0.175, p["lon"] + 0.175
        lat0, lat1 = p["lat"] - 0.175, p["lat"] + 0.175
        demp = []
        for j in range(h):
            la = lat1 - (j + 0.5) * (lat1 - lat0) / h
            for i in range(w):
                lo = lon0 + (i + 0.5) * (lon1 - lon0) / w
                dd = ((lo - p["lon"]) ** 2 + (la - p["lat"]) ** 2)
                demp.append(int(p["a"] - 2600 * dd / 0.03 + 120 * math.sin(i * .5) * math.cos(j * .4)))
        patch[p["id"]] = {"lon0": lon0, "lat0": lat0, "lon1": lon1, "lat1": lat1,
                          "w": w, "h": h, "dem": enc_ints(demp)}
    with open(os.path.join(SAMPLE, "datos-picos.js"), "w") as f:
        f.write("window.OCHO_PATCH=" + json.dumps(patch) + ";")
    print("sample OK:", os.path.join(SAMPLE, "datos-base.js"))

if __name__ == "__main__":
    main()
