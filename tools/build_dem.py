"""Build base DEM grid (1600x950) from AWS Terrain Tiles (Terrarium, z=8)."""
import math, os, sys
import numpy as np
import requests
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

LON0, LAT0, LON1, LAT1 = 73.5, 27.0, 89.5, 36.5
W, H = 1600, 950
Z = 8
CACHE = "/tmp/ochomiles_tiles/z8"
os.makedirs(CACHE, exist_ok=True)

DX = (LON1 - LON0) / W
DY = (LAT1 - LAT0) / H

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_connections=16, pool_maxsize=16)
session.mount("https://", adapter)
session.headers.update({"User-Agent": "ochomiles-data-builder/1.0"})


def frac_tile(lon, lat, z):
    """Fractional tile coords (x, y) for lon/lat arrays."""
    n = 2 ** z
    gx = (np.asarray(lon) + 180.0) / 360.0 * n
    lr = np.radians(np.asarray(lat))
    gy = (1.0 - np.log(np.tan(lr) + 1.0 / np.cos(lr)) / np.pi) / 2.0 * n
    return gx, gy


def fetch_tile(x, y):
    path = f"{CACHE}/{x}_{y}.png"
    if os.path.exists(path):
        return path
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png"
    try:
        r = session.get(url, timeout=30)
        if r.status_code == 404:
            open(path + ".missing", "w").write("404")
            return None
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    except Exception as e:
        print(f"tile {x}/{y} failed: {e}", flush=True)
        return None


def decode_terrarium(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    return a[..., 0] * 256.0 + a[..., 1] + a[..., 2] / 256.0 - 32768.0


def main():
    # cell centers
    ii, jj = np.meshgrid(np.arange(W, dtype=np.float64), np.arange(H, dtype=np.float64))
    lons = LON0 + (ii + 0.5) * DX
    lats = LAT1 - (jj + 0.5) * DY
    fx, fy = frac_tile(lons, lats, Z)
    xt = np.floor(fx).astype(np.int32)
    yt = np.floor(fy).astype(np.int32)
    tiles = sorted(set(zip(xt.ravel().tolist(), yt.ravel().tolist())))
    print(f"grid cells: {W*H}, tiles needed: {len(tiles)}", flush=True)

    with ThreadPoolExecutor(max_workers=8) as ex:
        paths = list(ex.map(lambda t: fetch_tile(*t), tiles))
    tile_path = dict(zip(tiles, paths))
    ok = [t for t, p in tile_path.items() if p]
    miss = [t for t, p in tile_path.items() if not p]
    print(f"downloaded: {len(ok)}, missing: {len(miss)} {miss[:10]}", flush=True)

    dem = np.full((H, W), np.nan, dtype=np.float32)
    for (x, y), path in tile_path.items():
        if not path:
            continue
        elev = decode_terrarium(path)
        elev = np.pad(elev, 1, mode="edge")  # for safe bilinear at borders
        m = (xt == x) & (yt == y)
        if not np.any(m):
            continue
        px = (fx[m] - x) * 256.0 + 1.0
        py = (fy[m] - y) * 256.0 + 1.0
        x0 = np.floor(px).astype(np.int64); dx = px - x0
        y0 = np.floor(py).astype(np.int64); dy = py - y0
        v00 = elev[y0, x0]; v10 = elev[y0, x0 + 1]
        v01 = elev[y0 + 1, x0]; v11 = elev[y0 + 1, x0 + 1]
        v = v00 * (1 - dx) * (1 - dy) + v10 * dx * (1 - dy) + v01 * (1 - dx) * dy + v11 * dx * dy
        if np.isnan(v).any():  # NaN propagation
            bad = np.isnan(v00) | np.isnan(v10) | np.isnan(v01) | np.isnan(v11)
            v[bad] = np.nan
        dem[m] = v
        del elev

    # fill NaNs by neighbor interpolation
    nan_n = int(np.isnan(dem).sum())
    print(f"NaN cells before fill: {nan_n}", flush=True)
    it = 0
    while nan_n and it < 200:
        m = np.isnan(dem)
        up = np.roll(dem, 1, 0); dn = np.roll(dem, -1, 0)
        lf = np.roll(dem, 1, 1); rt = np.roll(dem, -1, 1)
        s = np.zeros_like(dem); c = np.zeros_like(dem)
        for g in (up, dn, lf, rt):
            okg = ~np.isnan(g)
            s += np.where(okg, g, 0.0); c += okg
        fill = m & (c > 0)
        dem[fill] = (s / np.maximum(c, 1))[fill]
        nan_n = int(np.isnan(dem).sum())
        it += 1
        if it % 20 == 0:
            print(f"  fill iter {it}, remaining NaN: {nan_n}", flush=True)
    print(f"NaN cells after fill: {nan_n}, iters: {it}", flush=True)

    np.save("/tmp/ochomiles_work/dem.npy", dem)
    print(f"dem range: {np.nanmin(dem):.1f}..{np.nanmax(dem):.1f}", flush=True)


if __name__ == "__main__":
    main()
