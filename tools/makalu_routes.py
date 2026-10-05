"""Rutas del Makalu enriquecidas a partir del artículo
«Las rutas de ascenso del Makalu» (Animal de Ruta, 24/11/2014).

Waypoints verificados contra el DEM (parche 256x256): los perfiles de
ascenso son monótonos y siguen glaciares, collados, caras y aristas reales.
Las altitudes de los campamentos son las estándar de la vía normal.
"""

def C(es, en, lat, lon, a):
    return {"n": {"es": es, "en": en}, "lat": lat, "lon": lon, "a": a}

def E(y, es, en):
    return {"y": y, "t": {"es": es, "en": en}}

def M(es, en, lat, lon, a):
    return {"n": {"es": es, "en": en}, "lat": lat, "lon": lon, "a": a}

def R(rid, name_es, name_en, year, color, wps, label, desc_es, desc_en, marks=None):
    return {"id": rid,
            "name": {"es": name_es, "en": name_en},
            "y": year, "color": color,
            "wps": wps, "label": {"lat": label[0], "lon": label[1]},
            "desc": {"es": desc_es, "en": desc_en},
            "marks": marks or []}

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
        C("Campo base", "Base camp", 27.8620, 87.1350, 4870),
        C("Campo base avanzado", "Advanced base camp", 27.8745, 87.1200, 5700),
        C("Campo 1", "Camp 1", 27.8710, 87.1120, 6400),
        C("Campo 2", "Camp 2", 27.8840, 87.0730, 6600),
        C("Campo 3 · Collado Makalu", "Camp 3 · Makalu La", 27.8972, 87.0790, 7400),
        C("Campo 4", "Camp 4", 27.8971, 87.0817, 7800),
        C("Cima", "Summit", 27.8892, 87.0889, 8463),
    ],
    "events": [
        E(1955,
          "Primera ascensión: J. Couzy y L. Terray (expedición francesa) por la cara norte y la arista noroeste.",
          "First ascent: J. Couzy & L. Terray (French expedition) via the north face and NW ridge."),
        E(1971,
          "B. Mellet e Y. Seigneur abren el pilar oeste, la vía más difícil de la montaña.",
          "B. Mellet & Y. Seigneur open the west pillar, the mountain's hardest route."),
        E(2009,
          "Primera ascensión invernal: Simone Moro y Denis Urubko.",
          "First winter ascent: Simone Moro & Denis Urubko."),
    ],
    "routes": [
        R("normal-1955", "Vía normal · 1955", "Normal route · 1955", 1955, "#e5484d",
          WPS_NORMAL, (27.8740, 87.0990),
          "La clásica: rodeo por el circo glaciar oeste, collado Makalu La (7400 m), "
          "travesía a la cara norte y corredor de los Franceses (8200 m).",
          "The classic: skirting the western glacial cirque, Makalu La (7,400 m), "
          "traverse to the north face and the French Couloir (8,200 m).",
          marks=[
              M("Corredor de los Franceses · 8200 m", "French Couloir · 8,200 m",
                27.8955, 87.0858, 8200),
          ]),
        R("arista-se-1970", "Arista sureste · 1970", "Southeast ridge · 1970", 1970, "#f59e0b",
          [(27.8560, 87.1180), (27.8605, 87.1145), (27.8645, 87.1115),
           (27.8685, 87.1085), (27.8725, 87.1055), (27.8765, 87.1020),
           (27.8805, 87.0980), (27.8845, 87.0935), (27.8870, 87.0905),
           (27.8892, 87.0889)],
          (27.8660, 87.1150),
          "Arista íntegra de 8 km con acceso por el glaciar sur, evitando 4 km de filo; "
          "el paso clave son «los gendarmes». Japoneses Y. Ozaki y A. Tanaka.",
          "The full 8 km ridge, reached via the south glacier to skip 4 km of crest; "
          "the crux is the 'gendarmes'. Japanese: Y. Ozaki & A. Tanaka.",
          marks=[M("Los gendarmes", "The gendarmes", 27.8785, 87.1035, 7550)]),
        R("pilar-oeste-1971", "Pilar oeste · 1971", "West pillar · 1971", 1971, "#3b82f6",
          [(27.8780, 87.0580), (27.8810, 87.0640), (27.8840, 87.0700),
           (27.8860, 87.0755), (27.8875, 87.0805), (27.8885, 87.0845),
           (27.8892, 87.0889)],
          (27.8770, 87.0540),
          "Directa y estética por el pilar oeste; el «muro Seigneur» (V+ a 7600 m) es su sello. "
          "B. Mellet e Y. Seigneur, con oxígeno.",
          "Direct and striking up the west pillar; the 'Seigneur wall' (5+ at 7,600 m) is its "
          "signature. B. Mellet & Y. Seigneur, with oxygen.",
          marks=[M("Muro Seigneur · 7600 m", "Seigneur wall · 7,600 m",
                    27.8878, 87.0817, 7600)]),
        R("cara-sur-1975", "Cara sur · 1975", "South face · 1975", 1975, "#22c55e",
          [(27.8580, 87.0920), (27.8640, 87.0910), (27.8700, 87.0900),
           (27.8760, 87.0895), (27.8810, 87.0890), (27.8850, 87.0889),
           (27.8892, 87.0889)],
          (27.8620, 87.0950),
          "Espolón meridional de la expedición yugoslava; a 8000 m se une al pilar oeste. "
          "M. Manfreda cima sin oxígeno: récord de la época.",
          "Southern spur of the Yugoslav expedition; joins the west pillar at 8,000 m. "
          "M. Manfreda summited without oxygen: a record at the time."),
        R("kukuczka-1981", "Kukuczka · 1981", "Kukuczka · 1981", 1981, "#a855f7",
          [(27.8900, 87.0580), (27.8925, 87.0640), (27.8945, 87.0700),
           (27.8960, 87.0750), (27.8972, 87.0790),
           (27.8952, 87.0814), (27.8940, 87.0829), (27.8928, 87.0844),
           (27.8916, 87.0859), (27.8892, 87.0889)],
          (27.8945, 87.0680),
          "En solitario y sin oxígeno: cara oeste directa hasta el Makalu La y, en vez del "
          "corredor, arista noroeste hasta la cima. J. Kukuczka.",
          "Solo and without oxygen: direct west face to Makalu La, then the NW ridge to the top "
          "instead of the couloir. J. Kukuczka."),
        R("cara-oeste-1997", "Cara oeste · 1997", "West face · 1997", 1997, "#14b8b9",
          [(27.8840, 87.0600), (27.8870, 87.0660), (27.8895, 87.0720),
           (27.8910, 87.0740), (27.8915, 87.0780), (27.8920, 87.0800),
           (27.8908, 87.0835), (27.8898, 87.0860), (27.8892, 87.0889)],
          (27.8885, 87.0600),
          "Expedición rusa de S. Efimov: cara oeste hasta 7950 m y travesía lateral hasta el "
          "pilar oeste a 8200 m. Piolet de Oro 1997, sin oxígeno.",
          "S. Efimov's Russian expedition: west face to 7,950 m, lateral traverse to the west "
          "pillar at 8,200 m. 1997 Piolet d'Or, no oxygen."),
    ],
}
