"""J36: `dict[tuple[str, str], float]` keys stay strings, and a dumped
tuple-key default can't be reloaded.

Expected (from the existing tracker; first run here): keys are not converted to
tuples and any string is accepted as a key (REPRODUCED).
Needs: jsonargparse only.
"""
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_argument("--r", type=dict[tuple[str, str], float], default={("a", "b"): 1.0})
try:
    v = p.parse_string("r:\n  '[a, b]': 2.0\n  not-a-tuple: 3.0\n").r
    print("  YAML keys '[a, b]' and 'not-a-tuple' ->", v, "key types:", sorted({type(k).__name__ for k in v}))
    strkeys = any(isinstance(k, str) for k in v)
except Exception as e:
    strkeys = False
    print("  YAML string keys rejected:", " ".join(str(e).split())[:80])
try:
    d = p.dump(p.parse_args([]))
    print("  default dump:", " | ".join(d.splitlines()))
    p.parse_string(d)
    reload = "OK"
except Exception as e:
    reload = "FAIL " + " ".join(str(e).split())[:70]
print("  reload of default dump:", reload)
print("RESULT:", "REPRODUCED" if strkeys or reload != "OK" else "NOT REPRODUCED")
