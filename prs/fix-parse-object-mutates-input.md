# Fix parse_object replacing the class_path dicts in the lists and dicts of its input

Branch: `fix-parse-object-mutates-input` (draft, not opened)

## What does this PR do?

`parse_object` leaves its input unmodified, except that the `class_path` dicts
inside a `list` or `dict` value are replaced in place by namespaces:

```python
class Base:
    def __init__(self, n: int = 1): ...


parser.add_argument("--m", type=list[Base])
obj = {"m": [{"class_path": "__main__.Base", "init_args": {"n": 3}}]}
parser.parse_object(obj)
obj  # {'m': [Namespace(class_path='__main__.Base', init_args=Namespace(n=3))]}
```

A single `Base` value, or a dataclass section, is not touched, and a `dict[str, Base]`
behaves like the list. This is visible for example when the same object is
parsed twice or reused after parsing.

### Cause

`adapt_typehints` assigns the adapted items back into the value it was given
(`val[n] = ...` for lists, `val[k] = ...` for mappings), which for `parse_object`
is the caller's own container.

### Fix

The list and mapping branches now work on a copy of the container: a list was
already converted with `list(val)` for other iterables, and this now includes
lists; a `dict` is copied with `val.copy()`.

One place relied on the in-place modification: for an `apply_on="parse"` link
whose target is a list or dict type, `ActionLink.set_target_value` checked the
computed value with `_check_type` and ignored the returned, adapted value.
It now uses it. (For a single-spec target this means the target is stored as the
checked value too, not as the dict the compute function returned.)

### Testing

- `test_parse_object_does_not_modify_input` (list and dict). Fails on main.
- `test_on_parse_list_of_instances_target`, which already existed, fails if only
  the `adapt_typehints` change is made and covers the link change.
- Full suite as on main (only the two environmental argcomplete failures).

### Notes for review

- The containers are copied shallowly; the nested items are replaced, not
  mutated, by the adapters, so this is enough for the lists and dicts of specs.
  Nested containers (`list[list[Base]]`) go through the same branch, so they are
  copied at each level. I haven't audited other places (e.g. `Any` fields,
  tuples, sets) for the same pattern.
- The extra copy is linear in the container size per parse.
- The change doesn't apply as is to `v4` (the code has moved); the same two
  places exist there and would need a manual port.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
