"""Assemble datos-base.js and datos-picos.js from intermediate build products."""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from enc import enc_ints, enc_u8, enc_lines, dec_ints, dec_lines

WORK = "/tmp/ochomiles_work"
ROOT = os.path.join(os.path.dirname(__file__), "..")
LON0, LAT0, LON1, LAT1 = 73.5, 27.0, 89.5, 36.5
W, H = 1600, 950

FALLBACK_TOWNS = [
    ("Namche Bazaar", 27.8069, 86.7140), ("Lukla", 27.6869, 86.7297),
    ("Skardu", 35.2971, 75.6333), ("Gilgit", 35.9208, 74.3080),
    ("Pokhara", 28.2096, 83.9856), ("Shigar", 35.4229, 75.7336),
    ("Askole", 35.6811, 75.8153), ("Chitral", 35.8511, 71.7864),
    ("Zhangmu", 27.9786, 85.9837), ("Tingri", 28.5914, 87.1269),
    ("Syabrubesi", 28.1614, 85.3403), ("Samagaon", 28.5797, 84.6419),
    ("Jomsom", 28.7806, 83.7225), ("Marpha", 28.7556, 83.8597),
]

PEAKS = [
    dict(id="everest", n=("Everest", "Mount Everest"), aka=["Chomolungma", "Sagarmatha"],
         a=8848.86, prom=8848.86, lat=27.9881, lon=86.9250, zone="mahalangur",
         ctr=("Nepal / China (Tíbet)", "Nepal / China (Tibet)"),
         rng=("Mahalangur Himal", "Mahalangur Himal"), fa=(1953, "E. Hillary y T. Norgay", "E. Hillary & T. Norgay"),
         route=("Vía normal por el Collado Sur (6.400 m): cascada de hielo del Khumbu, Collado Sur y arista sureste hasta la cima.",
                "Normal route via the South Col (6,400 m): Khumbu Icefall, South Col and southeast ridge to the summit."),
         bc=("Campo base sur", "South Base Camp", 28.0026, 86.8528)),
    dict(id="k2", n=("K2", "K2"), aka=["Chogori"],
         a=8611, prom=4017, lat=35.8808, lon=76.5139, zone="karakorum",
         ctr=("Pakistán / China", "Pakistan / China"),
         rng=("Karakórum", "Karakoram"), fa=(1954, "A. Compagnoni y L. Lacedelli", "A. Compagnoni & L. Lacedelli"),
         route=("Vía normal por el Espolón de los Abruzos (arista sureste).",
                "Normal route via the Abruzzi Spur (southeast ridge)."),
         bc=("Campo base del K2", "K2 Base Camp", 35.8373, 76.5186)),
    dict(id="kangchenjunga", n=("Kangchenjunga", "Kangchenjunga"), aka=[],
         a=8586, prom=3922, lat=27.7025, lon=88.1475, zone="kangchenjunga",
         ctr=("Nepal / India (Sikkim)", "Nepal / India (Sikkim)"),
         rng=("Kangchenjunga Himal", "Kangchenjunga Himal"), fa=(1955, "G. Band y J. Brown", "G. Band & J. Brown"),
         route=("Vía normal por la cara suroeste y la Gran Repisa.",
                "Normal route via the southwest face and the Great Shelf."),
         bc=("Pangpema", "Pangpema", 27.7242, 88.1095)),
    dict(id="lhotse", n=("Lhotse", "Lhotse"), aka=[],
         a=8516, prom=610, lat=27.9617, lon=86.9330, zone="mahalangur",
         ctr=("Nepal / China (Tíbet)", "Nepal / China (Tibet)"),
         rng=("Mahalangur Himal", "Mahalangur Himal"), fa=(1956, "E. Reiss y F. Luchsinger", "E. Reiss & F. Luchsinger"),
         route=("Corredor del Lhotse desde el Collado Sur.",
                "Lhotse Couloir from the South Col."),
         bc=("Campo base sur", "South Base Camp", 28.0026, 86.8528)),
    dict(id="makalu", n=("Makalu", "Makalu"), aka=[],
         a=8463, prom=2378, lat=27.8897, lon=87.0889, zone="mahalangur",
         ctr=("Nepal / China (Tíbet)", "Nepal / China (Tibet)"),
         rng=("Mahalangur Himal", "Mahalangur Himal"), fa=(1955, "L. Couzy y L. Terray", "L. Couzy & L. Terray"),
         route=("Vía normal por la arista noroeste.",
                "Normal route via the northwest ridge."),
         bc=("Campo base del Makalu", "Makalu Base Camp", 27.8717, 87.1150)),
    dict(id="chooyu", n=("Cho Oyu", "Cho Oyu"), aka=[],
         a=8188, prom=2344, lat=28.0941, lon=86.6608, zone="mahalangur",
         ctr=("Nepal / China (Tíbet)", "Nepal / China (Tibet)"),
         rng=("Mahalangur Himal", "Mahalangur Himal"), fa=(1954, "H. Tichy, S. Jöchler y Pasang Dawa Lama", "H. Tichy, S. Jöchler & Pasang Dawa Lama"),
         route=("Vía normal por la cara noroeste desde el Nangpa La.",
                "Normal route via the northwest face from Nangpa La."),
         bc=("Campo base del Cho Oyu", "Cho Oyu Base Camp", 28.0244, 86.6950)),
    dict(id="dhaulagiri", n=("Dhaulagiri I", "Dhaulagiri I"), aka=[],
         a=8167, prom=3357, lat=28.6967, lon=83.4931, zone="dhaulagiri",
         ctr=("Nepal", "Nepal"),
         rng=("Dhaulagiri Himal", "Dhaulagiri Himal"), fa=(1960, "Expedición suiza", "Swiss expedition"),
         route=("Vía normal por el collado nordeste.",
                "Normal route via the Northeast Col."),
         bc=("Campo base del Dhaulagiri", "Dhaulagiri Base Camp", 28.7333, 83.5167)),
    dict(id="manaslu", n=("Manaslu", "Manaslu"), aka=[],
         a=8163, prom=3092, lat=28.5497, lon=84.5597, zone="manaslu",
         ctr=("Nepal", "Nepal"),
         rng=("Manaslu Himal", "Manaslu Himal"), fa=(1956, "T. Imanishi y Gyalzen Norbu", "T. Imanishi & Gyalzen Norbu"),
         route=("Vía normal por la cara noreste.",
                "Normal route via the northeast face."),
         bc=("Campo base del Manaslu", "Manaslu Base Camp", 28.5750, 84.5760)),
    dict(id="nangaparbat", n=("Nanga Parbat", "Nanga Parbat"), aka=[],
         a=8126, prom=4608, lat=35.2372, lon=74.5892, zone="nanga",
         ctr=("Pakistán", "Pakistan"),
         rng=("Nanga Parbat Himal", "Nanga Parbat Himal"), fa=(1953, "H. Buhl (en solitario)", "H. Buhl (solo)"),
         route=("Vía Kinshofer por la vertiente Diamir (oeste).",
                "Kinshofer route on the Diamir (west) face."),
         bc=("Campo base Diamir", "Diamir Base Camp", 35.3500, 74.6200)),
    dict(id="annapurna", n=("Annapurna I", "Annapurna I"), aka=[],
         a=8091, prom=2984, lat=28.5956, lon=83.9372, zone="annapurna",
         ctr=("Nepal", "Nepal"),
         rng=("Annapurna Himal", "Annapurna Himal"), fa=(1950, "M. Herzog y L. Lachenal (primer ochomil)", "M. Herzog & L. Lachenal (first 8000er)"),
         route=("Vía normal por la cara norte (vía francesa de 1950).",
                "Normal route via the north face (1950 French route)."),
         bc=("Campo base norte", "North Base Camp", 28.6000, 83.9300)),
    dict(id="gasherbrum1", n=("Gasherbrum I", "Gasherbrum I"), aka=["Hidden Peak"],
         a=8080, prom=2155, lat=35.7244, lon=76.6965, zone="karakorum",
         ctr=("Pakistán / China", "Pakistan / China"),
         rng=("Karakórum", "Karakoram"), fa=(1958, "P. Schoening y A. Kaufman", "P. Schoening & A. Kaufman"),
         route=("Vía normal por el corredor de los Americanos.",
                "Normal route via the American Couloir."),
         bc=("Campo base GI", "GI Base Camp", 35.7225, 76.6200)),
    dict(id="broadpeak", n=("Broad Peak", "Broad Peak"), aka=[],
         a=8047, prom=1701, lat=35.8106, lon=76.5653, zone="karakorum",
         ctr=("Pakistán / China", "Pakistan / China"),
         rng=("Karakórum", "Karakoram"), fa=(1957, "Expedición austriaca", "Austrian expedition"),
         route=("Vía normal por el collado y la arista oeste.",
                "Normal route via the col and west ridge."),
         bc=("Campo base del Broad Peak", "Broad Peak Base Camp", 35.7900, 76.5500)),
    dict(id="gasherbrum2", n=("Gasherbrum II", "Gasherbrum II"), aka=[],
         a=8035, prom=1523, lat=35.7575, lon=76.6528, zone="karakorum",
         ctr=("Pakistán / China", "Pakistan / China"),
         rng=("Karakórum", "Karakoram"), fa=(1956, "F. Larch, H. Reinagl y H. Willenpart", "F. Larch, H. Reinagl & H. Willenpart"),
         route=("Vía normal por la arista suroeste.",
                "Normal route via the southwest ridge."),
         bc=("Campo base GII", "GII Base Camp", 35.7400, 76.6000)),
    dict(id="shishapangma", n=("Shishapangma", "Shishapangma"), aka=[],
         a=8027, prom=2897, lat=28.3526, lon=85.7792, zone="jugal",
         ctr=("China (Tíbet)", "China (Tibet)"),
         rng=("Jugal Himal", "Jugal Himal"), fa=(1964, "Expedición china (último ochomil)", "Chinese expedition (last 8000er)"),
         route=("Vía normal por la cara norte.",
                "Normal route via the north face."),
         bc=("Campo base del Shishapangma", "Shishapangma Base Camp", 28.4000, 85.8000)),
]

