# Fix class default of a callable type dumped without its init_args in a union or dataclass default

Branch: `fix-protocol-class-default-dump` (one commit, on main 2656bf3). Draft, not opened; the changelog uses #1045, the next free number on 2026-11-27.

---

## What does this PR do?

For a callable type that returns a class, such as `Callable[[], Decoder]` or a
protocol whose `__call__` returns `Decoder`, a class can be given as default:
the class is the factory, and calling it gives the instance. As the type of an
argument, this default is dumped as `class_path` plus the class's `init_args`.
In a union, it is dumped as only the import path:

```python
class Decoder:
    def __init__(self, width: int = 4): ...


parser.add_argument("--plain", type=Callable[[], Decoder], default=Decoder)
parser.add_argument("--in_union", type=Union[Callable[[], Decoder], int], default=Decoder)
print(parser.dump(parser.parse_args([])))
# plain:
#   class_path: __main__.Decoder
#   init_args:
#     width: 4
# in_union: __main__.Decoder
```

The same happens for a field of a dataclass instance used as default, when
subclasses are enabled for dataclasses.

So the saved config doesn't record `width`. Loading it gives the class's
current defaults: if the default of `width` changes in the code, the saved
config silently gives a different value from the one used when it was saved.
Also, dumping the loaded config again gives the full form, so the two dumps
differ.

### Cause

`normalize_default_value` converts a class default to a `class_path` spec only
when the argument's own type is the callable type. In a union, or for a field
of a dataclass default, the class is kept as is, and is dumped as an import
path.

### Fix

`adapt_typehints` converts a class to a `class_path` spec when the type is a
callable that returns a class, next to where it already does this for an import
path given as a string. This applies wherever the type appears, so a union or a
dataclass default is dumped like a plain argument.

### Testing

- `test_callable_protocol_class_default_nested_dump`, for a dataclass instance
  default and for a union: the dump has `class_path` and `init_args`, and
  loading it and dumping again gives the same dump. Both cases fail on main.
- The existing tests pass, and the changed lines are covered.

### Notes for review

- In these positions, instantiating now gives a `functools.partial` of the
  class with its `init_args`, instead of the class itself, as it already does
  for a plain argument. Calling it gives the same instance.
- A class that can't be imported back, e.g. one defined inside a function, is
  now rejected in these positions with "Unexpected import path format", as it
  already is for a plain argument. Before, it was accepted and dumped as
  "Unable to serialize instance ...".

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [ ] Did you make sure that all changes preserve **backward compatibility**? (see the notes for review)
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
