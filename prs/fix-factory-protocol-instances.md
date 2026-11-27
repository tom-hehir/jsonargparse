# Fix callable protocols returning a class rejecting classes whose instances implement them

Branch: `fix-factory-protocol-instances` (one commit, on main cc53487). Expected PR number: #1043.

---

## What does this PR do?

Since v4.52.0, a class whose instances implement a callable protocol is rejected
as `class_path` if the protocol's `__call__` returns a class:

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

`MSE` instances implement `Loss`, so this should be accepted, as it was in
v4.51.0. A function that implements `Loss` is still accepted.

Separately, a protocol whose `__call__` has no return annotation rejects every
class and function, e.g. with "Expected ... to be a function that returns
_empty".

### Cause

1. A callable protocol is treated as an instance factory when its `__call__`
   returns a type that could itself be given as `class_path`, i.e. a class
   other than a builtin like `float` or `str`, a registered type, a `Path` or an
   `Enum`. `Loss` returns `Tensor`, so it is treated as a factory of tensors.
   A protocol returning `float` is not, so this problem doesn't arise there.
2. For an instance factory, a `class_path` can mean two things:
   - a subclass of the returned class, e.g. `SGD` for a protocol returning
     `Optimizer`: the class is the factory, and calling it gives the instance;
   - a class whose instances implement the protocol, e.g. `MSE` for `Loss`: the
     instance is the value, as for any other protocol type.
3. Before #959, any class with callable instances was accepted, without
   checking it against the protocol. #959 fixed this by accepting only the
   first kind, which also rejects the second. I think this was not intended,
   since a protocol type accepts its implementers everywhere else.

For the second problem, `get_protocol_call_return_type` returns
`inspect.Signature.empty` when `__call__` has no return annotation. That is a
class, so the protocol is treated as a factory of `_empty`.

### Fix

- In `adapt_typehints`, a class that is not a subclass of the return type is
  accepted if its instances implement the protocol. This uses
  `implements_protocol`, the same check as for any other protocol type, so a
  class that doesn't implement the protocol is still rejected, as #959
  intended. A subclass of the return type is still treated as a factory.
- For a protocol, the error message adds "or its instances to implement
  <protocol>".
- `get_protocol_call_return_type` returns `None` when the return is not
  annotated, as `get_callable_return_type` does when there is no return type.

This doesn't change what a config can import: the class is checked against the
import path denylist before this point, as before.

### Testing

- `test_callable_protocol_accepts_class_whose_instances_implement_it`: a class
  whose instances implement the protocol is accepted, and `instantiate` gives
  an instance of it. Run for a protocol that returns a class and for one
  without a return annotation.
- `test_callable_protocol_without_return_type_accepts_function`.
- These fail on main. The existing tests pass, and the changed lines are
  covered.

### Notes for review

Two related cases are still rejected, and this PR doesn't change them:

- **`Callable` with a class return type.** Typed as a `Callable` instead of a
  protocol, `MSE` is rejected for the same reason: `Tensor` is a class that
  could be given as `class_path`, so the `Callable` is treated as an instance
  factory. With a `float` return it isn't, and any class with callable
  instances is accepted:

  | type of `--loss` | `--loss=__main__.MSE` |
  |---|---|
  | `Loss` | rejected on main, accepted with this PR |
  | `Callable[[Tensor, Tensor], Tensor]` | rejected, also with this PR |
  | `Callable[[Tensor], float]` | accepted, as is any class whose instances are callable (not a factory) |

  I left `Callable` out because #959 restricted it on purpose, and there is no
  existing check of a class against a `Callable` signature, as
  `implements_protocol` is for protocols.
- **`torch.nn.Module` implementers.**

  ```python
  class MSEModule(torch.nn.Module):
      def forward(self, pred: Tensor, target: Tensor) -> Tensor: ...
  ```

  `MSEModule` is still rejected for `Loss`. The protocol check compares
  `__call__`, and `nn.Module.__call__` takes `*args, **kwargs` with no return
  annotation, which doesn't match `-> Tensor`. Accepting it would mean treating
  a missing annotation as matching any type, as static type checkers do. That
  is a broader change to how protocols are matched, so I've left it out of
  scope and mention it only for completeness.

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
