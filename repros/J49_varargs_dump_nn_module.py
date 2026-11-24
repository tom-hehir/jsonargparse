"""J49 (v5): an `nn.Module` subclass without its own `__init__` dumps as
`init_args: {args: []}`.

v5 supports `*args` (#986), so the inherited `nn.Module.__init__(*args, **kwargs)`
shows up in every dump. It reloads and instantiates; it is noise in saved configs
and config diffs.

Expected: 4.51, 4.53 only `class_path` (NOT REPRODUCED); 5.0.0rc2 `args: []`
(REPRODUCED).
Needs: torch.
"""
import json
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser
from torch import nn


class Child(nn.Module):
    def forward(self, x):
        return x


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_argument("--m", type=nn.Module)
d = p.dump(p.parse_args(["--m", json.dumps({"class_path": "__main__.Child"})]))
print("  dump:", " | ".join(d.splitlines()))
print("RESULT:", "REPRODUCED" if "args" in d else "NOT REPRODUCED")
