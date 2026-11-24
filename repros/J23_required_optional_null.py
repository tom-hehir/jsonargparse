"""J23 (v5): a required `X | None` parameter (no default) cannot be given `null`.

v5 made Optional parameters without a default required (as the v4 deprecation
announced). But `check_required` (`_core.py:1398`) treats a value equal to the
`unset_sentinel` setting, `None` by default, as missing, so an explicit `null` is
reported as "the following arguments are required". With
`set_parsing_settings(unset_sentinel=True)` it works.

Rows: parse_object None, CLI `=null`, YAML `null`, class_path/init_args null,
and the same with `unset_sentinel=True` (separate process).
Expected: 4.51, 4.53 all OK (NOT REPRODUCED); 5.0.0rc2 all FAIL, OK with
`unset_sentinel=True` (REPRODUCED).
Needs: jsonargparse only.
"""
import json
import subprocess
import sys
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings

UNSET = sys.argv[1:] == ["unset"]
if UNSET:
    set_parsing_settings(unset_sentinel=True)


class Seq:
    def __init__(self, count: int | None, dim: int = 1): ...


class Holder:
    def __init__(self, seq: Seq): ...


def mk(cls, key):
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(cls, key)
    return p


if not UNSET:
    print("jsonargparse", jsonargparse.__version__)
cases = {
    "parse_object None": lambda: mk(Seq, "seq").parse_object({"seq": {"count": None}}),
    "--seq.count=null": lambda: mk(Seq, "seq").parse_args(["--seq.count=null"]),
    "YAML count: null": lambda: mk(Seq, "seq").parse_string("seq:\n  count: null\n"),
    "class_path init_args null": lambda: mk(Holder, "h").parse_args(
        ["--h.seq", json.dumps({"class_path": "__main__.Seq", "init_args": {"count": None}})]),
}
fails = 0
for label, fn in cases.items():
    try:
        fn()
        r = "OK"
    except Exception as e:
        fails += 1
        r = "FAIL " + " ".join(str(e).split())[-60:]
    print(f"  {'[unset_sentinel=True] ' if UNSET else ''}{label:26} {r}")
if UNSET:
    sys.exit(0)
print(subprocess.run([sys.executable, __file__, "unset"], capture_output=True, text=True).stdout.rstrip())
print("RESULT:", "REPRODUCED" if fails else "NOT REPRODUCED")
