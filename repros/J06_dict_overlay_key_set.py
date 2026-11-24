"""J06: dict-typed fields in config overlays: the key set is replaced, the
surviving keys' values are merged, and the dotted CLI form merges everything.

Base config: `mods: {p: Net(x=1), q: Net(x=2)}`; overlay config:
`mods: {p: {init_args: {y: 9}}}`.
  * second `--config`: q is dropped, p keeps x=1 and gets y=9
  * dotted `--m.mods.p.init_args.y=9`: q kept
The per-key merge is not documented (DOCUMENTATION.rst only says a second dict
"replaces the previous value completely"). v5 `__include__` behaves like a
second config.

Expected: identical on 4.51, 4.53, 5.0.0rc2 (REPRODUCED).
Needs: jsonargparse, pyyaml.
"""
import os
import tempfile
import warnings

warnings.simplefilter("ignore")
import jsonargparse
import yaml
from jsonargparse import ActionConfigFile, ArgumentParser


class Net:
    def __init__(self, x: int = 0, y: int = 0): ...


class M:
    def __init__(self, mods: dict[str, Net]): ...


os.chdir(tempfile.mkdtemp())
yaml.safe_dump({"m": {"mods": {
    "p": {"class_path": "__main__.Net", "init_args": {"x": 1}},
    "q": {"class_path": "__main__.Net", "init_args": {"x": 2}}}}}, open("base.yaml", "w"))
yaml.safe_dump({"m": {"mods": {"p": {"init_args": {"y": 9}}}}}, open("over.yaml", "w"))


def run(args):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--config", action=ActionConfigFile)
    p.add_class_arguments(M, "m")
    mods = yaml.safe_load(p.dump(p.parse_args(args)))["m"]["mods"]
    return {k: v["init_args"] for k, v in mods.items()}


print("jsonargparse", jsonargparse.__version__)
two = run(["--config", "base.yaml", "--config", "over.yaml"])
dotted = run(["--config", "base.yaml", "--m.mods.p.init_args.y=9"])
print("  two configs :", two)
print("  dotted flag :", dotted)
bad = "q" not in two and two["p"].get("x") == 1 and "q" in dotted
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
