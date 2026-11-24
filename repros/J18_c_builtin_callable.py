"""J18: C builtins such as `torch.log1p` are rejected for
`Callable[[Tensor], Tensor]` (since 4.52, by design), and the setting that fixes
it is ignored once the stubs resolver has been created.

`stubs_resolver_allow_py_files=True` lets the resolver find torch's stubs, but
`get_stubs_resolver()` caches the resolver at the first stub lookup, so setting it
after that has no effect.

Rows: default; setting enabled before any parse (fresh process); setting enabled
after a parse that needed stubs (same process).
Expected: 4.51 accepts all (NOT REPRODUCED); 4.53 and 5.0.0rc2: rejected,
accepted, rejected (REPRODUCED).
Needs: torch.
"""
import subprocess
import sys
import warnings
from collections.abc import Callable

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings
from torch import Tensor


def try_parse():
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--f", type=Callable[[Tensor], Tensor])
    try:
        p.parse_args(["--f=torch.log1p"])
        return "accepted"
    except Exception:
        return "rejected"


if sys.argv[1:] == ["before"]:
    set_parsing_settings(stubs_resolver_allow_py_files=True)
    print(try_parse())
    sys.exit(0)

print("jsonargparse", jsonargparse.__version__)
default = try_parse()
before = subprocess.run([sys.executable, __file__, "before"], capture_output=True, text=True).stdout.strip()
set_parsing_settings(stubs_resolver_allow_py_files=True)
after = try_parse()
print(f"  default settings:                       {default}")
print(f"  setting enabled before the first parse: {before}")
print(f"  setting enabled after a parse:          {after}")
print("RESULT:", "REPRODUCED" if default == "rejected" else "NOT REPRODUCED",
      "(late setting ignored)" if before == "accepted" and after == "rejected" else "")
