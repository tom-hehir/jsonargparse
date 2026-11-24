"""J54: a `list[str]` field can't be given as a path to a file holding the list.

Expected (first run here): the path is rejected (or taken literally) without
`sub_configs=True`; with `sub_configs=True` the file is loaded. Prints both.
Needs: jsonargparse, pyyaml.
"""
import os
import tempfile
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

os.chdir(tempfile.mkdtemp())
open("names.yaml", "w").write("- alpha\n- beta\n")
print("jsonargparse", jsonargparse.__version__)
res = {}
for sub in (False, True):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--names", type=list[str], sub_configs=sub)
    try:
        res[sub] = repr(p.parse_args(["--names", "names.yaml"]).names)
    except Exception as e:
        res[sub] = "rejected: " + " ".join(str(e).split())[:60]
    print(f"  sub_configs={sub!s:5} --names names.yaml -> {res[sub]}")
print("RESULT:", "REPRODUCED" if "alpha" not in res[False] else "NOT REPRODUCED",
      "(works with sub_configs=True)" if "alpha" in res[True] else "")
