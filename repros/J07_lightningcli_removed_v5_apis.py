"""J07: LightningCLI (Lightning 2.6.x) calls jsonargparse APIs removed in v5.

`LightningCLI.__init__` calls `parser.add_instantiator(...)`; with
`load_from_checkpoint_support=False` it reaches `parser.instantiate_classes(...)`;
`SaveConfigCallback` and `_dump_config` pass `skip_none=False`. All three are gone
in v5, so a LightningCLI can't even be constructed. `--help` and
`--print_config` exit before that point, so they still work and give false
confidence.

Expected: 4.51, 4.53 OK (NOT REPRODUCED); 5.0.0rc2 AttributeError for both
variants (REPRODUCED). Lightning's open draft PR Lightning-AI/pytorch-lightning#22014
addresses it.
Needs: torch, lightning (tested with 2.6.5).
"""
import logging
import os
import warnings

warnings.simplefilter("ignore")
logging.disable(logging.WARNING)
os.environ.setdefault("JSONARGPARSE_DEPRECATION_WARNINGS", "off")
import jsonargparse
import lightning
import torch
from lightning.pytorch import LightningModule
from lightning.pytorch.cli import LightningCLI


class Tiny(LightningModule):
    def __init__(self, width: int = 2):
        super().__init__()
        self.layer = torch.nn.Linear(width, 1)


print("jsonargparse", jsonargparse.__version__, "lightning", lightning.__version__)
failed = False
for kw in ({}, {"load_from_checkpoint_support": False}):
    try:
        cli = LightningCLI(Tiny, run=False, args=["--model.width=3"], save_config_callback=None,
                           trainer_defaults={"accelerator": "cpu", "logger": False}, seed_everything_default=False, **kw)
        print(f"  OK   LightningCLI({kw or ''}) built {type(cli.model).__name__}")
    except Exception as e:
        failed = True
        print(f"  FAIL LightningCLI({kw or ''}) {type(e).__name__}: {str(e)[:100]}")
print("RESULT:", "REPRODUCED" if failed else "NOT REPRODUCED")
