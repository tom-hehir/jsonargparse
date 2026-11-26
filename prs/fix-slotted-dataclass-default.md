> **Superseded (local note, not for upstream):** the slots fix is now the second commit of
> `fix-default-instance-non-field-attributes`, which reads `__init__` parameters with `getattr`
> and so fixes both issues on the same lines. Keep this branch only if J16 is not filed.

# Fix dataclass with slots=True as default failing with a vars() error

Branch: `fix-slotted-dataclass-default` (draft, not opened)

## What does this PR do?

A `@dataclass(slots=True)` instance used as a default fails when the argument
or the parser is added:

```python
@dataclass(slots=True)
class Data:
    p1: int = 1


parser.add_argument("--data", type=Optional[Data], default=Data(p1=2))
# TypeError: vars() argument must have __dict__ attribute
```

### Cause

`convert_to_dict`, which turns a dataclass (or attrs, pydantic) instance default
into a dict, reads the attributes with `vars(value)`. Instances of a dataclass
with `slots=True` have no `__dict__`. Of the types handled by that function,
only dataclasses can be slotted without a `__dict__` (attrs is handled before,
and pydantic models have one).

### Fix

When the instance has no `__dict__`, the attributes are read from the dataclass
fields.

### Testing

- `test_dataclass_slots_instance_default` for the type and its `Optional`
  counterpart: parses with the default, instantiates and dumps. Fails on main.
- Full suite as on main (only the two environmental argcomplete failures).

### Notes for review

- This overlaps in the same lines with the pending change that keeps only the
  `__init__` parameters of a dataclass default
  (`fix-default-instance-non-field-attributes`); the two conflict textually but
  not semantically (with both, the slotted attributes go through the same
  filter). If both are sent, it would be simpler to combine them: for a
  dataclass read `{p.name: getattr(value, p.name) for p in <init params>}`,
  which needs neither `vars` nor the `__dict__` branch. This PR is the
  independent minimal version.
- `dataclasses.fields` includes `init=False` fields, as `vars` did for normal
  dataclasses; filtering those is the other change's concern.
- For `v4` the same change applies by hand (the line is `for name, attr in
  vars(value).items()` there, without the pydantic extras).

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
