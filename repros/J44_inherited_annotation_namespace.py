"""J44: an inherited dataclass's own fields are resolved in the base module's
namespace, so the same name bound to different classes in the two modules
resolves to the base module's class.

`checks_a.Checker(strict)` and `checks_b.Checker(other)` are different classes.
`base_cfg` imports `checks_b.Checker`; `run_cfg` imports `checks_a.Checker` and
defines `Config(BaseCfg)` with `checker: Checker | None`. jsonargparse reads that
field as `checks_b.Checker` and refuses `class_path: checks_a.Checker`. Same root
cause as J04 (`get_global_vars` merges the base's globals over the subclass's);
resolving each base's annotations in its own module fixes both.

Expected: 4.51, 4.53, 5.0.0rc2: valid class_path refused (REPRODUCED).
Needs: jsonargparse only.
"""
import json
import sys
import tempfile
import textwrap
import warnings
from pathlib import Path

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

tmp = Path(tempfile.mkdtemp())
(tmp / "checks_a.py").write_text("class Checker:\n    def __init__(self, strict: bool = False): ...\n")
(tmp / "checks_b.py").write_text("class Checker:\n    def __init__(self, other: int = 0): ...\n")
(tmp / "base_cfg.py").write_text(textwrap.dedent("""
    from __future__ import annotations
    from dataclasses import dataclass
    from checks_b import Checker

    @dataclass
    class BaseCfg:
        lr: float = 0.1
        base_checker: Checker | None = None
"""))
(tmp / "run_cfg.py").write_text(textwrap.dedent("""
    from __future__ import annotations
    from dataclasses import dataclass
    from checks_a import Checker
    from base_cfg import BaseCfg

    @dataclass
    class Config(BaseCfg):
        checker: Checker | None = None
"""))
sys.path.insert(0, str(tmp))
import run_cfg  # noqa: E402

print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(run_cfg.Config, "c")
try:
    v = p.parse_args(["--c.checker", json.dumps({"class_path": "checks_a.Checker"})]).c.checker
    r = f"accepted {v.class_path}"
except Exception as e:
    r = "refused: " + " ".join(str(e).split())[:90]
print("  checker: class_path checks_a.Checker ->", r)
print("RESULT:", "REPRODUCED" if r.startswith("refused") else "NOT REPRODUCED")
