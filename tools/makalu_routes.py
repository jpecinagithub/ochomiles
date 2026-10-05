"""Vía normal del Makalu a partir del artículo
«Las rutas de ascenso del Makalu» (Animal de Ruta, 24/11/2014).

Waypoints verificados contra el DEM (parche 256x256): los perfiles de
ascenso son monótonos y siguen glaciares, collados, caras y aristas reales.
Las altitudes de los campamentos son las estándar de la vía normal.
"""

def C(es, lat, lon, a):
    return {"n": es, "lat": lat, "lon": lon, "a": a}

def E(y, es):
    return {"y": y, "t": es}



# (lat, lon) de base a cima
WPS_NORMAL = [
    (27.8620, 87.1350), (27.8675, 87.1270), (27.8715, 87.1215),
    (27.8745, 87.1200),  # ABC 5700
    (27.8710, 87.1120), (27.8690, 87.1040), (27.8695, 87.0960),
    (27.8720, 87.0880), (27.8760, 87.0810), (27.8800, 87.0760),
    (27.8840, 87.0730), (27.8880, 87.0720), (27.8920, 87.0735),
    (27.8945, 87.0760), (27.8960, 87.0778),
    (27.8972, 87.0790),  # Makalu La 7400
    (27.8971, 87.0817), (27.8970, 87.0830), (27.8960, 87.0850),
    (27.8950, 87.0865), (27.8940, 87.0875), (27.8920, 87.0887),
    (27.8892, 87.0889),  # cima 8463
]

MAKALU = {
    "via": "Cara norte y arista noroeste (1955)",
    "camps": [
        C("Campo base", 27.8620, 87.1350, 4870),
        C("Campo base avanzado", 27.8745, 87.1200, 5700),
        C("Campo 1", 27.8710, 87.1120, 6400),
        C("Campo 2", 27.8840, 87.0730, 6600),
        C("Campo 3 · Collado Makalu", 27.8972, 87.0790, 7400),
        C("Campo 4", 27.8971, 87.0817, 7800),
        C("Cima", 27.8892, 87.0889, 8463),
    ],
    "events": [
        E(1955, "Primera ascensión: J. Couzy y L. Terray (expedición francesa) por la cara norte y la arista noroeste."),
        E(1971, "B. Mellet e Y. Seigneur abren el pilar oeste, la vía más difícil de la montaña."),
        E(2009, "Primera ascensión invernal: Simone Moro y Denis Urubko."),
    ],
    # (las 6 rutas del artículo se retiraron: el Makalu queda con vía única)
}
