"""Fetch peak photos from Wikimedia Commons via Wikipedia API, with attribution."""
import json, os, re, time
import requests

API = "https://en.wikipedia.org/w/api.php"
OUT = "/tmp/ochomiles_work"
os.makedirs(OUT, exist_ok=True)

TITLES = {
    "everest": "Mount Everest",
    "k2": "K2",
    "kangchenjunga": "Kangchenjunga",
    "lhotse": "Lhotse",
    "makalu": "Makalu",
    "chooyu": "Cho Oyu",
    "dhaulagiri": "Dhaulagiri",
    "manaslu": "Manaslu",
    "nangaparbat": "Nanga Parbat",
    "annapurna": "Annapurna Massif",
    "gasherbrum1": "Gasherbrum I",
    "broadpeak": "Broad Peak",
    "gasherbrum2": "Gasherbrum II",
    "shishapangma": "Shishapangma",
}

session = requests.Session()
session.headers.update({"User-Agent": "ochomiles-data-builder/1.0 (contact: none)"})


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def get_pageimage(title):
    r = session.get(API, params={
        "action": "query", "titles": title, "prop": "pageimages",
        "format": "json", "pithumbsize": 1200, "pilicense": "any"}, timeout=30)
    r.raise_for_status()
    pages = r.json()["query"]["pages"]
    for p in pages.values():
        pi = p.get("pageimage")
        if pi:
            return pi
    return None


def get_imageinfo(filename):
    r = session.get(API, params={
        "action": "query", "titles": f"File:{filename}", "prop": "imageinfo",
        "iiprop": "url|extmetadata", "iiurlwidth": 1600, "format": "json"}, timeout=30)
    r.raise_for_status()
    pages = r.json()["query"]["pages"]
    for p in pages.values():
        ii = p.get("imageinfo")
        if ii:
            return ii[0]
    return None


def main():
    photos = {}
    for pid, title in TITLES.items():
        try:
            fname = get_pageimage(title)
            if not fname:
                print(f"{pid}: no pageimage", flush=True)
                photos[pid] = None
                continue
            info = get_imageinfo(fname)
            if not info:
                print(f"{pid}: no imageinfo", flush=True)
                photos[pid] = None
                continue
            ext = info.get("extmetadata", {})
            artist = strip_html(ext.get("Artist", {}).get("value", ""))
            lic = strip_html(ext.get("LicenseShortName", {}).get("value", ""))
            photos[pid] = {
                "u": info.get("url", ""),
                "t": info.get("thumburl", ""),
                "by": artist,
                "lic": lic,
                "src": info.get("descriptionurl", ""),
            }
            print(f"{pid}: OK {fname[:60]} by={artist[:40]!r} lic={lic!r}", flush=True)
        except Exception as e:
            print(f"{pid}: ERROR {e}", flush=True)
            photos[pid] = None
        time.sleep(0.5)
    json.dump(photos, open(f"{OUT}/photos.json", "w"), ensure_ascii=False, indent=1)
    nok = sum(1 for v in photos.values() if v)
    print(f"photos OK: {nok}/14", flush=True)


if __name__ == "__main__":
    main()
