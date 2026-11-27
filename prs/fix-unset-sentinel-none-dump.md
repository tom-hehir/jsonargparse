# Fix None dumped as text for some union types with unset_sentinel=True

Branch: `fix-unset-sentinel-none-dump` (draft, not opened)

## What does this PR do?

With `set_parsing_settings(unset_sentinel=True)`, a `None` value of some union
types is dumped as text instead of `null`, so the dump can't be loaded back:

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

Reloading this fails for `interval`, and `path` comes back as the string
`'None'`. With LightningCLI this affects `Trainer(max_time=...,
val_check_interval=...)`, `ModelCheckpoint(dirpath=..., train_time_interval=...)`
and `ckpt_path`, so a saved `config.yaml` can't be used to re-run.

With the default settings `None` means "not given", so it is never serialized
and is dumped as `null`. That is why this only shows with `unset_sentinel=True`.

### Cause

When serializing a union value, the subtypes are tried in order and the first
that doesn't raise is used. Some of them accept `None`:

- registered types whose serializer is `str` (`os.PathLike`, `pathlib.Path`,
  `timedelta`) turn it into `"None"`;
- `Callable` uses `serialize_as_import_path`, which since #966 returns
  `"Unable to serialize instance None"` instead of raising.

So the `NoneType` subtype is never reached.

### Fix

`sort_subtypes_for_union` moves `NoneType` to the front when the value is
`None`. `None` is only ever valid for `NoneType` in a union, so trying it first
can't change the result for any other value, and it also avoids trying the
other subtypes for nothing.

The same change also fixes `--path=null` on the command line for
`Optional[os.PathLike]` giving `'None'` with the default settings, since that
`None` goes through the same union.

### Testing

- `test_unset_sentinel_dump_none_in_union`, for `Optional[os.PathLike]`,
  `Optional[Union[str, Path]]`, `Optional[timedelta]` and
  `Optional[Callable[[int], int]]`: with `unset_sentinel=True`, the dump of a
  `None` default is `null`, it reloads as `None`, and `--val=null` gives `None`.
  All four cases fail on main.
- The full test suite passes (2988 passed, 21 skipped).

### Notes for review

- A related case: a registered serializer is also applied to values of other
  types in a union, e.g. a sentinel type registered with
  `serializer=lambda v: "inherit"` in `Sentinel | bool` turns `False` into
  `"inherit"`. This PR doesn't change that; applying a registered serializer
  only to instances of its type would cover it, but is a bigger change.
- The same change applies cleanly to the `v4` branch.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
