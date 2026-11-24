"""J47: a `default_factory` dataclass whose `__post_init__` validates breaks
parser construction, with no context in the error.

`runtime: Runtime = field(default_factory=Runtime)` where `Runtime()` raises
because a required value is missing: `add_class_arguments` calls the factory to
build the default and raises the user's ValueError as is, so no flag can supply
the value, and `--help` fails too. Python's own `Job()` would fail the same way,
so the behaviour is defensible; the missing context ("while building the default
for Job.runtime") is the problem.

Expected: 4.51, 4.53, 5.0.0rc2: bare ValueError from `add_class_arguments`
(REPRODUCED).
Needs: jsonargparse only.
"""
import warnings
from dataclasses import dataclass, field
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclass
class Runtime:
    output_dir: Optional[str] = None

    def __post_init__(self):
        if self.output_dir is None:
            raise ValueError("output_dir is required")


@dataclass
class Job:
    runtime: Runtime = field(default_factory=Runtime)


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
try:
    p.add_class_arguments(Job, "job")
    r = "built"
except Exception as e:
    r = f"{type(e).__name__}: {e}"
print("  add_class_arguments(Job):", r)
ctx = "runtime" in r.replace("output_dir is required", "")
print("RESULT:", "REPRODUCED" if r != "built" and not ctx else "NOT REPRODUCED")
