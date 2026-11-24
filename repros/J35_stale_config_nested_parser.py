"""J35: with a parser subclass that adds `--config` in `__init__`, any nested
class with a `config` parameter fails.

jsonargparse builds nested parsers from `parent.__class__`, so the subclass's
`__init__` runs again and adds `--config`; the action is then removed from
`_actions` but not from `_option_string_actions`, which clashes. LightningCLI's
parser is not exposed (it adds `--config` after construction).

Expected: 4.51, 4.53, 5.0.0rc2: "argument '--config' already exists"
(REPRODUCED); a plain ArgumentParser works.
Needs: jsonargparse only.
"""
import warnings
from typing import Optional

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ActionConfigFile, ArgumentParser


class Inner:
    def __init__(self, config: Optional[dict] = None, width: int = 3): ...


class Outer:
    def __init__(self, inner: Inner): ...


class Enhanced(ArgumentParser):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.add_argument("--config", action=ActionConfigFile)


print("jsonargparse", jsonargparse.__version__)
res = {}
for cls in (ArgumentParser, Enhanced):
    p = cls(exit_on_error=False)
    try:
        p.add_class_arguments(Outer, "outer")
        p.parse_args(["--outer.inner.width=4"])
        res[cls.__name__] = "OK"
    except Exception as e:
        res[cls.__name__] = "FAIL " + " ".join(str(e).split())[-70:]
    print(f"  {cls.__name__:14} {res[cls.__name__]}")
print("RESULT:", "REPRODUCED" if res["Enhanced"] != "OK" else "NOT REPRODUCED")
