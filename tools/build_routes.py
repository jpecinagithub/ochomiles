"""Genera datos-rutas.js: vías normales aproximadas, campamentos y efemérides.

window.OCHO_ROUTES = { "<peak-id>": {
    "line": "<enc_lines con la polilínea BC→cima>",
    "camps": [{"n":..,"lat":..,"lon":..,"a":..}, ...],
    "events": [{"y":1996,"t":..}, ...] } }

Vías y campamentos APROXIMADOS (ver nota en la ficha: "Las vías son orientativas").
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from enc import enc_lines
from makalu_routes import MAKALU, WPS_NORMAL

ROOT = os.path.join(os.path.dirname(__file__), "..")

def C(es, lat, lon, a):
    return {"n": es, "lat": lat, "lon": lon, "a": a}

def E(y, es):
    return {"y": y, "t": es}

# waypoints: (nombre, lat, lon, alt)
ROUTES = {
"everest": {
  "via": "Collado Sur",
  "wps": [
    ("Campo base", 28.0026, 86.8528, 5364),
    ("Campo 1", 27.9950, 86.8830, 6065),
    ("Campo 2", 27.9870, 86.9000, 6400),
    ("Campo 3", 27.9790, 86.9130, 7162),
    ("Collado Sur", 27.9758, 86.9263, 7906),
    ("Cima", 27.9881, 86.9250, 8848.86),
  ],
  "events": [
    E(1996, "Una tormenta atrapa a varias expediciones cerca de la cima: 8 muertos en 24 horas."),
    E(2015, "El terremoto de Nepal provoca una avalancha sobre el campo base: 19 muertos."),
  ]},
"lhotse": {
  "via": "Corredor del Lhotse",
  "wps": [
    ("Campo base", 28.0026, 86.8528, 5364),
    ("Campo 2", 27.9870, 86.9000, 6400),
    ("Campo 3", 27.9790, 86.9130, 7162),
    ("Campo 4", 27.9680, 86.9260, 7800),
    ("Cima", 27.9617, 86.9330, 8516),
  ],
  "events": [
    E(1986, "Reinhold Messner la convierte en su 14.º ochomil y completa la colección."),
    E(0, "Su nombre significa «Pico Sur» en tibetano y comparte vía con el Everest hasta el campo 3."),
  ]},
"makalu": None,  # se genera desde tools/makalu_routes.py (vías del artículo Animal de Ruta)
"chooyu": {
  "via": "Cara noroeste",
  "wps": [
    ("Campo base", 28.0244, 86.6950, 5700),
    ("Campo 1", 28.0600, 86.6800, 6400),
    ("Campo 2", 28.0750, 86.6700, 7100),
    ("Campo 3", 28.0880, 86.6630, 7500),
    ("Cima", 28.0941, 86.6608, 8188),
  ],
  "events": [
    E(0, "Su nombre significa «Diosa Turquesa» en tibetano."),
    E(0, "Considerado el ochomil más asequible, sin grandes dificultades técnicas."),
  ]},
"kangchenjunga": {
  "via": "Cara suroeste",
  "wps": [
    ("Campo base (Pangpema)", 27.7242, 88.1095, 5140),
    ("Campo 1", 27.7150, 88.1250, 6000),
    ("Campo 2", 27.7100, 88.1350, 6400),
    ("Campo 3", 27.7050, 88.1420, 7300),
    ("Cima", 27.7025, 88.1475, 8586),
  ],
  "events": [
    E(1955, "Brown y Band se detienen a pocos metros de la cima por respeto a las creencias locales."),
    E(0, "Tercera montaña más alta del mundo, en la frontera entre Nepal e India."),
  ]},
"k2": {
  "via": "Espolón de los Abruzos",
  "wps": [
    ("Campo base", 35.8373, 76.5186, 4965),
    ("Campo base avanzado", 35.8450, 76.5300, 5350),
    ("Campo 1", 35.8550, 76.5200, 6065),
    ("Campo 2", 35.8650, 76.5180, 6650),
    ("Campo 3", 35.8720, 76.5160, 7350),
    ("Hombro", 35.8780, 76.5150, 7900),
    ("Cima", 35.8808, 76.5139, 8611),
  ],
  "events": [
    E(2008, "Una avalancha de seracs en el Cuello de Botella causa 11 muertos, el peor accidente del K2."),
    E(2021, "Primera ascensión invernal: equipo nepalí liderado por Nimsdai Purja."),
  ]},
"gasherbrum1": {
  "via": "Corredor de los Americanos",
  "wps": [
    ("Campo base", 35.7225, 76.6200, 5200),
    ("Campo 1", 35.7230, 76.6400, 5900),
    ("Campo 2", 35.7240, 76.6600, 6400),
    ("Campo 3", 35.7242, 76.6800, 7000),
    ("Cima", 35.7244, 76.6965, 8080),
  ],
  "events": [
    E(2012, "Primera ascensión invernal: Adam Bielecki y Janusz Gołąb (Polonia)."),
    E(0, "Conocido como «Pico Oculto» por lo remoto de su ubicación."),
  ]},
"gasherbrum2": {
  "via": "Arista suroeste",
  "wps": [
    ("Campo base", 35.7400, 76.6000, 5200),
    ("Campo 1", 35.7450, 76.6150, 5900),
    ("Campo 2", 35.7500, 76.6300, 6400),
    ("Campo 3", 35.7540, 76.6450, 7000),
    ("Cima", 35.7575, 76.6528, 8035),
  ],
  "events": [
    E(2011, "Primera ascensión invernal: Simone Moro, Denis Urubko y Cory Richards."),
    E(0, "Su glaciar de acceso, el Baltoro, es uno de los mayores fuera de las regiones polares."),
  ]},
"broadpeak": {
  "via": "Arista oeste",
  "wps": [
    ("Campo base", 35.7900, 76.5500, 4900),
    ("Campo 1", 35.7950, 76.5580, 5700),
    ("Campo 2", 35.8000, 76.5620, 6300),
    ("Campo 3", 35.8060, 76.5640, 7000),
    ("Cima", 35.8106, 76.5653, 8047),
  ],
  "events": [
    E(2013, "Primera ascensión invernal (equipo polaco); Maciej Berbeka muere en el descenso."),
    E(0, "Su nombre describe la cima: una arista de más de un kilómetro de longitud."),
  ]},
"nangaparbat": {
  "via": "Kinshofer (Diamir)",
  "wps": [
    ("Campo base (Diamir)", 35.3500, 74.6200, 4100),
    ("Campo 1", 35.3300, 74.6150, 4850),
    ("Campo 2", 35.3100, 74.6100, 6100),
    ("Campo 3", 35.2900, 74.6050, 6800),
    ("Campo 4", 35.2700, 74.6000, 7300),
    ("Cima", 35.2372, 74.5892, 8126),
  ],
  "events": [
    E(1970, "Los hermanos Messner abren la vertiente Rupal; Günther muere en el descenso."),
    E(2016, "Primera ascensión invernal: Moro, Txikon y Sadpara."),
  ]},
"dhaulagiri": {
  "via": "Collado nordeste",
  "wps": [
    ("Campo base", 28.7333, 83.5167, 4700),
    ("Campo 1", 28.7250, 83.5100, 5700),
    ("Campo 2", 28.7150, 83.5050, 6400),
    ("Campo 3", 28.7050, 83.5000, 7300),
    ("Cima", 28.6967, 83.4931, 8167),
  ],
  "events": [
    E(1808, "Se la cree la montaña más alta del mundo; lo será hasta 1838."),
    E(0, "Dhaulagiri significa «Montaña Blanca» en sánscrito."),
  ]},
"annapurna": {
  "via": "Cara norte",
  "wps": [
    ("Campo base norte", 28.6000, 83.9300, 4300),
    ("Campo 1", 28.5980, 83.9350, 5100),
    ("Campo 2", 28.5960, 83.9370, 6000),
    ("Campo 3", 28.5958, 83.9372, 6900),
    ("Cima", 28.5956, 83.9372, 8091),
  ],
  "events": [
    E(1950, "Primer ochomil de la historia (ya en la ficha); Herzog y Lachenal sufren graves congelaciones."),
    E(0, "La montaña con mayor tasa de mortalidad entre los ochomiles."),
  ]},
"manaslu": {
  "via": "Cara noreste",
  "wps": [
    ("Campo base", 28.5750, 84.5760, 4800),
    ("Campo 1", 28.5700, 84.5700, 5700),
    ("Campo 2", 28.5650, 84.5650, 6400),
    ("Campo 3", 28.5580, 84.5620, 7000),
    ("Campo 4", 28.5530, 84.5600, 7400),
    ("Cima", 28.5497, 84.5597, 8163),
  ],
  "events": [
    E(2012, "Una avalancha entre los campos 3 y 4 causa 11 muertos."),
    E(0, "Manaslu significa «Montaña del Espíritu» en sánscrito."),
  ]},
"shishapangma": {
  "via": "Cara norte",
  "wps": [
    ("Campo base", 28.4000, 85.8000, 5000),
    ("Campo base avanzado", 28.3900, 85.7950, 5600),
    ("Campo 1", 28.3800, 85.7900, 6400),
    ("Campo 2", 28.3680, 85.7850, 7000),
    ("Campo 3", 28.3600, 85.7820, 7400),
    ("Cima", 28.3526, 85.7792, 8027),
  ],
  "events": [
    E(1964, "Último ochomil en ser ascendido (ya en la ficha)."),
    E(0, "Íntegramente en el Tíbet: el único ochomil solo en China."),
  ]},
}

def build_line(wps, subdiv=6):
    pts = []
    for a, b in zip(wps, wps[1:]):
        for k in range(subdiv):
            f = k / subdiv
            pts.append((a[2] + (b[2] - a[2]) * f, a[1] + (b[1] - a[1]) * f))
    pts.append((wps[-1][2], wps[-1][1]))
    return pts

def build_makalu():
    """Entrada del Makalu: vía normal (1955), campamentos y efemérides."""
    return {
        "via": MAKALU["via"],
        "line": enc_lines([build_line([(None, la, lo, 0) for la, lo in WPS_NORMAL], subdiv=4)]),
        "camps": MAKALU["camps"],
        "events": MAKALU["events"],
    }

def main():
    out = {}
    for pid, r in ROUTES.items():
        if pid == "makalu":
            out[pid] = build_makalu()
            continue
        wps = r["wps"]
        out[pid] = {
            "via": r["via"],
            "line": enc_lines([build_line(wps)]),
            "camps": [C(*w) for w in wps],
            "events": [e for e in r["events"] if e["y"] > 0] +
                      [{"y": None, "t": e["t"]} for e in r["events"] if e["y"] == 0],
        }
    # normaliza eventos sin año
    for pid in out:
        for e in out[pid]["events"]:
            if e["y"] is None:
                del e["y"]
    path = os.path.join(ROOT, "datos-rutas.js")
    with open(path, "w") as f:
        f.write("window.OCHO_ROUTES=" + json.dumps(out, ensure_ascii=False) + ";")
    print("rutas:", len(out), "| tamaño:", os.path.getsize(path), "bytes")
    # verificación
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from enc import dec_lines
    for pid, r in out.items():
        pts = dec_lines(r["line"])[0]
        assert len(pts) > 10, pid
    print("verificación OK")

if __name__ == "__main__":
    main()
