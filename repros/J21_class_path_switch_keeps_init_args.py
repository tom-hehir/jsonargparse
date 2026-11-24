"""J21: changing `class_path` keeps the previous class's `init_args` that the new
class accepts, including values that were only the old class's defaults.

  a. default `OptA` (weight_decay default 0.0), config switches to `OptB`
     (weight_decay default 0.01) without init_args: OptB gets 0.0
     (the Adam -> AdamW `weight_decay=0` case)
  b. union field `LayerNormOpts | RMSNormOpts` with default instance
     `LayerNormOpts()` (eps 1e-5), config `class_path: RMSNormOpts`: RMSNormOpts
     gets eps 1e-5 instead of its own 1e-6. This is not the #968 leak (fixed in
     4.52); it is the same documented carry-over.
Documented (DOCUMENTATION.rst: changing class_path "discards the init_args that
the new class does not accept").

Expected: 4.51, 4.53, 5.0.0rc2: a gives 0.0, b gives 1e-05 (REPRODUCED).
Needs: jsonargparse, pyyaml.
"""
import json
import warnings
from dataclasses import dataclass, field

warnings.simplefilter("ignore")
import jsonargparse
import yaml
from jsonargparse import ArgumentParser, set_parsing_settings

set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])


class Opt:
    def __init__(self, lr: float = 1e-3): ...


class OptA(Opt):
    def __init__(self, lr: float = 1e-3, weight_decay: float = 0.0): ...


class OptB(Opt):
    def __init__(self, lr: float = 1e-3, weight_decay: float = 0.01): ...


class Model:
    def __init__(self, opt: Opt = {"class_path": "__main__.OptA"}): ...


@dataclass
class LayerNormOpts:
    eps: float = 1e-5


@dataclass
class RMSNormOpts:
    eps: float = 1e-6


@dataclass
class Block:
    norm: LayerNormOpts | RMSNormOpts = field(default_factory=LayerNormOpts)


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(Model, "m")
opt = yaml.safe_load(p.dump(p.parse_args(["--m.opt", json.dumps({"class_path": "__main__.OptB"})])))["m"]["opt"]
wd = opt["init_args"]["weight_decay"]
print(f"  a. default OptA -> class_path OptB: {opt['class_path']} weight_decay={wd} (OptB default 0.01)")
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(Block, "b")
norm = yaml.safe_load(p.dump(p.parse_args(["--b.norm", json.dumps({"class_path": "__main__.RMSNormOpts"})])))["b"]["norm"]
eps = norm["init_args"]["eps"]
print(f"  b. default LayerNormOpts() -> RMSNormOpts: eps={eps} (RMSNormOpts default 1e-06)")
print("RESULT:", "REPRODUCED" if wd == 0.0 or eps == 1e-5 else "NOT REPRODUCED")
