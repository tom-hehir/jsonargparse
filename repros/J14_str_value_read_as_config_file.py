"""J14: a string value that names an existing file is read as a config.

With `sub_configs=True` (LightningCLI sets it), a value for a parameter typed
`str | SomeDataclass` that names an existing file is loaded: a text file
becomes the parsed value (the file's contents replace the path), and a large
binary file is read into memory several times (parse and again in `dump`). A
plain `str` parameter added through a signature is not affected; a plain `str`
added directly with `add_argument(type=str, sub_configs=True)` is.

Rows (file `data.csv` containing "a,b\\n1,2\\n"):
  signature, `plain: str`            sub_configs False / True
  signature, `uni: str | D`          sub_configs False / True
  `add_argument(type=str, sub_configs=True)`
  `add_argument(type=os.PathLike | str, sub_configs=True)` (the workaround)

Expected: 4.51, 4.53, 5.0.0rc2: `uni` with sub_configs=True and the direct
`type=str` both return the file text (REPRODUCED); everything else returns
'data.csv'. Silent: no warning.
Needs: jsonargparse only.
"""
import dataclasses
import os
import tempfile
import warnings
from typing import Union

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclasses.dataclass
class D:
    x: int = 1


def f(plain: str = "", uni: Union[str, D] = ""): ...


os.chdir(tempfile.mkdtemp())
open("data.csv", "w").write("a,b\n1,2\n")
print("jsonargparse", jsonargparse.__version__)
read = []
for sub in (False, True):
    p = ArgumentParser(exit_on_error=False)
    p.add_function_arguments(f, "f", sub_configs=sub)
    for name in ("plain", "uni"):
        v = p.parse_args([f"--f.{name}=data.csv"]).f[name]
        print(f"  signature {name:5} sub_configs={sub!s:5} -> {v!r}")
        if v != "data.csv":
            read.append(name)
for label, tp in (("add_argument type=str", str), ("add_argument type=PathLike|str", Union[os.PathLike, str])):
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--path", type=tp, sub_configs=True)
    v = p.parse_args(["--path=data.csv"]).path
    print(f"  {label:34} -> {v!r}")
print("RESULT:", "REPRODUCED" if "uni" in read else "NOT REPRODUCED")
