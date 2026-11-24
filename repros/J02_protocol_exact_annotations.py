"""J02: Protocol matching compares annotations with `==`, so jaxtyping
annotations never match, and `nn.Module` implementers need `-> Any`.

jaxtyping builds a new class on every subscription, so
`Float[Tensor, "b d"] == Float[Tensor, "b d"]` is False. A Protocol with a
jaxtyped parameter can therefore never be implemented by a class that writes the
same annotation itself. A Module is matched on the untyped `nn.Module.__call__`,
so it passes only when the Protocol's return is `Any`.

Rows:
  a. non-Module class, jaxtyped arg written separately, Protocol `-> Any`
  b. same, but both use one shared alias object (workaround)
  c. `nn.Linear` vs Protocol `(x: Tensor) -> Tensor`
  d. `nn.Linear` vs Protocol `(x: Tensor) -> Any` (workaround)

Expected: a FAIL on 4.51, 4.53, 5.0.0rc2; b OK on all; c OK on 4.51, FAIL on
4.53 and 5.0.0rc2; d OK on all. REPRODUCED everywhere (row a).
Needs: torch, jaxtyping.
"""
import json
import warnings
from typing import Any, Protocol

warnings.simplefilter("ignore")
import jsonargparse
from jaxtyping import Float
from jsonargparse import ArgumentParser
from torch import Tensor

Emb = Float[Tensor, "b d"]


class PFresh(Protocol):
    def __call__(self, x: Float[Tensor, "b d"]) -> Any: ...


class ImplFresh:
    def __call__(self, x: Float[Tensor, "b d"]) -> Any: ...


class PShared(Protocol):
    def __call__(self, x: Emb) -> Any: ...


class ImplShared:
    def __call__(self, x: Emb) -> Any: ...


class PTensor(Protocol):
    def __call__(self, x: Tensor) -> Tensor: ...


class PAny(Protocol):
    def __call__(self, x: Tensor) -> Any: ...


LIN = {"class_path": "torch.nn.Linear", "init_args": {"in_features": 2, "out_features": 3}}
rows = [
    ("a. jaxtyped arg, separate annotations, -> Any", PFresh, {"class_path": "__main__.ImplFresh"}),
    ("b. jaxtyped arg, shared alias, -> Any", PShared, {"class_path": "__main__.ImplShared"}),
    ("c. nn.Linear vs Protocol -> Tensor", PTensor, LIN),
    ("d. nn.Linear vs Protocol -> Any", PAny, LIN),
]
print("jsonargparse", jsonargparse.__version__)
res = {}
for label, proto, spec in rows:
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--f", type=proto)
    try:
        p.parse_args(["--f", json.dumps(spec)])
        res[label[0]] = "OK"
        print(f"  OK   {label}")
    except Exception as e:
        res[label[0]] = "FAIL"
        print(f"  FAIL {label}  {' '.join(str(e).split())[:90]}")
print("RESULT:", "REPRODUCED" if res["a"] == "FAIL" else "NOT REPRODUCED",
      "(row c:", res["c"] + ")")
