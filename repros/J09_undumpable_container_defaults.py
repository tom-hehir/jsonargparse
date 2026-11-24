"""J09: defaults that are lists/tuples/dicts of dataclass instances dump as
"Unable to serialize instance ..." text, which does not reload.

A single dataclass default dumps as a mapping, but the same instance inside a
container goes through the import-path serializer, which writes the text and only
emits a `JsonargparseWarning`. An untyped `dict` holding an instance makes `dump`
raise instead.

Expected: 4.51, 4.53, 5.0.0rc2: list/tuple/dict rows write the text and fail
to reload (REPRODUCED); the single default is fine.
Needs: jsonargparse, pyyaml.
"""
import warnings
from dataclasses import dataclass, field

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclass
class Rule:
    pattern: str = "*"


FIELDS = {
    "single Rule": (Rule, lambda: Rule("one")),
    "list[Rule]": (list[Rule], lambda: [Rule("a.*")]),
    "tuple[Rule, ...]": (tuple[Rule, ...], lambda: (Rule("t"),)),
    "dict[str, Rule]": (dict[str, Rule], lambda: {"k": Rule("v")}),
    "dict (untyped)": (dict, lambda: {"k": Rule("v")}),
}
print("jsonargparse", jsonargparse.__version__)
bad = False
for label, (tp, factory) in FIELDS.items():
    W = dataclass(type("W", (), {"__annotations__": {"x": tp}, "x": field(default_factory=factory)}))
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(W, "w")
    try:
        text = p.dump(p.parse_args([]))
    except Exception as e:
        print(f"  {label:18} dump raises {type(e).__name__}")
        continue
    try:
        p.parse_string(text)
        reload = "reload OK"
    except Exception:
        reload = "reload FAIL"
    unser = "Unable to serialize" in text
    bad |= unser
    print(f"  {label:18} {reload:11} {' | '.join(text.splitlines())[:70]}")
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
