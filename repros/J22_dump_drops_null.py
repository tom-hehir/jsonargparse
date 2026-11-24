"""J22: `dump()` drops explicit `null`s, so a reload gives the default.

`x: Optional[int] = 3` given `null`: the default dump omits `x`, the reload gives
3. `skip_unset=False` (accepted on 4.x and v5; v5 removed `skip_none`) keeps it.

Expected: 4.51, 4.53, 5.0.0rc2: default dump reloads 3 (REPRODUCED).
Needs: jsonargparse only.
"""
import warnings
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_argument("--x", type=Optional[int], default=3)
ns = p.parse_args(["--x=null"])
d1 = p.dump(ns)
d2 = p.dump(ns, skip_unset=False)
r1, r2 = p.parse_string(d1).x, p.parse_string(d2).x
print(f"  parsed x={ns.x!r}; dump() -> {d1.strip()!r} reloads x={r1!r}; dump(skip_unset=False) -> {d2.strip()!r} reloads x={r2!r}")
print("RESULT:", "REPRODUCED" if r1 == 3 else "NOT REPRODUCED")
