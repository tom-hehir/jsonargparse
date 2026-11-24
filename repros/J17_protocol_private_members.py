"""J17: Protocol matching ignores `_`-prefixed members and has no variance.

  * a Protocol whose only member is `_encode` matches nothing
  * in a mixed Protocol the private member is not checked at all
  * `f(x: float | int)` does not implement `f(x: float)` (a wider argument),
    nor does `-> int` implement `-> float`, nor an unannotated `f(self, x)`
`get_protocol_members` skips names starting with `_` and `implements_protocol`
returns False when no members are left.

Expected: 4.51, 4.53, 5.0.0rc2 identical (REPRODUCED).
Needs: jsonargparse only.
"""
import json
import warnings
from typing import Protocol

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


class PPriv(Protocol):
    def _encode(self, x: int) -> int: ...


class CPriv:
    def _encode(self, x: int) -> int: ...


class PMixed(Protocol):
    def encode(self, x: int) -> int: ...
    def _decode(self, x: int) -> int: ...


class CNoPriv:
    def encode(self, x: int) -> int: ...


class PFloat(Protocol):
    def f(self, x: float) -> float: ...


class CWideArg:
    def f(self, x: float | int) -> float: ...


class CNarrowRet:
    def f(self, x: float) -> int: ...


class CNoAnn:
    def f(self, x): ...


cases = [("PPriv", PPriv, "CPriv", True), ("PMixed", PMixed, "CNoPriv", False),
         ("PFloat", PFloat, "CWideArg", True), ("PFloat", PFloat, "CNarrowRet", True), ("PFloat", PFloat, "CNoAnn", True)]
print("jsonargparse", jsonargparse.__version__)
diffs = 0
for pname, proto, cname, should in cases:
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--p", type=proto)
    try:
        p.parse_args(["--p", json.dumps({"class_path": f"__main__.{cname}"})])
        got = True
    except Exception:
        got = False
    diffs += got != should
    print(f"  {pname:7} <- {cname:11} accepted={got!s:5} static typing would: {should!s:5} {'' if got == should else '<< differs'}")
print("RESULT:", "REPRODUCED" if diffs else "NOT REPRODUCED")
