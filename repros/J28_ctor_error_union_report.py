"""J28: a constructor's exception inside an `X | None` field is reported as
"Does not validate against any of the Union subtypes" (fixed in v5, #1015).

On 4.x the real exception is only the `__cause__`; projects match the message
prefix to unwrap it. v5 raises the constructor's own exception, so such
unwrapping code becomes dead (and a test asserting the prefix fails).

Expected: 4.51, 4.53 wrapped (REPRODUCED); 5.0.0rc2 the ValueError itself
(NOT REPRODUCED).
Needs: jsonargparse only.
"""
import json
import warnings
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


class Base: ...


class Bad(Base):
    def __init__(self, n: int = 1):
        if n < 0:
            raise ValueError("n must be non-negative")


class Holder:
    def __init__(self, b: Optional[Base] = None): ...


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(Holder, "h")
ns = p.parse_args(["--h.b", json.dumps({"class_path": "__main__.Bad", "init_args": {"n": -1}})])
try:
    p.instantiate(ns)
except Exception as e:
    msg = str(e)
    print(f"  {type(e).__name__} ({len(msg)} chars): {msg.splitlines()[0][:80]}")
    print(f"  __cause__: {type(e.__cause__).__name__ if e.__cause__ else None}")
    print("RESULT:", "REPRODUCED" if msg.startswith("Does not validate against any of the Union subtypes") else "NOT REPRODUCED")
