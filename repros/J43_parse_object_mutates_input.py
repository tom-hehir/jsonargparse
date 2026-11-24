"""J43: `parse_object` mutates list and dict containers of `class_path` specs in
the caller's input.

Each element of a `list[Base]` (or value of a `dict[str, Base]`) is replaced in
place by a Namespace. Single specs and dataclass sections are not touched.

Expected: 4.51, 4.53, 5.0.0rc2: list and dict inputs mutated (REPRODUCED).
Needs: jsonargparse only.
"""
import copy
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


class Base:
    def __init__(self, n: int = 1): ...


print("jsonargparse", jsonargparse.__version__)
spec = {"class_path": "__main__.Base", "init_args": {"n": 3}}
mutated = {}
for label, tp, d in (("single Base", Base, {"m": dict(spec)}),
                     ("list[Base]", list[Base], {"m": [dict(spec)]}),
                     ("dict[str, Base]", dict[str, Base], {"m": {"k": dict(spec)}})):
    before = copy.deepcopy(d)
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--m", type=tp)
    p.parse_object(d)
    mutated[label] = d != before
    print(f"  {label:16} mutated={d != before!s:5} after: {str(d)[:80]}")
print("RESULT:", "REPRODUCED" if mutated["list[Base]"] else "NOT REPRODUCED")
