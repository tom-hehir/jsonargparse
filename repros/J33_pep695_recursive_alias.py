"""J33: a recursive PEP 695 `type` alias with a quoted self-reference (what
ruff's UP040 writes) doesn't work.

`type Nested[K, V] = dict[K, V | "Nested[K, V]"]` as `weights: Nested[str, float]`:
  4.51: read as untyped; `--c.weights.cross=1` gives a tuple `('cross', '1')`
  4.53, 5.0.0rc2: a nested dict `{"a": {"b": 1}}` is rejected
The unquoted self-reference works on 5.0.0rc2 and hits a RecursionError at
parser construction on 4.53. The `TypeAlias` spelling works for the dotted
override but leaves depth 2 unvalidated on all versions.

Expected: REPRODUCED on all three, with different symptoms.
Needs: Python 3.12+.
"""
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

type Nested[K, V] = dict[K, V | "Nested[K, V]"]


class C:
    def __init__(self, weights: Nested[str, float] = None): ...


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(C, "c")
out = {}
for label, args in (("--c.weights.cross=1", ["--c.weights.cross=1"]), ("nested JSON", ['--c.weights={"a": {"b": 1}}'])):
    try:
        out[label] = repr(p.parse_args(args).c.weights)
    except Exception as e:
        out[label] = "FAIL " + " ".join(str(e).split())[:60]
    print(f"  {label:20} {out[label]}")
bad = "tuple" in out["--c.weights.cross=1"] or "(" in out["--c.weights.cross=1"] or out["nested JSON"].startswith("FAIL")
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
