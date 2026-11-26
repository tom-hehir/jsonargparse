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
default, the value is parsed again without the previous value, so that the
members are checked on their own. Since #1038, changing the class discards the
prior `init_args`, so the `init_args` of the previous member are dropped too
(default `C(n=5)` with `{"tag": "b"}` gives `B()`, the same as without a
default).

#921's behaviour is kept: a value accepted by the default's class still updates
that class.

### Testing

- `test_union_dataclasses_tagged_with_instance_default` uses three tagged
  dataclasses with an instance default. It checks that a partial value keeps the
  default's class, that a value for another member gets that member's defaults,
  and that this also holds when the previous value was given earlier in the
  command line. It fails on main.
- The existing tests pass and all changed lines are covered.
- When no member accepts a value, the error is the same as on main.

### Notes for review

- Design choice: the previous `init_args` are discarded, not kept when the new
  member accepts them. In 4.49 a compatible one was kept (default `C(n=5)` with
  `{"tag": "b"}` gave `B(n=5)`). Discarding follows #1038 and avoids a member
  inheriting values of the default of another one. Keeping compatible ones is
  possible, but needs a retry per member on a copy of the previous value.
- The fallback only runs when every member has rejected the value, so values
  that parse on main are unaffected.
- With `subclasses_enabled` for the dataclasses, a dict without `class_path` is
  read as `init_args` for the previous class, so these values still fail. That
  was also the case in 4.49.
- `v4` does not take this diff as is (surrounding code differs); it would need a
  manual port, and there the previous `init_args` behaviour of that branch applies.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
