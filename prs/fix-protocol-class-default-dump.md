# Fix class default of a callable or protocol type dumped as a bare import path when nested

Branch: `fix-protocol-class-default-dump` (draft, not opened)

## What does this PR do?

A class used as default of a parameter typed as a callable returning a subclass
(`Callable[..., Decoder]`) or a callable Protocol is dumped with its `init_args`
when the parameter stands alone, but as a bare import path when it is inside a
union or inside a dataclass default. That config isn't a fixpoint (dump, parse,
dump gives something different) and omits the hyperparameters:

```python
class Decoder:
    def __init__(self, *, spec: int = 1, d: int = 8, width: int = 4): ...


class Factory(Protocol):
    def __call__(self, *, spec: int, d: int) -> Decoder: ...


@dataclass
class Config:
    head: Factory | Choice = Decoder   # Choice is another dataclass


parser.add_class_arguments(Config, "m")
parser.dump(parser.parse_args([]))
# m:
#   head: __main__.Decoder
# after parsing and dumping again: class_path plus init_args (width: 4)
```

A plain `head: Factory = Decoder` dumps `class_path` and `init_args` the first
time. Same for a field of a dataclass instance used as default
(`sel: Choice = Choice()` with `Choice.discrete: Factory = Decoder`).

### Cause

`normalize_default_value` turns a class default into a `class_path` spec only
when the action's own type hint is a callable that returns a subclass. In a union
the check doesn't match, and for a default dataclass instance the field values
inside it are never normalized with their field types. The class then stays in
the config as is, and the callable branch of `adapt_typehints` only parses a
string or a spec, so it is serialized as a bare import path. The sub-defaults
(`init_args`) are only added when a value is parsed as a spec.

### Fix

In the callable branch of `adapt_typehints`, a class is converted to a
`class_path` spec when the type is a callable returning a subclass, the same as
a string with the import path of a class already was a few lines below. This
covers every position the type can be in, at the place where the plain case
already ends up.

### Testing

- `test_callable_protocol_class_default_nested_dump`, parametrized for a
  dataclass instance default and a union with a dataclass: the dump has
  `class_path` and the `init_args` defaults and dump, parse, dump is a fixpoint.
  Fails on main.
- Suite passes (except the 2 environmental argcomplete failures) and the changed
  lines are covered.

### Notes for review

- Behaviour change: the parsed value in these positions is now a spec
  (`class_path`/`init_args`) instead of the class itself, so instantiating gives
  a `functools.partial` of the class with its defaults rather than the class. It
  is the same as what a plain field of that type already gives. Calling it gives
  the same object.
- A class that can't be imported back (e.g. defined in a function) now fails
  with a "Unexpected import path format" error in these positions, as it does for
  a plain field. Before, the dump contained "Unable to serialize instance" text.
- The branch in `normalize_default_value` is kept; I didn't want to touch it,
  but it could probably go once values are converted here. Only classes are
  converted if the type returns a subclass, as `Callable[..., Any]` with a class
  default is left as it was.
- Alternatives I didn't take: normalizing with the field types when a dataclass
  default is converted (more invasive), or serializing a class as a bare path
  deliberately (keeps the dump compact but not the hyperparameters).
- `v4`: the source change applies there, the test hunk needs adapting (different imports); not run on `v4`.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [ ] Did you make sure that all changes preserve **backward compatibility**? (see the first note)
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
