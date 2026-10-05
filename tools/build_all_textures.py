"""Descarga las texturas satelitales de todos los picos (salvo las ya hechas)."""
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))
from build_texture import build

PEAKS = ["everest", "k2", "kangchenjunga", "lhotse", "chooyu", "dhaulagiri",
         "manaslu", "nangaparbat", "annapurna", "gasherbrum1", "broadpeak",
         "gasherbrum2", "shishapangma"]

ok, fail = [], []
for pid in PEAKS:
    out = os.path.join("tex", pid + ".jpg")
    if os.path.exists(out) and os.path.getsize(out) > 100 * 1024:
        print(pid, "ya existe, salto", flush=True)
        ok.append(pid)
        continue
    t0 = time.time()
    try:
        build(pid)
        ok.append(pid)
        print("%s OK en %.0fs" % (pid, time.time() - t0), flush=True)
    except Exception as e:
        print("%s FALLO: %s" % (pid, e), flush=True)
        traceback.print_exc()
        fail.append(pid)
    time.sleep(5)

print("=" * 40)
print("OK (%d): %s" % (len(ok), ",".join(ok)))
print("FALLOS (%d): %s" % (len(fail), ",".join(fail)))
