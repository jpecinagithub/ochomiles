"""Marching-squares contours on base DEM grid; DP simplify; save lines JSON."""
import json, os, sys
import numpy as np

LON0, LAT0, LON1, LAT1 = 73.5, 27.0, 89.5, 36.5
W, H = 1600, 950
DX = (LON1 - LON0) / W
DY = (LAT1 - LAT0) / H
OUT = "/tmp/ochomiles_work"
LEVELS = list(range(500, 8501, 500))
TOL = 0.004  # degrees, applied in (lon*coslat, lat) space


def dp(pts, tol):
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
        d = np.hypot(sub[:, 0], sub[:, 1]) if L == 0 else \
            np.abs(sub[:, 0] * seg[1] - sub[:, 1] * seg[0]) / L
        k = int(np.argmax(d)) + a + 1
        if d[k - a - 1] > tol:
            keep[k] = True
            stack.append((a, k)); stack.append((k, b))
    return pts[keep]


def main():
    from skimage.measure import find_contours
    dem = np.load(f"{OUT}/dem_final.npy")
    print(f"dem loaded {dem.shape}, range {dem.min():.0f}..{dem.max():.0f}", flush=True)
    coslat = np.cos(np.radians(31.75))
    total_pts = 0
    total_lines = 0
    contours = []
    for e in LEVELS:
        raw = find_contours(dem, e)
        lines = []
        for c in raw:
            if len(c) < 4:
                continue
            # c: (row=j, col=i) index space -> lon/lat
            lons = LON0 + c[:, 1] * DX
            lats = LAT1 - c[:, 0] * DY
            proj = np.column_stack((lons * coslat, lats))
            s = dp(proj, TOL)
            if len(s) < 2:
                continue
            line = [(float(x / coslat), float(y)) for x, y in s]
            lines.append(line)
            total_pts += len(line)
        contours.append({"e": e, "lines": lines})
        total_lines += len(lines)
        print(f"level {e}: {len(raw)} raw -> {len(lines)} lines", flush=True)
    print(f"TOTAL lines={total_lines} points={total_pts}", flush=True)
    if total_pts > 700000:
        print("WARNING: over 700k point budget", flush=True)
    json.dump(contours, open(f"{OUT}/contours.json", "w"))
    print("contours saved", flush=True)


if __name__ == "__main__":
    main()
