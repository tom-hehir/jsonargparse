# Fix dump of lists, tuples and dicts of dataclass-like instances used as defaults

Branch: `fix-dump-container-defaults` (draft, not opened)

## What does this PR do?

A default that is a dataclass instance is dumped as a mapping, but the same
instances inside a list, tuple or dict are dumped as text that can't be parsed
back:

```python
@dataclass
class Rule:
    pattern: str = "*"


@dataclass
class Config:
    rules: list[Rule] = field(default_factory=lambda: [Rule("a.*")])


parser.add_class_arguments(Config, "config")
print(parser.dump(parser.get_defaults()))
# config:
#   rules:
#   - Unable to serialize instance Rule(pattern='a.*')
```

Parsing that text fails ("Expected a dot import path ..."). The same happens for
tuples, dicts, attrs and pydantic instances. In an untyped `dict`, `dump` raises
`RepresenterError`.

### Cause

`normalize_default_value` converts a default that is a dataclass, attrs or
pydantic instance into a dict (`convert_to_dict`), but it only looks at the
default itself. Instances inside a list, tuple or dict reach the serializer as
they are, which falls back to `serialize_as_import_path`, and instances that are
not importable are written as the "Unable to serialize" text.

### Fix

Defaults that are a list, tuple or dict are walked recursively and their
dataclass-like instances converted with `convert_to_dict`, the same as for a
single default. For a base class that allows subclasses (e.g. an abstract
class), `convert_to_dict` already gives the `class_path` form, so a
`list[Base]` holding subclass instances dumps with `class_path` and `init_args`
and round-trips.

### Testing

- `test_dataclass_instances_in_container_defaults_dump`: list, tuple, dict and
  untyped dict defaults dump as mappings and dump, parse, dump is a fixpoint.
- `test_dataclass_subclass_instances_in_container_default_dump`: a
  `list[AbstractBase]` of subclass instances dumps as `class_path`/`init_args`.
- `test_pydantic_instances_in_container_default_dump`.
- All fail on main, the suite passes and all changed lines are covered.

### Notes for review

- Behaviour change for a default that doesn't fit the type: for a concrete
  dataclass `Base`, `list[Base]` with a default holding a *subclass* instance
  (extra fields) parsed without complaint on main (the dump was the broken
  part). Now it is converted to `init_args` only and `parse_args([])` fails with
  "Option 'b' is not accepted", the same as a single `Base` default holding a
  subclass instance. I believe that is consistent, since dataclasses don't
  accept subclasses by default, but it is stricter than before.
- `type(x) in {list, tuple, dict}` is used on purpose, so that
  namedtuples and other subclasses (which can't be rebuilt from an iterable)
  are left alone. Instances nested in other containers (sets, deques) are not
  converted, as `convert_to_dict` didn't before either.
- `normalize_default_value` doesn't exist on `v4` (the change from #983 is not
  there), so a `v4` backport would need to be done at another place; the patch
  doesn't apply as is.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [ ] Did you make sure that all changes preserve **backward compatibility**? (see the first note)
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
