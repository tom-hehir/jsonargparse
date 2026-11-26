# Fix null for an os.PathLike parameter becoming the string "None"

Branch: `fix-pathlike-coercion` (draft, not opened)

## What does this PR do?

For a parameter typed `os.PathLike | None` (or `Optional[Union[os.PathLike, str]]`),
`null` in the command line gives the string `"None"` instead of `None`:

```python
parser.add_argument("--path", type=Optional[os.PathLike])
parser.parse_args(["--path=null"]).path    # 'None'
parser.parse_string("path: null").path     # None
```

In practice a run was staged into a directory called `None`.

### Cause

`os.PathLike` is registered with `register_type(os.PathLike, str, str)`, so any
value that is not already of the registered type goes through `str(value)`,
including the `None` that `null` loads as. In a union the `os.PathLike` arm is
tried before `None`, and it accepts the value. A YAML `null` is not affected
(the `None` of a config value does not go through that arm).

### Fix

A named deserializer, `pathlike_deserializer`, that raises `TypeError` for `None`
and otherwise does `str(value)` as before, so the `None` arm gets the value.
A bare `os.PathLike` parameter now takes `--path=null` as the path `null`,
the same as `str` and `pathlib.Path` do.

### Testing

- `test_optional_os_pathlike_null`, for `Optional[os.PathLike]` and
  `Optional[Union[os.PathLike, str]]`: `null` in the command line and in a
  config string gives `None`, and a normal path is unchanged. It fails on main.
- The existing tests pass and the changed lines are covered.

### Notes for review

- Scope: only `None` is rejected. `os.PathLike` still turns other non-string
  values into strings: `--path=7` gives `'7'` (reasonable on the command line),
  but also `path: 7` in YAML gives `'7'` and `--path=[a,b]` gives `"['a', 'b']"`,
  where `str` and `pathlib.Path` reject or keep the raw text. Is that intended?
  Neither the documentation (which lists `PathLike` as a supported type) nor the
  tests say. A stricter deserializer that accepts only `str` and `os.PathLike`
  (like `pattern_deserializer` does for `re.Pattern`) is a one-line change in the
  same function, but it would reject numeric names in YAML (`output: 2024`) that
  work today, so I left it out as a possible behaviour change.
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
