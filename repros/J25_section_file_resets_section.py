"""J25: a section file or inline mapping given to a parent group resets nullable
sections instead of merging (and, with subclass mode on, required ones too).

`add_class_arguments(Root, "trainer", sub_configs=True)`; base `a.yaml` sets
`{a: 1, b: 2}` in each section, overlay `b.yaml` sets only `{a: 5}`.
`--trainer a.yaml --trainer b.yaml` resets `b` to 0 in an `Optional[Section] = None`
section, while two whole-tree `--config` files, a dotted flag, or a per-section
file merge. v5 `__include__` in the overlay merges correctly.

Expected (subclass mode off): 4.51, 4.53, 5.0.0rc2: optional section b=0
(REPRODUCED), required section b=2.
Needs: jsonargparse, pyyaml.
"""
import os
import tempfile
import warnings
from dataclasses import dataclass
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
import yaml
from jsonargparse import ActionConfigFile, ArgumentParser


@dataclass
class Section:
    a: int = 0
    b: int = 0


@dataclass
class Root:
    req: Section
    opt: Optional[Section] = None


os.chdir(tempfile.mkdtemp())
yaml.safe_dump({k: {"a": 1, "b": 2} for k in ("req", "opt")}, open("a.yaml", "w"))
yaml.safe_dump({k: {"a": 5} for k in ("req", "opt")}, open("b.yaml", "w"))
yaml.safe_dump({"trainer": {k: {"a": 1, "b": 2} for k in ("req", "opt")}}, open("a_cfg.yaml", "w"))
yaml.safe_dump({"trainer": {k: {"a": 5} for k in ("req", "opt")}}, open("b_cfg.yaml", "w"))
print("jsonargparse", jsonargparse.__version__)
res = {}
for label, args in (("section files --trainer a --trainer b", ["--trainer", "a.yaml", "--trainer", "b.yaml"]),
                    ("whole-tree --config a --config b", ["--config", "a_cfg.yaml", "--config", "b_cfg.yaml"])):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--config", action=ActionConfigFile)
    p.add_class_arguments(Root, "trainer", sub_configs=True)
    c = p.parse_args(args).trainer
    res[label] = (c.req.b, c.opt.b)
    print(f"  {label:38} req.b={c.req.b} opt.b={c.opt.b}")
bad = res["section files --trainer a --trainer b"][1] == 0
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
