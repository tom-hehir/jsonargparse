"""J12: error messages bury the cause.

  1. a typo key three dataclasses deep (subclass mode on): the cause
     ("Option 'lrr' is not accepted") is the last of several
     "Problem with given class_path '...'" lines naming plain dataclasses
  2. a missing module inside `list[Base] | Base | None`: the value is printed
     more than once and every union arm is listed
  3. `add_subclass_arguments` on a dataclass with subclass mode off: the message
     names neither the cause nor the fix
Prints the length and the line on which the cause first appears.

Expected: 4.51 and 4.53 alike; 5.0.0rc2 shortens case 2 a little and adds a
`Source:` line, cases 1 and 3 are unchanged (REPRODUCED on all).
Needs: jsonargparse only.
"""
import json
import subprocess
import sys
import warnings
from dataclasses import dataclass, field
from typing import Optional, Union

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings

CASE = sys.argv[1] if len(sys.argv) > 1 else None


@dataclass
class L3:
    lr: float = 0.1


@dataclass
class L2:
    l3: L3 = field(default_factory=L3)


@dataclass
class L1:
    l2: L2 = field(default_factory=L2)


@dataclass
class Root:
    l1: L1 = field(default_factory=L1)


class Callback:
    def __init__(self, k: int = 1): ...


def report(err, needle):
    lines = str(err).splitlines()
    at = next((i + 1 for i, line in enumerate(lines) if needle in line), None)
    print(f"  {CASE}: {len(str(err))} chars, {len(lines)} lines, cause on line {at}: {lines[at - 1].strip()[:70] if at else '-'}")


if CASE == "1":
    set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(Root, "r")
    try:
        p.parse_object({"r": {"l1": {"l2": {"l3": {"lrr": 1}}}}})
    except Exception as e:
        report(e, "lrr")
        n = str(e).count("Problem with given class_path")
        print(f"     'Problem with given class_path' lines for plain dataclasses: {n}")
elif CASE == "2":
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--cb", type=Optional[Union[list[Callback], Callback]])
    val = [{"class_path": "__main__.Callback"}, {"class_path": "missing_pkg.mod.Thing"}]
    try:
        p.parse_args(["--cb", json.dumps(val)])
    except Exception as e:
        report(e, "missing_pkg")
        print("     value printed", str(e).count("missing_pkg.mod.Thing"), "times")
elif CASE == "3":
    p = ArgumentParser(exit_on_error=False)
    try:
        p.add_subclass_arguments(L3, "x")
    except Exception as e:
        report(e, "dataclass")
        print("     message:", str(e)[:110])
else:
    print("jsonargparse", jsonargparse.__version__)
    outs = [subprocess.run([sys.executable, __file__, c], capture_output=True, text=True).stdout.rstrip() for c in "123"]
    print("\n".join(outs))
    bad = "plain dataclasses: 0" not in outs[0]
    print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
