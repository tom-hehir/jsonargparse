# Fix work for shortlist (a): status

Branches pushed to the fork 2026-11-26; no issues or PRs opened. Every branch is
cut from upstream `main` at 3b30c14 and lives in its own worktree under
`.claude/worktrees/<branch>`. Diff links go to GitHub, against upstream `main`;
the two branches with two commits also link to each commit. PR drafts are in
[`prs/`](prs/), issue drafts in [`issues/`](issues/). IDs link to
[`inventory.md`](inventory.md).

**Priority** (from your triage of the shortlist):
🔴 high: shortlist 1–3, and J23 (time-sensitive for 5.0) ·
🟠 medium: the ones marked "worth doing" ·
🟡 lower: the ones marked "maybe" ·
⚪ superseded.

## Overview

Sorted by priority. **Sev** is the inventory severity. Line counts are added /
removed against upstream `main`: **Code** is the library (`jsonargparse/`),
**Tests** includes test helper modules and `conftest.py`, **Docs** is
`DOCUMENTATION.rst`, **CL** is `CHANGELOG.rst`.

| | ID | What it fixes | Sev | Recommendation | Code | Tests | Docs | CL | Diff |
|---|---|---|---|---|---|---|---|---|---|
| 🔴 | [J01](inventory.md#j01) | A callable Protocol (or `Callable[..., Class]`) rejects classes whose instances implement it | S1 | **PR** (commit 1), **issue first** (commit 2) | +23 −4 | +49 | — | +7 | [all](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances) · [commit 1](https://github.com/tom-hehir/jsonargparse/commit/d13b66eed01b61708c81c883c473d213f0d27fa9) · [commit 2](https://github.com/tom-hehir/jsonargparse/commit/4d05a3e431a043528962dbdb8f858598e4f35164) |
| 🔴 | [J04](inventory.md#j04) + [J44](inventory.md#j44) | A dataclass with a base from another module loses validation of every field, or binds a field to the wrong class | S1 | **PR** | +18 −7 | +40 −1 | — | +5 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) |
| 🔴 | [J15](inventory.md#j15) | A subscripted generic (`Model[int]`) rejects a subclass's own `init_args` | S2 | **PR** | +3 −4 | +27 | — | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) |
| 🔴 | [J23](inventory.md#j23) | v5: a required `X \| None` parameter can't be given `null` | S2 | **Issue only** | — | — | — | — | [issue draft](issues/required-nullable-null.md) |
| 🟠 | [J14](inventory.md#j14) | A `str` value naming an existing file is replaced by the file's contents | S2 | **Issue first** (prototype) | +2 | +32 | — | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) · [issue draft](issues/str-value-read-as-config.md) |
| 🟠 | [J16](inventory.md#j16) + [J39](inventory.md#j39) | Dataclass defaults with derived attributes (`__post_init__`, `init=False`), or with `slots=True`, are rejected | S2 | **PR** | +8 −1 | +45 | — | +8 | [all](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) · [commit 1](https://github.com/tom-hehir/jsonargparse/commit/59bdc3dc0492680eae30e45116dc19ef83bfd72d) · [commit 2](https://github.com/tom-hehir/jsonargparse/commit/de6966ad159b48415afed833b591d10029906ea6) |
| 🟠 | [J27](inventory.md#j27) | One unevaluable annotation silently disables validation of the whole class | S2 | **PR**, after J04 | +16 −1 | +27 | — | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) |
| 🟠 | [J09](inventory.md#j09) | Lists, tuples and dicts of dataclass defaults dump as unreloadable text | S2 | **PR** | +13 −1 | +65 | — | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) |
| 🟠 | [J13](inventory.md#j13) | A command-line `null` for `os.PathLike \| None` becomes the string `"None"` | S2 | **PR** | +8 −1 | +8 | — | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) |
| 🟠 | [J24](inventory.md#j24) | A Protocol field's class default, nested in a union or dataclass, is saved without its hyperparameters | S2 | **PR**, design point in text | +3 −1 | +27 −1 | — | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) |
| 🟠 | [J26](inventory.md#j26) | A tagged union with an instance default rejects values for another member | S2 | **PR with a question**, or issue first | +5 −1 | +36 −1 | — | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) |
| 🟡 | [J10](inventory.md#j10) | Calling `set_parsing_settings(subclasses_enabled=[...])` twice raises | S2 | **PR** | +5 −2 | +9 | +4 −4 | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) |
| 🟡 | [J12](inventory.md#j12) | Two error messages that point away from the cause | S2 | **Issue only** (or a #999 comment) | — | — | — | — | [issue draft](issues/error-message-wording.md) |
| 🟡 | [J17](inventory.md#j17) | Unhelpful error for a Protocol whose members all start with `_` | S2 | **Issue first** | +8 −1 | +15 | — | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) |
| 🟡 | [J43](inventory.md#j43) | `parse_object` modifies the caller's lists and dicts in place | S3 | **PR** | +5 −3 | +16 | — | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) |
| 🟡 | [J47](inventory.md#j47) | A failing `default_factory` raises with no hint of which class or field | S3 | **Small PR** or issue first | +4 −1 | +21 | — | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) |
| ⚪ | [J39](inventory.md#j39) | A slotted dataclass default crashes (now in J16's commit 2) | S3 | Superseded | +5 −1 | +15 | — | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-slotted-dataclass-default) |

The library changes are small: 2 to 23 added lines each, about 120 in total
across the 14 branches to be filed. Most of each diff is tests.

**Checks run on every branch**: the new tests fail without the fix and pass with
it; the full upstream suite passes on Python 3.12 and 3.14 (apart from 2
argcomplete tests that also fail on untouched main in this environment);
changed lines are covered; ruff is clean and mypy reports no new errors.

## Decisions and flags for each branch

Same order as above.

| | ID | Branch | Decisions or flags for you | v4 |
|---|---|---|---|---|
| 🔴 | [J01](inventory.md#j01) | [`fix-factory-protocol-instances`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances) | Commit 2 (`Callable`) relaxes a check added on purpose in 4.52 (#959) and checks `Callable` by return type only, as for functions. It can be dropped without affecting commit 1 | manual port |
| 🔴 | [J04](inventory.md#j04) + [J44](inventory.md#j44) | [`fix-inherited-annotation-namespace`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) | Mirrors upstream's own per-module resolution (#936). File before J27 (same function) | manual (trivial) |
| 🔴 | [J15](inventory.md#j15) | [`fix-subscripted-generic-init-args`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) | none | manual (3 lines) |
| 🟠 | [J14](inventory.md#j14) | [`fix-str-value-read-as-config`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) | Precedent: the maintainer fixed the same symptom for `os.PathLike` unions (#516/#518). The prototype keeps a path when the file is plain text; it doesn't remove the repeated reads of large files | manual |
| 🟠 | [J16](inventory.md#j16) + [J39](inventory.md#j39) | [`fix-default-instance-non-field-attributes`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) | Commit 2 reads `__init__` parameters with `getattr`, which also fixes slotted dataclasses (J39) on the same lines. Can be split if wanted | manual |
| 🟠 | [J27](inventory.md#j27) | [`fix-unevaluable-annotation-fallback`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) | Asks the maintainer whether the fallback to `Unvalidated` should warn instead of logging at DEBUG; no warning added | manual (trivial) |
| 🟠 | [J09](inventory.md#j09) | [`fix-dump-container-defaults`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) | Stricter: a `list[Base]` default holding a subclass instance with extra fields now fails at parse time, like a single `Base = Sub()` default already does | doesn't apply (function not on v4) |
| 🟠 | [J13](inventory.md#j13) | [`fix-pathlike-coercion`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) | Whether `os.PathLike` should reject `7` or lists is left as a question: rejecting would break numeric paths like `path: 2024` | applies |
| 🟠 | [J24](inventory.md#j24) | [`fix-protocol-class-default-dump`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) | Nested class defaults now dump as `class_path` + `init_args`, like a plain field already does; the alternative (bare path) is offered | source applies |
| 🟠 | [J26](inventory.md#j26) | [`fix-tagged-union-instance-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) | Reworked for #1038: switching member discards the old member's values (`C(n=5)` + `{"tag": "b"}` gives `B()`, where 4.49 gave `B(n=5)`). Consistent with #1038 | manual |
| 🟡 | [J10](inventory.md#j10) | [`fix-parsing-settings-idempotent`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) | Keeps the "unknown name" error, at the cost of one small set; the one-line alternative is in the draft. Getter and scoped API left as follow-ups | applies |
| 🟡 | [J17](inventory.md#j17) | [`fix-protocol-private-members-message`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) | Message-only change; the maintainer may prefer counting private members, or a warning when the parser is built | manual |
| 🟡 | [J43](inventory.md#j43) | [`fix-parse-object-mutates-input`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) | Also changes one line in `_link_arguments.py`, which relied on the mutation being fixed | manual |
| 🟡 | [J47](inventory.md#j47) | [`fix-default-factory-error-context`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) | Re-raises as `ValueError` (same wording as the existing wrapper nearby), so the exception type changes; `add_note` isn't used in the codebase | applies |
| ⚪ | [J39](inventory.md#j39) | [`fix-slotted-dataclass-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-slotted-dataclass-default) | Superseded by J16's commit 2; keep only if J16 isn't filed | manual |

**Upstream's guidance**: the bug template asks for a PR directly when the bug
and its fix are understood, so the default is "PR". "Issue first" is kept for
things the maintainer may consider intended, or that need his design choice.

Before filing anything: the PR template asks "If you used a coding agent, did
you fully understand and validate all generated code". That box is left
unticked in every draft for you to tick after your own review.

## Questions to raise inside PRs or issues (not separate items)

- J01 commit 2: return-type-only check for `Callable`, or a stricter signature check?
- J10: a public getter for parsing settings, and a scoped setting API (follow-ups).
- J13: should `os.PathLike` reject non-strings?
- J27: warn when a class or field falls back to `Unvalidated`?

## Filing order (suggested)

Two or three at a time. 🔴 first: J23 (time-sensitive for 5.0), J01 commit 1,
J04 + J44 and J15. Then 🟠: J16, J27, J09, J24, J26, J13, and the J14 issue.
Then 🟡: J10, J43, J47, and the issue-first J17 and J12.

## Not worked on (from the shortlist)

12 (J02 jaxtyping), 14 (J18 + J31, stubs setting), 17 (J35, J37, J33, J36,
J34). J31 is a tested one-line fix if wanted later.
