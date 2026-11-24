"""J24: a class default for a Protocol-typed field, held inside a dataclass
default or a union with a dataclass, dumps as a bare import path; the first dump
omits the class's `init_args` and is not a fixpoint.

`sel: Choice = Choice()` where `Choice.discrete: Factory = Decoder` (a `__call__`
Protocol returning `Decoder`): the first dump writes `discrete: __main__.Decoder`;
reloading and dumping again writes `class_path` plus `init_args` (`width: 4`). A
later change of the code default then silently changes what the saved config
means. Same for `field: Factory | Choice = Decoder`. `Callable[..., Decoder]`
fields are normalized on the first dump.

Expected: 4.51, 4.53, 5.0.0rc2: both Protocol shapes not a fixpoint
(REPRODUCED); the Callable field is.
Needs: jsonargparse only.
"""
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings

set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])


class Decoder:
    def __init__(self, *, spec: int = 1, d: int = 8, width: int = 4): ...

    def __call__(self):
        return self


class Factory(Protocol):
    def __call__(self, *, spec: int, d: int) -> Decoder: ...


@dataclass(frozen=True)
class Choice:
    discrete: Factory = Decoder


@dataclass
class InDataclassDefault:
    sel: Choice = Choice()


@dataclass
class InUnion:
    head: Factory | Choice = Decoder


@dataclass
class WithCallable:
    head: Callable[..., Decoder] = Decoder


print("jsonargparse", jsonargparse.__version__)
fix = {}
for cls in (InDataclassDefault, InUnion, WithCallable):
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(cls, "m")
    d1 = p.dump(p.parse_args([]))
    d2 = p.dump(p.parse_string(d1))
    fix[cls.__name__] = d1 == d2
    print(f"  {cls.__name__:19} fixpoint={d1 == d2!s:5} dump1: {' | '.join(d1.splitlines())[:75]}")
print("RESULT:", "REPRODUCED" if not (fix["InDataclassDefault"] and fix["InUnion"]) else "NOT REPRODUCED")
