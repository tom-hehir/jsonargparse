# Fix callable protocols returning a class rejecting classes whose instances implement them

Branch: `fix-factory-protocol-instances` (one commit, on main cc53487). Expected PR number: #1043.

---

## What does this PR do?

Since v4.52.0, a class whose instances implement a callable protocol is rejected
as its `class_path` when the protocol's `__call__` returns a class:

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
# error: Expected 'SGDFactory' to be a subclass of Optimizer.
```

`SGDFactory` instances implement `OptimizerFactory`, so it is a valid value
like for any other protocol type: an implementer given as `class_path` is
instantiated with its `init_args`, and the instance is the value.

Also, a protocol whose `__call__` has no return annotation rejects every class
and function, e.g. with "Expected ... to be a function that returns _empty".

### Cause

#959 fixed instance factory protocols accepting any class whose instances are
callable, without checking them against the protocol. Since then, a class must
be a subclass of the return type, i.e. a factory whose class is called to give
the instance. That restriction also rejects classes whose instances do
implement the protocol, which I think was not intended, since a protocol type
accepts its implementers everywhere else.

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

### Testing

- `test_callable_protocol_accepts_class_whose_instances_implement_it`, for a
  protocol with a class return type and for one without a return annotation:
  the class is accepted, instantiated with its `init_args`, and its instances
  return the expected object.
- `test_callable_protocol_without_return_type_accepts_function`.
- These fail on main. The existing tests pass, and the changed lines are
  covered.

### Notes for review

- `Callable[..., Optimizer]` has the same problem for a class whose instances
  are callable and return an `Optimizer`. This PR doesn't change it, since
  #959 restricted it on purpose and a `Callable` can only be checked by its
  return type. I can send that separately if you think it should be accepted.
- A class whose `__call__` has no return annotation, such as a
  `torch.nn.Module`, still doesn't implement a protocol with an annotated
  return, since protocol signatures have to match. That is unchanged.
- The `v4` branch has different code here, so the change doesn't apply as is;
  I can adapt it if you'd like it in a 4.x release.

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
