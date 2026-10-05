"""Per-peak hi-res DEM patches (0.35°x0.35°, Terrarium z=11 -> 256x256)."""
import math, os
import numpy as np
import requests
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

CACHE = "/tmp/ochomiles_tiles/z11"
os.makedirs(CACHE, exist_ok=True)
OUT = "/tmp/ochomiles_work"

PEAKS = {
    "everest": (27.9881, 86.9250), "k2": (35.8808, 76.5139),
    "kangchenjunga": (27.7025, 88.1475), "lhotse": (27.9617, 86.9330),
    "makalu": (27.8897, 87.0889), "chooyu": (28.0941, 86.6608),
    "dhaulagiri": (28.6967, 83.4931), "manaslu": (28.5497, 84.5597),
    "nangaparbat": (35.2372, 74.5892), "annapurna": (28.5956, 83.9372),
    "gasherbrum1": (35.7244, 76.6965), "broadpeak": (35.8106, 76.5653),
    "gasherbrum2": (35.7575, 76.6528), "shishapangma": (28.3526, 85.7792),
}
Z = 11
HALF = 0.175

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_connections=16, pool_maxsize=16)
session.mount("https://", adapter)
session.headers.update({"User-Agent": "ochomiles-data-builder/1.0"})


def frac_tile(lon, lat, z):
    n = 2 ** z
    gx = (lon + 180.0) / 360.0 * n
    lr = math.radians(lat)
    gy = (1.0 - math.log(math.tan(lr) + 1.0 / math.cos(lr)) / math.pi) / 2.0 * n
    return gx, gy


def fetch_tile(x, y):
    path = f"{CACHE}/{x}_{y}.png"
    if os.path.exists(path):
        return path
    if os.path.exists(path + ".missing"):
        return None
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
        print(f"tile z{Z} {x}/{y} failed: {e}", flush=True)
        return None


def decode(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    return a[..., 0] * 256.0 + a[..., 1] + a[..., 2] / 256.0 - 32768.0


def main():
    jobs = []
    meta = {}
    for pid, (lat, lon) in PEAKS.items():
        lon0, lon1 = lon - HALF, lon + HALF
        lat0, lat1 = lat - HALF, lat + HALF
        gx0, gy0 = frac_tile(lon0, lat1, Z)   # note: lat1 = north -> smaller gy
        gx1, gy1 = frac_tile(lon1, lat0, Z)
        xs = range(math.floor(gx0), math.floor(gx1) + 1)
        ys = range(math.floor(gy0), math.floor(gy1) + 1)
        meta[pid] = (lon0, lon1, lat0, lat1, list(xs), list(ys))
        for x in xs:
            for y in ys:
                jobs.append((x, y))
    jobs = sorted(set(jobs))
    print(f"patches: {len(PEAKS)}, tiles needed: {len(jobs)}", flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        paths = list(ex.map(lambda t: fetch_tile(*t), jobs))
    tp = dict(zip(jobs, paths))
    missing = sum(1 for p in paths if not p)
    print(f"missing tiles: {missing}", flush=True)

    patches = {}
    for pid, (lat, lon) in PEAKS.items():
        lon0, lon1, lat0, lat1, xs, ys = meta[pid]
        # mosaic
        mw, mh = len(xs) * 256, len(ys) * 256
        mos = np.full((mh, mw), np.nan, dtype=np.float32)
        x0t, y0t = xs[0], ys[0]
        for x in xs:
            for y in ys:
                p = tp.get((x, y))
                if p:
                    mos[(y - y0t) * 256:(y - y0t + 1) * 256,
                        (x - x0t) * 256:(x - x0t + 1) * 256] = decode(p)
        # crop exact bbox: pixel coords of (lon0,lat1)..(lon1,lat0) in mosaic
        gx0, gy0 = frac_tile(lon0, lat1, Z)
        gx1, gy1 = frac_tile(lon1, lat0, Z)
        px0 = int(round((gx0 - x0t) * 256)); py0 = int(round((gy0 - y0t) * 256))
        px1 = int(round((gx1 - x0t) * 256)); py1 = int(round((gy1 - y0t) * 256))
        crop = mos[py0:py1, px0:px1]
        # NaN fill inside crop (neighbor mean)
        m = np.isnan(crop)
        if m.any():
            f = np.nan_to_num(crop, nan=0.0)
            c = (~m).astype(np.float32)
            for _ in range(50):
                if not m.any():
                    break
                up = np.roll(f, 1, 0); dn = np.roll(f, -1, 0)
                lf = np.roll(f, 1, 1); rt = np.roll(f, -1, 1)
                cu = np.roll(c, 1, 0); cd = np.roll(c, -1, 0)
                cl = np.roll(c, 1, 1); cr = np.roll(c, -1, 1)
                s = up + dn + lf + rt; cc = cu + cd + cl + cr
                new = (cc > 0) & m
                f[new] = (s / np.maximum(cc, 1))[new]
                c[new] = 1.0
                m = np.isnan(f) | (c == 0)
            crop = f
        # resample to 256x256 via PIL (float32 -> float64 ok)
        img = Image.fromarray(crop.astype(np.float32), mode="F").resize((256, 256), Image.BICUBIC)
        arr = np.asarray(img)
        arr = np.nan_to_num(arr, nan=0.0)
        patches[pid] = {"lon0": lon0, "lat0": lat0, "lon1": lon1, "lat1": lat1,
                        "w": 256, "h": 256, "dem": np.round(arr).astype(np.int32)}
        print(f"{pid}: crop {crop.shape} -> 256x256, range {arr.min():.0f}..{arr.max():.0f}",
              flush=True)
    np.save(f"{OUT}/patches.npy", patches, allow_pickle=True)
    print("patches saved", flush=True)


if __name__ == "__main__":
    main()
