"""J37: three-state sentinels don't round-trip.

  a. a custom sentinel registered with `register_type` in `Sentinel | bool`:
     the sentinel's serializer is applied to every value, so `False` and `True`
     dump as the sentinel (silent data loss). `bool | Sentinel` is correct.
  b. `jsonargparse.Unset` as a default dumps as `jsonargparse._common.Unset`;
     5.0.0rc2 refuses to reload it (import path denylist).

Expected: a REPRODUCED on 4.51, 4.53, 5.0.0rc2; b reload OK on 4.x, FAIL on
5.0.0rc2.
Needs: jsonargparse only.
"""
import warnings
from dataclasses import dataclass
from typing import Union

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, Unset
from jsonargparse.typing import register_type


class InheritType:
    def __repr__(self):
        return "INHERIT"


INHERIT = InheritType()
register_type(InheritType, serializer=lambda v: "inherit",
              deserializer=lambda s: INHERIT if s == "inherit" else (_ for _ in ()).throw(ValueError(s)))


@dataclass
class SentinelFirst:
    x: Union[InheritType, bool] = INHERIT


@dataclass
class BoolFirst:
    x: Union[bool, InheritType] = INHERIT


print("jsonargparse", jsonargparse.__version__)
lost = False
for cls in (SentinelFirst, BoolFirst):
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(cls)
    ns = p.parse_args(["--x=false"])
    d = p.dump(ns).strip()
    back = p.parse_string(d).x
    lost |= back is not False
    print(f"  a. {cls.__name__:13} --x=false -> dump {d!r} -> reload {back!r}")
UnsetType = type(Unset)


@dataclass
class WithUnset:
    x: Union[UnsetType, bool] = Unset


p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(WithUnset)
d = p.dump(p.parse_args([]), skip_unset=False).strip()
try:
    r = "OK" if p.parse_string(d).x is Unset else "different value"
except Exception as e:
    r = "FAIL " + " ".join(str(e).split())[:70]
print(f"  b. Unset default dump {d!r} -> reload {r}")
print("RESULT:", "REPRODUCED" if lost else "NOT REPRODUCED", "(Unset reload fails)" if r != "OK" else "")
