"""J01: a Protocol whose `__call__` returns a class is read as a factory (4.52+).

A field typed with a callable Protocol (`__call__(...) -> Decoder`) or with
`Callable[[int], Decoder]` should accept a class whose *instances* implement the
call. Since 4.52 jsonargparse instead requires the class itself to be a subclass
of the return type, and rejects it, even when it is only the field's default.

Checks (subclass mode on, as our projects use it):
  1. a callable dataclass instance as the field default, `parse_args([])`
     (with such a default, every parse fails, whatever the arguments)
  2. the same class given as `class_path` (field without a default)
  3. `Callable[[int], Decoder]` given a class with callable instances (#1033)
  4. control: a class that is itself a factory (field without a default)

Expected: 4.51 all OK (NOT REPRODUCED); 4.52, 4.53, 5.0.0rc2 rows 1-3 FAIL with
"Expected '...' to be a subclass of Decoder" (REPRODUCED); row 4 OK everywhere.
The fix branch `fix-factory-protocol-instances` fixes rows 1-2, not row 3.
Needs: jsonargparse only.
"""
import json
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings

set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])


class Decoder: ...


class LinearDecoder(Decoder):
    def __init__(self, *, d: int, hidden: int = 8): ...


class DecoderFactory(Protocol):
    def __call__(self, *, d: int) -> Decoder: ...


@dataclass(kw_only=True)
class DecoderChoice:  # instances are DecoderFactory implementations
    default: DecoderFactory = LinearDecoder

    def __call__(self, *, d: int) -> Decoder:
        return self.default(d=d)


class Model:
    def __init__(self, decoder: DecoderFactory = DecoderChoice()): ...


class ModelNoDefault:
    def __init__(self, decoder: DecoderFactory | None = None): ...


class CallableInstances:
    def __init__(self, scale: float = 1.0): ...

    def __call__(self, x: int) -> Decoder: ...


def attempt(build, args):
    p = ArgumentParser(exit_on_error=False)
    build(p)
    try:
        p.parse_args(args)
        return "OK", ""
    except Exception as e:
        return "FAIL", " ".join(str(e).split())[:110]


rows = [
    ("default instance, parse_args([])", lambda p: p.add_class_arguments(Model, "m"), []),
    ("class_path of callable dataclass (no default)", lambda p: p.add_class_arguments(ModelNoDefault, "m"),
     ["--m.decoder", json.dumps({"class_path": "__main__.DecoderChoice"})]),
    ("Callable[[int], Decoder] <- callable-instance class", lambda p: p.add_argument("--f", type=Callable[[int], Decoder]),
     ["--f", json.dumps({"class_path": "__main__.CallableInstances"})]),
    ("control: class that is a factory (no default)", lambda p: p.add_class_arguments(ModelNoDefault, "m"),
     ["--m.decoder", json.dumps({"class_path": "__main__.LinearDecoder", "init_args": {"hidden": 4}})]),
]
print("jsonargparse", jsonargparse.__version__)
bad = False
for i, (label, build, args) in enumerate(rows):
    status, msg = attempt(build, args)
    print(f"  {status:4} {label}  {msg}")
    if i < 3 and status == "FAIL":
        bad = True
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
