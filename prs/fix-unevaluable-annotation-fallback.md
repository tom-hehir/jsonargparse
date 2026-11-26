# Fix a dataclass annotation that fails to evaluate leaving all fields unvalidated

Branch: `fix-unevaluable-annotation-fallback` (draft, not opened)

## What does this PR do?

Under `from __future__ import annotations`, a single dataclass field whose
annotation can't be evaluated makes every field of the dataclass fall back to
`Unvalidated`, e.g. with a quoted name inside `|` (`str | None` is a
`TypeError`):

```python
from __future__ import annotations

class Weights: ...

@dataclass
class Task:
    lr: float = 0.1
    weights: "Weights" | None = None

parser.add_class_arguments(Task, "task")
parser.parse_args(["--task.lr=abc"])  # accepted, should fail
```

Only a DEBUG log says why. For functions and methods the same annotation only
affects its own parameter.

### Cause

`get_types` resolves the annotations of a class all at once with
`typing.get_type_hints`, so one failure discards all of them. For functions
there is a fallback that evaluates each parameter from the source. For a class
that fallback can't work: it looks up `node.args` of the class definition, so
it raises `AttributeError`, which `evaluate_postponed_annotations` logs at
DEBUG, leaving every parameter as a string. (The dataclass branch of that
fallback was removed when Python 3.8 support was dropped, #752, once
`get_type_hints` could resolve them.)

### Fix

When `get_type_hints` fails for a class, its annotations are resolved one at a
time (`get_class_types_individually`), each with the names `get_type_hints`
would use, and a failure is kept as the exception for that field.
`evaluate_postponed_annotations` already skips parameters whose type is an
exception, so only those stay unresolved, and become `Unvalidated<...>` as
documented in "Unvalidated types".

### Testing

- `test_dataclass_unevaluable_annotation_only_affects_its_field`: a dataclass
  with a `"Weights" | None` field (in a base class, plus a field in the
  subclass) still validates the other fields, the failing one accepts any
  value, and the failure is in the debug log. Fails on main.
- Full suite passes (the two `test_argcomplete` failures are environmental and
  also fail on main); the changed lines are covered.

### Notes for review

- The affected field is still unvalidated, now `Unvalidated<'Weights' | None>`;
  it is not resolved. I didn't try to evaluate string elements inside `|`
  (e.g. resolving `"Weights"` before applying `|`): `typing.get_type_hints`
  rejects it too, and handling it would need rewriting the expression. Is that
  something you would want?
- Question: should falling back to `Unvalidated` for an annotation that
  failed to resolve warn instead of only logging at DEBUG? I didn't add one:
  the docs ("Unvalidated types") describe the DEBUG log as the place for the
  reason, and `warning` is otherwise used for runtime events (dumping,
  failing imports while listing subclasses). Happy to add one if you prefer.
- The per-field fallback re-evaluates annotations only on failure, so the
  success path is unchanged.
- `git apply` to `v4` fails only because `v4` calls `get_type_hints` without
  `include_extras=True`; the same change applies by hand.
- Related: a separate PR (dataclass bases from other modules resolved in the
  wrong namespace) changes the class path of `get_types` too, resolving each
  base in its own module. If that one is merged first, this fallback would be
  rebased to use each base's namespace instead of the class's; until then it
  uses the same namespace that the class-level `get_type_hints` call uses.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
