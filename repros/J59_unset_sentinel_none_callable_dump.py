"""J59: with `set_parsing_settings(unset_sentinel=True)`, a `None` in a
`Callable | None` or callable-Protocol `| None` field is dumped as the text
"Unable to serialize instance None", and the dump doesn't load back.

With the default settings `None` is the unset value, so it is never serialized
and is dumped as `null`. With `unset_sentinel=True`, `None` is a real value and
is serialized: the Callable arm of the union turns it into text
(`serialize_as_import_path`) instead of rejecting it, so the `None` arm is never
tried. Plain `int | None` is fine.

Expected: 4.53, 5.0.0rc2, main 670f094: `f` and `c` dumped as "Unable to
serialize instance None", reload fails (REPRODUCED). Default settings: `null`,
reload works.
Needs: jsonargparse only.
"""
import dataclasses
import warnings
from collections.abc import Callable
from typing import Optional, Protocol

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings


class Head:
    def __init__(self, *, d: int, width: int = 4): ...


class Factory(Protocol):
    def __call__(self, *, d: int) -> Head: ...


@dataclasses.dataclass
class Config:
    f: Optional[Factory] = None
    c: Optional[Callable[[int], Head]] = None
    n: Optional[int] = None


print("jsonargparse", jsonargparse.__version__)
try:
    set_parsing_settings(unset_sentinel=True)
except Exception as ex:
    print("  unset_sentinel not available:", ex)
    print("RESULT: NOT REPRODUCED")
    raise SystemExit
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(Config, "x")
dumped = p.dump(p.parse_args([]))
print("  dump:", " | ".join(dumped.splitlines()))
try:
    p.parse_string(dumped)
    reload = "reloads"
except Exception as ex:
    reload = "reload fails: " + " ".join(str(ex).split())[:70]
print(" ", reload)
print("RESULT:", "REPRODUCED" if "Unable to serialize instance None" in dumped else "NOT REPRODUCED")
