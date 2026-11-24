"""J48: there is no public warning category to filter on.

Projects filter Lightning-triggered deprecation warnings by the private path
`jsonargparse._deprecated.JsonargparseDeprecationWarning` (in pytest
`filterwarnings`). That module is gone in v5, so pytest reports
"Failed to import filter module" and the filter silently does nothing. The top-
level package exports no warning class on either version.

Expected: 4.51, 4.53: private path imports (works, but private); 5.0.0rc2:
ModuleNotFoundError (REPRODUCED).
Needs: jsonargparse only.
"""
import importlib
import warnings

warnings.simplefilter("ignore")
import jsonargparse

print("jsonargparse", jsonargparse.__version__)
try:
    importlib.import_module("jsonargparse._deprecated").JsonargparseDeprecationWarning
    r = "imports"
except Exception as e:
    r = f"{type(e).__name__}"
public = [n for n in dir(jsonargparse) if "Warning" in n]
print(f"  jsonargparse._deprecated.JsonargparseDeprecationWarning: {r}")
print(f"  public warning classes in jsonargparse: {public}")
print("RESULT:", "REPRODUCED" if r != "imports" else "NOT REPRODUCED (private path still importable)")
