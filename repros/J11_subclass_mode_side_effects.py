"""J11: side effects of `subclasses_enabled=["is_pure_dataclass"]`.

With the mode on, a nested dataclass field becomes a subclass-typed argument:
  a. a section file (`--cfg.output section.yaml`) is read as an import path:
     "Unexpected import path format" (works with the mode off)
  b. `--help` lists none of the nested field options (`--cfg.output.path`)
  c. `dump` wraps every nested dataclass in `class_path`/`init_args`
Dotted overrides (`--cfg.output.path=x`) still work; an earlier report that
they break was not reproduced.

Runs each check with the mode off (in a subprocess) and on.
Expected: 4.51, 4.53, 5.0.0rc2: a, b, c with the mode on (REPRODUCED).
Needs: jsonargparse, pyyaml.
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import warnings
from dataclasses import dataclass, field

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings

MODE = sys.argv[1] if len(sys.argv) > 1 else None
if MODE == "on":
    set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])


@dataclass
class Output:
    path: str = "out"
    overwrite: bool = False


@dataclass
class Cfg:
    name: str = "x"
    output: Output = field(default_factory=Output)


def check():
    os.chdir(tempfile.mkdtemp())
    open("section.yaml", "w").write("path: fromsection\n")
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(Cfg, "cfg")
    out = {}
    try:
        p.parse_args(["--cfg.output", "section.yaml"])
        out["section file"] = "OK"
    except Exception as e:
        out["section file"] = "ERR " + str(e).splitlines()[0][:70]
    try:
        p.parse_args(["--cfg.output.path=x"])
        out["dotted"] = "OK"
    except Exception as e:
        out["dotted"] = "ERR " + str(e).splitlines()[0][:70]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.suppress(SystemExit):
        p.parse_args(["--help"])
    out["help lists --cfg.output.path"] = "--cfg.output.path" in buf.getvalue()
    out["dump has class_path"] = "class_path" in p.dump(p.parse_args([]))
    return out


if MODE:
    for k, v in check().items():
        print(f"  [{MODE:3}] {k}: {v}")
    sys.exit(0)

print("jsonargparse", jsonargparse.__version__)
for mode in ("off", "on"):
    r = subprocess.run([sys.executable, __file__, mode], capture_output=True, text=True)
    print(r.stdout.rstrip())
    if mode == "on":
        on = r.stdout
bad = "section file: ERR" in on and "lists --cfg.output.path: False" in on
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
