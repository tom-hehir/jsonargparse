"""J38: a function given as `class_path` is judged only by its return annotation.

For a field `b: Base`, a function returning `Base` or a subclass is accepted;
one returning a TypeVar bound to `Base`, `Any`, a broader type, or nothing
annotated is rejected, and the message doesn't say the return annotation was the
thing checked.

Expected: 4.51, 4.53, 5.0.0rc2 identical (REPRODUCED: the bound TypeVar is
rejected).
Needs: jsonargparse only.
"""
import json
import warnings
from typing import Any, TypeVar

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


class Base: ...


class Sub(Base): ...


TB = TypeVar("TB", bound=Base)


def f_exact() -> Base: ...
def f_narrow() -> Sub: ...
def f_typevar_bound(cls: type[TB] = Base) -> TB: ...
def f_any() -> Any: ...
def f_noann(): ...


class Holder:
    def __init__(self, b: Base): ...


print("jsonargparse", jsonargparse.__version__)
res = {}
for name in ("f_exact", "f_narrow", "f_typevar_bound", "f_any", "f_noann"):
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(Holder, "h")
    try:
        p.parse_args(["--h.b", json.dumps({"class_path": f"__main__.{name}"})])
        res[name] = "OK"
    except Exception as e:
        res[name] = "FAIL " + " ".join(str(e).split())[:70]
    print(f"  {name:16} {res[name]}")
print("RESULT:", "REPRODUCED" if res["f_typevar_bound"] != "OK" else "NOT REPRODUCED")
