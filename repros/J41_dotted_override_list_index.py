"""J41: dotted overrides and `link_arguments` can't reach list entries, and links
can't reach dict entries.

`--m.l.0.init_args.y=3` for `l: list[Base]` fails; `--m.d.k.init_args.y=3` for
`d: dict[str, Base]` works on the command line, but `link_arguments` to either
target fails.

Expected: 4.51, 4.53, 5.0.0rc2 identical (REPRODUCED).
Needs: jsonargparse, pyyaml.
"""
import os
import tempfile
import warnings

warnings.simplefilter("ignore")
import jsonargparse
import yaml
from jsonargparse import ActionConfigFile, ArgumentParser


class Base:
    def __init__(self, x: int = 0, y: int = 0): ...


class M:
    def __init__(self, l: list[Base], d: dict[str, Base], src: int = 0): ...


os.chdir(tempfile.mkdtemp())
spec = {"class_path": "__main__.Base", "init_args": {"x": 1}}
yaml.safe_dump({"m": {"l": [spec, spec], "d": {"k": spec}}}, open("base.yaml", "w"))


def mk():
    p = ArgumentParser(exit_on_error=False)
    p.add_argument("--config", action=ActionConfigFile)
    p.add_class_arguments(M, "m")
    return p


def link_parse(target):
    p = mk()
    p.link_arguments("m.src", target, apply_on="parse")
    p.parse_args(["--config", "base.yaml", "--m.src=9"])


def attempt(fn):
    try:
        fn()
        return "OK"
    except Exception as e:
        return "FAIL " + " ".join(str(e).split())[:60]


print("jsonargparse", jsonargparse.__version__)
r = {
    "--m.l.0.init_args.y=3": attempt(lambda: mk().parse_args(["--config", "base.yaml", "--m.l.0.init_args.y=3"])),
    "--m.d.k.init_args.y=3": attempt(lambda: mk().parse_args(["--config", "base.yaml", "--m.d.k.init_args.y=3"])),
    "link -> m.l.0.init_args.y": attempt(lambda: link_parse("m.l.0.init_args.y")),
    "link -> m.d.k.init_args.y": attempt(lambda: link_parse("m.d.k.init_args.y")),
}
for k, v in r.items():
    print(f"  {k:28} {v}")
print("RESULT:", "REPRODUCED" if r["--m.l.0.init_args.y=3"] != "OK" else "NOT REPRODUCED")
