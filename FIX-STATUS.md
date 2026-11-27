# Fix branches: working notes

What to decide before filing each fix. The [README](README.md) has the order,
a one-line description, line counts and diff links for each; this file has the
rest. Draft texts are in [`prs/`](prs/) and [`issues/`](issues/); IDs link to
[`inventory.md`](inventory.md).

- **Branches**: pushed to the fork on 2026-11-26, each cut from upstream `main`
  at 3b30c14, each in its own worktree under `.claude/worktrees/<branch>`.
  The J59 branch was added on 2026-11-27, cut from `main` at cc53487, and is
  not pushed yet. Nothing is filed upstream yet.
- **Checks on every branch**: the new tests fail without the fix and pass with
  it; the full upstream suite passes on Python 3.12 and 3.14, apart from 2
  argcomplete tests that also fail on untouched `main` here; changed lines are
  covered; ruff is clean; mypy reports nothing new.
- **Before filing**: the PR template asks "If you used a coding agent, did you
  fully understand and validate all generated code". That box is left unticked
  in every draft, for you to tick after your own review.
- **PR or issue**: the bug template asks for a PR directly when the bug and its
  fix are understood, so PR is the default. Issue first is for behaviour the
  maintainer may consider intended, or that needs his design choice.

**Priority** (README order): 🔴 first round, top five · 🟠 first round, the
rest · 🟡 fixed locally, not planned for now · ⚪ superseded.

## Decisions and flags for each branch

| | ID | Branch (diff on GitHub) | Decisions or flags | Port to v4 |
|---|---|---|---|---|
| 🔴 | [J01](inventory.md#j01) | [`fix-factory-protocol-instances`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances) · [commit 1](https://github.com/tom-hehir/jsonargparse/commit/d13b66eed01b61708c81c883c473d213f0d27fa9) · [commit 2](https://github.com/tom-hehir/jsonargparse/commit/4d05a3e431a043528962dbdb8f858598e4f35164) | Commit 2 (`Callable`) relaxes a check added on purpose in 4.52 (#959) and checks `Callable` by return type only, as for functions. It can be dropped without affecting commit 1. Alone it doesn't unblock one of our projects on v5: its `nn.Module` losses also need `-> Any` on their Protocol (J02) | manual port |
| 🔴 | [J59](inventory.md#j59) | [`fix-unset-sentinel-none-dump`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unset-sentinel-none-dump) | Moves `NoneType` first in `sort_subtypes_for_union` when the value is `None`. Also fixes the `None` part of J13; the draft mentions J37 as related but leaves it alone | applies |
| 🔴 | [J16](inventory.md#j16) + [J39](inventory.md#j39) | [`fix-default-instance-non-field-attributes`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) · [commit 1](https://github.com/tom-hehir/jsonargparse/commit/59bdc3dc0492680eae30e45116dc19ef83bfd72d) · [commit 2](https://github.com/tom-hehir/jsonargparse/commit/de6966ad159b48415afed833b591d10029906ea6) | Commit 2 reads `__init__` parameters with `getattr`, which also fixes slotted dataclasses (J39) on the same lines. Can be split if wanted | manual |
| 🔴 | [J24](inventory.md#j24) | [`fix-protocol-class-default-dump`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) | Nested class defaults now dump as `class_path` + `init_args`, like a plain field already does; the alternative (bare path) is offered | source applies |
| 🔴 | [J15](inventory.md#j15) | [`fix-subscripted-generic-init-args`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) | none | manual (3 lines) |
| 🟠 | [J13](inventory.md#j13) | [`fix-pathlike-coercion`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) | Whether `os.PathLike` should reject `7` or lists is left as a question: rejecting would break numeric paths like `path: 2024`. Also needed for `unset_sentinel=True` (J23): it fixed the 3 path failures in that test | applies |
| 🟠 | [J14](inventory.md#j14) | [`fix-str-value-read-as-config`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) | Precedent: the maintainer fixed the same symptom for `os.PathLike` unions (#516/#518). The prototype keeps a path when the file is plain text; it doesn't remove the repeated reads of large files | manual |
| 🟠 | [J04](inventory.md#j04) + [J44](inventory.md#j44) | [`fix-inherited-annotation-namespace`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) | Mirrors upstream's own per-module resolution (#936). File before J27 (same function) | manual (trivial) |
| 🟠 | [J26](inventory.md#j26) | [`fix-tagged-union-instance-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) | Reworked for #1038: switching member discards the old member's values (`C(n=5)` + `{"tag": "b"}` gives `B()`, where 4.49 gave `B(n=5)`). Consistent with #1038 | manual |
| 🟡 | [J27](inventory.md#j27) | [`fix-unevaluable-annotation-fallback`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) | Asks the maintainer whether the fallback to `Unvalidated` should warn instead of logging at DEBUG; no warning added | manual (trivial) |
| 🟡 | [J09](inventory.md#j09) | [`fix-dump-container-defaults`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) | Stricter: a `list[Base]` default holding a subclass instance with extra fields now fails at parse time, like a single `Base = Sub()` default already does | doesn't apply (function not on v4) |
| 🟡 | [J43](inventory.md#j43) | [`fix-parse-object-mutates-input`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) | Also changes one line in `_link_arguments.py`, which relied on the mutation being fixed | manual |
| 🟡 | [J10](inventory.md#j10) | [`fix-parsing-settings-idempotent`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) | Keeps the "unknown name" error, at the cost of one small set; the one-line alternative is in the draft. Getter and scoped API left as follow-ups | applies |
| 🟡 | [J17](inventory.md#j17) | [`fix-protocol-private-members-message`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) | Message-only change; the maintainer may prefer counting private members, or a warning when the parser is built | manual |
| 🟡 | [J47](inventory.md#j47) | [`fix-default-factory-error-context`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) | Re-raises as `ValueError` (same wording as the existing wrapper nearby), so the exception type changes; `add_note` isn't used in the codebase | applies |
| ⚪ | [J39](inventory.md#j39) | [`fix-slotted-dataclass-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-slotted-dataclass-default) | Superseded by J16's commit 2; keep only if J16 isn't filed | manual |

J23 turned out to be intended (see its entry): no issue, just a docs note for
the v5 thread. J12 (issue only, not planned) has no branch.

## Questions to raise inside the PRs or issues

- J01 commit 2: check `Callable` by return type only, or a stricter signature check?
- J10: a public getter for parsing settings, and a scoped setting API (follow-ups).
- J13: should `os.PathLike` reject non-strings?
- J27: warn when a class or field falls back to `Unvalidated`?

## Filing order

Two or three at a time, in README order: J01 and J59 first, both promised in
the comment in the v5 thread (#999), which also carries the J23 docs note; J59
unblocks `unset_sentinel=True` (J23). Then J16, J24 and J15; then J13 (only its
coercion part is left once J59 is in), the J14 issue, J04 + J44 and J26. If
J27 is ever sent, file it after J04, since both
change the same function. The 🟡 items stay local for now.

## Not worked on

J02 (jaxtyping), J18 + J31 (stubs setting), and J33, J34, J35, J36, J37. J31 is
a tested one-line fix if wanted later.
