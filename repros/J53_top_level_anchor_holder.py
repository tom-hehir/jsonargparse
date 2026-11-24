"""J53: a top-level key that only holds YAML anchors (`_anchors:`) is rejected,
so anchors have to be defined inside a real section.

Expected (first run here): "_anchors" not accepted on 4.51, 4.53, 5.0.0rc2
(REPRODUCED). v5 `__include__` doesn't address it.
Needs: jsonargparse, pyyaml.
"""
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


class M:
    def __init__(self, width: int = 1, depth: int = 1): ...


cfg = "_anchors:\n  w: &w 64\nm:\n  width: *w\n  depth: 2\n"
print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(M, "m")
try:
    r = f"accepted, width={p.parse_string(cfg).m.width}"
except Exception as e:
    r = "rejected: " + " ".join(str(e).split())[:70]
print("  config with top-level _anchors:", r)
print("RESULT:", "REPRODUCED" if r.startswith("rejected") else "NOT REPRODUCED")
