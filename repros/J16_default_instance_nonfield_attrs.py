"""J16: a dataclass default instance with an attribute that is not an
`__init__` parameter is rejected under `Optional`, unions and subclass mode.

`convert_to_dict` builds `init_args` from `vars(value)`, so an attribute set in
`__post_init__` (public or `_`-prefixed) or a `field(init=False)` set there
becomes an unknown option. A plain dataclass-typed field without subclass mode is
fine. Fix branch: `fix-default-instance-non-field-attributes`.

Expected: 4.51, 4.53, 5.0.0rc2: plain OK, Optional FAIL "Option 'derived' is
not accepted" (REPRODUCED).
Needs: jsonargparse only.
"""
import warnings
from dataclasses import dataclass, field
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclass
class Pub:
    a: int = 1

    def __post_init__(self):
        self.derived = self.a * 2


@dataclass
class Plain:
    x: Pub = field(default_factory=Pub)


@dataclass
class Opt:
    x: Optional[Pub] = field(default_factory=Pub)


print("jsonargparse", jsonargparse.__version__)
res = {}
for cls in (Plain, Opt):
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(cls, "c")
    try:
        p.parse_args([])
        res[cls.__name__] = "OK"
    except Exception as e:
        res[cls.__name__] = "FAIL " + " ".join(str(e).split())[-60:]
    print(f"  {cls.__name__:6} {res[cls.__name__]}")
print("RESULT:", "REPRODUCED" if res["Opt"] != "OK" else "NOT REPRODUCED")
