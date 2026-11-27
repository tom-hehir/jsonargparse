# Fix branches: working notes

Open decisions and questions for each fix branch. The [README](README.md) has the order,
a one-line description, line counts and diff links for each; this file has the
rest. Draft texts are in [`prs/`](prs/) and [`issues/`](issues/); IDs link to
[`inventory.md`](inventory.md).

- **Branches**: on the fork, each cut from upstream `main` at 3b30c14, except
  J59, on `main` at cc53487, and J24, rebased on `main` at 2656bf3.
- **Checks on every branch**: the new tests fail without the fix and pass with
  it; the full upstream suite passes on Python 3.12 and 3.14, apart from 2
  argcomplete tests that also fail on untouched `main` here; changed lines are
  covered; ruff is clean; mypy reports nothing new.
- **Coding agent checkbox**: the PR template asks "If you used a coding agent,
  did you fully understand and validate all generated code". That box is left
  unticked in every draft until the code has been reviewed.
- **PR or issue**: the bug template asks for a PR directly when the bug and its
  fix are understood, so PR is the default. Issue first is for behaviour the
  maintainer may consider intended, or that needs his design choice.

**Priority** (README order): 🟢 merged upstream · 🔵 opened upstream · 🟠 higher priority ·
🟡 lower priority · ⚪ superseded.

## Decisions and flags for each branch

| | ID | Branch (diff on GitHub) | Decisions or flags | Port to v4 |
|---|---|---|---|---|
| 🟢 | [J01](inventory.md#j01) | [`fix-factory-protocol-instances`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances) | Merged as #1043 (2026-11-27). The `Callable[..., Class]` part (old commit 2) is held back on the local branch `fix-callable-class-instances`, since #959 restricted it on purpose; it is not offered in the PR. Doesn't apply to v4 as is | manual |
| 🔵 | [J59](inventory.md#j59) | [`fix-unset-sentinel-none-dump`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unset-sentinel-none-dump) | Moves `NoneType` first in `sort_subtypes_for_union` when the value is `None`. Also fixes the `None` part of J13; the draft mentions J37 as related but leaves it alone | applies |
| 🟠 | [J24](inventory.md#j24) | [`fix-protocol-class-default-dump`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) | Rebased on main 2656bf3 (2026-11-27). Nested class defaults now dump as `class_path` + `init_args`, like a plain field already does. In these positions `instantiate` now gives a `functools.partial` instead of the class, as for a plain field; the draft notes this. Workaround meanwhile: reload configs only with the code version that saved them | source applies |
| 🟠 | [J16](inventory.md#j16) + [J39](inventory.md#j39) | [`fix-default-instance-non-field-attributes`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) · [commit 1](https://github.com/tom-hehir/jsonargparse/commit/59bdc3dc0492680eae30e45116dc19ef83bfd72d) · [commit 2](https://github.com/tom-hehir/jsonargparse/commit/de6966ad159b48415afed833b591d10029906ea6) | Commit 2 reads `__init__` parameters with `getattr`, which also fixes slotted dataclasses (J39) on the same lines. Can be split if wanted | manual |
| 🟠 | [J14](inventory.md#j14) | [`fix-str-value-read-as-config`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) | Precedent: the maintainer fixed the same symptom for `os.PathLike` unions (#516/#518). The prototype keeps a path when the file is plain text; it doesn't remove the repeated reads of large files | manual |
| 🟠 | [J04](inventory.md#j04) + [J44](inventory.md#j44) | [`fix-inherited-annotation-namespace`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) | Mirrors upstream's own per-module resolution (#936). Changes the same function as J27 | manual (trivial) |
| 🟠 | [J15](inventory.md#j15) | [`fix-subscripted-generic-init-args`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) | none | manual (3 lines) |
| 🟠 | [J26](inventory.md#j26) | [`fix-tagged-union-instance-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) | Reworked for #1038: switching member discards the old member's values (`C(n=5)` + `{"tag": "b"}` gives `B()`, where 4.49 gave `B(n=5)`). Consistent with #1038 | manual |
| 🟡 | [J13](inventory.md#j13) | [`fix-pathlike-coercion`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) | Whether `os.PathLike` should reject `7` or lists is left as a question: rejecting would break numeric paths like `path: 2024`. The 3 path failures it fixed with `unset_sentinel=True` (J23) are also fixed by #1044 | applies |
| 🟡 | [J43](inventory.md#j43) | [`fix-parse-object-mutates-input`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) | Also changes one line in `_link_arguments.py`, which relied on the mutation being fixed | manual |
| 🟡 | [J09](inventory.md#j09) | [`fix-dump-container-defaults`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) | Stricter: a `list[Base]` default holding a subclass instance with extra fields now fails at parse time, like a single `Base = Sub()` default already does | doesn't apply (function not on v4) |
| 🟡 | [J27](inventory.md#j27) | [`fix-unevaluable-annotation-fallback`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) | Asks the maintainer whether the fallback to `Unvalidated` should warn instead of logging at DEBUG; no warning added | manual (trivial) |
| 🟡 | [J17](inventory.md#j17) | [`fix-protocol-private-members-message`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) | Message-only change; the maintainer may prefer counting private members, or a warning when the parser is built | manual |
| 🟡 | [J10](inventory.md#j10) | [`fix-parsing-settings-idempotent`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) | Keeps the "unknown name" error, at the cost of one small set; the one-line alternative is in the draft. Getter and scoped API left as follow-ups | applies |
| 🟡 | [J47](inventory.md#j47) | [`fix-default-factory-error-context`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) | Re-raises as `ValueError` (same wording as the existing wrapper nearby), so the exception type changes; `add_note` isn't used in the codebase | applies |
| ⚪ | [J39](inventory.md#j39) | [`fix-slotted-dataclass-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-slotted-dataclass-default) | Superseded by J16's commit 2; keep only if J16 isn't filed | manual |

J23 turned out to be intended (see its entry). J12 has an issue draft and no
branch.

## Open questions

- J01's held-back `Callable` part: check `Callable` by return type only, or a stricter signature check?
- J10: a public getter for parsing settings, and a scoped setting API (follow-ups).
- J13: should `os.PathLike` reject non-strings?
- J27: warn when a class or field falls back to `Unvalidated`?

## Dependencies between branches

- J59's fix also covers the `None` part of J13, so with J59 merged only J13's
  coercion part remains.
- J27 and J04 change the same function, so whichever is merged second needs
  rebasing.

## No fix branch

J02 (jaxtyping), J18 + J31 (stubs setting), and J33, J34, J35, J36, J37. J31 has
a tested one-line fix.
