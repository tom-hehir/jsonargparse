"""J60: with `set_parsing_settings(unset_sentinel=True)`, `--help` shows every
required option as "(required, type: ..., default: Unset)": the sentinel is
printed as if it were a default value. Cosmetic.

Expected: 4.53, 5.0.0rc2, main 670f094: "default: Unset" shown (REPRODUCED).
Default settings: "(required, type: int)".
Needs: jsonargparse only.
"""
import warnings
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings


class Model:
    def __init__(self, width: int, depth: Optional[int], bias: bool = True):
        """
        Args:
            width: units per layer
            depth: layers, or None for adaptive
            bias: whether to add a bias
        """


print("jsonargparse", jsonargparse.__version__)
set_parsing_settings(unset_sentinel=True)
p = ArgumentParser(prog="demo", exit_on_error=False)
p.add_class_arguments(Model, "model")
lines = [" ".join(line.split()) for line in p.format_help().splitlines()]
shown = [line for line in lines if "required" in line]
for line in shown:
    print(" ", line)
print("RESULT:", "REPRODUCED" if any("default: Unset" in line for line in shown) else "NOT REPRODUCED")
