# v5: a required parameter typed `X | None` can't be given `null`

Kind: issue (not a PR). Inventory: J23. No local branch: the fix needs a design
decision first (see "Possible directions").

## 🐛 Bug report

In v5, a signature parameter typed `X | None` without a default is required, as
the migration guide says ("they remain required"). But with the default
settings it can't be given the `None` its type allows: an explicit `null` is
reported as missing.

### To reproduce

```python
from jsonargparse import ArgumentParser


class Model:
    def __init__(self, count: int | None, dim: int = 1):
        self.count = count


parser = ArgumentParser(exit_on_error=False)
parser.add_class_arguments(Model, "model")

parser.parse_args(["--model.count=3"])     # Namespace(count=3, dim=1)
parser.parse_args(["--model.count=null"])  # ArgumentError: the following arguments are required: model.count
parser.parse_object({"model": {"count": None}})  # same error
```

The same happens for `count: null` in a config file, inside `init_args`, and
for nested dataclass fields. A config dumped with `skip_unset=False` that
writes `count: null` doesn't reload.

### Expected behavior

`null` is accepted, as it is for `Model(count=None)` in Python: the parameter
must be given, and `None` is one of its valid values. Omitting it should still
fail.

With `set_parsing_settings(unset_sentinel=True)` that is exactly what happens
(`null` gives `count=None`, omitting gives the "required" error), so the
behaviour already exists; it's the default that is inconsistent.

### Environment

- jsonargparse version: main (3b30c14) and 5.0.0rc2. On v4 (4.53.0 and the `v4`
  branch) both calls succeed, with the deprecation warning that such parameters
  will become required.
- Python version: 3.12
- How jsonargparse was installed: from source (`pip install .`)
- OS: macOS

### Cause

`check_required` compares values with the `unset_sentinel` setting, which is
`None` by default, so an explicit `None` counts as not given. This matches the
documented default ("an argument that is not given gets the value `None`... it
is impossible to tell apart", Unset values section), but in v5 it now meets
parameters that are both required and nullable, and for those the two
meanings can't share one value.

### Possible directions (for the maintainer to choose)

1. Use the `Unset` sentinel internally as the "not given" marker for required
   nullable parameters, whatever the global setting, so `None` stays a value.
2. Record that a key was given, separately from its value, in the required check.
3. If the current behaviour is kept: say in the migration guide entry and the
   deprecation message that `null` can't be given to such parameters unless
   `unset_sentinel=True` is set.

We tried flipping the `unset_sentinel` default locally; 111 upstream tests
fail, so (1) or (2) seem more contained than changing the default. Happy to
work on a PR once a direction is chosen.
