# Fix subscripted generic class types rejecting the init_args of a subclass

Branch: `fix-subscripted-generic-init-args` (draft, not opened)

## What does this PR do?

For a parameter typed with a subscripted generic class, a `class_path` naming a
subclass is parsed with the generic class's parameters instead of the
subclass's, so the subclass's own parameters are rejected:

```python
class Model(Generic[T]):
    def __init__(self, value: Optional[T] = None): ...


class IntModel(Model[int]):
    def __init__(self, depth: int = 1): ...


parser.add_argument("--model", type=Model[int])
parser.parse_args(["--model=IntModel", "--model.depth=2"])
# Option 'depth' is not accepted
```

A plain `Model` annotation works.

### Cause

Since #775, `adapt_class_type` builds the parser for a subscripted generic type
from the subscripted type itself, whatever the `class_path` is. That is needed
when the `class_path` is the generic class, so that its type variables are
replaced by the type arguments, but not for a subclass.

### Fix

The subscripted type is used only when the `class_path` is the generic class
itself; otherwise the class in `class_path` is used. The `not is_protocol(...)`
condition is no longer needed, since a Protocol given as `class_path` is rejected
earlier.

### Testing

- `test_subclass_of_subscripted_generic` parses and instantiates a subclass with
  its own parameter, and checks that the generic class itself still has its type
  variable replaced (`value=x` is rejected for `Model[int]`). No existing test
  covered that substitution. It fails on main.
- The existing tests pass and all changed lines are covered.

### Notes for review

- A subclass that is itself generic (e.g. `class Sub(Model[T])` under
  `Model[int]`) parses with this change, but its type variables are not resolved
  from the annotation's type arguments.
- On `v4` the same three-line change applies by hand (the surrounding lines differ because of the `prior_init_args` handling), so it could be backported.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
