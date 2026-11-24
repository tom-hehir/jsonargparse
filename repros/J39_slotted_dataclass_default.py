"""J39: a `slots=True` dataclass instance as a default crashes parser
construction: `vars() argument must have __dict__ attribute` in
`convert_to_dict` (`_signatures.py`).

Fix (tested in a copy of v5): use `dataclasses.fields` when `__dict__` is absent.
Expected: 4.51, 4.53, 5.0.0rc2 TypeError (REPRODUCED). Not limited to 4.52.
Needs: jsonargparse only.
"""
import warnings
from dataclasses import dataclass, field

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclass(slots=True)
class S:
    a: int = 1


@dataclass
class W:
    x: S = field(default_factory=S)


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
try:
    p.add_class_arguments(W, "c")
    p.parse_args([])
    r = "OK"
except Exception as e:
    r = f"{type(e).__name__}: {e}"
print("  slotted default:", r)
print("RESULT:", "REPRODUCED" if r != "OK" else "NOT REPRODUCED")
