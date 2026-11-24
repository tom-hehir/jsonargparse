"""J40: `null` is accepted for a non-Optional field that has a default (null
means "unset"), but only from a config, not from the command line.

Control: `parse_object({"m": None})` for a *required* class-typed argument is
rejected. (An earlier note that it is silently accepted used a non-required
argument, where accepting None is expected.)

Expected: 4.51, 4.53, 5.0.0rc2: YAML `a: null` for `a: int = 3` accepted,
`--a=null` rejected (REPRODUCED); required `m=None` rejected.
Needs: jsonargparse only.
"""
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


class Model:
    def __init__(self, k: int = 1): ...


def attempt(fn):
    try:
        return f"accepted ({fn()!r})"
    except Exception:
        return "rejected"


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_argument("--a", type=int, default=3)
yaml_null = attempt(lambda: p.parse_string("a: null\n").a)
cli_null = attempt(lambda: p.parse_args(["--a=null"]).a)
q = ArgumentParser(exit_on_error=False)
q.add_argument("--m", type=Model, required=True)
obj_none = attempt(lambda: q.parse_object({"m": None}).m)
print(f"  a: int = 3, YAML a: null -> {yaml_null}; CLI --a=null -> {cli_null}")
print(f"  required --m: Model, parse_object m=None -> {obj_none}")
print("RESULT:", "REPRODUCED" if yaml_null.startswith("accepted") else "NOT REPRODUCED")
