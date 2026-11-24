"""J29: parsing a long list takes time quadratic in its length (fixed in v5, #975).

`--x=<json list>` for `type=list[str]` with 1000, 2000 and 4000 items.
REPRODUCED if doubling the length costs more than 3x.
Expected: 4.51, 4.53 REPRODUCED (about 4x per doubling, about 3 CPU s at 4000);
5.0.0rc2 NOT REPRODUCED (about 2x, well under 0.1 s).
Needs: jsonargparse only.
"""
import json
import time
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

print("jsonargparse", jsonargparse.__version__)
t = {}
for n in (1000, 2000, 4000):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--x", type=list[str])
    arg = "--x=" + json.dumps([f"item{i}" for i in range(n)])
    t0 = time.process_time()
    p.parse_args([arg])
    t[n] = time.process_time() - t0
    print(f"  {n:5} items: {t[n]:.3f} CPU s")
ratio = t[4000] / max(t[2000], 1e-3)
print(f"  4000/2000 = {ratio:.1f}x")
print("RESULT:", "REPRODUCED" if ratio > 3 else "NOT REPRODUCED")
