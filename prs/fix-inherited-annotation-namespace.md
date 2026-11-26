# Fix dataclass fields resolved in the wrong module namespace with inheritance

Branch: `fix-inherited-annotation-namespace` (draft, not opened)

## What does this PR do?

For a dataclass that inherits from dataclasses of other modules, all using
`from __future__ import annotations`, two things go wrong.

1. When a base that is not the first one is in another module, the names that
   only that module has are not found, and every field of the class is left
   unvalidated (only a DEBUG log says so):

```python
# base_opts.py
from __future__ import annotations
from collections.abc import Callable

@dataclass
class ModelOpts:
    fn: Callable[[int], int] | None = None
    batch_size: int = 16

# run_opts.py
from __future__ import annotations
from base_opts import ModelOpts

@dataclass
class RunOpts:
    seed: int | None = None

@dataclass
class Opts(RunOpts, ModelOpts): ...

parser.add_class_arguments(Opts)
parser.parse_object({"batch_size": "sixteen"})  # accepted, should fail
```

With the bases swapped, the value is rejected.

2. When the modules of a subclass and of a base bind the same name to different
   classes, an inherited field is resolved in the wrong module. E.g. `Config`
   in `run_cfg` has a field `checker: Checker | None` with `Checker` imported
   from `checks_a`, while its base in `base_cfg` imports a different `Checker`
   from `checks_b`. The subclass's own field is read as `checks_b.Checker`, and
   `class_path: checks_a.Checker` is refused.

### Cause

`get_global_vars` merges the globals of a dataclass with the ones of its first
base, recursively, so the other bases are never consulted. The merge also lets
the base's names override the ones of the subclass. The annotations of all the
classes in the hierarchy were then resolved at once with that single namespace.

### Fix

Each class in the MRO resolves its own annotations with its own namespace
(`get_class_type_hints`), which is what `typing.get_type_hints` does by default,
and the bases merge is removed from `get_global_vars`. The per-module namespace
still includes the names of `TYPE_CHECKING` blocks, as before. This is the same
approach as taken for TypedDict keys inherited from other modules in #936.

### Testing

- `test_dataclass_inherit_different_module_second_base`: a second base whose
  module only has a name in a `TYPE_CHECKING` block; checks that it resolves and
  that the fields of the first base are validated. Fails on main.
- `test_dataclass_inherit_different_module_same_name`: a name defined in both
  modules resolves, for each field, to the one of the module defining the field.
  Fails on main.
- Both use a dataclass added to the existing helper module
  `different_module_type_checking.py`. Full suite passes (the two
  `test_argcomplete` failures are environmental and also fail on main).

### Notes for review

- `get_types` still calls `get_global_vars(obj)` for a class, which is now only
  used in the AST fallback path (that path can't handle a class anyway); the
  per-base call recomputes it for `obj` itself. I left it to keep the diff small.
- A base whose annotations can't be resolved still makes the whole class fall
  back to unvalidated fields (no per-field fallback here; that is a separate
  matter).
- Tests compare the resolved class by an attribute (`defined_in`), not identity,
  because `test_get_types_source_unavailable` removes the test module from
  `sys.modules`, so the module may be imported twice later in the same session.
- `git apply` to `v4` fails only because `v4` calls `get_type_hints` without
  `include_extras=True`; the same change applies by hand with that difference.
- Related: a separate PR (unevaluable annotation of one field disabling
  validation of the whole class) changes the class path of `get_types` too. If
  both are accepted, the per-field fallback there would naturally use the
  per-base namespaces introduced here, so this one is best merged first.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
