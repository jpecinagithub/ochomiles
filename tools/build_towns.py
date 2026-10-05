"""Fetch towns near each peak via Overpass API; dedupe; fallback list."""
import json, os, time, unicodedata
import requests

OUT = "/tmp/ochomiles_work"
os.makedirs(OUT, exist_ok=True)

PEAKS = [
    ("everest", 27.9881, 86.9250), ("k2", 35.8808, 76.5139),
    ("kangchenjunga", 27.7025, 88.1475), ("lhotse", 27.9617, 86.9330),
    ("makalu", 27.8897, 87.0889), ("chooyu", 28.0941, 86.6608),
    ("dhaulagiri", 28.6967, 83.4931), ("manaslu", 28.5497, 84.5597),
    ("nangaparbat", 35.2372, 74.5892), ("annapurna", 28.5956, 83.9372),
    ("gasherbrum1", 35.7244, 76.6965), ("broadpeak", 35.8106, 76.5653),
    ("gasherbrum2", 35.7575, 76.6528), ("shishapangma", 28.3526, 85.7792),
]

FALLBACK = [
    ("Namche Bazaar", 27.8069, 86.7140), ("Lukla", 27.6869, 86.7297),
    ("Skardu", 35.2971, 75.6333), ("Gilgit", 35.9208, 74.3080),
    ("Pokhara", 28.2096, 83.9856), ("Shigar", 35.4229, 75.7336),
    ("Askole", 35.6811, 75.8153), ("Chitral", 35.8511, 71.7864),
    ("Zhangmu", 27.9786, 85.9837), ("Tingri", 28.5914, 87.1269),
    ("Syabrubesi", 28.1614, 85.3403), ("Samagaon", 28.5797, 84.6419),
    ("Jomsom", 28.7806, 83.7225), ("Marpha", 28.7556, 83.8597),
]

session = requests.Session()
session.headers.update({"User-Agent": "ochomiles-data-builder/1.0"})


def norm(name):
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return n.strip().lower()


def query_peak(pid, lat, lon):
    q = (f'[out:json][timeout:60];'
         f'(node["place"~"^(city|town|village)$"](around:90000,{lat},{lon}););'
         f'out body 60;')
    r = session.post("https://overpass-api.de/api/interpreter", data={"data": q}, timeout=90)
    r.raise_for_status()
    els = r.json().get("elements", [])
    out = []
    for e in els:
        tags = e.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        if not name:
            continue
        place = tags.get("place", "")
        k = 2 if place == "city" else 1
        out.append({"n": name, "lat": e["lat"], "lon": e["lon"], "k": k})
    return out


def main():
    seen = {}
    ok_any = False
    for pid, lat, lon in PEAKS:
        try:
            towns = query_peak(pid, lat, lon)
            ok_any = True
            print(f"{pid}: {len(towns)} towns", flush=True)
            for t in towns:
                key = norm(t["n"])
                if key and key not in seen:
                    seen[key] = t
        except Exception as e:
            print(f"{pid}: ERROR {e}", flush=True)
        time.sleep(1)
    if not ok_any:
        print("Overpass failed everywhere -> fallback list", flush=True)
        seen = {}
        for n, lat, lon in FALLBACK:
            seen[norm(n)] = {"n": n, "lat": lat, "lon": lon, "k": 1}
    # keep ~80, prefer cities then closer to peaks? simple: cities first, then name-sorted
    towns = sorted(seen.values(), key=lambda t: (-t["k"], t["n"]))[:80]
    json.dump(towns, open(f"{OUT}/towns.json", "w"), ensure_ascii=False, indent=1)
    print(f"towns total: {len(towns)}", flush=True)


if __name__ == "__main__":
    main()
