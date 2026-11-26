# Fix dataclass instance defaults with non-init attributes rejected by union and subclass types

Branch: `fix-default-instance-non-field-attributes` (draft, not opened)

## What does this PR do?

A dataclass instance given as default of a union, `Optional` or subclass type is
rejected when it has attributes that are not `__init__` parameters, e.g. an
`init=False` field or an attribute set in `__post_init__`:

```python
@dataclasses.dataclass
class Data:
    a: int = 1

    def __post_init__(self):
        self._cache = self.a * 10


parser.add_argument("--data", type=Optional[Data], default=Data())
parser.parse_args([])
# Expected type: Optional[Data]. Got value: {'a': 1, '_cache': 10}
#   - Data: Problem with given class_path '__main__.Data':
#       Option '_cache' is not accepted
```

The same default works with `type=Data`, and the same values given as
`class_path` and `init_args` in a config also work. For unions and `Optional`,
it fails since 4.50.0 (and in 4.42 to 4.45). For subclass types, e.g. a base
dataclass with `subclasses_enabled=["is_pure_dataclass"]`, or a plain base class
with a dataclass subclass instance as default, it has failed since such defaults
are accepted (4.42).

The second commit fixes a related failure on the same lines: a default instance
of a dataclass with `slots=True` fails with `vars() argument must have __dict__
attribute`, also for a plain `type=DataSlots`.

### Cause

`convert_to_dict` builds the `init_args` of a dataclass instance from
`vars(value)`, so every instance attribute is included. Before #781 it used
`dataclasses.asdict`; #781 switched to `vars()` to handle dataclasses and
pydantic models in one loop and add `class_path`. For a plain dataclass type,
`add_class_arguments` drops keys that were not added as arguments ("skip
init=False and pydantic extra fields", #650), but `normalize_default_value`,
used for unions, `Optional` and subclass types, has no such filter.

### Fix

For dataclasses, `convert_to_dict` keeps only the attributes that are parameters
of the class's signature, as given by `get_signature_parameters`. These are the
keys that the parser of the class accepts, so the result matches what a plain
dataclass type keeps.

Filtering by `dataclasses.fields()` with `f.init` was considered, but it is not
right for some dataclasses that work on main:

- `@dataclass(init=False)` with a hand-written `__init__` (see #991): a
  parameter that is not a field but is stored as an attribute, e.g.
  `self.x = x`, would be dropped, so a default `C(x=5)` would silently become
  `x=0`. A field that the hand-written `__init__` doesn't accept would still be
  kept and rejected.
- An `InitVar` stored under its own name in `__post_init__` would be dropped,
  since `InitVar`s are not in `fields()`.

The signature handles both, and also follows a `**kwargs` forwarded to a parent
class.

In the second commit, the parameters are read with `getattr` instead of
filtering `vars(value)`, so a dataclass with slots, which has no `__dict__`,
works too, and the filter step goes away:

```python
if dataclasses.is_dataclass(value_type):
    params = get_signature_parameters(value_type)
    attributes = {p.name: getattr(value, p.name) for p in params if hasattr(value, p.name)}
else:
    attributes = {**vars(value), **get_pydantic_extra_fields(value)}
```

Pydantic models and attrs classes are unchanged. Pydantic dataclasses are
dataclasses, so they get the same filter; an attribute set in their
`__post_init__` failed in the same way and now works.

### Testing

- `test_dataclass_instance_default_non_init_attributes` uses a dataclass with an
  `init=False` field and a private attribute set in `__post_init__`, as default
  of an `Optional` type and of a base dataclass type with subclasses enabled. It
  checks that a command-line value parses and instantiates, and that the dump
  doesn't include those attributes and parses back to the same config. It fails
  on main.
- `test_dataclass_slots_instance_default` (second commit) uses a `slots=True`
  dataclass instance as default of the type and of its `Optional`, checking
  parse, instantiate and dump. It fails with only the first commit.
- The existing tests pass on Python 3.12 and 3.14, and all changed lines are
  covered.
- Also checked by hand: `Union[Data, Other]`, a plain base class with a
  dataclass subclass default, public attributes set in `__post_init__`, a nested
  dataclass default whose field is typed as a base dataclass and defaults to a
  subclass instance (with a sibling field overridden in the command line), the
  hand-written `__init__` and `InitVar` cases above, and pydantic models with
  private attributes and `extra="allow"`.

### Notes for review

- The skip in `add_class_arguments` is kept. It is still needed for pydantic
  extra fields and for `init=False` fields of attrs classes, which go through
  `attrs.asdict`.
- attrs classes have the same problem for `init=False` fields with a union or
  subclass type, since `attrs.asdict` includes them. This PR doesn't change
  attrs; it could be a follow-up.
- Two cases change from an error to dropping the attribute, the same as a plain
  dataclass type already does: an attribute set from an unresolved `**kwargs`
  of a hand-written `__init__`, and a pydantic dataclass field whose alias is
  the only accepted name. In both cases the default's value is not kept.
- With `getattr`, a parameter of a hand-written `__init__` that the instance
  doesn't store, but that exists as a class attribute of the same name, would
  now be read from the class; `vars()` didn't see it. This seems unlikely in
  practice; the `hasattr` check skips parameters that are not stored at all,
  e.g. `InitVar`s.
- The two commits can be split into two PRs if preferred; the slots fix alone
  would be a `hasattr(value, "__dict__")` branch on the current code.
- On `v4` the same filter applies by hand (`convert_to_dict` there has no pydantic extra fields line, so the diff context differs); `get_signature_parameters` is already imported in `_signatures.py`.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
