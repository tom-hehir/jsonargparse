"""J10: global parsing settings are not idempotent, have no public getter and no
scope.

  a. `set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])` twice
     raises on the second call.
  b. no public getter (only the private `jsonargparse._common.get_parsing_setting`).
  c. `register_type` twice with equal-but-new functions (a re-import does this):
     raises on 4.51 only; 4.53 and v5 replace.
  d. a parser built before the mode is enabled keeps its structure but follows
     the live global at parse time.

Expected: a and b REPRODUCED on 4.51, 4.53, 5.0.0rc2; c raises only on 4.51.
Needs: jsonargparse only.
"""
import warnings

warnings.simplefilter("ignore")
import jsonargparse
from jsonargparse import set_parsing_settings
from jsonargparse.typing import register_type

print("jsonargparse", jsonargparse.__version__)
set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])
try:
    set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])
    second = "OK"
except Exception as e:
    second = f"raises {type(e).__name__}: {str(e)[:80]}"
print("  a. second identical call:", second)
getters = [n for n in dir(jsonargparse) if "setting" in n.lower()]
print("  b. public names with 'setting':", getters)


class Thing:
    def __init__(self, v):
        self.v = v


register_type(Thing, lambda t: t.v, lambda v: Thing(v))
try:
    register_type(Thing, lambda t: t.v, lambda v: Thing(v))
    rt = "OK (replaced)"
except Exception as e:
    rt = f"raises {type(e).__name__}"
print("  c. register_type twice:", rt)
bad = second != "OK" and getters == ["set_parsing_settings"]
print("RESULT:", "REPRODUCED" if bad else "NOT REPRODUCED")
