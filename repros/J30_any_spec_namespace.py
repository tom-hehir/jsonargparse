"""J30: a `class_path` spec inside an `Any` field is converted to a Namespace
and filled with defaults even when instantiation is off; and `parse_object`
mutates the input dict.

With `instantiate_subclass_spec_in_any=False` (v5's default), a spec inside `Any`,
`object` or `dict[str, Any]` is not built, but it is still turned into a
`Namespace` with every default filled; only `dict`, `dict | None` and
`Optional[dict]` pass the value through. The caller's dict is modified in place
(the spec inside it becomes a Namespace). Parsing the same dict again works here;
an earlier report that it fails came from a test that passed the inner dict at the
top level.

Expected: 4.51, 4.53 (setting off), 5.0.0rc2: `Any` -> Namespace, input mutated
(REPRODUCED); bare `dict` -> dict.
Needs: jsonargparse only.
"""
import copy
import warnings
from dataclasses import dataclass
from typing import Any

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings

try:
    set_parsing_settings(instantiate_subclass_spec_in_any=False)
except Exception:
    pass


class Opt:
    def __init__(self, lr: float = 0.1, betas: tuple = (0.9, 0.99), eps: float = 1e-8): ...


@dataclass
class WithAny:
    x: Any = None


@dataclass
class WithDict:
    x: dict = None


print("jsonargparse", jsonargparse.__version__)
res = {}
for cls in (WithAny, WithDict):
    d = {"opt": {"class_path": "__main__.Opt", "init_args": {"lr": 0.5}}}
    before = copy.deepcopy(d)
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(cls)
    ns = p.parse_object({"x": d})
    kind = type(ns.x["opt"]).__name__
    lines = len(p.dump(ns).splitlines())
    try:
        p.parse_object({"x": d})
        again = "OK"
    except Exception as e:
        again = "FAIL " + " ".join(str(e).split())[-45:]
    res[cls.__name__] = (kind, d != before)
    print(f"  {cls.__name__:8} value type={kind:9} dump lines={lines:2} input mutated={d != before!s:5} second parse of same dict: {again}")
print("RESULT:", "REPRODUCED" if res["WithAny"][0] == "Namespace" else "NOT REPRODUCED")
