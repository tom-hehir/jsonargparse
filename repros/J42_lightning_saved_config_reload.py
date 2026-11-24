"""J42: a LightningCLI-saved `config.yaml` doesn't load as-is into a
`LightningCLI(run=False)`.

The saved config is flattened for the chosen subcommand, so it contains
subcommand-only keys (`ckpt_path`, `weights_only`); a `run=False` parser has no
subcommands and rejects them ("Option 'ckpt_path' is not accepted"). The script
writes a config with the same top-level keys a `fit` run saves.

Expected: 4.51, 4.53 rejected (REPRODUCED); 5.0.0rc2 blocked earlier by J07
(LightningCLI can't be constructed).
Needs: torch, lightning (tested with 2.6.5).
"""
import logging
import os
import tempfile
import warnings

warnings.simplefilter("ignore")
logging.disable(logging.WARNING)
os.environ.setdefault("JSONARGPARSE_DEPRECATION_WARNINGS", "off")
import jsonargparse
import torch
import yaml
from lightning.pytorch import LightningModule
from lightning.pytorch.cli import LightningCLI


class Tiny(LightningModule):
    def __init__(self, width: int = 2):
        super().__init__()
        self.layer = torch.nn.Linear(width, 1)


os.chdir(tempfile.mkdtemp())
yaml.safe_dump({"seed_everything": 0, "trainer": {"max_steps": 2}, "model": {"width": 3},
                "ckpt_path": None, "weights_only": None}, open("config.yaml", "w"))
print("jsonargparse", jsonargparse.__version__)
kw = dict(save_config_callback=None, trainer_defaults={"accelerator": "cpu", "logger": False})
try:
    LightningCLI(Tiny, run=False, args=["--model.width=3"], **kw)
except AttributeError as e:
    print("  LightningCLI itself fails (J07):", str(e)[:80])
    print("RESULT: NOT REPRODUCED (blocked by J07)")
    raise SystemExit(0)
try:
    cli = LightningCLI(Tiny, run=False, args=["--config", "config.yaml"], parser_kwargs={"exit_on_error": False}, **kw)
    r = "loaded"
except (Exception, SystemExit) as e:
    r = "rejected: " + " ".join(str(e).split())[:80]
print("  run=False --config <saved fit config>:", r)
print("RESULT:", "REPRODUCED" if r != "loaded" else "NOT REPRODUCED")
