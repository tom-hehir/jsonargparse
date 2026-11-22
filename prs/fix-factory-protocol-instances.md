# Fix callable protocols returning a class rejecting classes whose instances implement them

Branch: `fix-factory-protocol-instances` (draft, not opened)

## What does this PR do?

Since 4.52.0, a Protocol whose `__call__` returns a class is treated as an
instance factory. A class given as `class_path` must then be a subclass of the
return type, so a class whose *instances* implement the Protocol is rejected:

```python
class OptimizerFactory(Protocol):
    def __call__(self, params: List[float]) -> Optimizer: ...


class SGDFactory:
    def __init__(self, lr: float = 0.1):
        self.lr = lr

    def __call__(self, params: List[float]) -> Optimizer:
        return SGD(params, lr=self.lr)


parser.add_argument("--optimizer", type=OptimizerFactory)
parser.parse_args(["--optimizer=SGDFactory", "--optimizer.lr=0.01"])
# Expected 'SGDFactory' to be a subclass of Optimizer.
```

Also, a `__call__` without a return annotation makes the Protocol a factory whose
return type is `inspect.Signature.empty`, so every class and function is rejected
("subclass of _empty").

### Cause

#959 removed a fallback that accepted any class whose instances are callable,
which was too permissive. Since then, only the factory reading is considered.

### Fix

- When a class is not a subclass of the return type, it is accepted if its
  instances implement the Protocol, using `implements_protocol`, the same check
  used for other Protocols. `Callable[..., Ret]` is not a Protocol, so the
  tightening from #959 is unchanged for it.
- For a Protocol, the error adds ", or its instances to implement ...".
- A `__call__` without a return annotation doesn't make the Protocol an instance
  factory.

A class that is a subclass of the return type is still treated as a factory,
even if its instances also implement the Protocol.

### Testing

- `test_callable_protocol_accepts_implementers` covers a Protocol with a class
  return type and one without a return annotation, with a class whose instances
  implement it and with a function. Both cases fail on main.
- The existing tests pass and all changed lines are covered.

### Notes for review

- Classes whose `__call__` has no return annotation, such as `torch.nn.Module`,
  still don't implement a Protocol with an annotated return, because Protocol
  signatures have to match exactly. That rule is unchanged here.
- The same change applies to the `v4` branch with a one-line adaptation, and its
  suite passes.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
