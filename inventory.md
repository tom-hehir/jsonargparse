# jsonargparse pain-point inventory

Six of our research projects use jsonargparse for training and pipeline
configs: nested dataclasses with
`set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])`, `class_path`
values four to six levels deep, callable Protocols, generics, and LightningCLI.
This inventory lists every jsonargparse problem those projects hit or would hit,
ranked by what it cost us.

- **Versions checked**: 4.51.0, 4.53.0 (latest v4), 5.0.0rc2 plus main at
  29d6f00 ("v5" below). Some boundaries also on 4.50.0, 4.52.0 and 4.49.
- **Date**: 2026-11-24; updated 2026-11-26 ([J21](#j21) fixed upstream and verified on main).
- **Method**: the projects' code, history, notes and agent transcripts were
  surveyed for workarounds, pins and incidents. Each candidate was then
  re-checked with a standalone script on each version, and the projects' test
  suites and CLIs were run against v5 in separate environments. "Hit in N of 6"
  counts the projects where we found code, a pin or an incident caused by the
  issue.
- **See also**: the public tracker [README.md](README.md) (fix branches, draft
  PRs) and [repros/](repros/) (one standalone script per issue, with a results
  table).

> [!IMPORTANT]
> **At a glance**: 52 open issues (🔴 5 S1 · 🟠 18 S2 · 🟡 18 S3 · ⚪ 11 S4), 5 resolved upstream (🟢), and one checked and found not to be a jsonargparse issue. Start with the [shortlist](#shortlist); every issue ID links to its detailed entry.

<a id="contents"></a>

## Contents

- [How to read this](#how-to-read-this)
- [🔴 Open issues](#open-issues)
  - [Shortlist](#shortlist): [(a) bug fixes](#shortlist-a) · [(b) design requests](#shortlist-b) · [(c) v5 feedback](#shortlist-c)
  - [Overview of open issues](#overview)
  - [Detailed entries](#open-details): [Bugs](#kind-bugs) · [Intended or documented behaviour that is awkward](#kind-intended-or-documented-behaviour-that-is-awkward) · [Missing features](#kind-missing-features) · [Regressions and pins](#kind-regressions-and-pins) · [LightningCLI interplay](#kind-lightningcli-interplay) · [v5 migration](#kind-v5-migration) · [Warning noise](#kind-warning-noise)
- [🟢 Resolved upstream](#resolved)
- [Checked, not an issue](#not-an-issue)
- [Relationship to README.md](#readme-corrections)

<a id="how-to-read-this"></a>

## How to read this

**Colours**

| | Meaning |
|---|---|
| 🔴 🟠 🟡 ⚪ | Severity S1, S2, S3, S4 (below) |
| ❌ ✅ | Per version: the problem is present / absent or fixed |
| 🔧 and a blue *Note* box | Work begun: our own fix branch or upstream PR |
| 🟢 and a green *Tip* box | Fixed upstream (merged; the entry says whether it is released) |

**Severity**

| | Meaning |
|---|---|
| 🔴 S1 | Silent wrong values or silent loss of validation in normal use, or it blocks an upgrade |
| 🟠 S2 | Forces an ugly or fragile workaround, or is a recurring time sink; or silent but needs an unusual trigger |
| 🟡 S3 | Real but contained, or has a clean workaround |
| ⚪ S4 | Cosmetic, noise, rare, or a non-issue kept for the record |

**Kind**: bug · intended-but-awkward (documented or deliberate behaviour that
hurts) · missing-feature · performance · error-message · regression-or-pin ·
lightning-interplay · v5-migration · warning-noise.

**Fix effort**: trivial (a few lines) · small (under about 50 lines plus tests,
or a fix branch exists) · medium (several code paths or a design choice) ·
design-change · done (fixed upstream) · n/a.

**Upstream appetite**: likely-bug (a maintainer would probably take a fix) ·
debatable (defensible either way) · intended (documented or deliberate; at
most a docs change or an opt-in).

🔧 *Work begun* marks the open issues we had already started fixing (fix
branches, or our own upstream PR). They are ranked where their impact puts
them, as if no work had started. Once a fix is merged upstream, the issue
moves to [Resolved upstream](#resolved).

**Status** per version: ❌ the problem is present, ✅ absent or fixed, – not
applicable, ? not checked. Line references are to v5 (5.0.0rc2 + 29d6f00)
unless marked.

[↑ Contents](#contents)

---

<a id="open-issues"></a>

# 🔴 Open issues

<a id="shortlist"></a>

## Shortlist

Ranked by impact on our work: forced ugly workarounds, or patterns we wanted but
couldn't use. Issues with a clean workaround are down-ranked.

<a id="shortlist-a"></a>

### (a) Upstream bug fixes likely to be accepted

| # | ID | Why it matters | Sev | Effort | Appetite |
|---|---|---|---|---|---|
| 1 | [J01](#j01) | A callable Protocol (or `Callable[..., Class]`) rejects classes whose instances implement it, even as the field's own default. Keeps 3 of 6 projects off 4.52+ and v5; a fourth gave up its return types. 🔧 *Work begun: branch `fix-factory-protocol-instances`, draft PR in `prs/`; commit 1 covers Protocols, a separable commit 2 the `Callable` case.* | 🔴 S1 | small | likely-bug |
| 2 | [J04](#j04) + [J44](#j44) | Inherited dataclass fields are resolved in the wrong module's namespace: every field of a class silently unvalidated ([J04](#j04)), or a field bound to the wrong class ([J44](#j44)). 🔧 *Work begun: branch `fix-inherited-annotation-namespace`, draft PR in `prs/`.* | 🔴 S1 | small | likely-bug |
| 3 | [J15](#j15) | A subscripted generic annotation (`Codec[Spectrum]`) rejects a subclass's own `init_args`, so the precise annotation can't be used. One project added per-type marker ABCs instead (15 files, +293 lines, plus a review rule). 🔧 *Work begun: branch `fix-subscripted-generic-init-args`, draft PR in `prs/`.* | 🟠 S2 | small | likely-bug |
| 4 | [J14](#j14) | A `str \| SomeClass` value naming an existing file is replaced by the file's contents, silently; a multi-GB file is read several times (one incident hung a run). Forced a path-alias convention in 28 files across 4 projects. | 🟠 S2 | small | likely-bug |
| 5 | [J16](#j16) | A dataclass default with derived attributes (`__post_init__`, `init=False`) is rejected under `Optional`, unions or subclass mode. It forced a registry redesign, and 9 of 223 dataclasses in one project can't be used as defaults. 🔧 *Work begun: branch `fix-default-instance-non-field-attributes`, draft PR in `prs/`.* | 🟠 S2 | small | likely-bug |
| 6 | [J27](#j27) | One unevaluable annotation (a quoted name inside `\|`) leaves every field of the class silently unvalidated. **Quick win** alongside: warn, not DEBUG-log, when a class falls back to `Unvalidated` (would have caught [J04](#j04) too). | 🟠 S2 | small | likely-bug |
| 7 | [J09](#j09) | Lists/dicts of dataclass defaults dump as "Unable to serialize instance" text that doesn't reload. Forced `None` defaults that hide the effective value from `--print_config`. | 🟠 S2 | small | likely-bug |
| 8 | [J10](#j10) | `set_parsing_settings(subclasses_enabled=[...])` raises on a second identical call, with no public getter. 3 projects copy private-import save/restore helpers; one release broke on it. **Quick win** (idempotence, getter). | 🟠 S2 | small | likely-bug |
| 9 | [J13](#j13) | `os.PathLike` stringifies anything; CLI `null` becomes `"None"` (a run staged into `./None`). **Quick win**. | 🟠 S2 | small | likely-bug |
| 10 | [J24](#j24) | A class default for a Protocol field inside a dataclass default or union dumps as a bare import path, so saved configs omit hyperparameters and silently follow later code-default changes. | 🟠 S2 | small | likely-bug |
| 11 | [J26](#j26) | A tagged union of dataclasses with an instance default rejects values for another member (a 4.50 regression); one project capped below 4.50 for a while. 🔧 *Work begun: branch `fix-tagged-union-instance-default`, draft PR in `prs/`.* | 🟠 S2 | small | likely-bug |
| 12 | [J02](#j02) | jaxtyping annotations never compare equal in Protocol matching; Modules need `-> Any`. 2 projects gave up typed returns. | 🟠 S2 | small | likely-bug (jaxtyping) |
| 13 | [J12](#j12) | Errors bury the cause under wrapper lines for plain dataclasses and repeated value dumps (2-17 KB). Three concrete message fixes. | 🟠 S2 | medium | likely-bug |
| 14 | [J18](#j18) + [J31](#j31) | The stubs setting is read once ([J18](#j18)) and makes sklearn's `Ridge` lose all parameters ([J31](#j31)). Two **quick wins** (reset the cached resolver; `skip=skip \| {name}`), which together make the clean route for typed C builtins usable. | 🟠 S2/S3 | trivial | likely-bug |
| 15 | [J17](#j17) | A Protocol with only `_` members matches nothing, with an unhelpful message. **Quick win** for the message; variance is debatable. | 🟠 S2 | trivial | likely-bug (message) |
| 16 | [J43](#j43), [J39](#j39), [J47](#j47) | `parse_object` mutates list/dict inputs; slotted dataclass defaults crash; a failing `default_factory` gives no context. **Quick wins**. | 🟡 S3 | trivial | likely-bug |
| 17 | [J35](#j35), [J37](#j37), [J33](#j33), [J36](#j36), [J34](#j34) | Stale `--config` in nested parsers; `register_type` serializer applied by union arm (silent data loss if used); quoted PEP 695 aliases; tuple keys; docstring-parser failure dropping parameters. | 🟡 S3 | small | likely-bug |

[J23](#j23) (v5) is in [(c)](#shortlist-c). [J08](#j08), ranked 3rd before, is now [resolved upstream](#resolved). A patch for [J31](#j31) was prototyped during this investigation but has no branch; [J39](#j39)'s fix is part of the [J16](#j16) branch.

<a id="shortlist-b"></a>

### (b) Design-level requests (debatable or intended)

| ID | Ask | For | Against | Sev |
|---|---|---|---|---|
| [J06](#j06) | Document the per-key merge of dict fields; offer an opt-in deep merge with a delete marker | Silent key loss; inconsistent with dotted overrides; one project generates ~50 standalone configs from a ~1,600-line script to avoid overlays | Replace is documented and pinned by tests (incl. `__include__`); a merge needs a delete syntax | 🔴 S1 |
| [J05](#j05) | Warn or raise when a plain-class instance default can't serve as the base for overrides (or recover its args) | Silent wrong value from the most natural way to write a default | "Use `lazy_instance`" is a documented answer | 🔴 S1 |
| [J25](#j25) | Merge section files given to a parent group like whole-tree configs, or document the difference | Silent resets of nullable sections | Consistent with "a value replaces"; v5 `__include__` composes correctly | 🟠 S2 |
| [J19](#j19) | A pre-validation interpolation hook, or document `set_loader` for env expansion | 5 of 6 projects hand-roll placeholder strategies | omegaconf mode exists; `set_loader` already works for config files | 🟠 S2 |
| [J20](#j20) | A spec-only type (e.g. `Spec[T]`) that validates a `class_path` but returns the spec | One project wrote and later removed a ~700-line deferred-recipe layer | New API surface; `lazy_instance` partly covers it | 🟠 S2 |
| [J11](#j11) | Under subclass mode, keep reading section files and list nested options in `--help` | The mode is the only way to get `class_path` on dataclasses | The field really is subclass-typed then | 🟠 S2 |
| [J30](#j30) | Treat `Any`/`object` values as data (no Namespace conversion, no filling, no mutation) | Consumers get Namespaces with filled defaults they never wrote | v5 already turns instantiation off; some users want filling | 🟡 S3 |
| [J22](#j22) | Keep explicit `null`s that differ from the default in `dump()` | Lossy default dump | `skip_unset=False` is a clean workaround on 4.x and v5 | 🟡 S3 |
| [J41](#j41) | Dotted overrides and links into list indices (and links into dict keys) | Lists of stages can't be patched from the CLI | Medium effort; `+=` append exists | 🟡 S3 |
| [J38](#j38) | Accept a function `class_path` whose return is a TypeVar bound by the field type | Loader functions with a generic return can't be used | Narrow use | 🟡 S3 |
| [J40](#j40) | Optional strict mode: `null` only for nullable types | Catches `x: null` meant as "default" | Documented meaning of `null` | 🟡 S3 |

<a id="shortlist-c"></a>

### (c) v5 feedback for the RC thread (mauvilsa/jsonargparse#999)

1. **[J23](#j23), required `X | None` can't take `null`** (S2, likely-bug, time-sensitive).
   v5 makes such parameters required, but `check_required` (`_core.py:1398`)
   treats `None` as unset, so `count: null`, `--x.count=null` and
   `init_args: {count: null}` all fail with "the following arguments are
   required"; a `skip_unset=False` dump that writes `null` no longer reloads.
   Hit in 2 of 6 projects (7 and 14 test failures). `unset_sentinel=True` makes
   it work; flipping that default fails 111 upstream tests, so there is no
   one-line fix. Ask: decide the representation, and meanwhile name
   `unset_sentinel=True` in the deprecation message and migration guide.
2. **[J01](#j01) also covers `Callable[..., Class]`**: since 4.52 (not v5; an
   earlier note here blamed #1033), a class whose instances are the callable is
   rejected for `Callable[[int], Base]`, as for callable Protocols. The fix
   branch now has a separate second commit for the `Callable` case, which
   relaxes a check added on purpose in 4.52 (#959), so it is a question for
   the maintainer rather than plain feedback.
3. **LightningCLI is not v5-ready** ([J07](#j07)). Lightning 2.6.x calls
   `add_instantiator`, `instantiate_classes` and `skip_none`; Lightning main
   still calls the per-parser `add_instantiator` and pins
   `jsonargparse <4.51.0` in `requirements/pytorch/extra.txt`. The draft
   Lightning-AI/pytorch-lightning#22014 covers it. Lightning caps `<5` only in
   its extras, so a fresh install of a project without its own `<5` will pick
   v5 and break. `--help` and `--print_config` still work, which gives false
   confidence. Ask: a guide note on LightningCLI status, and confirmation that
   `instantiate(..., instantiators=...)` is stable API. A shim mapping
   `skip_none=False` to `skip_unset=False` produced an identical saved
   `config.yaml` and checkpoint hparams in a small test.
4. **Migration-guide gaps** ([J45](#j45)): the `add_instantiator` row says use
   `instantiators=` while the v4 deprecation text says use the global function;
   `merge_config` is called "internal API" but was public; subclasses that
   override `instantiate(self, namespace, instantiate_groups=True)` must now
   forward `**kwargs`; untyped constructor parameters of third-party classes
   (sklearn meta-estimators) now receive a `Namespace` and fail with
   `'Namespace' object has no attribute '__sklearn_tags__'` ([J30](#j30)); the union
   error no longer starts with "Does not validate against any of the Union
   subtypes", which downstream code matched on ([J28](#j28)); the `omegaconf>=2.4.0`
   floor is only in the changelog; removed methods give a bare `AttributeError`
   (a `__getattr__` pointing to the guide would help).
5. **`JSONARGPARSE_DEBUG=1` raises** `ValueError: Invalid boolean value`, so a
   common way of enabling debug output aborts the program. This is by design
   since 4.47 (only `true`/`false` accepted) and the same on 4.51, 4.53 and v5,
   so it is not a v5 regression; accepting `1`/`0` or warning instead would be
   kinder.
6. **The `_deprecated` warning path** ([J48](#j48)): projects filter Lightning-triggered
   warnings with `jsonargparse._deprecated.JsonargparseDeprecationWarning` in
   pytest; on v5 pytest reports "Failed to import filter module" and the filter
   does nothing. No warning class is exported publicly on either version. Ask:
   export `JsonargparseWarning` (and the deprecation subclass) from the package.
7. **Other v5 changes we noticed**: `init_args: {args: []}` for every
   `nn.Module` subclass without its own `__init__` ([J49](#j49), cosmetic); a
   `jsonargparse.Unset` default no longer reloads (import-path denylist, [J37](#j37)).
8. 🟢 **What v5 fixed for us** (see [Resolved upstream](#resolved)): nested `class_path` parse time ([J08](#j08), our #1036: 35 and 17 CPU s
   down to 3.8 s on real configs; about 3x on another project); quadratic list
   parsing ([J29](#j29)); constructor errors raised as themselves ([J28](#j28)); a `class_path`
   change discarding the old class's `init_args` ([J21](#j21), #1038, merged after rc2);
   unquoted recursive `type` aliases ([J33](#j33)); `Optional[S]` with an instance default now
   merges across section files ([J25](#j25)); `Source: config file:line` provenance and
   "Known subclasses" in errors ([J12](#j12)). Every v5-only test failure across our
   five suites traced to [J01](#j01), [J07](#j07), [J23](#j23), [J30](#j30)'s sklearn case or [J45](#j45)'s renames;
   nothing else broke.

[↑ Contents](#contents)

<a id="overview"></a>

## Overview of open issues

| ID | Title | Kind | Sev | Effort | Appetite | Status | Repro |
|---|---|---|---|---|---|---|---|
| [J01](#j01) | Callable Protocol (and `Callable[..., C]`) rejects classes whose instances implement it 🔧 *(work begun)* | regression-or-pin | 🔴 S1 | small | likely-bug | 4.51 ✅ 4.53 ❌ v5 ❌ | [`J01_protocol_call_returns_class.py`](repros/J01_protocol_call_returns_class.py) |
| [J02](#j02) | Protocol matching needs identical annotations: jaxtyping never equal; Modules need `-> Any` | bug | 🟠 S2 | small | likely-bug / debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J02_protocol_exact_annotations.py`](repros/J02_protocol_exact_annotations.py) |
| [J04](#j04) | Dataclass with a non-first base from another module: every field silently unvalidated | bug | 🔴 S1 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J04_mixin_base_unvalidated.py`](repros/J04_mixin_base_unvalidated.py) |
| [J05](#j05) | Plain-class instance default: a partial override silently discards its values | bug | 🔴 S1 | small–medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J05_instance_default_partial_override.py`](repros/J05_instance_default_partial_override.py) |
| [J06](#j06) | Dict fields in overlays: key set replaced, surviving keys merged; dotted form merges | intended-but-awkward | 🔴 S1 | medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J06_dict_overlay_key_set.py`](repros/J06_dict_overlay_key_set.py) |
| [J07](#j07) | LightningCLI 2.6.x calls APIs removed in v5 | lightning-interplay | 🔴 S1 | small (Lightning) | n/a (PR open) | 4.51 ✅ 4.53 ✅ v5 ❌ | [`J07_lightningcli_removed_v5_apis.py`](repros/J07_lightningcli_removed_v5_apis.py) |
| [J09](#j09) | Container defaults of dataclasses dump as "Unable to serialize instance" | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J09_undumpable_container_defaults.py`](repros/J09_undumpable_container_defaults.py) |
| [J10](#j10) | Global settings: not idempotent, no public getter, no scope | missing-feature | 🟠 S2 | small | likely-bug / debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J10_global_settings_not_idempotent.py`](repros/J10_global_settings_not_idempotent.py) |
| [J11](#j11) | Subclass mode: section files rejected, nested options hidden from `--help`, dump shape changes | intended-but-awkward | 🟠 S2 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J11_subclass_mode_side_effects.py`](repros/J11_subclass_mode_side_effects.py) |
| [J12](#j12) | Error messages bury the cause | error-message | 🟠 S2 | medium | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ (better) | [`J12_error_messages_bury_cause.py`](repros/J12_error_messages_bury_cause.py) |
| [J13](#j13) | `os.PathLike` stringifies anything; CLI `null` becomes `"None"` | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J13_pathlike_null_and_coercion.py`](repros/J13_pathlike_null_and_coercion.py) |
| [J14](#j14) | A `str` value naming an existing file is read as a config (silent) | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J14_str_value_read_as_config_file.py`](repros/J14_str_value_read_as_config_file.py) |
| [J15](#j15) | Subscripted generic (`Model[int]`) rejects a subclass's `init_args` 🔧 *(work begun)* | bug | 🟠 S2 | small (branch) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J15_subscripted_generic_subclass.py`](repros/J15_subscripted_generic_subclass.py) |
| [J16](#j16) | Default instance with non-`__init__` attributes rejected under Optional/union/subclass mode 🔧 *(work begun)* | bug | 🟠 S2 | small (branch) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J16_default_instance_nonfield_attrs.py`](repros/J16_default_instance_nonfield_attrs.py) |
| [J17](#j17) | Protocols with only `_` members match nothing; no variance | bug | 🟠 S2 | trivial–small | likely-bug / debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J17_protocol_private_members.py`](repros/J17_protocol_private_members.py) |
| [J18](#j18) | C builtins rejected for `Callable[[Tensor], Tensor]`; stubs setting read once | intended-but-awkward | 🟠 S2 | trivial | intended / likely-bug | 4.51 ✅ 4.53 ❌ v5 ❌ | [`J18_c_builtin_callable.py`](repros/J18_c_builtin_callable.py) |
| [J19](#j19) | No placeholder interpolation before validation | missing-feature | 🟠 S2 | medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J19_placeholder_in_typed_field.py`](repros/J19_placeholder_in_typed_field.py) |
| [J20](#j20) | No deferred instantiation (validate a `class_path` now, build later) | missing-feature | 🟠 S2 | medium | debatable | ? (feature) | — |
| [J22](#j22) | `dump()` drops explicit `null`s; reload gives the default | intended-but-awkward | 🟡 S3 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J22_dump_drops_null.py`](repros/J22_dump_drops_null.py) |
| [J23](#j23) | v5: a required `X \| None` can't be given `null` | v5-migration | 🟠 S2 | medium | likely-bug | 4.51 ✅ 4.53 ✅ v5 ❌ | [`J23_required_optional_null.py`](repros/J23_required_optional_null.py) |
| [J24](#j24) | Protocol-typed class default inside a dataclass default or union dumps as a bare path; not a fixpoint | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J24_protocol_class_default_dump.py`](repros/J24_protocol_class_default_dump.py) |
| [J25](#j25) | A section file given to a parent group resets nullable sections | intended-but-awkward | 🟠 S2 | small–medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J25_section_file_resets_section.py`](repros/J25_section_file_resets_section.py) |
| [J26](#j26) | Tagged union with an instance default rejects another member 🔧 *(work begun)* | regression-or-pin | 🟠 S2 | small (branch) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J26_tagged_union_instance_default.py`](repros/J26_tagged_union_instance_default.py) |
| [J27](#j27) | One unevaluable annotation leaves every field of the class unvalidated | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J27_quoted_forward_ref_in_union.py`](repros/J27_quoted_forward_ref_in_union.py) |
| [J30](#j30) | `class_path` specs in `Any` fields are converted to Namespaces and filled; input mutated | intended-but-awkward | 🟡 S3 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J30_any_spec_namespace.py`](repros/J30_any_spec_namespace.py) |
| [J31](#j31) | `stubs_resolver_allow_py_files=True` gives sklearn `Ridge` zero parameters | bug | 🟡 S3 | trivial | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J31_stubs_py_files_sklearn_ridge.py`](repros/J31_stubs_py_files_sklearn_ridge.py) |
| [J32](#j32) | `**kwargs`/untyped constructors need hand-written typed wrappers | intended-but-awkward | 🟡 S3 | n/a | intended | ? | — |
| [J33](#j33) | Recursive PEP 695 alias with a quoted self-reference fails | bug | 🟡 S3 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J33_pep695_recursive_alias.py`](repros/J33_pep695_recursive_alias.py) |
| [J34](#j34) | A docstring-parser failure silently drops constructor parameters | bug | 🟡 S3 | trivial | likely-bug | ? (not rerun) | — |
| [J35](#j35) | Stale `--config` in nested parsers of a parser subclass | bug | 🟡 S3 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J35_stale_config_nested_parser.py`](repros/J35_stale_config_nested_parser.py) |
| [J36](#j36) | Tuple-keyed dicts keep string keys; tuple-key default dump doesn't reload | bug | 🟡 S3 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J36_tuple_keyed_dict.py`](repros/J36_tuple_keyed_dict.py) |
| [J37](#j37) | Sentinels: `register_type` serializer applied by union arm; `Unset` doesn't reload on v5 | bug | 🟡 S3 | small–medium | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J37_register_type_union_serializer.py`](repros/J37_register_type_union_serializer.py) |
| [J38](#j38) | Function as `class_path` judged by return annotation only | intended-but-awkward | 🟡 S3 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J38_function_class_path_return.py`](repros/J38_function_class_path_return.py) |
| [J39](#j39) | Slotted dataclass defaults crash (`vars()`) | bug | 🟡 S3 | trivial | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J39_slotted_dataclass_default.py`](repros/J39_slotted_dataclass_default.py) |
| [J40](#j40) | `null` accepted for non-Optional fields with a default (config only) | intended-but-awkward | 🟡 S3 | small | intended | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J40_null_for_non_optional.py`](repros/J40_null_for_non_optional.py) |
| [J41](#j41) | Dotted overrides can't reach list entries; links can't reach list or dict entries | missing-feature | 🟡 S3 | medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J41_dotted_override_list_index.py`](repros/J41_dotted_override_list_index.py) |
| [J42](#j42) | Saved LightningCLI `config.yaml` doesn't load into `run=False` | lightning-interplay | 🟡 S3 | small (Lightning) | debatable | 4.51 ❌ 4.53 ❌ v5 – ([J07](#j07)) | [`J42_lightning_saved_config_reload.py`](repros/J42_lightning_saved_config_reload.py) |
| [J43](#j43) | `parse_object` mutates list/dict containers in its input | bug | 🟡 S3 | trivial | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J43_parse_object_mutates_input.py`](repros/J43_parse_object_mutates_input.py) |
| [J44](#j44) | Inherited dataclass field resolved in the base module's namespace | bug | 🟡 S3 | small (with [J04](#j04)) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J44_inherited_annotation_namespace.py`](repros/J44_inherited_annotation_namespace.py) |
| [J45](#j45) | v5 migration of our own code, and migration-guide gaps | v5-migration | 🟡 S3 | small | likely (docs) | v5 only | — |
| [J47](#j47) | Failing `default_factory` (validating `__post_init__`) breaks parser construction without context | intended-but-awkward | 🟡 S3 | trivial | intended / likely (message) | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J47_default_factory_postinit.py`](repros/J47_default_factory_postinit.py) |
| [J48](#j48) | No public warning category; private filter path removed in v5 | warning-noise | ⚪ S4 | trivial | debatable | 4.51 ✅ 4.53 ✅ v5 ❌ | [`J48_deprecation_warning_filter.py`](repros/J48_deprecation_warning_filter.py) |
| [J49](#j49) | v5 dumps `init_args: {args: []}` for `nn.Module` subclasses | v5-migration | ⚪ S4 | trivial | likely-bug | 4.51 ✅ 4.53 ✅ v5 ❌ | [`J49_varargs_dump_nn_module.py`](repros/J49_varargs_dump_nn_module.py) |
| [J50](#j50) | `exit_on_error=True` default raises `SystemExit` in library code | intended-but-awkward | ⚪ S4 | n/a | intended | ? | — |
| [J51](#j51) | `instantiate` doesn't build a dataclass added at the root | intended-but-awkward | ⚪ S4 | n/a | intended | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J51_instantiate_root_dataclass.py`](repros/J51_instantiate_root_dataclass.py) |
| [J52](#j52) | Field docs in `--help` need a global setting | intended-but-awkward | ⚪ S4 | n/a | intended | ? | — |
| [J53](#j53) | A top-level `_anchors:` holder for YAML anchors is rejected | intended-but-awkward | ⚪ S4 | n/a | intended | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J53_top_level_anchor_holder.py`](repros/J53_top_level_anchor_holder.py) |
| [J54](#j54) | A list field can't be loaded from a file path (without `sub_configs=True`) | missing-feature | ⚪ S4 | n/a | intended | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J54_list_field_from_file.py`](repros/J54_list_field_from_file.py) |
| [J55](#j55) | argcomplete crashes on subcommand options and misses `class_path` fields | missing-feature | ⚪ S4 | ? | ? | ? | — |
| [J56](#j56) | `Union[Dataclass, dict]` with an empty-dict default is filled with the dataclass defaults | warning-noise | ⚪ S4 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J56_union_dataclass_dict_empty_default.py`](repros/J56_union_dataclass_dict_empty_default.py) |
| [J57](#j57) | Bare-generic dataloader fields failed with `__args__` | bug | ⚪ S4 | ? | ? | worked around in our code; not rechecked | — |
| [J58](#j58) | `--print_config` writes relative paths as given; `--config` resolves them against the file | intended-but-awkward | ⚪ S4 | n/a | intended | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J58_print_config_relative_paths.py`](repros/J58_print_config_relative_paths.py) |

Resolved upstream, so not in this table: [J03](#j03), [J08](#j08), [J21](#j21), [J28](#j28), [J29](#j29) (see [Resolved upstream](#resolved)). [J46](#j46) was checked and is [not a jsonargparse issue](#not-an-issue).

[↑ Contents](#contents)

<a id="open-details"></a>

## Detailed entries

<a id="kind-bugs"></a>

### Bugs

#### <a id="j04"></a>J04 Dataclass with a non-first base from another module: every field silently unvalidated
🔴 **S1** · small · likely-bug · hit in 1 of 6 (5 config classes that every pipeline run uses; a scan of 4 projects found no others) · [`J04_mixin_base_unvalidated.py`](repros/J04_mixin_base_unvalidated.py)

> [!NOTE]
> **🔧 Work begun**: branch `fix-inherited-annotation-namespace`, which fixes this and [J44](#j44) (draft PR in `prs/`).

**In one sentence:** if a dataclass has two bases and the second one is defined
in another module, jsonargparse can silently stop validating every field of the
class.

**Why it happens:**

1. With `from __future__ import annotations`, a field like `batch_size: int`
   stores its type as the string `"int"`. jsonargparse has to look up the names
   in that string to get the type back.
2. It looks names up in two places only: the subclass's own module and its
   first base's module. It never checks the second base's module.
3. So when a field of the second base uses a name that only its own module
   imports, such as `Callable`, the lookup fails.
4. When the lookup fails, jsonargparse doesn't skip just that field. It turns
   off validation for the whole class, and any value is accepted, with no
   warning.

**Example** (both files use `from __future__ import annotations`):

```python
# base.py
from collections.abc import Callable

@dataclass
class B:
    fn: Callable | None = None
    batch_size: int = 16
```

```python
# main.py: doesn't import Callable
from base import B

@dataclass
class A:
    seed: int = 0

@dataclass
class C(A, B): ...   # B is second
```

For `C`, `batch_size: "sixteen"` is accepted. Write `class C(B, A)` instead and
it's rejected.

**What it costs us:**

- In one project, the 5 stage config classes have no validation at all
  (`batch_size: "sixteen"`, a bad `Literal`, `freeze_model: "maybe"` all pass),
  although that project's docs say they are validated.
- It also makes parsing slower, because the unvalidated path walks through
  nested `class_path` values. Measured on 4.53.0 with the fix applied by hand,
  on that project's real run files (2026-11-26):

  | prepare command | without fix | with fix |
  |---|---|---|
  | largest run (7 stages), whole command | 7.4 s | 5.6 s |
  | same run, stage parsing only | 2.3 s CPU | 0.6 s CPU |
  | a finetune run | 1.4 s CPU | 0.4 s CPU |
  | an MLP-head run | 0.55 s CPU | 0.65 s CPU |

  The MLP run gets slightly slower because its fields are now actually checked.
  All four real run files still pass with validation on.
- The speed difference is too small to matter for us: about 1-2 s on the
  largest commands. The extra time grows in a straight line with the number of
  stages parsed, so it would only add up for something like a sweep parsing
  hundreds of stage configs. The reason to fix J04 is the missing validation.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Workaround:** import the missing names in the subclass's module too, or put
the other module's base first.

**The fix** (branch, +18 −7): look up each field's names in the module where
that field was written, which is what `typing.get_type_hints` already does. The
maintainer took the same approach for `TypedDict` keys inherited from other
modules (#936). It also fixes [J44](#j44).

#### <a id="j44"></a>J44 Inherited dataclass field resolved in the base module's namespace
🟡 **S3** (S2 if the project's affected class has this shape; not confirmed) · small (same fix as [J04](#j04)) · likely-bug · hit in 1 of 6 (led to a "never shadow a library class name" rule) · [`J44_inherited_annotation_namespace.py`](repros/J44_inherited_annotation_namespace.py)

> [!NOTE]
> **🔧 Work begun**: fixed on the [J04](#j04) branch `fix-inherited-annotation-namespace`.

**In one sentence:** the same lookup as [J04](#j04), going wrong the other way:
if a subclass's module and its base's module import different classes under the
same name, jsonargparse uses the base module's one, even for fields written in
the subclass.

**Example** (both files use `from __future__ import annotations`):

```python
# base.py
from checks_b import Checker

@dataclass
class Base:
    lr: float = 0.1
```

```python
# main.py
from checks_a import Checker   # a different class with the same name
from base import Base

@dataclass
class Config(Base):
    checker: Checker | None = None
```

`Config.checker` means `checks_a.Checker`, but jsonargparse reads it as
`checks_b.Checker`, so a valid `class_path: checks_a.Checker` is refused.

**What it costs us:** an import alias, and a rule not to reuse class names
across modules. Whether the class that prompted the rule has this exact shape
wasn't checked.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**The fix:** the [J04](#j04) fix.

#### <a id="j14"></a>J14 A `str` value naming an existing file is read as a config
🟠 **S2** (silent when hit) · small · likely-bug · incident in 1 of 6 (a predict run hung reading a multi-GB HDF5 during config dumping); a `PathLike | str` alias convention in 28 files across 4 projects · [`J14_str_value_read_as_config_file.py`](repros/J14_str_value_read_as_config_file.py)

- **What happens**: with `sub_configs=True` (LightningCLI sets it), a value
  that names an existing file is loaded as a config:
  | parameter | `sub_configs=False` | `sub_configs=True` |
  |---|---|---|
  | signature `plain: str` | `'data.csv'` | `'data.csv'` |
  | signature `uni: str \| D` (D a dataclass) | `'data.csv'` | **`'a,b\n1,2\n'`** (file text) |
  | `add_argument("--p", type=str, sub_configs=True)` | – | **file text** |
  | `add_argument(type=os.PathLike \| str, sub_configs=True)` | – | `'data.csv'` |

  So through signatures (the LightningCLI path) only a union of `str` with a
  class is affected; a direct `add_argument(type=str, sub_configs=True)` is
  affected too. A text file silently becomes the value; a file that parses as a
  mapping becomes the dataclass arm. A 300 MB binary file is opened three times
  in `parse_args` and again in `dump`, with peak RSS about 3.3 times the file
  size, which scales into a hang for multi-GB files. Nothing warns.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌ (plain parser; LightningCLI path checked on
  4.51 and 4.53).
- **Workaround**: type path fields `os.PathLike | str` (`is_pathlike` turns
  `enable_path` off). Works, but it is a convention every path field in every
  LightningCLI-built class must follow, and it relies on [J13](#j13)'s lenient
  `PathLike`.
- **Cause**: `ActionTypeHint.__init__` keeps `enable_path` unless the type
  contains `os.PathLike` (`_typehints.py:424`; 4.53: 389); `parse_value_or_config`
  then reads any string that names a file and falls back to the string only if
  loading or validation fails.
- **Fix**: never read a file for a value that is valid for a `str` arm; read
  sub-configs only for arms that can hold a config (class, dataclass, mapping),
  and only when the string is not accepted as is.
- **Upstream summary**: With `sub_configs=True`, a string for a `str | SomeClass`
  parameter (or for `add_argument(type=str, sub_configs=True)`) that names an
  existing file is replaced by the file's contents; large files are read several
  times, including by `dump`. 4.51.0, 4.53.0, 5.0.0rc2. Expected: a `str` value
  stays the string.

#### <a id="j27"></a>J27 One unevaluable annotation leaves every field of the class unvalidated
🟠 **S2** · small · likely-bug · hit in 2 of 6 (one removed `from __future__` from its config modules; the other lost a parameter on ≤4.50) · [`J27_quoted_forward_ref_in_union.py`](repros/J27_quoted_forward_ref_in_union.py)

- **What happens**: under `from __future__ import annotations`,
  `weights: "Weights" | None = None` (a quoted name inside `|`) can't be
  evaluated (`str | None` raises TypeError) although `Weights` is importable.
  Since 4.51 every field of the class becomes `Unvalidated`: `weights: 7` and
  `lr: "abc"` are both accepted. On 4.50 and earlier the parameter was dropped
  instead.
- **Status**: 4.50 dropped; 4.51 ❌ 4.53 ❌ v5 ❌. Only `JSONARGPARSE_DEBUG=true`
  shows why.
- **Workaround**: avoid quoted names inside `|`, or drop postponed annotations.
- **Fix**: evaluate per field (one bad annotation shouldn't disable the class),
  try evaluating string elements before applying `|`, and emit a warning when a
  field or class falls back to `Unvalidated`.
- **Upstream summary**: `weights: "Weights" | None` under postponed annotations
  silently disables validation for all fields of the dataclass (4.51.0-5.0.0rc2);
  expected per-field degradation plus a warning.

#### <a id="j01"></a>J01 Callable Protocol rejects classes whose instances implement it
🔴 **S1** · small · likely-bug · hit in 4 of 6 (an exact `==4.51.0` pin in one, 4.51 locks in two more, `-> Any` on three Protocols in another) · [`J01_protocol_call_returns_class.py`](repros/J01_protocol_call_returns_class.py)

> [!NOTE]
> **🔧 Work begun**: branch `fix-factory-protocol-instances` (draft PR in `prs/`), rebased on main 2026-11-26: commit 1 fixes the Protocol case, and a separable commit 2 the `Callable[..., Class]` case.

- **What happens**:
  ```python
  class DecoderFactory(Protocol):
      def __call__(self, *, d: int) -> Decoder: ...
  @dataclass(kw_only=True)
  class DecoderChoice:                       # instances implement the Protocol
      default: DecoderFactory = LinearDecoder
      def __call__(self, *, d: int) -> Decoder: ...
  class Model:
      def __init__(self, decoder: DecoderFactory = DecoderChoice()): ...
  ```
  With subclass mode on, `parse_args([])` fails with
  `Expected '__main__.DecoderChoice' to be a subclass of Decoder`: the field's own
  default is rejected, so every parse of `Model` fails. `class_path:
  DecoderChoice` fails too, and so does `Callable[[int], Decoder]` given a class
  with callable instances (also since 4.52). The message never mentions the Protocol.
- **Status**: 4.51 ✅ 4.52 ❌ 4.53 ❌ v5 ❌. In one project this was 82 of 89
  v5-only test failures; in another 137 of 140.
- **Workaround**: stay on 4.51; or annotate the Protocol's return as `Any`
  (works for `nn.Module` implementers, loses the return type; see [J02](#j02)); or widen
  the field to `Factory | Choice`.
- **Cause**: 4.52 added "a class `class_path` must be a subclass of the
  `__call__` return type" in the Callable branch (`_typehints.py:1944`,
  `if subclass_types:`), before the callable-instances check.
- **Fix**: the branch `fix-factory-protocol-instances` checks conformance with
  `implements_protocol` for classes with callable instances; it fixes the
  Protocol rows but not `Callable[[int], Base]`, and it rejects a `__call__` with
  no return annotation against a Protocol returning a class (4.51 accepted it).
  A one-line reordering (`if subclass_types and not callable_instances(val_class)`)
  restores 4.51 exactly but checks no conformance (wrong arity accepted).
  Suggested: the branch's conformance check, also for `Callable[[...], Class]`
  with an arity check.
- **Upstream summary**: since 4.52.0 a Protocol whose `__call__` returns a class
  (and likewise a `Callable[..., Class]`) is treated as a factory for that
  class, so a class whose *instances* implement it is rejected, even as the
  field's default. Repro above. Expected (4.51): accepted.

#### <a id="j02"></a>J02 Protocol matching needs identical annotations
🟠 **S2** · small · likely-bug (jaxtyping) / debatable (untyped implementer returns) · hit in 2 of 6 · [`J02_protocol_exact_annotations.py`](repros/J02_protocol_exact_annotations.py)

- **What happens**: `Float[Tensor, "b d"] == Float[Tensor, "b d"]` is False
  (jaxtyping builds a new class per subscription), so a Protocol with a jaxtyped
  parameter can't be implemented by a class that writes the same annotation
  itself, on any version. A shared alias object (`Emb = Float[...]` used in both)
  works. An `nn.Module` is matched on the untyped `nn.Module.__call__`, so it
  passes only against `-> Any` (4.53/v5; 4.51 skipped the check, see [J01](#j01)).
- **Status**: separate jaxtyped annotations: 4.51 ❌ 4.53 ❌ v5 ❌;
  `nn.Linear` vs `-> Tensor`: 4.51 ✅ 4.53 ❌ v5 ❌.
- **Workaround**: `-> Any` on the Protocol plus a shared alias for jaxtyped
  arguments. Verified end to end: one project's full training config then parses
  on stock v5 with output identical to 4.51. Cost: the output shape lives only in
  docstrings.
- **Cause**: `type_var_wildcard_matches` (`_typehints.py:2149`) falls back to
  `==`; `protocol_params_match` (`:2208`) requires every parameter to match.
- **Fix**: compare objects exposing `dtype`/`dim_str`/`array_type`
  structurally (or by `repr`) after `==`; optionally treat an unannotated
  implementer return as compatible.
- **Upstream summary**: a Protocol `__call__(self, x: Float[Tensor, "b d"]) -> Any`
  is never implemented by a class with its own `x: Float[Tensor, "b d"]`
  ("does not implement protocol"), 4.51.0-5.0.0rc2.

#### <a id="j09"></a>J09 Container defaults of dataclasses dump as "Unable to serialize instance"
🟠 **S2** · small · likely-bug · hit in 4 of 6 · [`J09_undumpable_container_defaults.py`](repros/J09_undumpable_container_defaults.py)

- **What happens**: a single dataclass default dumps as a mapping, but
  `list[Rule]`, `tuple[Rule, ...]` and `dict[str, Rule]` defaults (also pydantic
  models) dump as `- Unable to serialize instance Rule(pattern='a.*')`, which
  doesn't reload ("Unexpected import path format"). An untyped `dict` holding an
  instance makes `dump` raise `RepresenterError`. The only signal is a
  `JsonargparseWarning`, shown once per location.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Workaround**: `None` defaults plus a runtime constant, so `--print_config`
  hides the effective value; elsewhere, garbage in saved configs.
- **Cause**: contained instances go through `serialize_as_import_path`, which
  returns the literal "Unable to serialize instance ..." on `ValueError`
  (`_typehints.py:3324-3330`).
- **Fix**: serialize dataclass/pydantic/attrs instances inside containers the
  same way as a single default; raise instead of writing text.
- **Upstream summary**: `rules: list[Rule] = field(default_factory=lambda: [Rule("a.*")])`
  dumps as text that doesn't reload (4.51.0-5.0.0rc2).

#### <a id="j13"></a>J13 `os.PathLike` stringifies anything; CLI `null` becomes `"None"`
🟠 **S2** · small · likely-bug · hit in 3 of 6 (a run staged into `./None`; a ~50-line convention docstring) · [`J13_pathlike_null_and_coercion.py`](repros/J13_pathlike_null_and_coercion.py)

- **What happens**: for `os.PathLike | str | None`, `--p=null` gives `'None'`,
  `--p=7` gives `'7'`, `--p=[a,b]` gives `"['a', 'b']"`. YAML `p: null` gives
  `None`, so only the command line (or any source passing a real `None` to the
  union) is affected.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Cause**: `register_type(os.PathLike, str, str)` (`typing.py:607`; 4.53: 591)
  makes the deserializer `str`, and the PathLike arm is tried before `None`.
- **Fix**: a deserializer that accepts only `str`/`PathLike`; try `None` first.
- **Upstream summary**: `--p=null` for `os.PathLike | None` yields the string
  `'None'`, and `PathLike` accepts ints and lists as strings (4.51.0-5.0.0rc2).

#### <a id="j24"></a>J24 Protocol-typed class default dumps as a bare import path
🟠 **S2** · small · likely-bug · hit in 1 of 6 (the saved config of every training run) · [`J24_protocol_class_default_dump.py`](repros/J24_protocol_class_default_dump.py)

- **What happens**: with `discrete: Factory = Decoder` (a `__call__` Protocol)
  held inside a dataclass default (`sel: Choice = Choice()`) or in a union with a
  dataclass (`head: Factory | Choice = Decoder`), the first dump writes
  `discrete: __main__.Decoder`; reloading and dumping again writes `class_path`
  plus `init_args` (`width: 4`). The saved config omits the hyperparameters, so a
  later change of the code default silently changes what an old config means.
  A plain `x: Factory = Decoder` field and `Callable[..., Decoder]` are normalized
  on the first dump (checked here; narrower than first reported).
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Workaround**: none in use (the project dumps once).
- **Fix**: normalize class defaults of Protocol fields to `class_path`/`init_args`
  when the default comes from an enclosing default instance or union.
- **Upstream summary**: a Protocol-typed class default nested in a dataclass
  default dumps as a bare path; dump then reload then dump differs (4.51.0-5.0.0rc2).

#### <a id="j15"></a>J15 Subscripted generic rejects a subclass's `init_args`
🟠 **S2** · small (branch `fix-subscripted-generic-init-args`) · likely-bug · hit in 2 of 6 (one added per-type marker ABCs: 15 files, +293 lines, plus a review rule; the other first misread it as a depth problem) · [`J15_subscripted_generic_subclass.py`](repros/J15_subscripted_generic_subclass.py)

> [!NOTE]
> **🔧 Work begun**: branch `fix-subscripted-generic-init-args` (draft PR in `prs/`).

- **What happens**: `--model` typed `Model[int]`, `class_path: IntModel` with
  `--model.depth=2`: "Option 'depth' is not accepted". Plain `Model` works.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Cause / fix**: since #775 `adapt_class_type` builds the parser from the
  subscripted type whatever the `class_path`; use it only when `class_path` is
  the generic class itself (draft PR in `prs/`).

#### <a id="j16"></a>J16 Default instance with non-`__init__` attributes rejected
🟠 **S2** · small (branch `fix-default-instance-non-field-attributes`) · likely-bug · hit in 2 of 6 (a registry redesign; derived values turned into properties; 9 of 223 dataclasses in one project would break if used as defaults) · [`J16_default_instance_nonfield_attrs.py`](repros/J16_default_instance_nonfield_attrs.py)

> [!NOTE]
> **🔧 Work begun**: branch `fix-default-instance-non-field-attributes` (draft PR in `prs/`); it fixes every shape tested.

- **What happens**: a dataclass default that sets `self.derived` (or `_cache`,
  or an `init=False` field) in `__post_init__` is rejected ("Option 'derived' is
  not accepted") when the field is `Optional`, a union, or subclass-typed. A
  plain dataclass field without subclass mode is fine;
  `field(init=False, default=7)` is fine.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌; the branch fixes every shape tested.
- **Cause / fix**: `convert_to_dict` builds `init_args` from `vars(value)`; keep
  only `__init__` parameters (draft PR in `prs/`).

#### <a id="j17"></a>J17 Protocols with only `_` members match nothing; no variance
🟠 **S2** · trivial (message) / small · likely-bug (message) / debatable (variance) · incident in 1 of 6 (the only training config unusable); an "ABCs, not Protocols" rule in 5 of 6 · [`J17_protocol_private_members.py`](repros/J17_protocol_private_members.py)

- **What happens**: a Protocol whose only member is `_encode` matches nothing
  ("does not implement protocol"); in a mixed Protocol the private member isn't
  checked at all; `f(x: float | int)` doesn't implement `f(x: float)`,
  `-> int` doesn't implement `-> float`, and an unannotated `f(self, x)` is
  rejected.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Cause**: `get_protocol_members` (`_typehints.py:2283`) skips non-dunder `_`
  names; `implements_protocol` returns False when no members remain (`:2334`).
- **Fix**: say "protocol P has no checkable members (names starting with `_` are
  ignored)"; consider variance-aware comparison.
- Simple public Protocols do work; the blanket rule overstates the limit.

#### <a id="j12"></a>J12 Error messages bury the cause
🟠 **S2** · medium · likely-bug (specific cases) · hit in 6 of 6 · [`J12_error_messages_bury_cause.py`](repros/J12_error_messages_bury_cause.py)

- **What happens** (small values; real configs give 2-17 KB):
  1. a typo three plain dataclasses deep (subclass mode on): the cause
     `Option 'lrr' is not accepted` is line 7 of 7, after three
     `Problem with given class_path '...'` lines for dataclasses that never had a
     `class_path` (one project's docs quote this genre as *the* symptom of an
     unrelated problem);
  2. a missing module in one element of `list[Callback] | Callback | None`:
     every arm is listed, the value is printed twice, plus a "Subclass types
     expect one of" blurb per arm;
  3. `add_subclass_arguments(SomeDataclass)` with subclass mode off:
     `Expected 'baseclass' to be a subclass type ...`, naming neither the cause
     nor the fix.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌. v5 is better: `Source: file:line`,
  "Known subclasses", and constructor-argument errors cut from 263 to 121
  characters; cases 1 and 3 are unchanged; the whole value is still printed in
  `Got value:` (about 17 KB for one wrong key in a real config).
- **Fix**: (1) don't wrap non-subclass types in `Problem with given
  class_path`; lead with `Parser key "a.b.c": Option 'lrr' is not accepted`.
  (2) print the value once, last, truncated; drop arms that can't apply (the
  NoneType arm for a non-null value). (3) reuse the clear "Subclasses are
  disabled for X" text that the `class_path` path already has.

#### <a id="j18"></a>J18 C builtins rejected for `Callable[[Tensor], Tensor]`; stubs setting read once
🟠 **S2** · trivial (cache) · intended (rejection, #959/#963) / likely-bug (caching) · cited by pins in 5 of 6 · [`J18_c_builtin_callable.py`](repros/J18_c_builtin_callable.py)

- **What happens**: since 4.52 `torch.log1p` is rejected for
  `Callable[[Tensor], Tensor]`, since a function given by path must have a
  matching return annotation or stub. `stubs_resolver_allow_py_files=True` fixes
  torch, but only if set before the first stub lookup; set later, it is ignored.
  (`math.sqrt` is correctly rejected: its stub returns `float`.)
- **Status**: 4.51 ✅ 4.53 ❌ v5 ❌; late setting ignored on 4.53 and v5.
- **Workaround**: `Callable[[Tensor], Any]` (type check lost), or enable the
  setting early, which then triggers [J31](#j31) for sklearn.
- **Cause**: `get_stubs_resolver()` (`_stubs_resolver.py:104-110`) caches the
  resolver in a module global. torch has no `torch/__init__.pyi`; its stubs are
  reachable only through `.py` files.
- **Fix**: reset the cached resolver when the setting changes (in
  `set_parsing_settings`).

#### <a id="j31"></a>J31 `stubs_resolver_allow_py_files=True` gives sklearn `Ridge` zero parameters
🟡 **S3** · trivial · likely-bug · hit in 3 of 6 (setting removed in one; 2 tests failed in another; planned in a third) · [`J31_stubs_py_files_sklearn_ridge.py`](repros/J31_stubs_py_files_sklearn_ridge.py)

- **What happens**: `add_class_arguments(Ridge, "r")` registers 8 parameters by
  default and 0 with the setting; the RecursionError is only a DEBUG log, so the
  user sees "Option 'alpha' is not accepted" later.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌ (scikit-learn 1.8 and 1.9).
- **Cause**: `StubsResolver.add_module_aliases` (`_stubs_resolver.py:214`)
  treats every assignment in `_ridge.py`, including function-local ones, as an
  alias and recurses with `skip={name}`, which breaks only 1-cycles; `X`,
  `intercept_column`, `sqrt_sw`, `xp`, `n_samples` form a longer cycle.
- **Fix**: `skip=skip | {name}` (tested in a copy of v5: all 8 parameters back);
  also catch `RecursionError` so a failed stub never removes signature
  parameters.

#### <a id="j33"></a>J33 Recursive PEP 695 alias with a quoted self-reference fails
🟡 **S3** · small · likely-bug · hit in 2 of 6 (a lint rule reverted; 62 tests failed once) · [`J33_pep695_recursive_alias.py`](repros/J33_pep695_recursive_alias.py)

- **What happens**: `type Nested[K, V] = dict[K, V | "Nested[K, V]"]` (the form
  ruff's UP040 writes): on 4.51 `--c.weights.cross=1` gives `('cross', '1')`; on
  4.53 and v5 a nested dict is rejected. The unquoted form works on v5 and hits a
  RecursionError at parser construction on 4.53.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌ (unquoted: v5 ✅).
- **Workaround**: a `TypeAlias` with `noqa`; it works for dotted overrides but
  leaves depth 2 unvalidated on all versions.
- **Fix**: resolve the quoted self-reference in the alias's own scope.

#### <a id="j35"></a>J35 Stale `--config` in nested parsers of a parser subclass
🟡 **S3** · small · likely-bug · hit in 1 of 6 (a patch to the private `_option_string_actions`) · [`J35_stale_config_nested_parser.py`](repros/J35_stale_config_nested_parser.py)

- **What happens**: a parser subclass that adds `--config` in `__init__`, and a
  nested class with a `config` parameter: "Unable to add parameter 'config' ...
  because argument '--config' already exists". A plain `ArgumentParser` works.
  LightningCLI's parser is not affected (it adds `--config` after construction).
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Cause / fix**: nested parsers are built from `parent.__class__`; the
  re-added action is removed from `_actions` but not from
  `_option_string_actions`. Remove both, or build nested parsers without the
  subclass's extra options.

#### <a id="j36"></a>J36 Tuple-keyed dicts
🟡 **S3** · small · likely-bug · hit in 1 of 6 (a wrapper type) · [`J36_tuple_keyed_dict.py`](repros/J36_tuple_keyed_dict.py)

- `dict[tuple[str, str], float]` accepts any string as a key (`'[a, b]'`,
  `'not-a-tuple'`) and keeps it as a string; a default with tuple keys dumps as a
  YAML complex key that doesn't reload (on v5, "Failed to parse as JSON").
  4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j37"></a>J37 Three-state sentinels don't round-trip
🟡 **S3** (S1-grade silent data loss if used) · small–medium · likely-bug · hit in 1 of 6 (a sentinel design note; the projects avoid `register_type`) · [`J37_register_type_union_serializer.py`](repros/J37_register_type_union_serializer.py)

- **What happens**: a sentinel registered with `register_type(InheritType,
  serializer=lambda v: "inherit", ...)` in `x: InheritType | bool = INHERIT`:
  `--x=false` dumps as `x: inherit` and reloads as the sentinel. `bool |
  InheritType` is correct. Separately, a `jsonargparse.Unset` default dumps as
  `jsonargparse._common.Unset`, which reloads on 4.x and is refused by v5's
  import-path denylist.
- **Status**: serializer 4.51 ❌ 4.53 ❌ v5 ❌; `Unset` reload 4.51 ✅ 4.53 ✅ v5 ❌.
  `Union[Any, Sentinel]` crashed `dump` on 4.50 and round-trips since 4.51, so
  "sentinel arm first" hacks can go.
- **Fix**: apply a registered serializer only to values of its type.

#### <a id="j39"></a>J39 Slotted dataclass defaults crash
🟡 **S3** (no current user) · trivial · likely-bug · hit in 1 of 6 (a monkeypatch, since removed) · [`J39_slotted_dataclass_default.py`](repros/J39_slotted_dataclass_default.py)

- `@dataclass(slots=True)` instance as a default: `TypeError: vars() argument
  must have __dict__ attribute` at `add_class_arguments`, from `convert_to_dict`
  (`_signatures.py:815`). 4.51 ❌ 4.53 ❌ v5 ❌ (not only 4.52). Fix: use
  `dataclasses.fields` when `__dict__` is absent (tested in a copy of v5).

#### <a id="j43"></a>J43 `parse_object` mutates list/dict containers in its input
🟡 **S3** · trivial · likely-bug · hit in 1 of 6 (fresh dicts built for every parse) · [`J43_parse_object_mutates_input.py`](repros/J43_parse_object_mutates_input.py)

- Each `class_path` dict inside a `list[Base]` or `dict[str, Base]` is replaced
  in place by a Namespace; single specs and dataclass sections are untouched.
  The same happens inside `Any` fields ([J30](#j30)). 4.51 ❌ 4.53 ❌ v5 ❌. Fix: copy the
  container in the list/dict branch.

#### <a id="j34"></a>J34 A docstring-parser failure silently drops constructor parameters
🟡 **S3** · trivial · likely-bug · hit in 1 of 6 · no repro (needs `bidict`; not rerun)

- With `docstring_parse_attribute_docstrings=True`, a class whose base breaks
  the docstring parser (e.g. `bidict`) loses all its parameters ("Option 'specs'
  is not accepted"). In the tracker already. Fix: catch per class and keep the
  parameters.

#### <a id="j57"></a>J57 Bare-generic dataloader fields failed with `__args__`
⚪ **S4** · resolved in the project by typing the fields `Any`; not rechecked.

[↑ Contents](#contents)

<a id="kind-intended-or-documented-behaviour-that-is-awkward"></a>

### Intended or documented behaviour that is awkward

#### <a id="j06"></a>J06 Dict fields in config overlays
🔴 **S1** · medium (opt-in) or design-change · debatable (docs: near-certain) · hit in 3 of 6 (largest workaround: a ~1,600-line generator producing ~50 standalone configs, a 40-way launcher switch, contradictory docs; KeyError crashes in workers after a successful parse) · [`J06_dict_overlay_key_set.py`](repros/J06_dict_overlay_key_set.py)

- **What happens**: for a `dict[K, V]` field (also `Optional[dict]`,
  `Mapping`): a later `--config`, a JSON value or an `__include__` replaces the
  key set, but for each key present in both, the previous value is merged by V's
  rules (subclass `init_args` and dataclass fields merge; scalars and plain dicts
  replace). A dotted flag (`--m.mods.p.init_args.y=9`) merges into the existing
  dict. Base `{p: Net(x=1), q: Net(x=2)}` plus overlay `{p: {init_args: {y: 9}}}`
  gives `{p: Net(x=1, y=9)}` from a second config but keeps `q` from the dotted
  flag. Dotted keys can't be written in YAML. For `dict[str, dict]` the dotted
  form stores values as strings.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌ (identical; `__include__` behaves like a
  second config by design, `test_include_in_dict_value_replaces_as_a_whole`).
- **Workaround**: restate every key to keep (`{}` keeps an entry as is), so an
  overlay *can* drop keys by omission but can't change one entry alone; or
  generate dotted flags; or generate whole configs.
- **Cause**: `adapt_typehints`, mapping branch (`_typehints.py:1776-1830`):
  `NestedArg` builds `{**prev_val, key: val}` (1780-1786); a whole dict passes
  `prev_val.get(k)` only for keys of the new dict (1810-1817). `Namespace.update`
  treats a dict as a leaf (`_namespace.py:289`). Documented only as "a second
  JSON dict replaces the previous value completely" (`DOCUMENTATION.rst:1099`).
- **Fix**: document the per-key merge; an opt-in `dict_merge` setting is about
  two lines (prototyped: `val = {**prev_val, **val}`), but breaks 5 tests that
  pin replace, and needs a delete marker since `{}` would no longer clear.

#### <a id="j05"></a>J05 Plain-class instance default: a partial override discards its values
🔴 **S1** · small–medium · debatable · hit in 1 of 6 (an agent-guideline rule; `None`-then-construct defaults in 5 places that hide the real default from `--help`) · [`J05_instance_default_partial_override.py`](repros/J05_instance_default_partial_override.py)

- **What happens**: `sampler: Sampler = field(default_factory=lambda:
  Sampler(fraction=0.2))` with a plain class. `--c.sampler.seed=3` (or YAML)
  builds `Sampler(fraction=0.0, seed=3)`: the 0.2 is silently replaced by the
  class default. `Optional[Sampler]` too. The default dump writes "Unable to
  serialize instance <...>" ([J09](#j09)), which doesn't reload. `lazy_instance` and
  pydantic instances keep 0.2.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Cause**: only None/dict/Namespace/lazy/dataclass-like defaults are converted
  (`_signatures.py:132-136, 170-182`); a plain instance stays opaque and
  overrides start from the class defaults.
- **Fix**: recover `init_args` when every `__init__` parameter is readable as an
  attribute; otherwise warn or raise at `add_argument` time ("use
  `lazy_instance`").

#### <a id="j25"></a>J25 A section file given to a parent group resets nullable sections
🟠 **S2** · small–medium · debatable (docs) · hit in 1 of 6 (four sections silently reset; a data overlay reset worker counts) · [`J25_section_file_resets_section.py`](repros/J25_section_file_resets_section.py)

- **What happens**: `add_class_arguments(Root, "trainer", sub_configs=True)`;
  `--trainer a.yaml --trainer b.yaml` where `b.yaml` sets only `a`: in an
  `Optional[Section] = None` section, `b` is reset to its default. With subclass
  mode on, required sections reset too. Whole-tree `--config` files, dotted
  flags and per-section files (`--trainer.opt b.yaml`) merge. On 4.x with the
  mode off, `Optional[S]` with an instance default also resets (to the class
  defaults); v5 merges that case.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌. v5 `__include__: a.yaml` inside `b.yaml`
  merges correctly, but only if the overlay names its base.
- **Fix**: merge like whole-tree configs, or document the rule precisely.

#### <a id="j11"></a>J11 Subclass mode side effects
🟠 **S2** (section file) / S3 (help, dump) · small · debatable · hit in 3 of 6 · [`J11_subclass_mode_side_effects.py`](repros/J11_subclass_mode_side_effects.py)

- **What happens** with `subclasses_enabled=["is_pure_dataclass"]`: a nested
  dataclass field becomes subclass-typed, so (a) `--cfg.output section.yaml`
  fails with "Unexpected import path format" (fine with the mode off); (b)
  `--help` lists none of the nested options (`--cfg.output.path`); (c) every
  nested dataclass dumps as `class_path`/`init_args`, so saved-config consumers
  must handle both shapes. Dotted overrides work.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Workaround**: pass sections as extra whole-tree configs; read
  `value.get("init_args", value)` at every level.
- **Fix**: keep the file-path form for dataclass groups under the mode (or say
  why it fails); list nested fields in `--help`.

#### <a id="j30"></a>J30 `class_path` specs in `Any` fields are converted and filled
🟡 **S3** · small · debatable · hit in 3 of 6 (a rule to use bare `dict` for payloads) · [`J30_any_spec_namespace.py`](repros/J30_any_spec_namespace.py)

- **What happens**: with instantiation off (`instantiate_subclass_spec_in_any=False`
  on 4.x, the v5 default), a spec inside `Any`, `object`, `dict[str, Any]` or
  `dict[str, object]` is not built but is turned into a Namespace with every
  default filled (9 dump lines instead of 5 in the repro); the caller's dict is
  mutated ([J43](#j43)). `dict`, `dict | None` and `Optional[dict]` pass values through.
  On v5, untyped parameters of third-party classes get the Namespace too, so
  sklearn meta-estimators fail with `'Namespace' object has no attribute
  '__sklearn_tags__'`, far from the cause.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌.
- **Fix**: treat `Any` values as data unless instantiation is on; on v5, warn
  when a spec is passed to an untyped parameter.

#### <a id="j22"></a>J22 `dump()` drops explicit `null`s
🟡 **S3** (down-ranked: clean workaround) · small · debatable · hit in 2 of 6 · [`J22_dump_drops_null.py`](repros/J22_dump_drops_null.py)

- `x: Optional[int] = 3` given `null` dumps as `{}` and reloads 3, also inside
  `init_args`. `skip_unset=False` keeps it and is accepted on 4.x and v5 alike
  (v5 removed `skip_none`). LightningCLI's saved config already uses it. 4.51 ❌
  4.53 ❌ v5 ❌.

#### <a id="j38"></a>J38 Function as `class_path` judged by return annotation only
🟡 **S3** · small · debatable · hit in 1 of 6 · [`J38_function_class_path_return.py`](repros/J38_function_class_path_return.py)

- For `b: Base`, functions returning `Base` or a subclass are accepted; a
  TypeVar bound to `Base`, `Any` or no annotation is rejected with "does not
  correspond to a subclass of Base", not mentioning the return annotation.
  4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j40"></a>J40 `null` accepted for non-Optional fields with a default
🟡 **S3** · small (strict option) · intended · hit in 1 of 6 · [`J40_null_for_non_optional.py`](repros/J40_null_for_non_optional.py)

- `a: int = 3`: YAML `a: null` is accepted (null means unset), `--a=null` is
  rejected. 4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j47"></a>J47 A failing `default_factory` breaks parser construction without context
🟡 **S3** · trivial (message) · intended / likely (message) · hit in 1 of 6 · [`J47_default_factory_postinit.py`](repros/J47_default_factory_postinit.py)

- `runtime: Runtime = field(default_factory=Runtime)` whose `__post_init__`
  raises: `add_class_arguments` raises the bare `ValueError: output_dir is
  required`, so `--help` and any flag that would supply the value fail too. The
  call is at `_signatures.py:499` (also `_parameter_resolvers.py:1118, 1144,
  1158`). Python's own `Job()` fails too; the missing part is context. Fix:
  `ex.add_note("while building the default_factory of Job.runtime ...")`.
  4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j32"></a>J32 `**kwargs` and untyped constructors need typed wrappers
🟡 **S3** · n/a · intended · hit in 3 of 6 (a typed `Pipeline` re-declaration, `Sequential` wrappers, a `copy_signature` helper). A collision between a library's `**kwargs` expansion and private constructors was reported but not reproduced; it may be a real resolver bug. No repro.

#### <a id="j50"></a><a id="j51"></a><a id="j52"></a><a id="j53"></a><a id="j54"></a><a id="j58"></a>J50, J51, J52, J53, J54, J58 (S4)
- **[J50](#j50)** `exit_on_error=True` (default) raises `SystemExit` inside library
  code; callers pass `exit_on_error=False`. Intended. Not rerun.
- **[J51](#j51)** `instantiate` returns a Namespace for a dataclass added at the root
  (`add_class_arguments(DC)`); with a nested key it builds `DC`. One project
  wrote a helper. [`J51_instantiate_root_dataclass.py`](repros/J51_instantiate_root_dataclass.py), all versions.
- **[J52](#j52)** field docs in `--help` need the global
  `docstring_parse_attribute_docstrings`, which also triggers [J34](#j34). Intended.
- **[J53](#j53)** a top-level `_anchors:` key that only holds YAML anchors is rejected
  ("Option '_anchors.w' is not accepted"), so anchors are defined deep inside a
  section. [`J53_top_level_anchor_holder.py`](repros/J53_top_level_anchor_holder.py), all versions.
- **[J54](#j54)** a `list[str]` field given a file path is rejected without
  `sub_configs=True` and loaded with it, so this is a clean workaround rather
  than a missing feature. [`J54_list_field_from_file.py`](repros/J54_list_field_from_file.py).
- **[J58](#j58)** `--print_config` writes relative paths as given (relative to the
  working directory) while `--config` resolves them against the config file, so
  a printed config saved elsewhere doesn't reload.
  [`J58_print_config_relative_paths.py`](repros/J58_print_config_relative_paths.py), all versions.

[↑ Contents](#contents)

<a id="kind-missing-features"></a>

### Missing features

#### <a id="j10"></a>J10 Global parsing settings: not idempotent, no public getter, no scope
🟠 **S2** · small · likely-bug (idempotence) / debatable (scope) · hit in 6 of 6 (save/restore helpers with private imports copied in 3; order-dependent CI failures, 11 of 12 runs red once; one release broke every run of one config family with exit 2) · [`J10_global_settings_not_idempotent.py`](repros/J10_global_settings_not_idempotent.py)

- **What happens**: a second identical
  `set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])` raises
  `ValueError: There is no function 'is_pure_dataclass' registered in
  subclasses_disabled`; there is no public getter (only the private
  `jsonargparse._common.get_parsing_setting`); a parser built before the mode is
  enabled keeps its group structure but follows the live global at parse time, so
  two parsers in one process can't have different modes. `register_type` twice
  with equal-but-new functions raises only on 4.51 (4.53 and v5 replace).
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌. The private names we import still exist on v5.
- **Cause**: `subclass_type_behavior` (`_common.py:707`, raise at 714-716) pops
  the selector and raises when it is already gone.
- **Fix**: make enabling an already-enabled selector a no-op (about 3 lines);
  export `get_parsing_setting`; a `parsing_settings(**kw)` context manager that
  snapshots and restores the settings and selector tables.

#### <a id="j19"></a>J19 No placeholder interpolation before validation
🟠 **S2** · medium (or docs for `set_loader`) · debatable · hit in 5 of 6 (three hand-built strategies in one; a parse, dump-without-validation, fill, reparse loop in another; two placeholder syntaxes in a third) · [`J19_placeholder_in_typed_field.py`](repros/J19_placeholder_in_typed_field.py)

- `${N}` in an `int`, `float` or `bool` field is rejected in the default mode.
  `omegaconf` mode resolves only config files; `omegaconf+` also CLI and
  `parse_object` values; both need every variable set, even for
  `--print_config`. A custom `set_loader` that runs `os.path.expandvars` before
  `yaml.safe_load` works for config files on 4.x and v5 (and for CLI values on
  v5). 4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j20"></a>J20 No deferred instantiation
🟠 **S2** · medium · debatable · hit in 2 of 6 (a ~700-line deferred-recipe layer, later removed; a private re-parse step) · no repro

- Wanted: validate a `class_path` spec now and build it later, e.g. a
  `Spec[Tokenizer]` type that checks the spec and returns it unbuilt.
  `lazy_instance` is discouraged in the docs and doesn't cover specs from
  configs.

#### <a id="j41"></a>J41 Dotted overrides and links into list and dict entries
🟡 **S3** · medium · debatable · hit in 1 of 6 (stages written as a mapping to make them addressable; a seed set "in both stages") · [`J41_dotted_override_list_index.py`](repros/J41_dotted_override_list_index.py)

- `--m.l.0.init_args.y=3` for `list[Base]` fails; `--m.d.k.init_args.y=3` for
  `dict[str, Base]` works; `link_arguments` to `m.l.0.init_args.y` and
  `m.d.k.init_args.y` both fail. `--m.l+=...` (append) is the only list edit.
  4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j55"></a>J55 argcomplete crashes on subcommand options and misses `class_path` fields
⚪ **S4** · not checked (the project removed argcomplete).

[↑ Contents](#contents)

<a id="kind-regressions-and-pins"></a>

### Regressions and pins

#### <a id="j26"></a>J26 Tagged union with an instance default rejects another member
🟠 **S2** · small (branch `fix-tagged-union-instance-default`) · likely-bug · hit in 1 of 6 (an earlier `<4.50` cap), possibly 2 · [`J26_tagged_union_instance_default.py`](repros/J26_tagged_union_instance_default.py)

> [!NOTE]
> **🔧 Work begun**: branch `fix-tagged-union-instance-default` (draft PR in `prs/`).

- `--u` typed `A | B` (tagged by `type: Literal[...]`) with default `A()`
  rejects `{"type": "b", "x": 3}`; fine without the default and with dotted
  flags. Since 4.50 (#921). 4.51 ❌ 4.53 ❌ v5 ❌.

[J01](#j01) (4.52) and [J18](#j18) (4.52) are the regressions behind the pins; see Bugs and
Intended.

[↑ Contents](#contents)

<a id="kind-lightningcli-interplay"></a>

### LightningCLI interplay

#### <a id="j07"></a>J07 LightningCLI 2.6.x calls APIs removed in v5
🔴 **S1** for v5 · small (in Lightning) · n/a (Lightning PR open) · hit in 4 of 6 (every LightningCLI entry point) · [`J07_lightningcli_removed_v5_apis.py`](repros/J07_lightningcli_removed_v5_apis.py)

- **What happens**: `LightningCLI(...)` on v5: `AttributeError:
  'LightningArgumentParser' object has no attribute 'add_instantiator'` (with
  `load_from_checkpoint_support=False`: `instantiate_classes`). Calls in
  `lightning/pytorch/cli.py` 2.6.5/2.6.6: `add_instantiator` (596, 601),
  `instantiate_classes` (612, 904), `skip_none=False` (290, 307, 590). `--help`
  and `--print_config` exit before this, so they work.
- **Status**: 4.51 ✅ 4.53 ✅ v5 ❌ (Lightning 2.6.5).
- **Lightning side**: main uses `instantiate`/`skip_unset` since #21906 but still
  calls the per-parser `add_instantiator` (with a TODO for v5) and pins
  `jsonargparse <4.51.0` in `requirements/pytorch/extra.txt`. Draft PR
  Lightning-AI/pytorch-lightning#22014 passes instantiators through
  `instantiate(..., instantiators=...)`.
- **Workaround**: a monkeypatch shim (`add_instantiator` stored and passed as
  `instantiators=`, `instantiate_classes = instantiate`, `skip_none` to
  `skip_unset`): with it, 17 of 18 v5-only failures in one project pass, and a
  small model's saved `config.yaml` and checkpoint hparams are identical to 4.53.

#### <a id="j42"></a>J42 Saved LightningCLI `config.yaml` doesn't load into `run=False`
🟡 **S3** · small (Lightning) · debatable · hit in 1 of 6 (an override of a private Lightning method; scripts that pop keys) · [`J42_lightning_saved_config_reload.py`](repros/J42_lightning_saved_config_reload.py)

- The saved config is flattened for the subcommand and contains `ckpt_path` and
  `weights_only`; a `run=False` CLI rejects them ("Option 'ckpt_path' is not
  accepted"). `fit --config saved.yaml` works. 4.51 ❌ 4.53 ❌; v5 blocked by [J07](#j07).

[↑ Contents](#contents)

<a id="kind-v5-migration"></a>

### v5 migration

#### <a id="j23"></a>J23 v5: a required `X | None` can't be given `null`
🟠 **S2** (top for v5) · medium · likely-bug · hit in 2 of 6 (7 and 14 v5 test failures; 15 recipe files use the value), further unverified candidates in a third · [`J23_required_optional_null.py`](repros/J23_required_optional_null.py)

- **What happens**:
  ```python
  class Seq:
      def __init__(self, count: int | None, dim: int = 1): ...
  p.add_class_arguments(Seq, "seq"); p.parse_object({"seq": {"count": None}})
  ```
  v5: "the following arguments are required: seq.count", also via
  `--seq.count=null`, YAML, `init_args`, nested dataclasses, `dict`/`list`
  values. 4.x accepts (with a deprecation warning that such parameters "will be
  required"). A `skip_unset=False` dump that writes `count: null` doesn't reload.
- **Status**: 4.51 ✅ 4.53 ✅ v5 ❌; with `set_parsing_settings(unset_sentinel=True)`
  every route works and an omitted value still fails.
- **Cause**: `check_required` (`_core.py:1398`) compares with
  `get_parsing_setting("unset_sentinel")`, which is `None` by default, so an
  explicit `None` counts as missing.
- **Workaround**: `= None` at each site (a semantic change: the field becomes
  optional; the suites find only sites that configs exercise); or
  `unset_sentinel=True`, which in one project made 52 tests fail (`Unset`
  leaking as the string 'None'; not re-checked).
- **Fix**: no one-line fix: flipping the default fails 111 upstream tests; a
  narrower variant fails 288 and misses `init_args`. Needs a decision (default
  required nullable parameters to `Unset` internally, or record that a key was
  given). Meanwhile name `unset_sentinel=True` in the deprecation message and
  guide.

#### <a id="j45"></a>J45 v5 migration of our own code, and guide gaps
🟡 **S3** · small · likely (docs) · hit in 5 of 6 · no repro

- **Our code**: removed `parser.instantiate_classes` in 2 projects (one
  production CLI, one test, some scripts); `skip_none` in docstrings and
  comments; pytest filters on `jsonargparse._deprecated` in 2 projects ([J48](#j48));
  one stale `<5` pin comment blaming a call the project no longer makes; two
  `instantiate` overrides that must forward `**kwargs`; the
  `jsonargparse[signatures,yaml]` extra. All private imports we use (`_common`
  selectors, `_optionals` docstring options, `_parameter_resolvers`,
  `_namespace.expand_dict`) still resolve on 5.0.0rc2.
- **Guide gaps**: listed in Shortlist (c) item 4.

#### <a id="j49"></a>J49 v5 dumps `init_args: {args: []}` for `nn.Module` subclasses
⚪ **S4** · trivial · likely-bug · [`J49_varargs_dump_nn_module.py`](repros/J49_varargs_dump_nn_module.py)

- An `nn.Module` subclass without its own `__init__` inherits
  `__init__(*args, **kwargs)`; with v5's `*args` support (#986) every dump gains
  `init_args: {args: []}`. Reloads fine; noise in saved configs and diffs.
  4.51 ✅ 4.53 ✅ v5 ❌. Suggest: omit empty varargs.

[↑ Contents](#contents)

<a id="kind-warning-noise"></a>

### Warning noise

#### <a id="j48"></a>J48 No public warning category; the private filter path is gone in v5
⚪ **S4** · trivial · debatable · hit in 3 of 6 · [`J48_deprecation_warning_filter.py`](repros/J48_deprecation_warning_filter.py)

- Lightning's calls trigger `JsonargparseDeprecationWarning`s; the first one
  shown on 4.x is a generic "only one per type is shown" banner, so the real
  message reads as a second warning. Projects filter by
  `jsonargparse._deprecated.JsonargparseDeprecationWarning`; on v5 the module is
  gone and pytest reports "Failed to import filter module". No warning class is
  exported publicly on any version. Use a message filter or
  `JSONARGPARSE_DEPRECATION_WARNINGS=off` until one is.

#### <a id="j56"></a>J56 `Union[Dataclass, dict]` with an empty-dict default is filled
⚪ **S4** · small · debatable · hit in 1 of 6 (a third-party warning on every run, filtered) · [`J56_union_dataclass_dict_empty_default.py`](repros/J56_union_dataclass_dict_empty_default.py)

- A third-party config class with `quant: Union[QuantConfig, dict] =
  field(default_factory=dict)`: jsonargparse takes the dataclass arm for the
  empty default and fills it (`Namespace(bits=4, iters=1)`), so the library gets
  a non-empty value it never asked for. 4.51 ❌ 4.53 ❌ v5 ❌. Better raised as an
  example in a general issue about unions of dataclass and dict.

---

[↑ Contents](#contents)

---

<a id="resolved"></a>

# 🟢 Resolved upstream

Merged upstream. The *Released* column says whether a release has it yet.

| ID | Issue | Sev | Fixed by | Released | What it unlocks, or what is left |
|---|---|---|---|---|---|
| [J21](#j21) | Changing `class_path` keeps the old class's `init_args`, including defaults | 🟠 S2 | #1038 (main), #1037 (v4 branch), by the maintainer; merged 2026-11-25 | No: after 5.0.0rc2; 4.54 not out | Switching a class (Adam to AdamW) gets the new class's own defaults. On v5, overlays that switch `class_path` and relied on values carrying over need `prior_init_args: keep` |
| [J08](#j08) | Nested `class_path` parse time grows exponentially with depth | 🟠 S2 | our #1036 (main); merged 2026-11-23 | No: after 5.0.0rc2; no 4.x backport | Real configs parse in 3.8 s, not 35 s; a parked ~180-line cache can go |
| [J28](#j28) | Constructor errors reported as a union mismatch | 🟡 S3 | #1015 (v5) | In 5.0.0rc2 | Deleting two copies of a message-matching unwrapper and their tests |
| [J29](#j29) | Quadratic list parsing | 🟡 S3 | #975 (v5) | In 5.0.0rc2 | Large lists in typed fields; a backport is low value for us now (the workaround is in place) |
| [J03](#j03) | The #968 union-default leak, which our 4.51.0 pins keep | 🔴 S1 | #968 | 4.52.0 | Fixed upstream; what is left is ours: move off 4.51 once [J01](#j01) lands ([J18](#j18), [J07](#j07) also hold pins) |

Partly fixed, so still listed as open: [J30](#j30) (#969 turns instantiation in `Any`
off by default in v5, but specs are still converted and filled) and [J12](#j12) (v5
messages are better, but still bury the cause).

#### <a id="j21"></a>🟢 J21 Changing `class_path` keeps the old class's `init_args`
🟠 **S2** · done (main, v4 branch; unreleased) · intended · hit in 3 of 6 (an optimizer switched from Adam to AdamW trained with `weight_decay=0`; a replace-only config edit language; required optimizer fields) · [`J21_class_path_switch_keeps_init_args.py`](repros/J21_class_path_switch_keeps_init_args.py)

> [!TIP]
> **🟢 Fixed upstream by the maintainer (merged 2026-11-25, not yet released)**: [#1038](https://github.com/mauvilsa/jsonargparse/pull/1038) (main, v5) makes a
> `class_path` change discard the earlier `init_args`, adds a
> `prior_init_args: keep | discard` key (`--opt:keep` / `--opt:discard` on the
> command line), and makes `keep` skip the old class's signature defaults;
> [#1037](https://github.com/mauvilsa/jsonargparse/pull/1037) (v4 branch, 4.54)
> adds the same options to v4 and deprecates keeping. That covers both fixes
> suggested below.
>
> **Verified on main (3b30c14, 2026-11-26)**: the repro gives `OptB` its own
> `weight_decay=0.01` and `RMSNormOpts` its own `eps=1e-6`. With layered config
> files, a `dict[str, Base]` entry switched from `OptA` to `OptB` gets `OptB`'s
> defaults; repeating the same class still layers; and `prior_init_args: keep`
> keeps the given values for both the dict entry and the union-of-dataclasses
> field (rc2 rejects the key). [J26](#j26) still reproduces on main, so its branch is
> still needed. On v5, check whether any of our overlays switch `class_path` and
> rely on values carrying over; those now need `prior_init_args: keep`.

- **What happens**: when `class_path` changes, only `init_args` the new class
  doesn't accept are dropped; everything else carries over, including values
  that were just the old class's *defaults*. Two shapes:
  - default `OptA` (`weight_decay` default 0.0), config `class_path: OptB`
    (default 0.01): `OptB` gets 0.0.
  - union field `LayerNormOpts | RMSNormOpts` with default instance
    `LayerNormOpts()` (eps 1e-5), config `class_path: RMSNormOpts` with no
    `init_args`: RMSNormOpts gets eps 1e-5 instead of its own 1e-6. This is not
    the #968 leak (fixed in 4.52); it is this documented carry-over and is
    present on every released version.
  Same inside `dict[str, Base]` overlays.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ❌ (5.0.0rc2); main ✅ (3b30c14, #1038).
- **Cause** (before #1038): `discard_init_args_on_class_path_change` (`_typehints.py:2757-2779`;
  Namespace twin `:590-612`). Documented (`DOCUMENTATION.rst:1473`) and pinned by
  tests.
- **Fix**: an opt-in "reset on class change" (prototyped, about one line; breaks
  14 tests if on by default); or reset only values whose provenance is
  "default", keeping ones the user set.

#### <a id="j08"></a>🟢 J08 Nested `class_path` parse time grows exponentially with depth
🟠 **S2** · done on main (#1036, v5 only); backport medium · likely-bug · hit in 3 of 6 · [`J08_nested_class_path_depth.py`](repros/J08_nested_class_path_depth.py)

> [!TIP]
> **🟢 Fixed upstream by our #1036** (merged 2026-11-23 into main, after 5.0.0rc2; not yet released). There is no 4.x backport.

- A chain of `Optional[Base]` specs: on 4.53 depth 4 takes 0.06 CPU s and depth
  8 takes 2.6 s (about 2.5x per level); on v5 depth 8 takes 0.02 s. Real
  configs: 35.3 and 17.3 CPU s on 4.53 against 3.8 s each on v5, with identical
  output apart from [J49](#j49); another project 17-22 s per parse on 4.51, and about 3x
  faster on v5 for a third. One project parked a ~180-line cache mixin that
  touches five private context variables.
- **Status**: 4.51 ❌ 4.53 ❌ v5 ✅.

#### <a id="j28"></a>🟢 J28 Constructor errors reported as a union mismatch
🟡 **S3** · done (#1015, v5) · hit in 4 of 6 (two copies of a message-matching unwrapper, one imported by a third project) · [`J28_ctor_error_union_report.py`](repros/J28_ctor_error_union_report.py)

- A constructor's `ValueError` inside `Optional[Base]` arrives as "Does not
  validate against any of the Union subtypes" with the real error as
  `__cause__` (4.50 chains the wrong cause). v5 raises the constructor's own
  exception, so the unwrappers become dead code, and a subclass that overrides
  `instantiate` must forward v5's `instantiators=` keyword. 4.51 ❌ 4.53 ❌ v5 ✅.
- See also [J12](#j12), [J47](#j47).

#### <a id="j29"></a>🟢 J29 Quadratic list parsing
🟡 **S3** · done (#975, v5) · hit in 2 of 6 (a 74k-item list took about an hour; large lists moved out of typed fields) · [`J29_list_parse_quadratic.py`](repros/J29_list_parse_quadratic.py)

- `list[str]` via `--x=<json>`: 4k items 3.2 s, 16k items 51 s on 4.51; 0.09 s
  and 0.38 s on v5. 4.51 ❌ 4.53 ❌ v5 ✅.

#### <a id="j03"></a>🟢 J03 Version pins keep 4 of 6 projects on 4.51.0, which has the #968 leak
🔴 **S1** (meta) · n/a (unblocked by [J01](#j01), [J18](#j18), [J07](#j07)) · hit in 6 of 6

- **State**: four projects lock 4.51.0 (one with an exact `==4.51.0` pin, the
  others `!=4.52.0`); two lock 4.53.0. The pin comments cite #959 ([J18](#j18)) and
  Protocol `class_path` handling ([J01](#j01)); one project's own configs pass on 4.52.0,
  so its exclusion is defensive. One floor is `>=4.50`, which would allow 4.50's
  worse behaviour if the lock were regenerated.
- **#968** (fixed in 4.52.0: "each union subtype is now adapted against a
  pristine copy of the value"): on 4.51 one project's smoke config came out with
  `eps: 1.0e-05` in two places where its RMSNorm default is 1e-6; 4.52, 4.53 and
  v5 are correct. A by-hand check of another project's production config on 4.51
  (87 `class_path` nodes) found no leaked value, and its output is identical on
  v5. No standalone repro: the trigger needs the real classes. The
  instance-default carry-over that remains on every released version is [J21](#j21).
- **Upper bounds**: Lightning caps `jsonargparse<5` only in its
  `pytorch-extra`/`pytorch-all` extras; 3 of 6 projects have no `<5` of their
  own, so a fresh resolve after v5 ships would pick v5 and break LightningCLI
  ([J07](#j07)).

[↑ Contents](#contents)

---

<a id="not-an-issue"></a>

## Checked, not an issue (or not reproduced)

- <a id="j46"></a>**[J46](#j46)**: saved configs that name a since-removed class or use an old
  placeholder syntax don't reload. Not a jsonargparse defect.
- **[J11](#j11), dotted overrides under subclass mode**: reported as breaking; not
  reproduced in plain, nested, `Optional` or config-plus-flag shapes. The
  section-file failure is what reproduces.
- **[J30](#j30), "a second parse of the same dict fails"**: came from a test that passed
  the inner dict at the top level. With the right shape the second parse works;
  the input is still mutated. A reported "Option 'params' is not accepted" for
  AdamW inside `Any` did not reproduce in 12 shapes.
- **[J12](#j12) case 4, `None` silently accepted for a required subclass argument**:
  the argument in that test was not required; with `required=True` it is
  rejected.
- **[J14](#j14) through signatures for a plain `str`**: not read, even with
  `sub_configs=True`; only `str | Class` unions (and direct `add_argument(type=str,
  sub_configs=True)`) are.
- **[J24](#j24) for a plain Protocol field**: a fixpoint; only defaults nested in a
  dataclass default or a union are not.
- **[J03](#j03), #968 in one project's production config on 4.51**: no leaked value.
- **[J17](#j17), "use ABCs, not Protocols"**: simple public Protocols parse fine; the
  rule overstates the limit.
- **[J35](#j35) for LightningCLI's parser**: not exposed.
- **[J37](#j37), `Union[Any, Sentinel]` dump crash**: fixed in 4.51.0.
- **[J10](#j10), `register_type` "already registered"**: 4.51 only.
- **`JSONARGPARSE_DEBUG=1` raising**: by design since 4.47 (not v5-specific);
  see (c) item 5.

[↑ Contents](#contents)

---

<a id="readme-corrections"></a>

## Relationship to README.md

Statements in the tracker that this work corrects or extends:

1. **Slotted dataclasses**: present on 4.51.0 as well as 4.53.0 and main; the
   belief that it was specific to 4.52.0 came from a monkeypatch that was only
   written for that version.
2. **"Not reproduced on 4.53 or main: a parameter with an unevaluable
   annotation being dropped"**: version-dependent. It was dropped on 4.50 and
   earlier and is kept, unvalidated, since 4.51. The tested trigger is a quoted
   name inside `|` under postponed annotations.
3. **Unevaluable annotations**: add a second trigger with no broken annotation
   at all: a non-first dataclass base from another module ([J04](#j04)), and its cousin
   [J44](#j44) (a field bound to the wrong class).
4. **A path is read as a config**: right for signatures (`str | SomeDataclass`
   only); add that `add_argument(type=str, sub_configs=True)` is affected too,
   that a large file is read into memory several times including by `dump`,
   and that `os.PathLike | str` avoids it.
5. **Path types**: the `"None"` result is command-line only (YAML `null` gives
   `None`); lists are stringified too.
6. **Protocols**: add that jaxtyping annotations never compare equal (a shared
   alias works), that private members of mixed Protocols are not checked, and
   that unannotated implementer methods are rejected.
7. **Protocols with `__call__` (Being fixed)**: the branch does not cover
   `Callable[[...], Class]`, which 4.52 changed in the same way, and it
   rejects a `__call__` without a return annotation against a Protocol returning
   a class, which 4.51 accepted.
8. **Undumpable defaults**: extend to lists, tuples and dicts of dataclass or
   pydantic instances, and to plain-class instance defaults, whose partial
   overrides also silently discard values ([J05](#j05)).
9. **Attributes that aren't `__init__` parameters**: `field(init=False,
   default=...)` is fine; an `init=False` field set in `__post_init__` is what
   fails. The README's "Not reproduced: `field(init=False)` breaking defaults"
   and its fix-branch description should say which.
10. **Global settings**: add no scope (a parser follows the live global), and
    that `register_type` raising on a repeat registration is 4.51 only.
11. **`link_arguments` can't target a dict or list entry**: add that dotted CLI
    overrides reach dict keys but not list indices.
12. **sklearn `Ridge`**: the recursion is a cycle among function-local names
    (`X`, `intercept_column`, `sqrt_sw`, `xp`, `n_samples`), and a one-line fix
    is tested (`skip=skip | {name}`).
13. **C builtins**: the setting is ignored only after the first stub lookup;
    `math.sqrt` is correctly rejected.
14. **Changing a `class_path` keeps the old `init_args`** (now under Fixed
    upstream): it also carried the old class's *defaults*, and covered a union
    field with an instance default (LayerNorm default instance,
    `class_path: RMSNorm`, eps 1e-5) on every released version; that is distinct
    from the fixed #968. Both are fixed on main by #1038.
15. **A section file replaces the section**: only a section file or inline
    mapping given to the parent group, and only for nullable sections (and
    required ones under subclass mode); whole-tree configs, dotted flags and
    per-section files merge; v5 `__include__` in the overlay composes correctly.
16. **PEP 695 aliases**: the quoted self-reference (what ruff writes) still
    fails on main; 4.51 reads the alias as untyped and gives tuples.
17. **`class_path` specs inside `object`/`Any` (Fixed upstream)**: instantiation
    stops, but specs are still converted to Namespaces with defaults filled, the
    input dict is mutated, and v5's default breaks untyped third-party
    parameters with an unhelpful error.
18. **Constructor errors (Fixed upstream)**: note that the message prefix
    changed in v5, so code matching it becomes dead.
19. **Nested subclass parsing (Fixed upstream, main)**: v5 only; 4.x users keep
    the exponential cost unless it is backported.
20. **`Unset` sentinel**: in our check a `jsonargparse.Unset` default dumped as
    `jsonargparse._common.Unset` reloads on 4.51 and 4.53 and is denied on v5
    (the `==UNSET==` form was not tested).
21. **Not in the README at all**: [J05](#j05), [J06](#j06), [J07](#j07), [J09](#j09) (containers), [J12](#j12), [J21](#j21)'s
    union case, [J23](#j23), [J24](#j24), [J25](#j25)'s exact rule, [J27](#j27)'s version history, [J43](#j43), [J44](#j44),
    [J47](#j47), [J49](#j49), [J51](#j51), [J53](#j53), [J56](#j56), [J58](#j58).

[↑ Contents](#contents)
