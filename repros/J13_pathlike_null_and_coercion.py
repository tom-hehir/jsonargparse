"""J13: `os.PathLike` accepts and stringifies anything; a command-line `null`
for `os.PathLike | None` becomes the string "None".

`register_type(os.PathLike, str, str)` (`jsonargparse/typing.py`) makes the
deserializer `str`, and the PathLike arm is tried before `None`.

Expected: 4.51, 4.53, 5.0.0rc2: `--p=null` -> 'None', `--p=7` -> '7',
`--p=[a,b]` -> "['a', 'b']" (REPRODUCED). YAML `p: null` gives None (fine).
Needs: jsonargparse only.
"""
import os
import warnings
from typing import Optional, Union

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser

print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_argument("--p", type=Optional[Union[os.PathLike, str]])
got = {}
for args in (["--p=null"], ["--p=7"], ["--p=[a,b]"]):
    got[args[0]] = p.parse_args(args).p
    print(f"  {args[0]:12} -> {got[args[0]]!r}")
print(f"  {'YAML p: null':12} -> {p.parse_string('p: null').p!r}")
print("RESULT:", "REPRODUCED" if got["--p=null"] == "None" else "NOT REPRODUCED")
