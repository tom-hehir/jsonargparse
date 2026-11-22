# Fix union of dataclasses with an instance default rejecting values for another member

Branch: `fix-tagged-union-instance-default` (draft, not opened)

## What does this PR do?

Since 4.50.0, a union of dataclasses with an instance as default rejects a value
meant for a member other than the default's class:

```python
@dataclasses.dataclass
class A:
    type: Literal["a"] = "a"


@dataclasses.dataclass
class B:
    type: Literal["b"] = "b"
    x: int = 0


parser.add_argument("--u", type=Union[A, B], default=A())
parser.parse_args(['--u={"type": "b", "x": 3}'])
# - Expected type: Literal['a']. Got value: b
# - Subclasses are disabled for B, thus '__main__.A' is not accepted
```

It works without the default, and with dotted `--u.type=b --u.x=3`. It worked in
4.49.

### Cause

#921 keeps the `class_path` of a subclasses-disabled default while parsing, so
that a partial value such as `{"x": 3}` updates the default's class rather than
switching to another member. In a union, every member is then checked against
the default's class, so only that class can match.

### Fix

When no member accepts the value and the previous value is a subclasses-disabled
default, each member is tried again with its own `class_path`. Previous
`init_args` that the chosen member doesn't accept are discarded, as for a
`class_path` given explicitly, and compatible ones are kept, as in 4.49 (default
`C(n=5)` with `{"tag": "b"}` gives `B(n=5)`). Each member is first tried on a copy
of the previous value, so a member that rejects the value can't discard
`init_args` that a later member would accept.

#921's behaviour is kept: a value accepted by the default's class still updates
that class.

### Testing

- `test_union_dataclasses_tagged_with_instance_default` uses three tagged
  dataclasses with an instance default. It checks that a partial value keeps the
  default's class, that a value for another member keeps the compatible
  `init_args` (also when a member tried before it rejects them), and that
  incompatible ones are dropped. It fails on main.
- The existing tests pass and all changed lines are covered.
- Also checked by hand against 4.49: values given in a config file,
  `Optional[A | B]`, a `list[A | B]`, a nested field, and a config followed by a
  command-line value give the same results, except where #921 intentionally
  differs (a partial value keeps the default's class). When no member accepts a
  value, the error is the same as on main.

### Notes for review

- The fallback only runs when every member has rejected the value, so values
  that parse on main are unaffected. The member that accepts is adapted twice,
  first on the copy and then on the previous value.
- With `subclasses_enabled` for the dataclasses, a dict without `class_path` is
  read as `init_args` for the previous class, so these values still fail. That
  was also the case in 4.49.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
