"""J08: parse time of nested `class_path` values grows exponentially with depth.

A chain of `Optional[Base]` parameters nested d levels deep, each level a
`class_path` spec. On 4.x the parse time grows by about 2.5x per level; on
v5 (#1036, merged 2026-11-23) it is linear. Real configs with 4-6 levels of
nesting took 17-35 CPU s on 4.53 and 3.8 s on 5.0.0rc2.

Prints CPU seconds per depth. REPRODUCED if depth 8 costs more than 20x
depth 4.
Expected: 4.51, 4.53 REPRODUCED (about 1-3 s at depth 8); 5.0.0rc2 NOT
REPRODUCED (well under 0.1 s).
Needs: jsonargparse only.
"""
import json
import time
import warnings
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


class Base: ...


class Node(Base):
    def __init__(self, a: Optional[Base] = None, b: Optional[Base] = None, width: int = 1): ...


def spec(d):
    init = {"width": d}
    if d:
        init["a"] = spec(d - 1)
    return {"class_path": "__main__.Node", "init_args": init}


print("jsonargparse", jsonargparse.__version__)
times = {}
for d in range(1, 9):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--m", type=Base)
    t = time.process_time()
    p.parse_args(["--m", json.dumps(spec(d))])
    times[d] = time.process_time() - t
    print(f"  depth {d}: {times[d]:.3f} CPU s")
ratio = times[8] / max(times[4], 1e-3)
print(f"  depth 8 / depth 4 = {ratio:.1f}x")
print("RESULT:", "REPRODUCED" if ratio > 20 else "NOT REPRODUCED")
