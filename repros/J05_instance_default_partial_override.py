"""J05: a plain-class instance default loses its values on a partial override.

`sampler: Sampler = field(default_factory=lambda: Sampler(fraction=0.2))` with a
plain (non-dataclass) `Sampler`. Overriding only `seed` builds
`Sampler(fraction=0.0, seed=3)`: the 0.2 from the default instance is silently
replaced by the class default. The default dump writes
"Unable to serialize instance <...>", which does not reload. `lazy_instance`
keeps 0.2.

Expected: 4.51, 4.53, 5.0.0rc2: instance default -> fraction 0.0 after the
override (REPRODUCED); lazy_instance -> 0.2.
Needs: jsonargparse only.
"""
import warnings
from dataclasses import dataclass, field

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, lazy_instance


class Sampler:
    def __init__(self, fraction: float = 0.0, seed: int = 0):
        self.fraction, self.seed = fraction, seed


@dataclass
class WithInstance:
    sampler: Sampler = field(default_factory=lambda: Sampler(fraction=0.2))


@dataclass
class WithLazy:
    sampler: Sampler = field(default_factory=lambda: lazy_instance(Sampler, fraction=0.2))


print("jsonargparse", jsonargparse.__version__)
got = {}
for cls in (WithInstance, WithLazy):
    for label, args in (("no override", []), ("--c.sampler.seed=3", ["--c.sampler.seed=3"])):
        p = ArgumentParser(exit_on_error=False)
        p.add_argument("--c", type=cls)
        ns = p.parse_args(args)
        s = p.instantiate(ns).c.sampler
        got[(cls.__name__, label)] = s.fraction
        print(f"  {cls.__name__:12} {label:20} fraction={s.fraction} seed={s.seed}")
    if cls is WithInstance:
        dump = p.dump(p.parse_args([]))
        print("  default dump:", " | ".join(dump.splitlines())[:100])
bad = got[("WithInstance", "--c.sampler.seed=3")] != 0.2
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
