# Fix None dumped as text for some union types with unset_sentinel=True

Branch: `fix-unset-sentinel-none-dump` (one commit, on main cc53487). Opened as [#1044](https://github.com/mauvilsa/jsonargparse/pull/1044) on 2026-11-27.

---

## What does this PR do?

With `set_parsing_settings(unset_sentinel=True)`, `None` in some unions with
`None` (here written as `Optional[X]`, i.e. `Union[X, None]`) is dumped as text
instead of `null`, so the dump can't be loaded back:

```python
set_parsing_settings(unset_sentinel=True)
parser.add_argument("--path", type=Optional[Union[str, Path]], default=None)
parser.add_argument("--interval", type=Optional[timedelta], default=None)
parser.add_argument("--fn", type=Optional[Callable[[int], int]], default=None)
print(parser.dump(parser.parse_args([])))
# path: None
# interval: None
# fn: Unable to serialize instance None
```

Loading this back fails for `interval`, and `path` becomes the string `'None'`.
With LightningCLI this affects `Trainer(max_time=..., val_check_interval=...)`,
`ModelCheckpoint(dirpath=..., train_time_interval=...)` and `ckpt_path`, so a
saved `config.yaml` can't be used to run again.

With the default settings `None` means "not given" and is never serialized, so
this only shows with `unset_sentinel=True`.

### Cause

For a union, the subtypes are tried in order and the first that doesn't raise
is used. `NoneType` comes after the other subtypes, so that `Optional[X]` reads
as written, but some of them accept `None` when serializing:

- registered types whose serializer is `str`, such as `os.PathLike`,
  `pathlib.Path` and `timedelta`, give `"None"`;
- `Callable` uses `serialize_as_import_path`, which since #966 returns
  `"Unable to serialize instance None"` instead of raising.

So `NoneType` is never reached.

### Fix

`sort_subtypes_for_union` moves `NoneType` to the front when the value is
`None`, in the same way as it already moves sequence types to the front when
appending to a list.

This only changes which subtype handles a `None`. Any other value is tried in
the same order as before, and the help still lists `NoneType` last. It also
fixes `--path=null` giving the string `'None'` for `Optional[os.PathLike]`,
with the default settings too.

### Testing

- `test_unset_sentinel_dump_none_in_union`, for `Optional[os.PathLike]`,
  `Optional[Union[str, Path]]`, `Optional[timedelta]` and
  `Optional[Callable[[int], int]]`: with `unset_sentinel=True`, a `None`
  default is dumped as `null`, loads back as `None`, and `--val=null` gives
  `None`. All four cases fail on main.
- The existing tests pass, and the changed lines are covered.

### Notes for review

A related problem that this PR doesn't change: a registered serializer is
applied to any value in a union, not only to instances of its type:

```python
class MyClass:
    pass


def my_class_serializer(value):
    return "my_class"


def my_class_deserializer(value):
    if value != "my_class":
        raise ValueError(value)
    return MyClass()


register_type(MyClass, serializer=my_class_serializer, deserializer=my_class_deserializer)
parser.add_argument("--value", type=Union[MyClass, int])
parser.dump(parser.parse_args(["--value=3"]))
# value: my_class
```

The `3` is dumped as `my_class`, so the dump loads back as `MyClass()`.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
