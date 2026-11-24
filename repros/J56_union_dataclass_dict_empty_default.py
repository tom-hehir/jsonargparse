"""J56: a `Union[Dataclass, dict]` field whose default is an empty dict is
filled with the dataclass's defaults.

Shape of a third-party config class (a field typed `Union[QuantConfig, dict]`
with `default_factory=dict`): jsonargparse takes the dataclass arm for the empty
default and fills it, so the class receives a non-empty value it never asked for
(in our case this only triggered a warning in the library).

Expected (first run of this standalone form): filled on 4.51, 4.53, 5.0.0rc2
(REPRODUCED).
Needs: jsonargparse only.
"""
import json
import warnings
from dataclasses import dataclass, field
from typing import Optional, Union

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclass
class QuantConfig:
    bits: int = 4
    iters: int = 1


@dataclass
class AdapterConfig:
    r: int = 8
    quant: Union[QuantConfig, dict] = field(default_factory=dict)


class Model:
    def __init__(self, adapter: Optional[AdapterConfig] = None): ...


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(Model, "m")
ns = p.parse_args(["--m.adapter", json.dumps({"r": 16})])
q = ns.m.adapter.quant if not hasattr(ns.m.adapter, "init_args") else ns.m.adapter.init_args.quant
print("  adapter.quant after parse:", q)
print("RESULT:", "REPRODUCED" if q not in ({}, None) else "NOT REPRODUCED")
