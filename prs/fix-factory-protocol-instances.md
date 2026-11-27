# Fix callable protocols returning a class rejecting classes whose instances implement them

Branch: `fix-factory-protocol-instances` (one commit, on main cc53487). Expected PR number: #1043.

---

## What does this PR do?

Since v4.52.0, a class whose instances implement a callable protocol is rejected
as `class_path` when the protocol's `__call__` returns a class:

```python
class Loss(Protocol):
    def __call__(self, pred: Tensor, target: Tensor) -> Tensor: ...


class MSE:
    def __call__(self, pred: Tensor, target: Tensor) -> Tensor:
        return ((pred - target) ** 2).mean()


parser.add_argument("--loss", type=Loss)
parser.parse_args(["--loss=__main__.MSE"])
# error: Expected '__main__.MSE' to be a subclass of Tensor.
```

`MSE` instances implement `Loss`, and this worked in v4.51.0. A function
implementing `Loss` is still accepted.

Also, a protocol whose `__call__` has no return annotation rejects every class
and function, e.g. with "Expected ... to be a function that returns _empty".

### Cause

A callable protocol whose `__call__` returns a class is taken to be an instance
factory of that class. #959 fixed these accepting any class whose instances are
callable, without checking them against the protocol. Since then, a class given
as `class_path` must be a subclass of the return type, here `Tensor`. That also
rejects classes whose instances do implement the protocol, which I think was not
intended, since a protocol type accepts its implementers everywhere else.

Separately, `get_protocol_call_return_type` returns `inspect.Signature.empty`
for a `__call__` without return annotation. That is a class, so the protocol is
taken as returning instances of `_empty`.

### Fix

- In `adapt_typehints`, a class that is not a subclass of the return type is
  accepted if its instances implement the protocol, checked with
  `implements_protocol` as for any other protocol. Classes that don't implement
  it are still rejected, as #959 intended, and a subclass of the return type is
  still treated as a factory.
- For a protocol, the error message adds "or its instances to implement
  <protocol>", since that is now also accepted.
- `get_protocol_call_return_type` returns `None` for an unannotated return,
  like `get_callable_return_type` does when there is no return type.

This doesn't widen what a config can import: the class is still checked against
the import path denylist before this point, and it must implement the protocol,
as for any other protocol type.

### Testing

- `test_callable_protocol_accepts_class_whose_instances_implement_it`, for a
  protocol with a class return type and for one without a return annotation:
  the class is accepted, instantiated with its `init_args`, and its instances
  give the expected result.
- `test_callable_protocol_without_return_type_accepts_function`.
- These fail on main. The existing tests pass, and the changed lines are
  covered.

### Notes for review

- With `Callable[[Tensor, Tensor], Tensor]` instead of the protocol, `MSE` is
  still rejected, for the same reason: the return type is a class, so the
  `Callable` is taken to be an instance factory. This PR leaves `Callable` as it
  is, since #959 restricted it on purpose, and unlike for a protocol there is no
  existing check of whether a class's instances match a `Callable`. For
  comparison, `Callable[[Tensor], float]` accepts any class whose instances are
  callable, without checking their signature.
- `torch.nn.Module` subclasses are still rejected for `Loss`, since
  `nn.Module.__call__` has no return annotation (it forwards to `forward`), and
  the signatures of a protocol's methods have to match. This PR doesn't change
  that rule.

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
