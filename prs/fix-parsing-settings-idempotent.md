# Make enabling an already enabled subclasses function in set_parsing_settings a no-op

Branch: `fix-parsing-settings-idempotent` (draft, not opened)

## What does this PR do?

Calling `set_parsing_settings` twice with the same function name in
`subclasses_enabled` raises on the second call:

```python
set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])
set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])
# ValueError: There is no function 'is_pure_dataclass' registered in subclasses_disabled
```

This is easy to hit when the setting is applied from code that can run more
than once in a process (a test fixture, a module imported by several entry
points, a notebook cell). Disabling twice already works.

### Cause

Enabling a function name removes it from `subclasses_disabled_selectors`. A
repeated call no longer finds it there, and reports it as unknown, the same as a
misspelled name.

### Fix

The names that were enabled are kept in a new set, `subclasses_enabled_selectors`.
A name that is registered is unregistered and remembered; a name that was
already enabled is accepted; any other name still raises as before, so typos
are still caught.

### Testing

- `test_subclass_enable_function_repeated` enables the same function twice. It
  fails on main (and, without the `if`/`elif` change, once the fixture resets the
  new set).
- The `subclass_behavior` fixture also resets the new set. The existing tests
  pass; the changed lines are covered.

### Notes for review

- The simplest alternative is `subclasses_disabled_selectors.pop(enable_item, None)`.
  I did not use it because the documentation says the name must have been
  registered, and `test_unknown_subclass_disable_function` checks the error, so
  silently accepting typos would change a documented behaviour. If you prefer
  the one-liner, the docs sentence and that test would go.
- One sentence was added to the documentation: enabling a function that is
  already unregistered has no effect.
- Only idempotence is covered. Possible follow-ups, which would be new API and
  so are left for a separate discussion: a public getter for the current
  settings (only the private `jsonargparse._common.get_parsing_setting` exists)
  and a scoped way to change settings, e.g. a context manager that restores them.
- The same change applies cleanly to the `v4` branch.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [x] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
