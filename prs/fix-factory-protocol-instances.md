# Fix callable types returning a class rejecting classes whose instances are the callable

Branch: `fix-factory-protocol-instances` (draft, not opened). Two commits: the first is the Protocol fix,
the second extends it to `Callable` and can be dropped on its own.

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

The same happens with `Callable[[List[float]], Optimizer]` (and `Callable[..., Optimizer]`).
This also makes a field whose default is such an instance unparseable, since the
default is validated the same way.

Also, a Protocol whose `__call__` has no return annotation is treated as a factory
whose return type is `inspect.Signature.empty`, so every class and function is
rejected ("subclass of _empty", "function that returns _empty").

### Cause

#959 removed a fallback that accepted any class whose instances are callable,
which was too permissive. Since then, only the factory reading is considered:
a class that is not a subclass of the return type is rejected before checking
whether its instances are callable. Separately, `get_protocol_call_return_type`
returned `inspect.Signature.empty`, a class, for an unannotated return.

### Fix

First commit (Protocol):
- When a class is not a subclass of the return type, it is accepted if its
  instances implement the Protocol, using `implements_protocol`, the same check
  used for other Protocols.
- For a Protocol, the error adds ", or its instances to implement ...".
- `get_protocol_call_return_type` returns `None` for an unannotated return,
  like `get_callable_return_type` does when there is no return type.

Second commit (`Callable`):
- New `instances_implement_callable`, which uses the above for a Protocol and,
  for a `Callable`, requires the return type of the class's `__call__` to be a
  subclass of the expected one. That is how a function is already checked for a
  `Callable`: the return type only, not the arguments.
- The error message mentions the instances for both kinds of type.

A class that is a subclass of the return type is still treated as a factory,
even if its instances are also callable.

### Testing

- `test_callable_protocol_accepts_implementers` covers a Protocol with a class
  return type and one without a return annotation, with a class whose instances
  implement it and with a function.
- `test_callable_accepts_class_with_callable_instances` covers `Callable[[...], Ret]`
  and `Callable[..., Ret]`; `test_callable_rejects_class_with_callable_instances_returning_other_type`
  checks that a callable class returning another type is still rejected.
- The accepting tests fail on main. The existing tests pass and all changed
  lines are covered.

### Notes for review

- The `Callable` part touches the check added deliberately in #959 and shaped by #1033, so
  it is a separate commit; happy to open it as an issue first or drop it.
- For a `Callable`, a class is accepted by the return type of its `__call__` alone, so
  `Callable[[int], Base]` accepts a class with `__call__(self)` and fails at call time.
  Functions given for a `Callable` already behave like that. A Protocol is checked
  fully (arguments too) by `implements_protocol`.
- Precedence when a class is both: a subclass of the return type whose instances are also
  callable with the right signature is a factory (unchanged), so `class_path` cannot select
  its instances. This is the same for Protocols and `Callable`.
- Classes whose `__call__` has no return annotation, such as `torch.nn.Module`,
  still don't implement a Protocol with an annotated return, because Protocol
  signatures have to match exactly. That rule is unchanged here. Likewise a
  `Callable` rejects them.
- The `v4` branch has a simpler version of this code (no `implement` wording from
  #1033), so the patch doesn't apply as is and needs a manual adaptation.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [x] If this is a **bug fix**, did you verify that the **tests fail without the code fix**?
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
