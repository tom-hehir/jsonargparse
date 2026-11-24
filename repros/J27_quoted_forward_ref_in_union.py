"""J27: one unevaluable annotation leaves every field of the class silently
unvalidated (4.51+); on 4.50 and earlier the parameter was dropped instead.

Under `from __future__ import annotations`, `weights: "Weights" | None` (a quoted
name inside `|`) can't be evaluated (`str | None` is a TypeError), although
`Weights` is importable. Since 4.51 the class's fields all fall back to
`Unvalidated` and accept anything, including `lr: "abc"`; 4.50 dropped the
parameter. Only a DEBUG log says so.

Expected: 4.51, 4.53, 5.0.0rc2: `weights: 7` and `lr: "abc"` accepted
(REPRODUCED).
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
(tmp / "task_mod.py").write_text(textwrap.dedent('''
    from __future__ import annotations
    from dataclasses import dataclass

    class Weights:
        def __init__(self, a: float = 1.0): ...

    @dataclass
    class Task:
        lr: float = 0.1
        weights: "Weights" | None = None
'''))
sys.path.insert(0, str(tmp))
import task_mod  # noqa: E402

print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(task_mod.Task, "t")
opts = [s for a in p._actions for s in a.option_strings if "weights" in s]
print("  options for weights:", opts or "none (parameter dropped)")
res = {}
for bad in ({"weights": 7}, {"lr": "abc"}):
    try:
        p.parse_object({"t": bad})
        res[str(bad)] = "accepted"
    except Exception:
        res[str(bad)] = "rejected"
    print(f"  {bad} -> {res[str(bad)]}")
r = res[str({"lr": "abc"})]
print("RESULT:", "REPRODUCED" if r == "accepted" or not opts else "NOT REPRODUCED")
