"""J31: with `stubs_resolver_allow_py_files=True`, sklearn's `Ridge` registers
zero parameters.

The stubs resolver reads `sklearn/linear_model/_ridge.py`, treats every
assignment (including function-local ones) as an alias, and
`add_module_aliases` recurses with `skip={name}`, which only breaks 1-cycles.
The RecursionError is logged at DEBUG level and the class silently ends up with
no parameters. Tested fix: `skip=skip | {name}`.

Expected: 4.51, 4.53, 5.0.0rc2: 8 parameters by default, 0 with the setting
(REPRODUCED). Tested with scikit-learn 1.8.
Needs: scikit-learn.
"""
import subprocess
import sys
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import ArgumentParser, set_parsing_settings


def count():
    from sklearn.linear_model import Ridge
    p = ArgumentParser(exit_on_error=False)
    p.add_class_arguments(Ridge, "r")
    return len([a for a in p._actions if a.dest.startswith("r.")])


if sys.argv[1:] == ["stubs"]:
    set_parsing_settings(stubs_resolver_allow_py_files=True)
    print(count())
    sys.exit(0)
import sklearn  # noqa: E402

print("jsonargparse", jsonargparse.__version__, "sklearn", sklearn.__version__)
default = count()
stubs = int(subprocess.run([sys.executable, __file__, "stubs"], capture_output=True, text=True).stdout.strip() or -1)
print(f"  Ridge parameters, default: {default}; with stubs_resolver_allow_py_files=True: {stubs}")
print("RESULT:", "REPRODUCED" if stubs == 0 and default > 0 else "NOT REPRODUCED")
