"""J04: a dataclass whose non-first base lives in another module (both using
`from __future__ import annotations`) loses validation for every field.

`get_global_vars` (`_postponed_annotations.py`) merges module globals only along
the first-base chain, so names that only the other base's module imports (here
`Callable`) can't be resolved, and all fields fall back to `Unvalidated`. Only a
DEBUG log is written; nothing warns.

Writes two small modules to a temp dir:
  base_opts.ModelOpts (imports Callable), run_opts.RunOpts,
  run_opts.SecondBase(RunOpts, ModelOpts)   <- other module's base second
  run_opts.FirstBase(ModelOpts, RunOpts)    <- control
and feeds invalid values.

Expected: 4.51, 4.53, 5.0.0rc2: SecondBase accepts all three bad values
(REPRODUCED); FirstBase rejects them.
Needs: jsonargparse only.
"""
import sys
import tempfile
import textwrap
import warnings
from pathlib import Path

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

tmp = Path(tempfile.mkdtemp())
(tmp / "base_opts.py").write_text(textwrap.dedent("""
    from __future__ import annotations
    from collections.abc import Callable
    from dataclasses import dataclass
    from typing import Literal

    @dataclass(kw_only=True)
    class ModelOpts:
        split: Literal["train", "val"] = "train"
        fn: Callable[[int], int] | None = None
        batch_size: int = 16
"""))
(tmp / "run_opts.py").write_text(textwrap.dedent("""
    from __future__ import annotations
    from dataclasses import dataclass
    from base_opts import ModelOpts

    @dataclass(kw_only=True)
    class RunOpts:
        seed: int | None = None

    @dataclass(kw_only=True)
    class SecondBase(RunOpts, ModelOpts):
        pass

    @dataclass(kw_only=True)
    class FirstBase(ModelOpts, RunOpts):
        pass
"""))
sys.path.insert(0, str(tmp))
import run_opts  # noqa: E402

print("jsonargparse", jsonargparse.__version__)
accepted = {}
for cls in (run_opts.FirstBase, run_opts.SecondBase):
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(cls)
    acc = []
    for bad in ({"batch_size": "sixteen"}, {"split": "banana"}, {"seed": [1, 2]}):
        try:
            p.parse_object(bad)
            acc.append(bad)
        except Exception:
            pass
    accepted[cls.__name__] = acc
    print(f"  {cls.__name__:10} invalid values accepted: {acc}")
print("RESULT:", "REPRODUCED" if accepted["SecondBase"] and not accepted["FirstBase"] else "NOT REPRODUCED")
