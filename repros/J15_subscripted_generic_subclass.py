"""J15: a field typed with a subscripted generic (`Model[int]`) rejects the
`init_args` of a subclass.

Since #775 the parser for a subscripted generic is built from the subscripted
type, whatever the `class_path`, so a subclass's own parameter is "not accepted".
A plain `Model` annotation works. Fix branch: `fix-subscripted-generic-init-args`.

Expected: 4.51, 4.53, 5.0.0rc2: `Model[int]` rejects `depth` (REPRODUCED);
plain `Model` accepts it.
Needs: jsonargparse only.
"""
import warnings
from typing import Generic, Optional, TypeVar

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

T = TypeVar("T")


class Model(Generic[T]):
    def __init__(self, value: Optional[T] = None): ...


class IntModel(Model[int]):
    def __init__(self, depth: int = 1): ...


print("jsonargparse", jsonargparse.__version__)
res = {}
for label, tp in (("Model[int]", Model[int]), ("Model", Model)):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--model", type=tp)
    try:
        p.parse_args(["--model=__main__.IntModel", "--model.depth=2"])
        res[label] = "OK"
    except Exception as e:
        res[label] = "FAIL " + " ".join(str(e).split())[:80]
    print(f"  {label:11} {res[label]}")
print("RESULT:", "REPRODUCED" if res["Model[int]"] != "OK" else "NOT REPRODUCED")
