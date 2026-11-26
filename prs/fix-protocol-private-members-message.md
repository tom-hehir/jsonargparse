# Explain in the error why a Protocol with only private members matches nothing

Branch: `fix-protocol-private-members-message` (draft, not opened)

## What does this PR do?

A `Protocol` whose members all start with an underscore is implemented by no
class, and the error doesn't say why:

```python
class Encoder(Protocol):
    def _encode(self, x: int) -> int: ...


class Impl:
    def _encode(self, x: int) -> int: ...


parser.add_argument("--enc", type=Encoder)
parser.parse_args(["--enc=Impl"])
# Import path Impl does not implement protocol Encoder
```

`Impl` has exactly the method that the protocol asks for, so the message
looks wrong. With this change a line is added:

```
Import path Impl does not implement protocol Encoder
The protocol has no public members to check, since names starting with '_' are not checked.
```

### Cause

`get_protocol_members` skips names that start with an underscore (other than
some dunders), and `implements_protocol` returns `False` when no members are
left, so a protocol with only such members, or with no members at all, is
implemented by nothing. That seems a deliberate choice (private methods are
not part of an interface), but the resulting error is confusing.

### Fix

When the typehint is a protocol with no members to check, the error for a
class path that doesn't implement it gets the extra line above, through a small
helper, in the same way as the known subclasses line. The matching itself is
unchanged.

### Testing

- `test_parse_protocol_only_private_members_error`. Fails on main (no such line).
- Full suite as on main (only the two environmental argcomplete failures).

### Notes for review

- Only the message changes. I did not touch the matching: whether private
  members should count, and variance (a `float | int` argument for `float`,
  an unannotated parameter), are separate design questions.
- Mixed protocols (public and private members) still don't check the private
  ones, silently; there is no error to attach a note to in that case.
- An empty protocol also gets this message; "no public members" is accurate
  for it too.
- It would be friendlier to warn when the protocol is added to the parser
  instead; I kept to the smallest change.
- For `v4` the code is different; I haven't checked a port.

## Before submitting

- [x] Did you read the [contributing guideline](https://github.com/mauvilsa/jsonargparse/blob/main/CONTRIBUTING.rst)?
- [ ] If you used a **coding agent**, did you fully understand and validate all generated code and ensure it follows the contributing guidelines?
- [n/a] Did you update **the documentation**? (readme and public docstrings)
- [x] Did you write **unit tests** such that there is 100% coverage on related code? (required for bug fixes and new features)
- [x] Did you verify that new and existing **tests pass locally**?
- [n/a] If this is a **bug fix**, did you verify that the **tests fail without the code fix**? (failing on main: yes)
- [x] Did you make sure that all changes preserve **backward compatibility**?
- [x] Did you update **the CHANGELOG** including a pull request link? (not for typos, docs, test updates, or minor internal changes/refactors)
