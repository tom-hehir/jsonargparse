# Add context to the error of a failing dataclass default_factory

Branch: `fix-default-factory-error-context` (draft, not opened)

## What does this PR do?

When the `default_factory` of a dataclass field raises, e.g. because the created
object validates itself in `__post_init__`, adding the class fails with the bare
exception, which doesn't say which class or field it comes from:

```python
@dataclass
class Runtime:
    output_dir: Optional[str] = None

    def __post_init__(self):
        if self.output_dir is None:
            raise ValueError("output_dir is required")


@dataclass
class Job:
    runtime: Runtime = field(default_factory=Runtime)


parser.add_class_arguments(Job, "job")
# ValueError: output_dir is required
```

With this change:

```
ValueError: Unable to add parameter "runtime" from "Job.__init__": default_factory failed: output_dir is required
```

### Cause

`_add_signature_parameter` calls the `default_factory` to get the default to
add, without handling a failure. In a large dataclass hierarchy the bare message
leaves no hint of where it comes from.

### Fix

The call is wrapped in `try`/`except`, re-raising a `ValueError` chained from the
original, with the same `Unable to add parameter "<name>" from "<origin>": ...`
form that the same function already uses for annotations it can't handle.

### Testing

- `test_dataclass_field_default_factory_error_context` checks the parameter,
  its origin and the original message. Fails on main.
- Full suite as on main (only the two environmental argcomplete failures).

### Notes for review

- The exception type becomes `ValueError`, whatever the factory raised (the
  original is kept as `__cause__`). I followed the existing convention in this
  function rather than `Exception.add_note`, which would keep the type but needs
  Python 3.11 while the project supports 3.10, and would not show up in the
  `ArgumentError` text some callers produce. If keeping the type matters more,
  `raise type(ex)(...) from ex` (as the link code does) is an alternative, but
  breaks for exceptions with custom constructors.
- The failure is not a bug in jsonargparse: calling `Job()` fails the same way
  in plain Python. Only the message is improved. The default is required at
  definition time, so `--help` and any flag that would supply the value still
  can't work; changing that would be a larger design decision.
- Only the call in `_signatures.py` is wrapped. The `default_factory()` calls
  for pydantic fields in `_parameter_resolvers.py` are not; they could get the
  same treatment if wanted.
- For `v4` the code is different; I haven't checked a port.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [n/a] If this is a **bug fix**, did you verify that the **tests fail without the code fix**? (failing on main: yes)
- [x] Did you make sure that all changes preserve **backward compatibility**? (exception type changes if the factory raised a non-ValueError)
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
