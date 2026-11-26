"""J59: with `set_parsing_settings(unset_sentinel=True)`, a `None` in an
`X | None` field is dumped as text whenever another member of the union
serializes it: `Path`, `os.PathLike` and `timedelta` (serializer `str`) write
the bare text `None`, which reloads as the string `'None'` or fails; a Callable
or callable Protocol writes "Unable to serialize instance None".

With the default settings `None` is the unset value, so it is never serialized
and is dumped as `null`. With `unset_sentinel=True`, `None` is a real value and
is serialized: the union tries its members in order and the first one that
doesn't raise wins, so the `None` member is never reached. Plain `int | None`
and `str | None` are fine.

LightningCLI is affected through `Trainer(max_time=..., val_check_interval=...)`,
`ModelCheckpoint(dirpath=..., train_time_interval=...)` and `ckpt_path`, so a
saved `config.yaml` can't be re-run.

Expected: 4.51: only the Callable cases fine; 4.52, 4.53, 5.0.0rc2, main
670f094: all four dumped as text (REPRODUCED). Default settings: `null`,
reload works.
Fix: when the value is `None`, try the `None` member of the union first.
Needs: jsonargparse only.
"""
import dataclasses
import os
import warnings
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Optional, Protocol, Union

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings


class Head:
    def __init__(self, *, d: int, width: int = 4): ...


class Factory(Protocol):
    def __call__(self, *, d: int) -> Head: ...


@dataclasses.dataclass
class Config:
    path: Optional[Union[str, Path]] = None
    pathlike: Optional[os.PathLike] = None
    interval: Optional[timedelta] = None
    factory: Optional[Factory] = None
    fn: Optional[Callable[[int], Head]] = None
    n: Optional[int] = None
    s: Optional[str] = None


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
lines = [line.strip() for line in dumped.splitlines() if ":" in line and not line.startswith("x:")]
bad = [line for line in lines if not line.endswith(": null")]
print("  dump:", " | ".join(lines))
try:
    reloaded = p.parse_string(dumped)
    not_none = [k for k, v in vars(reloaded.x).items() if v is not None]
    reload = f"reloads; not None after reload: {not_none}" if not_none else "reloads as None"
except Exception as ex:
    reload = "reload fails: " + " ".join(str(ex).split())[:90]
print(" ", reload)
print("  dumped as text:", [line.split(":")[0] for line in bad])
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
