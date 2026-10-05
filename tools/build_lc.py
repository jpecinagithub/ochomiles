"""Carve official summit altitudes into DEM + generate land cover classes."""
import numpy as np

LON0, LAT0, LON1, LAT1 = 73.5, 27.0, 89.5, 36.5
W, H = 1600, 950
DX = (LON1 - LON0) / W
DY = (LAT1 - LAT0) / H
OUT = "/tmp/ochomiles_work"

PEAKS = {  # id: (lat, lon, official_alt)
    "everest": (27.9881, 86.9250, 8848.86), "k2": (35.8808, 76.5139, 8611.0),
    "kangchenjunga": (27.7025, 88.1475, 8586.0), "lhotse": (27.9617, 86.9330, 8516.0),
    "makalu": (27.8897, 87.0889, 8463.0), "chooyu": (28.0941, 86.6608, 8188.0),
    "dhaulagiri": (28.6967, 83.4931, 8167.0), "manaslu": (28.5497, 84.5597, 8163.0),
    "nangaparbat": (35.2372, 74.5892, 8126.0), "annapurna": (28.5956, 83.9372, 8091.0),
    "gasherbrum1": (35.7244, 76.6965, 8080.0), "broadpeak": (35.8106, 76.5653, 8047.0),
    "gasherbrum2": (35.7575, 76.6528, 8035.0), "shishapangma": (28.3526, 85.7792, 8027.0),
}


def cell(lat, lon):
    i = int(round((lon - LON0) / DX - 0.5))
    j = int(round((LAT1 - lat) / DY - 0.5))
    return j, i


def carve(dem, peaks, sigma):
    # highest first so lower peaks never touch higher terrain
    for pid, (lat, lon, alt) in sorted(peaks.items(), key=lambda kv: -kv[1][2]):
        j, i = cell(lat, lon)
        v0 = dem[j, i]
        r = 8
        j0, j1 = max(0, j - r), min(dem.shape[0], j + r + 1)
        i0, i1 = max(0, i - r), min(dem.shape[1], i + r + 1)
        jj, ii = np.mgrid[j0:j1, i0:i1]
        d2 = (jj - j) ** 2 + (ii - i) ** 2
        if alt > v0:
            bump = (alt - v0) * np.exp(-d2 / (2 * sigma ** 2))
            win = dem[j0:j1, i0:i1]
            # raise toward alt but never above alt, and never lower existing terrain
            win = np.minimum(win + bump, np.maximum(win, alt))
            dem[j0:j1, i0:i1] = win
            print(f"{pid}: cell=({i},{j}) {v0:.0f} -> {dem[j, i]:.1f} (official {alt})")
        else:
            print(f"{pid}: cell already {v0:.0f} >= {alt} (no carve)")


def main():
    dem = np.load(f"{OUT}/dem.npy")
    carve(dem, PEAKS, sigma=1.5)
    np.save(f"{OUT}/dem_final.npy", dem)

    # land cover with noise to avoid banding
    rng = np.random.default_rng(42)
    noise = (rng.random(dem.shape, dtype=np.float32) - 0.5) * 400.0
    e = dem + noise
    lc = np.full(dem.shape, 5, dtype=np.uint8)
    lc[e > 5600] = 1
    lc[(e > 4600) & (e <= 5600)] = 2
    lc[(e > 3600) & (e <= 4600)] = 3
    lc[(e > 2200) & (e <= 3600)] = 4
    np.save(f"{OUT}/lc.npy", lc)
    uniq, counts = np.unique(lc, return_counts=True)
    print("lc classes:", dict(zip(uniq.tolist(), counts.tolist())))

    # carve patch summits too (patch center = peak)
    patches = np.load(f"{OUT}/patches.npy", allow_pickle=True).item()
    for pid, p in patches.items():
        lat, lon, alt = PEAKS[pid]
        demp = p["dem"].astype(np.float64)
        h, w = demp.shape
        cj, ci = h // 2, w // 2
        # cap any overshoot from the earlier carve at the official altitude
        demp = np.minimum(demp, alt)
        p["dem"] = np.round(demp).astype(np.int32)
        print(f"patch {pid}: center {p['dem'][cj, ci]}, max {p['dem'].max()} (official {alt})")
    np.save(f"{OUT}/patches.npy", patches, allow_pickle=True)
    print("done")


if __name__ == "__main__":
    main()