ZONES = [
    ("karakorum", "Karakórum", "Karakoram"),
    ("nanga", "Nanga Parbat", "Nanga Parbat"),
    ("dhaulagiri", "Dhaulagiri", "Dhaulagiri"),
    ("annapurna", "Annapurna", "Annapurna"),
    ("manaslu", "Manaslu", "Manaslu"),
    ("jugal", "Jugal Himal", "Jugal Himal"),
    ("mahalangur", "Mahalangur Himal", "Mahalangur Himal"),
    ("kangchenjunga", "Kangchenjunga", "Kangchenjunga"),
]


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    print(f"WARN: missing {path}, using fallback", flush=True)
    return default


def main():
    dem = np.load(f"{WORK}/dem_final.npy")
    lc = np.load(f"{WORK}/lc.npy")
    contours = load_json(f"{WORK}/contours.json", [])
    vectors = load_json(f"{WORK}/vectors.json", {"rivers": [], "lakes": [], "borders": []})
    towns = load_json(f"{WORK}/towns.json", None)
    photos_raw = load_json(f"{WORK}/photos.json", {})

    if towns is None:
        towns = [{"n": n, "lat": lat, "lon": lon, "k": 1} for n, lat, lon in FALLBACK_TOWNS]
        towns_src = "fallback"
    else:
        towns_src = "overpass"

    # ---- photos ----
    photos = []
    photo_idx = {}
    for p in PEAKS:
        pr = photos_raw.get(p["id"])
        if pr:
            photo_idx[p["id"]] = len(photos)
            photos.append(pr)
        else:
            photo_idx[p["id"]] = None

    peaks_js = []
    for p in PEAKS:
        y, by_es, by_en = p["fa"]
        peaks_js.append({
            "id": p["id"],
            "n": {"es": p["n"][0], "en": p["n"][1]},
            "aka": p["aka"],
            "a": p["a"], "prom": p["prom"],
            "lat": p["lat"], "lon": p["lon"],
            "zone": p["zone"],
            "ctr": {"es": p["ctr"][0], "en": p["ctr"][1]},
            "rng": {"es": p["rng"][0], "en": p["rng"][1]},
            "fa": {"y": y, "by": {"es": by_es, "en": by_en}},
            "route": {"es": p["route"][0], "en": p["route"][1]},
            "photo": photo_idx[p["id"]],
            "bc": {"n": {"es": p["bc"][0], "en": p["bc"][1]}, "lat": p["bc"][2], "lon": p["bc"][3]},
        })

    # ---- encodings ----
    dem_i = np.round(dem).astype(np.int32)
    print("encoding dem...", flush=True)
    dem_s = enc_ints(dem_i.ravel().tolist())
    print("encoding lc...", flush=True)
    lc_s = enc_u8(lc.tobytes())

    print("encoding contours...", flush=True)
    contours_js = []
    total_pts = 0
    for c in contours:
        d = enc_lines(c["lines"])
        total_pts += sum(len(l) for l in c["lines"])
        contours_js.append({"e": c["e"], "d": d})

    def enc_feats(feats):
        out = []
        for f in feats:
            lines = [f["d"]] if isinstance(f, dict) else [f]
            item = {"d": enc_lines(lines)}
            if isinstance(f, dict) and f.get("n"):
                item = {"n": f["n"], "d": item["d"]}
            out.append(item)
        return out

    rivers_js = enc_feats(vectors.get("rivers", []))
    lakes_js = enc_feats(vectors.get("lakes", []))
    border_lines = vectors.get("borders", [])
    borders_js = [{"d": enc_lines(border_lines)}] if border_lines else []

    ocho = {
        "meta": {"v": 1, "built": "2026-10-05", "lang": ["es", "en"],
                 "sources": [
                     "Relieve: AWS Terrain Tiles (Terrarium; datos SRTM de la NASA)",
                     "Ríos, lagos y fronteras: Natural Earth (dominio público)",
                     "Pueblos: © colaboradores de OpenStreetMap (ODbL)",
                     "Fotos: Wikimedia Commons (autor y licencia en la ficha de cada cima)",
                     "Lista de cimas y altitudes: Wikipedia",
                 ]},
        "grid": {"lon0": LON0, "lat0": LAT0, "lon1": LON1, "lat1": LAT1, "w": W, "h": H},
        "dem": dem_s,
        "lc": lc_s,
        "contours": contours_js,
        "rivers": rivers_js,
        "lakes": lakes_js,
        "borders": borders_js,
        "towns": towns,
        "peaks": peaks_js,
        "zones": [{"id": zid, "n": {"es": es, "en": en}} for zid, es, en in ZONES],
        "photos": photos,
    }

    with open(os.path.join(ROOT, "datos-base.js"), "w", encoding="utf-8") as f:
        f.write("window.OCHO=")
        json.dump(ocho, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";")

    # ---- patches ----
    patches = np.load(f"{WORK}/patches.npy", allow_pickle=True).item()
    patch_js = {}
    for pid, p in patches.items():
        patch_js[pid] = {
            "lon0": p["lon0"], "lat0": p["lat0"], "lon1": p["lon1"], "lat1": p["lat1"],
            "w": int(p["w"]), "h": int(p["h"]),
            "dem": enc_ints(p["dem"].ravel().tolist()),
        }
    with open(os.path.join(ROOT, "datos-picos.js"), "w", encoding="utf-8") as f:
        f.write("window.OCHO_PATCH=")
        json.dump(patch_js, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";")

    # ---- verification ----
    print("verifying...", flush=True)
    raw = open(os.path.join(ROOT, "datos-base.js"), encoding="utf-8").read()
    assert raw.startswith("window.OCHO=") and raw.endswith(";")
    o2 = json.loads(raw[len("window.OCHO="):-1])
    d = dec_ints(o2["dem"])
    assert len(d) == W * H, f"dem cells {len(d)} != {W*H}"
    assert not any(v != v for v in d), "NaN in dem"
    dem_np = np.array(d, dtype=np.float64).reshape(H, W)
    j = int(round((LAT1 - 27.9881) / ((LAT1 - LAT0) / H) - 0.5))
    i = int(round((86.9250 - LON0) / ((LON1 - LON0) / W) - 0.5))
    ev = dem_np[j, i]
    print(f"everest cell ({i},{j}) = {ev} (need 8848.86±60): {'OK' if abs(ev-8848.86)<=60 else 'FAIL'}")
    ph = [p["photo"] for p in o2["peaks"]]
    print(f"peaks with photo: {sum(x is not None for x in ph)}/14, nulls: {sum(x is None for x in ph)}")
    raw2 = open(os.path.join(ROOT, "datos-picos.js"), encoding="utf-8").read()
    p2 = json.loads(raw2[len("window.OCHO_PATCH="):-1])
    assert set(p2.keys()) == {p["id"] for p in PEAKS}
    for pid, pp in p2.items():
        dd = dec_ints(pp["dem"])
        assert len(dd) == pp["w"] * pp["h"], pid
    print("patches OK:", len(p2))

    import os as _os
    s1 = _os.path.getsize(os.path.join(ROOT, "datos-base.js"))
    s2 = _os.path.getsize(os.path.join(ROOT, "datos-picos.js"))
    print(f"datos-base.js: {s1/1e6:.2f} MB")
    print(f"datos-picos.js: {s2/1e6:.2f} MB")
    print(f"contours: {len(contours_js)} levels, {total_pts} points")
    print(f"rivers: {len(rivers_js)}, lakes: {len(lakes_js)}, borders: {len(borders_js)}")
    print(f"towns: {len(towns)} (src={towns_src}), photos: {len(photos)}/14")
    print("DONE")


if __name__ == "__main__":
    main()
