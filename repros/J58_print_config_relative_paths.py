"""J58: `--print_config` writes relative paths as given (relative to the
working directory), but `--config` resolves relative paths against the config
file's directory, so `--print_config > other/x.yaml; --config other/x.yaml`
fails.

Expected (from a project report; first standalone run here): reload from
another directory fails on 4.51, 4.53, 5.0.0rc2 (REPRODUCED).
Needs: jsonargparse, pyyaml.
"""
import contextlib
import io
import os
import tempfile
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ActionConfigFile, ArgumentParser
from jsonargparse.typing import Path_fr


def mk():
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--config", action=ActionConfigFile)
    p.add_argument("--data", type=Path_fr)
    return p


os.chdir(tempfile.mkdtemp())
os.makedirs("inputs")
os.makedirs("saved")
open("inputs/x.txt", "w").write("x")
print("jsonargparse", jsonargparse.__version__)
buf = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.suppress(SystemExit):
    mk().parse_args(["--data", "inputs/x.txt", "--print_config"])
open("saved/run.yaml", "w").write(buf.getvalue())
print("  printed:", buf.getvalue().strip())
try:
    mk().parse_args(["--config", "saved/run.yaml"])
    r = "OK"
except Exception as e:
    r = "FAIL " + " ".join(str(e).split())[:80]
print("  --config saved/run.yaml:", r)
print("RESULT:", "REPRODUCED" if r != "OK" else "NOT REPRODUCED")
