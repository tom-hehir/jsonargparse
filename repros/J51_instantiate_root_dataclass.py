"""J51: `instantiate` does not build a dataclass added at the root with
`add_class_arguments(DC)` (no nested key); it does with a nested key.

Expected (first run here): root -> Namespace, nested -> DC. Intended behaviour
(the root has no key to put the instance under).
Needs: jsonargparse only.
"""
import warnings
from dataclasses import dataclass

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser


@dataclass
class DC:
    a: int = 1


print("jsonargparse", jsonargparse.__version__)
p = ArgumentParser(exit_on_error=False)
p.add_class_arguments(DC)
root = type(p.instantiate(p.parse_args([]))).__name__
q = ArgumentParser(exit_on_error=False)
q.add_class_arguments(DC, "c")
nested = type(q.instantiate(q.parse_args([])).c).__name__
print(f"  root add_class_arguments(DC): instantiate -> {root}; nested 'c': -> {nested}")
print("RESULT:", "REPRODUCED" if root != "DC" else "NOT REPRODUCED")
