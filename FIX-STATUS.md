# Fix work for shortlist (a): status

Branches pushed to the fork 2026-11-26; no issues or PRs opened. Every branch is
cut from upstream `main` at 3b30c14 and lives in its own worktree under
`.claude/worktrees/<branch>`, and is pushed to the fork (2026-11-26). Each
branch name links to its diff against upstream `main` on GitHub; for the two
branches with two commits there are also links to each commit. PR drafts are in
[`prs/`](prs/), issue drafts in [`issues/`](issues/). IDs link to
[`inventory.md`](inventory.md).

**Checks run on every branch**: the new tests fail without the fix and pass with
it; the full upstream suite passes on Python 3.12 and 3.14 (apart from 2
argcomplete tests that also fail on untouched main in this environment);
changed lines are covered; ruff is clean and mypy reports no new errors.

**Upstream's guidance**: the bug template asks for a PR directly when the bug
and its fix are understood, so the default below is "PR". "Issue first" is kept
for things the maintainer may consider intended, or that need his design choice.

Before filing anything: the PR template asks "If you used a coding agent, did
you fully understand and validate all generated code". That box is left
unticked in every draft for you to tick after your own review.

## Branches

| # | ID | Branch | Commits | Recommendation | Decisions or flags for you | v4 |
|---|---|---|---|---|---|---|
| 1 | [J01](inventory.md#j01) | [`fix-factory-protocol-instances`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances) | 2 | **PR** for commit 1 (Protocol). **Issue first** for commit 2 (`Callable`) | Commit 2 relaxes a check added on purpose in 4.52 (#959) and checks `Callable` by return type only, as for functions. It can be dropped without affecting commit 1 | manual port |
| 2 | [J04](inventory.md#j04) + [J44](inventory.md#j44) | [`fix-inherited-annotation-namespace`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) | 1 | **PR** | Mirrors upstream's own per-module resolution (#936). File before J27 (same function) | manual (trivial) |
| 3 | [J15](inventory.md#j15) | [`fix-subscripted-generic-init-args`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) | 1 | **PR** | none | manual (3 lines) |
| 4 | [J14](inventory.md#j14) | [`fix-str-value-read-as-config`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) (prototype) | 1 | **Issue first**: [issues/str-value-read-as-config.md](issues/str-value-read-as-config.md) | Precedent: the maintainer fixed the same symptom for `os.PathLike` unions (#516/#518). The prototype keeps a path when the file is plain text; it doesn't remove the repeated reads of large files | manual |
| 5 | [J16](inventory.md#j16) (+ [J39](inventory.md#j39)) | [`fix-default-instance-non-field-attributes`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) | 2 | **PR** | Commit 2 reads `__init__` parameters with `getattr`, which also fixes slotted dataclasses (J39) on the same lines. Can be split if wanted | manual |
| 6 | [J27](inventory.md#j27) | [`fix-unevaluable-annotation-fallback`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) | 1 | **PR**, after J04 | Asks the maintainer whether the fallback to `Unvalidated` should warn instead of logging at DEBUG; no warning added | manual (trivial) |
| 7 | [J09](inventory.md#j09) | [`fix-dump-container-defaults`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) | 1 | **PR** | Stricter: a `list[Base]` default holding a subclass instance with extra fields now fails at parse time, like a single `Base = Sub()` default already does | doesn't apply (function not on v4) |
| 8 | [J10](inventory.md#j10) | [`fix-parsing-settings-idempotent`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) | 1 | **PR** | Keeps the "unknown name" error, at the cost of one small set; the one-line alternative is in the draft. Getter and scoped API left as follow-ups | applies |
| 9 | [J13](inventory.md#j13) | [`fix-pathlike-coercion`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) | 1 | **PR** (CLI `null` only) | Whether `os.PathLike` should reject `7` or lists is left as a question: rejecting would break numeric paths like `path: 2024` | applies |
| 10 | [J24](inventory.md#j24) | [`fix-protocol-class-default-dump`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) | 1 | **PR**, with the design point in the text | Nested class defaults now dump as `class_path` + `init_args`, like a plain field already does; the alternative (bare path) is offered | source applies |
| 11 | [J26](inventory.md#j26) | [`fix-tagged-union-instance-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) | 1 | **PR with an explicit question**, or issue first | Reworked for #1038: switching member discards the old member's values (`C(n=5)` + `{"tag": "b"}` gives `B()`, where 4.49 gave `B(n=5)`). Consistent with #1038 | manual |
| 15 | [J17](inventory.md#j17) | [`fix-protocol-private-members-message`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) | 1 | **Issue first** | Message-only change; the maintainer may prefer counting private members, or a warning when the parser is built | manual |
| 16 | [J43](inventory.md#j43) | [`fix-parse-object-mutates-input`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) | 1 | **PR** | Also changes one line in `_link_arguments.py`, which relied on the mutation being fixed | manual |
| 16 | [J39](inventory.md#j39) | [`fix-slotted-dataclass-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-slotted-dataclass-default) | 1 | Superseded by J16's commit 2 | Keep only if J16 isn't filed | manual |
| 16 | [J47](inventory.md#j47) | [`fix-default-factory-error-context`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) | 1 | **Small PR or issue first** | Re-raises as `ValueError` (same wording as the existing wrapper nearby), so the exception type changes; `add_note` isn't used in the codebase | applies |

## Size of each change

Lines added / removed against upstream `main`. **Code** is the library
(`jsonargparse/`), **Tests** includes test helper modules and `conftest.py`,
**Docs** is `DOCUMENTATION.rst`, **Changelog** is `CHANGELOG.rst`.

| ID | Diff | Code | Tests | Docs | Changelog | Source files changed |
|---|---|---|---|---|---|---|
| [J01](inventory.md#j01) | [all](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances) · [commit 1](https://github.com/tom-hehir/jsonargparse/commit/d13b66eed01b61708c81c883c473d213f0d27fa9) · [commit 2](https://github.com/tom-hehir/jsonargparse/commit/4d05a3e431a043528962dbdb8f858598e4f35164) | +23 −4 | +49 | — | +7 | `_typehints.py` |
| [J04](inventory.md#j04) + [J44](inventory.md#j44) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) | +18 −7 | +40 −1 | — | +5 | `_postponed_annotations.py` |
| [J15](inventory.md#j15) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) | +3 −4 | +27 | — | +4 | `_typehints.py` |
| [J14](inventory.md#j14) (prototype) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) | +2 | +32 | — | +4 | `_typehints.py` |
| [J16](inventory.md#j16) + [J39](inventory.md#j39) | [all](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) · [commit 1](https://github.com/tom-hehir/jsonargparse/commit/59bdc3dc0492680eae30e45116dc19ef83bfd72d) · [commit 2](https://github.com/tom-hehir/jsonargparse/commit/de6966ad159b48415afed833b591d10029906ea6) | +8 −1 | +45 | — | +8 | `_signatures.py` |
| [J27](inventory.md#j27) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) | +16 −1 | +27 | — | +4 | `_postponed_annotations.py` |
| [J09](inventory.md#j09) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) | +13 −1 | +65 | — | +3 | `_signatures.py`, `_typehints.py` |
| [J10](inventory.md#j10) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) | +5 −2 | +9 | +4 −4 | +3 | `_common.py` |
| [J13](inventory.md#j13) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) | +8 −1 | +8 | — | +3 | `typing.py` |
| [J24](inventory.md#j24) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) | +3 −1 | +27 −1 | — | +4 | `_typehints.py` |
| [J26](inventory.md#j26) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) | +5 −1 | +36 −1 | — | +4 | `_typehints.py` |
| [J17](inventory.md#j17) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) | +8 −1 | +15 | — | +3 | `_typehints.py` |
| [J43](inventory.md#j43) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) | +5 −3 | +16 | — | +3 | `_typehints.py`, `_link_arguments.py` |
| [J39](inventory.md#j39) (superseded) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-slotted-dataclass-default) | +5 −1 | +15 | — | +3 | `_signatures.py` |
| [J47](inventory.md#j47) | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) | +4 −1 | +21 | — | +3 | `_signatures.py` |

The library changes are small: 1 to 23 added lines each, about 120 in total
across the 14 branches to be filed (excluding superseded J39). Most of each diff is tests.

## Issue only (no branch)

| # | ID | Draft | Why not a PR |
|---|---|---|---|
| — | [J23](inventory.md#j23) | [issues/required-nullable-null.md](issues/required-nullable-null.md) | Needs the maintainer to choose how "not given" is represented; time-sensitive (before 5.0) |
| 13 | [J12](inventory.md#j12) | [issues/error-message-wording.md](issues/error-message-wording.md) | Main already fixed most of it; two wording suggestions left. Could be a comment in #999 instead |

## Questions to raise inside PRs or issues (not separate items)

- J01 commit 2: return-type-only check for `Callable`, or a stricter signature check?
- J10: a public getter for parsing settings, and a scoped setting API (follow-ups).
- J13: should `os.PathLike` reject non-strings?
- J27: warn when a class or field falls back to `Unvalidated`?

## Filing order (suggested)

Two or three at a time. J23 first (time-sensitive for 5.0), with J01 commit 1,
J04 + J44 and J15. Then J16, J27, J09, J24, J26. Then the small ones: J10, J13,
J43, J47, and the issue-first items J14 and J17.

## Not worked on (from the shortlist)

12 (J02 jaxtyping), 14 (J18 + J31, stubs setting), 17 (J35, J37, J33, J36,
J34). J31 is a tested one-line fix if wanted later.
