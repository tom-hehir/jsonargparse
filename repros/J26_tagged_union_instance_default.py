"""J26: a union of tagged dataclasses with an instance default rejects a value
for another member (since 4.50).

`--u` typed `A | B` with default `A()`; `{"type": "b", "x": 3}` is rejected
because #921 keeps the default's class while parsing, so every member is checked
against `A`. Works without the default and with dotted `--u.type=b`. Fix branch:
`fix-tagged-union-instance-default`.

Expected: 4.51, 4.53, 5.0.0rc2 FAIL (REPRODUCED); 4.49 OK (not run here).
Needs: jsonargparse only.
"""
import dataclasses
import warnings
from typing import Literal, Union

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclasses.dataclass
class A:
    type: Literal["a"] = "a"


@dataclasses.dataclass
class B:
    type: Literal["b"] = "b"
    x: int = 0


print("jsonargparse", jsonargparse.__version__)
res = {}
for label, kw in (("default A()", {"default": A()}), ("no default", {})):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--u", type=Union[A, B], **kw)
    try:
        res[label] = repr(p.parse_args(['--u={"type": "b", "x": 3}']).u)
    except Exception as e:
        res[label] = "FAIL " + " ".join(str(e).split())[:70]
    print(f"  {label:12} {res[label]}")
print("RESULT:", "REPRODUCED" if res["default A()"].startswith("FAIL") else "NOT REPRODUCED")
