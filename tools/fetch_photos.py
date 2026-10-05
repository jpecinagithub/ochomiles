"""Completa las fotos que falten en datos-base.js vía Wikipedia API."""
import json, re, sys, time, urllib.parse, urllib.request

ROOT = "/home/hatch/workspace/ochomiles"
TITLES = {
    "everest": "Mount Everest", "k2": "K2", "kangchenjunga": "Kangchenjunga",
    "nangaparbat": "Nanga Parbat", "annapurna": "Annapurna Massif",
    "gasherbrum1": "Gasherbrum I", "broadpeak": "Broad Peak",
    "gasherbrum2": "Gasherbrum II", "shishapangma": "Shishapangma",
}

def api(params):
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "OCHOMILES/1.0 (personal project)"})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print("  retry:", e, file=sys.stderr)
            time.sleep(2)
    return None

def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()

def fetch_photo(title):
    d = api({"action": "query", "titles": title, "prop": "pageimages",
             "format": "json", "pithumbsize": 1200, "pilicense": "any"})
    pages = (d or {}).get("query", {}).get("pages", {})
    page = next(iter(pages.values()), None) if pages else None
    if not page or "pageimage" not in page:
        return None
    fname = page["pageimage"]
    d2 = api({"action": "query", "titles": "File:" + fname, "prop": "imageinfo",
              "iiprop": "url|extmetadata", "iiurlwidth": 800, "format": "json"})
    pages2 = (d2 or {}).get("query", {}).get("pages", {})
    p2 = next(iter(pages2.values()), None) if pages2 else None
    info = (p2 or {}).get("imageinfo", [{}])[0]
    ext = info.get("extmetadata", {})
    # strip utm params from thumbnail urls
    t = (info.get("thumburl") or "").split("?")[0]
    u = (info.get("url") or "").split("?")[0]
    if not u:
        return None
    return {
        "u": u, "t": t or u,
        "by": strip_html(ext.get("Artist", {}).get("value")) or "Wikimedia Commons",
        "lic": strip_html(ext.get("LicenseShortName", {}).get("value")) or "?",
        "src": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(fname),
    }

def main():
    path = ROOT + "/datos-base.js"
    src = open(path).read()
    assert src.startswith("window.OCHO=")
    O = json.loads(src[len("window.OCHO="):].rstrip().rstrip(";"))
    peaks = {p["id"]: p for p in O["peaks"]}
    added = 0
    for pid, title in TITLES.items():
        p = peaks.get(pid)
        if not p or p.get("photo") is not None:
            continue
        print("fetching", pid, "-", title)
        ph = fetch_photo(title)
        time.sleep(1)
        if ph:
            p["photo"] = len(O["photos"])
            O["photos"].append(ph)
            added += 1
            print("  OK:", ph["by"], "|", ph["lic"])
        else:
            print("  FAILED")
    with open(path, "w") as f:
        f.write("window.OCHO=" + json.dumps(O, ensure_ascii=False) + ";")
    print("added", added, "photos; total now", len(O["photos"]))

if __name__ == "__main__":
    main()
