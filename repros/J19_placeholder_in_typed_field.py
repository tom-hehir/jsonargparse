"""J19: no way to interpolate placeholders (`${N}`) before validation.

A `${N}` placeholder in an `int`/`float`/`bool` field is rejected in the default
parser mode, so projects build their own fill-then-reparse steps. omegaconf mode
resolves only config files (`omegaconf+` also CLI and `parse_object` values) and
needs every variable set, even for `--print_config`. `set_loader` is an existing
hook that can expand environment variables for config files.

Expected: 4.51, 4.53, 5.0.0rc2: `${N}` rejected (REPRODUCED); the custom
loader resolves it in a config string.
Needs: jsonargparse, pyyaml (omegaconf not needed).
"""
import os
import warnings

warnings.simplefilter("ignore")
import jsonargparse
import yaml
from jsonargparse import ArgumentParser, set_loader


class D:
    def __init__(self, workers: int = 1, lr: float = 0.1): ...


os.environ["N"] = "4"
print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(D, "d")
try:
    p.parse_string("d:\n  workers: ${N}\n")
    plain = "accepted"
except Exception as e:
    plain = "rejected: " + " ".join(str(e).split())[:60]
print("  default mode, config 'workers: ${N}':", plain)
set_loader("envyaml", lambda s: yaml.safe_load(os.path.expandvars(s)))
p2 = ArgumentParser(exit_on_error=False, parser_mode="envyaml")
p2.add_class_arguments(D, "d")
print("  custom set_loader with expandvars:", p2.parse_string("d:\n  workers: ${N}\n").d.workers)
print("RESULT:", "REPRODUCED" if plain != "accepted" else "NOT REPRODUCED")
