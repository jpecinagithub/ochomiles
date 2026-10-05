"""Download Natural Earth geojson vectors, clip to region, simplify, save JSON."""
import json, os, math
import numpy as np
import requests

LON0, LAT0, LON1, LAT1 = 73.5, 27.0, 89.5, 36.5
BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"
OUT = "/tmp/ochomiles_work"
os.makedirs(OUT, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "ochomiles-data-builder/1.0"})


def douglas_peucker(pts, tol):
    """Iterative DP on [(x,y)] with euclidean tolerance. Returns list."""
    n = len(pts)
    if n < 3:
        return pts
    pts = np.asarray(pts, dtype=np.float64)
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        seg = pts[b] - pts[a]
        L = float(np.hypot(*seg))
        sub = pts[a + 1:b] - pts[a]
        if L == 0:
            d = np.hypot(sub[:, 0], sub[:, 1])
        else:
            d = np.abs(sub[:, 0] * seg[1] - sub[:, 1] * seg[0]) / L
        k = int(np.argmax(d)) + a + 1
        if d[k - a - 1] > tol:
            keep[k] = True
            stack.append((a, k)); stack.append((k, b))
    return [tuple(p) for p in pts[keep]]


def clip_and_project(geom, scale_lon):
    """Extract LineString/MultiLineString/Polygon rings, clip coords to region+pad,
    return list of [ (lon,lat), ... ] lines. scale_lon for DP weighting."""
    lines = []
    geoms = []
    t = geom["type"]
    if t == "LineString":
        geoms = [geom["coordinates"]]
    elif t == "MultiLineString":
        geoms = geom["coordinates"]
    elif t == "Polygon":
        geoms = geom["coordinates"]
    elif t == "MultiPolygon":
        for poly in geom["coordinates"]:
            geoms.extend(poly)
    pad = 0.5
    for coords in geoms:
        line = []
        for c in coords:
            lon, lat = c[0], c[1]
            if LON0 - pad <= lon <= LON1 + pad and LAT0 - pad <= lat <= LAT1 + pad:
                line.append((lon, lat))
            else:
                if len(line) >= 2:
                    lines.append(line)
                line = []
        if len(line) >= 2:
            lines.append(line)
    return lines


def fetch(name):
    local = f"{OUT}/{name}"
    if os.path.exists(local):
        print(f"load local {name} ...", flush=True)
        return json.load(open(local, encoding="utf-8"))
    url = f"{BASE}/{name}"
    print(f"fetch {name} ...", flush=True)
    r = session.get(url, timeout=120)
    r.raise_for_status()
    return r.json()


def process(name, keep_names, tol=0.005):
    gj = fetch(name)
    feats = gj["features"] if gj["type"] == "FeatureCollection" else [gj]
    out = []
    n_in, n_out = 0, 0
    lat_mean = math.radians((LAT0 + LAT1) / 2)
    coslat = math.cos(lat_mean)
    for f in feats:
        props = f.get("properties") or {}
        geom = f.get("geometry")
        if not geom:
            continue
        lines = clip_and_project(geom, coslat)
        n_in += len(lines)
        for line in lines:
            # DP in (lon*coslat, lat) space so tol is ~uniform in meters
            proj = [(lon * coslat, lat) for lon, lat in line]
            simp = douglas_peucker(proj, tol)
            if len(simp) < 2:
                continue
            orig = [(x / coslat, y) for x, y in simp]
            n_out += 1
            item = {"d": orig}
            if keep_names:
                nm = props.get("name")
                if nm:
                    item["n"] = nm
            out.append(item)
    print(f"{name}: {n_in} segs -> {n_out} lines", flush=True)
    return out


def main():
    rivers = process("ne_10m_rivers_lake_centerlines.geojson", keep_names=True)
    lakes = process("ne_10m_lakes.geojson", keep_names=True)
    borders = process("ne_10m_admin_0_boundary_lines_land.geojson", keep_names=False)
    # borders: merge into single item list of lines
    border_lines = []
    for b in borders:
        border_lines.append(b["d"])
    json.dump({"rivers": rivers, "lakes": lakes, "borders": border_lines},
              open(f"{OUT}/vectors.json", "w"), ensure_ascii=False)
    print("vectors saved", flush=True)


if __name__ == "__main__":
    main()
