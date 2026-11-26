# jsonargparse issue inventory

Every jsonargparse problem that six of our research projects hit, or would hit,
with what it cost us, a repro script, and a suggested fix. Which ones we plan to
send upstream, and the fix branches, are in the [README](README.md); this file
has the detail.

- **Versions checked**: 4.51.0, 4.53.0 (latest v4), and 5.0.0rc2 plus main at
  29d6f00 ("v5" below); some boundaries also on 4.49, 4.50 and 4.52. Entries
  that changed on main since were re-checked on 3b30c14.
- **Dates**: surveyed 2026-11-24; updated 2026-11-26.
- **Method**: we went through the projects' code, history and notes for
  workarounds, version pins and incidents, re-checked each candidate with a
  standalone script on each version ([repros/](repros/)), and ran the projects'
  test suites and CLIs against v5. "Hit in N of 6" counts the projects with
  code, a pin or an incident caused by the issue.

> [!IMPORTANT]
> **53 open issues** (🔴 5 S1 · 🟠 19 S2 · 🟡 18 S3 · ⚪ 11 S4), **5 fixed
> upstream** (🟢), and one found not to be a jsonargparse issue.

<a id="contents"></a>

## Contents

- [How to read an entry](#how-to-read-this)
- [Open issues](#open-issues): [design requests](#design-requests) · [v5 feedback](#v5-feedback) · [all open issues](#overview)
- [Detailed entries](#open-details): [bugs](#kind-bugs) · [intended but awkward](#kind-intended-or-documented-behaviour-that-is-awkward) · [missing features](#kind-missing-features) · [regressions and pins](#kind-regressions-and-pins) · [LightningCLI](#kind-lightningcli-interplay) · [v5 migration](#kind-v5-migration) · [warning noise](#kind-warning-noise)
- [🟢 Fixed upstream](#resolved)
- [Checked, not an issue](#not-an-issue)

<a id="how-to-read-this"></a>

## How to read an entry

Each entry starts with one line:

> 🟠 **S2** · small · likely-bug · hit in 3 of 6 · `repro script`

That is severity · effort to fix · whether upstream would likely take a fix ·
how many of our six projects it affected · the script that reproduces it.

| Field | Values |
|---|---|
| **Severity** | 🔴 **S1** silent wrong values or lost validation in normal use, or blocks an upgrade · 🟠 **S2** forces an awkward or fragile workaround, or is silent but needs an unusual setup · 🟡 **S3** real but contained, or has a clean workaround · ⚪ **S4** cosmetic, rare, or kept for the record |
| **Effort** | trivial (a few lines) · small (under ~50 lines plus tests) · medium (several code paths, or a design choice) · design-change · done |
| **Appetite** | likely-bug (upstream would probably take a fix) · debatable · intended (documented or deliberate; at most a docs change or an opt-in) |
| **Status** | per version: ❌ present · ✅ absent or fixed · – not applicable · ? not checked |
| **Boxes** | 🔧 blue *Note*: we have a fix branch · 🟢 green *Tip*: fixed upstream |

[↑ Contents](#contents)

---

<a id="open-issues"></a>

# Open issues

Our priorities for sending fixes upstream, with diffs and line counts, are in
the [README](README.md). The two lists below cover what doesn't fit there:
requests that need a design decision, and feedback for the v5 release.

<a id="design-requests"></a><a id="shortlist-b"></a>

## Design requests (debatable or intended)

Behaviour that is documented or deliberate, but cost us. Each would be a
discussion upstream, not a bug report.

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

<a id="v5-feedback"></a><a id="shortlist-c"></a>

## v5 feedback

For the release-candidate thread (mauvilsa/jsonargparse#999). Every v5-only
test failure in our five suites traced to [J01](#j01), [J07](#j07), [J23](#j23),
[J30](#j30)'s sklearn case, or [J45](#j45)'s renames; nothing else broke.

1. **[J23](#j23): a required `X | None` parameter can't take `null` with the
   default settings.** Intended (#678, #969); `unset_sentinel=True` is the way
   to allow it, and in our tests it works once [J59](#j59) and [J13](#j13) are
   fixed. Ask: say so in the migration guide's "become required" entry and in
   the v4 deprecation message. Docs only, not an issue.
2. **[J07](#j07): LightningCLI 2.6.x doesn't run on v5.** It calls APIs v5
   removed. Lightning caps `jsonargparse<5` only in its extras, so a fresh
   install of a project without its own `<5` picks v5 and breaks, while
   `--help` and `--print_config` still work and give false confidence. The
   draft Lightning-AI/pytorch-lightning#22014 covers it. Ask: a note in the
   guide on LightningCLI's status, and confirmation that
   `instantiate(..., instantiators=...)` is stable API.
3. **[J01](#j01) also affects `Callable[..., Class]`.** Since 4.52, not new in
   v5. The fix branch handles it in a separate second commit, which relaxes a
   check added on purpose in 4.52 (#959), so it is a question for the
   maintainer.
4. **Gaps in the migration guide** ([J45](#j45)):
   - the `add_instantiator` row says to use `instantiators=`, while the v4
     deprecation message says to use the global function;
   - `merge_config` is called "internal API", but it was public;
   - subclasses that override `instantiate(self, namespace,
     instantiate_groups=True)` must now forward `**kwargs`;
   - untyped constructor parameters of third-party classes (sklearn
     meta-estimators) now receive a `Namespace` and fail with
     `'Namespace' object has no attribute '__sklearn_tags__'` ([J30](#j30));
   - the union error no longer starts with "Does not validate against any of
     the Union subtypes", which downstream code matched on ([J28](#j28));
   - the `omegaconf>=2.4.0` floor is only in the changelog;
   - removed methods give a bare `AttributeError`; a `__getattr__` pointing to
     the guide would help.
5. **No public warning class** ([J48](#j48)). Projects filter Lightning-triggered
   warnings in pytest with `jsonargparse._deprecated.JsonargparseDeprecationWarning`;
   on v5 pytest reports "Failed to import filter module" and the filter does
   nothing. Ask: export `JsonargparseWarning` and its deprecation subclass.
6. **`JSONARGPARSE_DEBUG=1` raises** `ValueError: Invalid boolean value`, so a
   common way of turning on debug output aborts the program. By design since
   4.47 (only `true`/`false`), so not a v5 regression; accepting `1`/`0`, or
   warning, would be kinder.
7. **Smaller v5 changes**: `init_args: {args: []}` is dumped for every
   `nn.Module` subclass without its own `__init__` ([J49](#j49), cosmetic); a
   `jsonargparse.Unset` default no longer reloads (import-path denylist,
   [J37](#j37)).
8. 🟢 **What v5 fixed for us** (see [Fixed upstream](#resolved)):
   - nested `class_path` parse time ([J08](#j08), our #1036): 35 and 17 CPU s
     down to 3.8 s on real configs, and about 3x faster on another project;
   - quadratic list parsing ([J29](#j29));
   - constructor errors raised as themselves ([J28](#j28));
   - a `class_path` change discards the old class's `init_args` ([J21](#j21),
     #1038, merged after rc2);
   - unquoted recursive `type` aliases ([J33](#j33));
   - `Optional[S]` with an instance default merges across section files
     ([J25](#j25));
   - `Source: config file:line` and "Known subclasses" in error messages
     ([J12](#j12)).

[↑ Contents](#contents)

<a id="overview"></a>

## All open issues

Sorted by severity, then ID. 🔧 marks the ones with a fix branch.

| ID | Title | Kind | Sev | Effort | Appetite | Status | Repro |
|---|---|---|---|---|---|---|---|
| [J01](#j01) | Callable Protocol (and `Callable[..., C]`) rejects classes whose instances implement it 🔧 | regression-or-pin | 🔴 S1 | small | likely-bug | 4.51 ✅ 4.53 ❌ v5 ❌ | [`J01_protocol_call_returns_class.py`](repros/J01_protocol_call_returns_class.py) |
| [J04](#j04) | Dataclass with a non-first base from another module: every field silently unvalidated 🔧 | bug | 🔴 S1 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J04_mixin_base_unvalidated.py`](repros/J04_mixin_base_unvalidated.py) |
| [J05](#j05) | Plain-class instance default: a partial override silently discards its values | bug | 🔴 S1 | small–medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J05_instance_default_partial_override.py`](repros/J05_instance_default_partial_override.py) |
| [J06](#j06) | Dict fields in overlays: key set replaced, surviving keys merged; dotted form merges | intended-but-awkward | 🔴 S1 | medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J06_dict_overlay_key_set.py`](repros/J06_dict_overlay_key_set.py) |
| [J07](#j07) | LightningCLI 2.6.x calls APIs removed in v5 | lightning-interplay | 🔴 S1 | small (Lightning) | n/a (PR open) | 4.51 ✅ 4.53 ✅ v5 ❌ | [`J07_lightningcli_removed_v5_apis.py`](repros/J07_lightningcli_removed_v5_apis.py) |
| [J02](#j02) | Protocol matching needs identical annotations: jaxtyping never equal; Modules need `-> Any` | bug | 🟠 S2 | small | likely-bug / debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J02_protocol_exact_annotations.py`](repros/J02_protocol_exact_annotations.py) |
| [J09](#j09) | Container defaults of dataclasses dump as "Unable to serialize instance" 🔧 | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J09_undumpable_container_defaults.py`](repros/J09_undumpable_container_defaults.py) |
| [J10](#j10) | Global settings: not idempotent, no public getter, no scope 🔧 | missing-feature | 🟠 S2 | small | likely-bug / debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J10_global_settings_not_idempotent.py`](repros/J10_global_settings_not_idempotent.py) |
| [J11](#j11) | Subclass mode: section files rejected, nested options hidden from `--help`, dump shape changes | intended-but-awkward | 🟠 S2 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J11_subclass_mode_side_effects.py`](repros/J11_subclass_mode_side_effects.py) |
| [J12](#j12) | Error messages bury the cause | error-message | 🟠 S2 | medium | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ (better) | [`J12_error_messages_bury_cause.py`](repros/J12_error_messages_bury_cause.py) |
| [J13](#j13) | `os.PathLike` stringifies anything; CLI `null` becomes `"None"` 🔧 | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J13_pathlike_null_and_coercion.py`](repros/J13_pathlike_null_and_coercion.py) |
| [J14](#j14) | A `str` value naming an existing file is read as a config (silent) 🔧 | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J14_str_value_read_as_config_file.py`](repros/J14_str_value_read_as_config_file.py) |
| [J15](#j15) | Subscripted generic (`Model[int]`) rejects a subclass's `init_args` 🔧 | bug | 🟠 S2 | small (branch) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J15_subscripted_generic_subclass.py`](repros/J15_subscripted_generic_subclass.py) |
| [J16](#j16) | Default instance with non-`__init__` attributes rejected under Optional/union/subclass mode 🔧 | bug | 🟠 S2 | small (branch) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J16_default_instance_nonfield_attrs.py`](repros/J16_default_instance_nonfield_attrs.py) |
| [J17](#j17) | Protocols with only `_` members match nothing; no variance 🔧 | bug | 🟠 S2 | trivial–small | likely-bug / debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J17_protocol_private_members.py`](repros/J17_protocol_private_members.py) |
| [J18](#j18) | C builtins rejected for `Callable[[Tensor], Tensor]`; stubs setting read once | intended-but-awkward | 🟠 S2 | trivial | intended / likely-bug | 4.51 ✅ 4.53 ❌ v5 ❌ | [`J18_c_builtin_callable.py`](repros/J18_c_builtin_callable.py) |
| [J19](#j19) | No placeholder interpolation before validation | missing-feature | 🟠 S2 | medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J19_placeholder_in_typed_field.py`](repros/J19_placeholder_in_typed_field.py) |
| [J20](#j20) | No deferred instantiation (validate a `class_path` now, build later) | missing-feature | 🟠 S2 | medium | debatable | ? (feature) | — |
| [J23](#j23) | v5: a required `X \| None` can't be given `null` unless `unset_sentinel=True` | v5-migration | 🟠 S2 | n/a | intended | 4.51 ✅ 4.53 ✅ v5 ❌ | [`J23_required_optional_null.py`](repros/J23_required_optional_null.py) |
| [J24](#j24) | Protocol-typed class default inside a dataclass default or union dumps as a bare path; not a fixpoint 🔧 | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J24_protocol_class_default_dump.py`](repros/J24_protocol_class_default_dump.py) |
| [J25](#j25) | A section file given to a parent group resets nullable sections | intended-but-awkward | 🟠 S2 | small–medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J25_section_file_resets_section.py`](repros/J25_section_file_resets_section.py) |
| [J26](#j26) | Tagged union with an instance default rejects another member 🔧 | regression-or-pin | 🟠 S2 | small (branch) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J26_tagged_union_instance_default.py`](repros/J26_tagged_union_instance_default.py) |
| [J27](#j27) | One unevaluable annotation leaves every field of the class unvalidated 🔧 | bug | 🟠 S2 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J27_quoted_forward_ref_in_union.py`](repros/J27_quoted_forward_ref_in_union.py) |
| [J59](#j59) | With `unset_sentinel=True`, a `None` in a `Callable \| None` field is dumped as "Unable to serialize instance None" | regression-or-pin | 🟠 S2 | trivial | likely-bug | 4.51 ✅ 4.53 ❌ v5 ❌ | [`J59_unset_sentinel_none_callable_dump.py`](repros/J59_unset_sentinel_none_callable_dump.py) |
| [J22](#j22) | `dump()` drops explicit `null`s; reload gives the default | intended-but-awkward | 🟡 S3 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J22_dump_drops_null.py`](repros/J22_dump_drops_null.py) |
| [J30](#j30) | `class_path` specs in `Any` fields are converted to Namespaces and filled; input mutated | intended-but-awkward | 🟡 S3 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J30_any_spec_namespace.py`](repros/J30_any_spec_namespace.py) |
| [J31](#j31) | `stubs_resolver_allow_py_files=True` gives sklearn `Ridge` zero parameters | bug | 🟡 S3 | trivial | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J31_stubs_py_files_sklearn_ridge.py`](repros/J31_stubs_py_files_sklearn_ridge.py) |
| [J32](#j32) | `**kwargs`/untyped constructors need hand-written typed wrappers | intended-but-awkward | 🟡 S3 | n/a | intended | ? | — |
| [J33](#j33) | Recursive PEP 695 alias with a quoted self-reference fails | bug | 🟡 S3 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J33_pep695_recursive_alias.py`](repros/J33_pep695_recursive_alias.py) |
| [J34](#j34) | A docstring-parser failure silently drops constructor parameters | bug | 🟡 S3 | trivial | likely-bug | ? (not rerun) | — |
| [J35](#j35) | Stale `--config` in nested parsers of a parser subclass | bug | 🟡 S3 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J35_stale_config_nested_parser.py`](repros/J35_stale_config_nested_parser.py) |
| [J36](#j36) | Tuple-keyed dicts keep string keys; tuple-key default dump doesn't reload | bug | 🟡 S3 | small | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J36_tuple_keyed_dict.py`](repros/J36_tuple_keyed_dict.py) |
| [J37](#j37) | Sentinels: `register_type` serializer applied by union arm; `Unset` doesn't reload on v5 | bug | 🟡 S3 | small–medium | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J37_register_type_union_serializer.py`](repros/J37_register_type_union_serializer.py) |
| [J38](#j38) | Function as `class_path` judged by return annotation only | intended-but-awkward | 🟡 S3 | small | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J38_function_class_path_return.py`](repros/J38_function_class_path_return.py) |
| [J39](#j39) | Slotted dataclass defaults crash (`vars()`) 🔧 | bug | 🟡 S3 | trivial | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J39_slotted_dataclass_default.py`](repros/J39_slotted_dataclass_default.py) |
| [J40](#j40) | `null` accepted for non-Optional fields with a default (config only) | intended-but-awkward | 🟡 S3 | small | intended | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J40_null_for_non_optional.py`](repros/J40_null_for_non_optional.py) |
| [J41](#j41) | Dotted overrides can't reach list entries; links can't reach list or dict entries | missing-feature | 🟡 S3 | medium | debatable | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J41_dotted_override_list_index.py`](repros/J41_dotted_override_list_index.py) |
| [J42](#j42) | Saved LightningCLI `config.yaml` doesn't load into `run=False` | lightning-interplay | 🟡 S3 | small (Lightning) | debatable | 4.51 ❌ 4.53 ❌ v5 – ([J07](#j07)) | [`J42_lightning_saved_config_reload.py`](repros/J42_lightning_saved_config_reload.py) |
| [J43](#j43) | `parse_object` mutates list/dict containers in its input 🔧 | bug | 🟡 S3 | trivial | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J43_parse_object_mutates_input.py`](repros/J43_parse_object_mutates_input.py) |
| [J44](#j44) | Inherited dataclass field resolved in the base module's namespace 🔧 | bug | 🟡 S3 | small (with [J04](#j04)) | likely-bug | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J44_inherited_annotation_namespace.py`](repros/J44_inherited_annotation_namespace.py) |
| [J45](#j45) | v5 migration of our own code, and migration-guide gaps | v5-migration | 🟡 S3 | small | likely (docs) | v5 only | — |
| [J47](#j47) | Failing `default_factory` (validating `__post_init__`) breaks parser construction without context 🔧 | intended-but-awkward | 🟡 S3 | trivial | intended / likely (message) | 4.51 ❌ 4.53 ❌ v5 ❌ | [`J47_default_factory_postinit.py`](repros/J47_default_factory_postinit.py) |
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

Fixed upstream, so not in this table: [J03](#j03), [J08](#j08), [J21](#j21),
[J28](#j28), [J29](#j29). [J46](#j46) [is not a jsonargparse issue](#not-an-issue).

[↑ Contents](#contents)

<a id="open-details"></a>

## Detailed entries

<a id="kind-bugs"></a>

### Bugs

#### <a id="j01"></a>J01 A callable Protocol rejects a class whose instances implement it, even as the default
🔴 **S1** · small · likely-bug · hit in 4 of 6 · [`J01_protocol_call_returns_class.py`](repros/J01_protocol_call_returns_class.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-factory-protocol-instances` (draft PR in `prs/`), rebased on main 2026-11-26. Commit 1 fixes the Protocol case; a separable commit 2 fixes the `Callable[..., Class]` case.

**In short:** since 4.52, a Protocol whose `__call__` returns a class (and
likewise a `Callable[..., Class]`) is treated as a factory for that class. So a
class whose *instances* implement the Protocol is rejected, even when it is the
field's own default, and every parse fails. The error never mentions the
Protocol.

**Example:**

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
`Expected '__main__.DecoderChoice' to be a subclass of Decoder`, so every parse
of `Model` fails. `class_path: DecoderChoice` fails too, and so does
`Callable[[int], Decoder]` given a class with callable instances (also since
4.52).

**Impact on us:** one project pins exactly `==4.51.0`, two more lock 4.51, and
another puts `-> Any` on three Protocols. On v5, this caused 82 of 89 v5-only
test failures in one project and 137 of 140 in another. The fix branch alone
unblocks only the first: the second project's loss classes are `nn.Module`s,
whose `__call__` has no return annotation, so they still don't implement its
Protocol returning `Float[Tensor, " "]` ([J02](#j02)). That project needs
`-> Any` on the Protocol as well (checked 2026-11-26).

**Status:** 4.51 ✅ 4.52 ❌ 4.53 ❌ v5 ❌.

**Workaround:** stay on 4.51; or annotate the Protocol's return as `Any` (works
for `nn.Module` implementers, loses the return type; see [J02](#j02)); or widen
the field to `Factory | Choice`.

**Cause:** 4.52 added a rule in the Callable branch of `_typehints.py` (the
`if subclass_types:` check): a `class_path` class must be a subclass of the
`__call__` return type. It runs before the check for classes with callable
instances.

**Fix:** branch `fix-factory-protocol-instances`, in two commits.

- Commit 1 (Protocols): a class that isn't a subclass of the return type is
  accepted if its instances implement the Protocol (`implements_protocol`).
- Commit 2 (`Callable[..., Class]`): a class is accepted if its `__call__`
  returns a subclass of `Class`. Like functions, it is checked by return type
  only, so a wrong arity is accepted and fails at call time. This relaxes a
  check added on purpose in 4.52 (#959), so it is a question for the
  maintainer and can be dropped.
- Still rejected: a class whose `__call__` has no return annotation (such as
  `nn.Module`) against a Protocol with an annotated return, which 4.51
  accepted; see [J02](#j02).

A one-line reordering (`if subclass_types and not callable_instances(val_class)`)
would restore 4.51 exactly, but checks no conformance at all.

#### <a id="j04"></a>J04 Dataclass with a non-first base from another module: every field silently unvalidated
🔴 **S1** · small · likely-bug · hit in 1 of 6 · [`J04_mixin_base_unvalidated.py`](repros/J04_mixin_base_unvalidated.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-inherited-annotation-namespace`, which fixes this and [J44](#j44) (draft PR in `prs/`).

**In short:** if a dataclass has two bases and the second one is defined
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

**Impact on us:**

- In one project, the 5 stage config classes, which every pipeline run uses,
  have no validation at all (`batch_size: "sixteen"`, a bad `Literal`,
  `freeze_model: "maybe"` all pass), although that project's docs say they are
  validated. A scan of 4 projects found no other affected classes.
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

**Fix:** branch `fix-inherited-annotation-namespace` (+18 −7): look up each
field's names in the module where that field was written, which is what
`typing.get_type_hints` already does. The maintainer took the same approach for
`TypedDict` keys inherited from other modules (#936). It also fixes [J44](#j44).

#### <a id="j44"></a>J44 Inherited dataclass field resolved in the base module's namespace
🟡 **S3** · small · likely-bug · hit in 1 of 6 · [`J44_inherited_annotation_namespace.py`](repros/J44_inherited_annotation_namespace.py)

> [!NOTE]
> **🔧 Fix branch**: fixed on the [J04](#j04) branch `fix-inherited-annotation-namespace`.

**In short:** the same lookup as [J04](#j04), going wrong the other way:
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

**Impact on us:** an import alias, and a rule not to reuse class names
across modules ("never shadow a library class name"). Whether the class that
prompted the rule has this exact shape wasn't checked; if it has, this is S2.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Fix:** the [J04](#j04) fix (same branch, same small change).

#### <a id="j02"></a>J02 Protocol matching needs identical annotations
🟠 **S2** · small · likely-bug (jaxtyping) / debatable (untyped implementer returns) · hit in 2 of 6 · [`J02_protocol_exact_annotations.py`](repros/J02_protocol_exact_annotations.py)

**In short:** a class implements a Protocol only if every parameter annotation
is equal (`==`). This breaks in two cases:

- **jaxtyping:** jaxtyping builds a new class on each subscription, so
  `Float[Tensor, "b d"] == Float[Tensor, "b d"]` is False. A Protocol with
  `__call__(self, x: Float[Tensor, "b d"]) -> Any` is never implemented by a
  class that writes its own `x: Float[Tensor, "b d"]` (it fails with "does not
  implement protocol"), on any version. A shared alias object
  (`Emb = Float[...]` used in both) works.
- **`nn.Module`:** it is matched on the untyped `nn.Module.__call__`, so it
  passes only against a Protocol returning `-> Any`. Even with the [J01](#j01)
  fix branch, one project's `nn.Module` losses are rejected for this reason.

**Status:** separate jaxtyped annotations: 4.51 ❌ 4.53 ❌ v5 ❌. `nn.Linear`
against `-> Tensor`: 4.51 ✅ 4.53 ❌ v5 ❌ (4.51 skipped the check, see
[J01](#j01)).

**Workaround:** `-> Any` on the Protocol plus a shared alias for jaxtyped
arguments. Verified end to end: one project's full training config then parses
on stock v5 with output identical to 4.51. Cost: the output shape lives only in
docstrings.

**Cause:** `type_var_wildcard_matches` in `_typehints.py` falls back to `==`,
and `protocol_params_match` requires every parameter to match.

**Fix:** after `==`, compare objects that expose `dtype`/`dim_str`/`array_type`
structurally (or by `repr`); optionally treat an unannotated implementer return
as compatible.

#### <a id="j09"></a>J09 Lists and dicts of dataclasses as defaults are saved as "Unable to serialize instance"
🟠 **S2** · small · likely-bug · hit in 4 of 6 · [`J09_undumpable_container_defaults.py`](repros/J09_undumpable_container_defaults.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-dump-container-defaults` (draft PR in `prs/`; local only for now).

**In short:** a single dataclass default is saved as a mapping, but a default
that is a `list[Rule]`, `tuple[Rule, ...]` or `dict[str, Rule]` (also of
pydantic models) is saved as the text
`- Unable to serialize instance Rule(pattern='a.*')`, which fails to reload
with "Unexpected import path format". An untyped `dict` holding an instance
makes `dump` raise `RepresenterError`. The only signal is a
`JsonargparseWarning`, shown once per location.

**Example:** `rules: list[Rule] = field(default_factory=lambda: [Rule("a.*")])`
dumps as text that doesn't reload.

**Impact on us:** where the workaround isn't used, saved configs contain this
unreloadable text.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Workaround:** `None` defaults plus a runtime constant, so `--print_config`
hides the effective value.

**Cause:** instances inside containers go through `serialize_as_import_path` in
`_typehints.py`, which returns the literal text "Unable to serialize instance
..." on `ValueError`.

**Fix:** serialize dataclass/pydantic/attrs instances inside containers the
same way as a single default, and raise instead of writing text.

#### <a id="j12"></a>J12 Error messages bury the cause
🟠 **S2** · medium · likely-bug (specific cases) · hit in 6 of 6 · [`J12_error_messages_bury_cause.py`](repros/J12_error_messages_bury_cause.py)

**In short:** in three common cases the real cause is hidden under unrelated
or repeated text. With the small values of the repro; real configs give
messages of 2-17 KB:

1. A typo three plain dataclasses deep (subclass mode on): the cause,
   `Option 'lrr' is not accepted`, is line 7 of 7. It comes after three
   `Problem with given class_path '...'` lines for dataclasses that never had a
   `class_path`.
2. A missing module in one element of `list[Callback] | Callback | None`: every
   arm of the union is listed, the value is printed twice, and each arm adds a
   "Subclass types expect one of" blurb.
3. `add_subclass_arguments(SomeDataclass)` with subclass mode off gives
   `Expected 'baseclass' to be a subclass type ...`, naming neither the cause
   nor the fix.

**Impact on us:** hit in all 6 projects. One project's docs quote the case-1
kind of message as *the* symptom of an unrelated problem.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌. v5 is better: it adds `Source: file:line` and
"Known subclasses", and cuts constructor-argument errors from 263 to 121
characters. Cases 1 and 3 are unchanged, and the whole value is still printed in
`Got value:` (about 17 KB for one wrong key in a real config).

**Fix:** (1) don't wrap non-subclass types in `Problem with given class_path`;
lead with `Parser key "a.b.c": Option 'lrr' is not accepted`. (2) Print the
value once, last, truncated; drop arms that can't apply (the NoneType arm for a
non-null value). (3) Reuse the clear "Subclasses are disabled for X" text that
the `class_path` path already has. Issue draft: `issues/error-message-wording.md`.

#### <a id="j13"></a>J13 `os.PathLike` turns anything into a string; a command-line `null` becomes `"None"`
🟠 **S2** · small · likely-bug · hit in 3 of 6 · [`J13_pathlike_null_and_coercion.py`](repros/J13_pathlike_null_and_coercion.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-pathlike-coercion` (draft PR in `prs/`).

**In short:** for a field typed `os.PathLike | str | None` (or
`os.PathLike | None`), `--p=null` on the command line gives the string
`'None'` instead of `None`. `os.PathLike` also accepts any value as a string:
`--p=7` gives `'7'`, `--p=[a,b]` gives `"['a', 'b']"`.

**Impact on us:** a run was staged into a directory called `./None`; there is
also a ~50-line convention docstring. It also blocks `unset_sentinel=True`
([J23](#j23)): with that setting `None` is validated like any other value, so a
`None` reaching a path field from a config or a Python mapping becomes
`'None'` too. That broke 3 tests in one project; the fix branch fixes them.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌. A YAML `p: null` gives `None` correctly; only
the command line (or any source passing a real `None` to the union) is
affected.

**Cause:** `register_type(os.PathLike, str, str)` in `typing.py` makes the
deserializer `str`, and the `PathLike` arm is tried before `None`.

**Fix:** a deserializer that accepts only `str`/`PathLike`; try `None` first.

#### <a id="j14"></a>J14 A `str` value that names an existing file is replaced by the file's contents
🟠 **S2** · small · likely-bug · incident in 1 of 6 · [`J14_str_value_read_as_config_file.py`](repros/J14_str_value_read_as_config_file.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-str-value-read-as-config` (a prototype; to be raised as an issue first, draft in `issues/`).

**In short:** with `sub_configs=True` (LightningCLI sets it), a string value
that names an existing file is loaded as a config. A text file silently becomes
the value; a file that parses as a mapping becomes the dataclass arm. Nothing
warns. Through signatures (the LightningCLI path) only a union of `str` with a
class is affected; a direct `add_argument(type=str, sub_configs=True)` is
affected too.

**Example:** the value `data.csv`, an existing file holding `a,b\n1,2\n`, gives:

| parameter | `sub_configs=False` | `sub_configs=True` |
|---|---|---|
| signature `plain: str` | `'data.csv'` | `'data.csv'` |
| signature `uni: str \| D` (D a dataclass) | `'data.csv'` | **`'a,b\n1,2\n'`** (file text) |
| `add_argument("--p", type=str, sub_configs=True)` | – | **file text** |
| `add_argument(type=os.PathLike \| str, sub_configs=True)` | – | `'data.csv'` |

**Impact on us:** a predict run hung reading a multi-GB HDF5 file during config
dumping. A 300 MB binary file is opened three times in `parse_args` and again
in `dump`, with peak memory (RSS) about 3.3 times the file size, so multi-GB
files hang. To avoid this, 4 projects follow a `PathLike | str` alias
convention, in 28 files.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌ (plain parser; the LightningCLI path checked
on 4.51 and 4.53).

**Workaround:** type path fields `os.PathLike | str` (`is_pathlike` turns
`enable_path` off). It works, but every path field in every LightningCLI-built
class must follow it, and it relies on [J13](#j13)'s lenient `PathLike`.

**Cause:** `ActionTypeHint.__init__` in `_typehints.py` keeps `enable_path`
unless the type contains `os.PathLike`; `parse_value_or_config` then reads any
string that names a file, and falls back to the string only if loading or
validation fails.

**Fix:** never read a file for a value that is valid for a `str` arm. Read
sub-configs only for arms that can hold a config (class, dataclass, mapping),
and only when the string is not accepted as is.

#### <a id="j15"></a>J15 A subclass's `init_args` are rejected when the type is a subscripted generic
🟠 **S2** · small · likely-bug · hit in 2 of 6 · [`J15_subscripted_generic_subclass.py`](repros/J15_subscripted_generic_subclass.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-subscripted-generic-init-args` (draft PR in `prs/`).

**In short:** if an argument is typed `Model[int]`, a subclass given as its
`class_path` cannot take its own parameters. With a plain `Model` type it works.

**Example:**

```python
class Model(Generic[T]):
    def __init__(self, value: Optional[T] = None): ...

class IntModel(Model[int]):
    def __init__(self, depth: int = 1): ...

parser.add_argument("--model", type=Model[int])
parser.parse_args(["--model=__main__.IntModel", "--model.depth=2"])
```

This fails with "Option 'depth' is not accepted". With `type=Model` it is
accepted.

**Impact on us:** one project added per-type marker ABCs to avoid it (15 files,
+293 lines, plus a review rule); the other first misread it as a depth
problem.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Cause:** since #775, `adapt_class_type` builds the parser from the
subscripted type, whatever the `class_path` is.

**Fix:** use the subscripted type only when the `class_path` is the generic
class itself.

#### <a id="j16"></a>J16 A default instance is rejected if it has attributes that are not `__init__` parameters
🟠 **S2** · small · likely-bug · hit in 2 of 6 · [`J16_default_instance_nonfield_attrs.py`](repros/J16_default_instance_nonfield_attrs.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-default-instance-non-field-attributes` (draft PR in `prs/`); it fixes every shape tested.

**In short:** a dataclass instance used as a default is rejected if its
`__post_init__` sets an extra attribute (such as `self.derived`, a `_cache`, or
an `init=False` field). This happens when the field is `Optional`, a union, or
subclass-typed.

**Example:**

```python
@dataclass
class Pub:
    a: int = 1
    def __post_init__(self):
        self.derived = self.a * 2

@dataclass
class Opt:
    x: Optional[Pub] = field(default_factory=Pub)

parser.add_class_arguments(Opt, "c")
parser.parse_args([])
```

This fails with "Option 'derived' is not accepted". It works if `x` is typed
plain `Pub` (without subclass mode), and `field(init=False, default=7)` is fine.

**Impact on us:** a registry was redesigned, and derived values were turned
into properties. 9 of 223 dataclasses in one project would break if used as
defaults.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Cause:** `convert_to_dict` builds `init_args` from `vars(value)`, so every
instance attribute becomes an option.

**Fix:** keep only `__init__` parameters. The branch's second commit also
fixes [J39](#j39).

#### <a id="j17"></a>J17 A Protocol whose members all start with `_` matches nothing; no variance in Protocol checks
🟠 **S2** · trivial (message) / small · likely-bug (message) / debatable (variance) · incident in 1 of 6 · [`J17_protocol_private_members.py`](repros/J17_protocol_private_members.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-protocol-private-members-message`, for the message only (draft PR in `prs/`; local only for now).

**In short:** a Protocol whose only member is `_encode` matches no class ("does
not implement protocol"). In a Protocol with both public and private members,
the private one is not checked at all. Checks also ignore variance:
`f(x: float | int)` does not count as implementing `f(x: float)`, `-> int` does
not count as implementing `-> float`, and an unannotated `f(self, x)` is
rejected.

**Impact on us:** in one project this made the only training config unusable.
An "ABCs, not Protocols" rule exists in 5 of 6 projects. Simple public
Protocols do work, so the blanket rule overstates the limit.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Cause:** `get_protocol_members` in `_typehints.py` skips `_` names that are
not dunders; `implements_protocol` returns False when no members remain.

**Fix:** give a clear message, e.g. "protocol P has no checkable members (names
starting with `_` are ignored)".
Separately, consider a variance-aware comparison.

#### <a id="j18"></a>J18 C builtins rejected for `Callable[[Tensor], Tensor]`; the stubs setting is read only once
🟠 **S2** · trivial (cache) · intended (rejection, #959/#963) / likely-bug (caching) · cited by pins in 5 of 6 · [`J18_c_builtin_callable.py`](repros/J18_c_builtin_callable.py)

**In short:** since 4.52, `torch.log1p` is rejected for
`Callable[[Tensor], Tensor]`, because a function given by path must have a
matching return annotation or stub (this is intended). Setting
`stubs_resolver_allow_py_files=True` makes torch work, but only if it is set
before the first stub lookup; set later, it is ignored. (`math.sqrt` is
correctly rejected: its stub returns `float`.)

**Impact on us:** cited by pins in 5 of 6 projects.

**Status:** 4.51 ✅ 4.53 ❌ v5 ❌. The late setting is ignored on 4.53 and v5.

**Workaround:** type it `Callable[[Tensor], Any]` (the type check is lost), or
enable the setting early, which then triggers [J31](#j31) for sklearn.

**Cause:** `get_stubs_resolver()` in `_stubs_resolver.py` caches the resolver
in a module global. torch has no `torch/__init__.pyi`; its stubs are reachable
only through `.py` files.

**Fix:** reset the cached resolver when the setting changes (in
`set_parsing_settings`).

#### <a id="j24"></a>J24 A class default for a Protocol field is saved as a bare import path, without its arguments
🟠 **S2** · small · likely-bug · hit in 1 of 6 · [`J24_protocol_class_default_dump.py`](repros/J24_protocol_class_default_dump.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-protocol-class-default-dump` (draft PR in `prs/`).

**In short:** take `discrete: Factory = Decoder`, where `Factory` is a
`__call__` Protocol. When this default sits inside a dataclass default
(`sel: Choice = Choice()`) or in a union with a dataclass
(`head: Factory | Choice = Decoder`), the first dump writes
`discrete: __main__.Decoder`. Reloading and dumping again writes `class_path`
plus `init_args` (`width: 4`). So the saved config leaves out the
hyperparameters, and a later change of the code default silently changes what
an old config means.

A plain `x: Factory = Decoder` field and `Callable[..., Decoder]` are saved
correctly on the first dump (checked; narrower than first reported).

**Impact on us:** affects the saved config of every training run in one
project.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Workaround:** none in use (the project dumps only once).

**Fix:** save class defaults of Protocol fields as `class_path`/`init_args`
when the default comes from an enclosing default instance or a union.

#### <a id="j27"></a>J27 One unevaluable annotation leaves every field of the class unvalidated
🟠 **S2** · small · likely-bug · hit in 2 of 6 · [`J27_quoted_forward_ref_in_union.py`](repros/J27_quoted_forward_ref_in_union.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-unevaluable-annotation-fallback` (draft PR in `prs/`; local only for now).

**In short:** under `from __future__ import annotations`, a field written
`weights: "Weights" | None = None` (a quoted name inside `|`) can't be
evaluated, although `Weights` is importable. Since 4.51 this turns off
validation for every field of the class, silently: `weights: 7` and
`lr: "abc"` are both accepted. On 4.50 and earlier the parameter was dropped
instead.

**Impact on us:** one project removed `from __future__ import annotations`
from its config modules; another lost a parameter on 4.50 or earlier.

**Status:** 4.50 drops the parameter; 4.51 ❌ 4.53 ❌ v5 ❌. Only
`JSONARGPARSE_DEBUG=true` shows why.

**Workaround:** avoid quoted names inside `|`, or drop postponed annotations.

**Cause:** evaluating `"Weights" | None` means evaluating `str | None`, which
raises `TypeError`; the whole class then falls back to `Unvalidated`.

**Fix:** evaluate each field separately (one bad annotation shouldn't disable
the class), try evaluating string elements before applying `|`, and warn when a
field or class falls back to `Unvalidated`.

#### <a id="j31"></a>J31 `stubs_resolver_allow_py_files=True` gives sklearn `Ridge` zero parameters
🟡 **S3** · trivial · likely-bug · hit in 3 of 6 · [`J31_stubs_py_files_sklearn_ridge.py`](repros/J31_stubs_py_files_sklearn_ridge.py)

**In short:** `add_class_arguments(Ridge, "r")` registers 8 parameters
normally and 0 with this setting on. The underlying RecursionError appears only
as a DEBUG log, so the user just sees "Option 'alpha' is not accepted" later.

**Impact on us:** one project removed the setting; in another, 2 tests failed;
a third had planned to use it.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌ (scikit-learn 1.8 and 1.9).

**Cause:** `StubsResolver.add_module_aliases` in `_stubs_resolver.py` treats
every assignment in `_ridge.py`, including ones inside functions, as an alias.
It recurses with `skip={name}`, which breaks only cycles of length 1; `X`,
`intercept_column`, `sqrt_sw`, `xp` and `n_samples` form a longer cycle.

**Fix:** use `skip=skip | {name}` (tested in a copy of v5: all 8 parameters
come back). Also catch `RecursionError`, so a failed stub never removes
signature parameters.

#### <a id="j33"></a>J33 A recursive PEP 695 alias with a quoted self-reference fails
🟡 **S3** · small · likely-bug · hit in 2 of 6 · [`J33_pep695_recursive_alias.py`](repros/J33_pep695_recursive_alias.py)

**In short:** with `type Nested[K, V] = dict[K, V | "Nested[K, V]"]` (the form
ruff's UP040 writes), on 4.51 `--c.weights.cross=1` gives `('cross', '1')`; on
4.53 and v5 a nested dict is rejected. The unquoted form works on v5, but on
4.53 it hits a RecursionError when the parser is built.

**Impact on us:** one project reverted a lint rule; once, 62 tests failed.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌ (unquoted form: v5 ✅).

**Workaround:** a `TypeAlias` with `noqa`. Dotted overrides then work, but depth 2
is left unvalidated on all versions.

**Fix:** resolve the quoted self-reference in the alias's own scope.

#### <a id="j34"></a>J34 A docstring-parser failure silently drops constructor parameters
🟡 **S3** · trivial · likely-bug · hit in 1 of 6 · no repro (needs `bidict`; not rerun)

**In short:** with `docstring_parse_attribute_docstrings=True`, a class whose
base breaks the docstring parser (e.g. `bidict`) loses all its parameters
("Option 'specs' is not accepted"). In the tracker already.

**Fix:** catch the failure per class and keep the parameters.

#### <a id="j35"></a>J35 Nested parsers of a parser subclass inherit its `--config`
🟡 **S3** · small · likely-bug · hit in 1 of 6 · [`J35_stale_config_nested_parser.py`](repros/J35_stale_config_nested_parser.py)

**In short:** with a parser subclass that adds `--config` in `__init__`, a
nested class with a `config` parameter fails with "Unable to add parameter
'config' ... because argument '--config' already exists". A plain
`ArgumentParser` works. LightningCLI's parser is not affected, because it adds
`--config` after construction.

**Impact on us:** one project patches the private `_option_string_actions`.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Cause:** nested parsers are built from `parent.__class__`. The re-added action is removed from `_actions` but
not from `_option_string_actions`.

**Fix:** remove it from both, or build nested parsers without the subclass's
extra options.

#### <a id="j36"></a>J36 Tuple-keyed dicts are not parsed or saved correctly
🟡 **S3** · small · likely-bug · hit in 1 of 6 · [`J36_tuple_keyed_dict.py`](repros/J36_tuple_keyed_dict.py)

**In short:** `dict[tuple[str, str], float]` accepts any string as a key
(`'[a, b]'`, `'not-a-tuple'`) and keeps it as a string. A default with tuple
keys is saved as a YAML complex key that doesn't load back (on v5: "Failed to
parse as JSON"). One project uses a wrapper type instead.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j37"></a>J37 Three-state sentinels don't round-trip
🟡 **S3** (S1-grade silent data loss if used) · small–medium · likely-bug · hit in 1 of 6 · [`J37_register_type_union_serializer.py`](repros/J37_register_type_union_serializer.py)

**In short:** a sentinel type registered with a serializer can make other values
in a union be saved as the sentinel. Given `register_type(InheritType, serializer=lambda v:
"inherit", ...)` and `x: InheritType | bool = INHERIT`, `--x=false` is saved as
`x: inherit` and loads back as the sentinel. With `bool | InheritType` it is
correct. Separately, a `jsonargparse.Unset` default is saved as
`jsonargparse._common.Unset`; 4.x loads it back, but v5's import-path denylist
refuses it.

**Impact on us:** one project has a sentinel design note; the projects avoid
`register_type`.

**Status:** serializer 4.51 ❌ 4.53 ❌ v5 ❌; `Unset` reload 4.51 ✅ 4.53 ✅
v5 ❌. `Union[Any, Sentinel]` crashed `dump` on 4.50 and round-trips since
4.51, so "sentinel arm first" hacks can go.

**Fix:** apply a registered serializer only to values of its type.

#### <a id="j39"></a>J39 A slotted dataclass instance as a default crashes
🟡 **S3** (no current user) · trivial · likely-bug · hit in 1 of 6 · [`J39_slotted_dataclass_default.py`](repros/J39_slotted_dataclass_default.py)

> [!NOTE]
> **🔧 Fix branch**: fixed on the [J16](#j16) branch `fix-default-instance-non-field-attributes` (commit 2).

**In short:** using a `@dataclass(slots=True)` instance as a default fails at
`add_class_arguments` with `TypeError: vars() argument must have __dict__
attribute`, raised from `convert_to_dict` in `_signatures.py`. One project
worked around it with a monkeypatch, since removed.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌ (not only 4.52).

**Fix:** read the `__init__` parameters with `getattr` instead of `vars()`.
This is the second commit of the [J16](#j16) branch; the standalone branch
`fix-slotted-dataclass-default` (which used `dataclasses.fields` when
`__dict__` is absent) is superseded.

#### <a id="j43"></a>J43 `parse_object` changes list and dict containers in its input
🟡 **S3** · trivial · likely-bug · hit in 1 of 6 · [`J43_parse_object_mutates_input.py`](repros/J43_parse_object_mutates_input.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-parse-object-mutates-input` (draft PR in `prs/`; local only for now).

**In short:** each `class_path` dict inside a `list[Base]` or
`dict[str, Base]` in the input is replaced in place by a Namespace. Single specs
and dataclass sections are left untouched. The same happens inside `Any` fields
([J30](#j30)). One project builds fresh dicts for every parse.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Fix:** copy the container in the list/dict branch.

#### <a id="j57"></a>J57 Bare-generic dataloader fields failed with `__args__`
⚪ **S4** · resolved in the project by typing the fields `Any`; not rechecked.

[↑ Contents](#contents)

<a id="kind-intended-or-documented-behaviour-that-is-awkward"></a>

### Intended or documented behaviour that is awkward

#### <a id="j06"></a>J06 A later config replaces a dict field's key set but merges the surviving keys
🔴 **S1** · medium (opt-in) or design-change · debatable (docs: near-certain) · hit in 3 of 6 · [`J06_dict_overlay_key_set.py`](repros/J06_dict_overlay_key_set.py)

**In short:** for a `dict[K, V]` field (also `Optional[dict]`, `Mapping`), a
later `--config`, a JSON value or an `__include__` drops every key it doesn't
name. Keys it does name are merged with the previous value by V's rules:
subclass `init_args` and dataclass fields merge; scalars and plain dicts are
replaced. A dotted flag instead merges into the existing dict and keeps all
keys.

**Example:**

```yaml
# base.yaml
m: {mods: {p: Net(x=1), q: Net(x=2)}}   # written as class_path/init_args
# over.yaml
m: {mods: {p: {init_args: {y: 9}}}}
```

`--config base.yaml --config over.yaml` gives `{p: Net(x=1, y=9)}`: `q` is
gone. `--config base.yaml --m.mods.p.init_args.y=9` keeps `q`. Dotted keys
can't be written in YAML, and for `dict[str, dict]` the dotted form saves
values as strings.

**Impact on us:** the largest workaround is a ~1,600-line generator that
produces ~50 standalone configs, plus a 40-way launcher switch and docs that
contradict each other. Workers crashed with `KeyError` after a successful parse.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌, identical. `__include__` behaves like a
second config by design (`test_include_in_dict_value_replaces_as_a_whole`).

**Workaround:** restate every key to keep (`{}` keeps an entry as is). So an
overlay *can* drop keys by leaving them out, but can't change one entry alone.
Or generate dotted flags, or whole configs.

**Cause:** in `_typehints.py`, `adapt_typehints` (mapping branch): a
`NestedArg` builds `{**prev_val, key: val}`, while a whole dict passes
`prev_val.get(k)` only for the keys of the new dict. `Namespace.update` in
`_namespace.py` treats a dict as a leaf. `DOCUMENTATION.rst` only says "a second
JSON dict replaces the previous value completely".

**Ask:** document the per-key merge. An opt-in `dict_merge` setting is about two
lines (prototyped: `val = {**prev_val, **val}`). Against it: it breaks 5 tests
that pin the replace behaviour, and needs a delete marker, since `{}` would no
longer clear an entry.

#### <a id="j05"></a>J05 Overriding one field of a plain-class instance default discards its other values
🔴 **S1** · small–medium · debatable · hit in 1 of 6 · [`J05_instance_default_partial_override.py`](repros/J05_instance_default_partial_override.py)

**In short:** when a field's default is an instance of a plain class, setting
one of its fields (on the command line or in YAML) rebuilds it from the class
defaults, silently losing the other values of the default instance.

**Example:**

```python
sampler: Sampler = field(default_factory=lambda: Sampler(fraction=0.2))
```

`--c.sampler.seed=3` builds `Sampler(fraction=0.0, seed=3)`: the 0.2 is lost.
`Optional[Sampler]` behaves the same. The default dump writes "Unable to
serialize instance <...>" ([J09](#j09)), which doesn't reload. `lazy_instance`
and pydantic instances keep 0.2.

**Impact on us:** a rule in one project's agent guidelines, and
`None`-then-construct defaults in 5 places, which hide the real default from
`--help`.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Cause:** `_signatures.py` converts only None, dict, Namespace, lazy and
dataclass-like defaults. A plain instance stays opaque, so overrides start from
the class defaults.

**Ask:** recover `init_args` when every `__init__` parameter can be read back as
an attribute; otherwise warn or raise at `add_argument` time ("use
`lazy_instance`").

#### <a id="j25"></a>J25 A section file given to a parent group resets nullable sections
🟠 **S2** · small–medium · debatable (docs) · hit in 1 of 6 · [`J25_section_file_resets_section.py`](repros/J25_section_file_resets_section.py)

**In short:** with `add_class_arguments(Root, "trainer", sub_configs=True)`,
`--trainer base.yaml --trainer over.yaml`, where `over.yaml` sets only field
`a`, resets field `b` of an `Optional[Section] = None` section to its default
instead of keeping the value from `base.yaml`. With subclass mode on, required
sections are reset too. Whole-tree `--config` files, dotted flags and
per-section files (`--trainer.opt over.yaml`) merge as expected. On 4.x with the
mode off, `Optional[S]` with an instance default is also reset (to the class
defaults); v5 merges that case.

**Impact on us:** four sections were silently reset; a data overlay reset the
worker counts.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌. On v5, `__include__: base.yaml` inside
`over.yaml` merges correctly, but only if the overlay names its base.

**Ask:** merge like whole-tree configs, or document the rule precisely.

#### <a id="j11"></a>J11 Subclass mode breaks section files, hides nested options in `--help` and changes the dump shape
🟠 **S2** (section file) / S3 (help, dump) · small · debatable · hit in 3 of 6 · [`J11_subclass_mode_side_effects.py`](repros/J11_subclass_mode_side_effects.py)

**In short:** with `subclasses_enabled=["is_pure_dataclass"]`, a nested
dataclass field becomes subclass-typed, so:

- `--cfg.output section.yaml` fails with "Unexpected import path format" (it
  works with the mode off);
- `--help` lists none of the nested options (such as `--cfg.output.path`);
- every nested dataclass is saved as `class_path`/`init_args`, so code that reads
  saved configs must handle both shapes.

Dotted overrides work.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Workaround:** pass sections as extra whole-tree configs; read
`value.get("init_args", value)` at every level.

**Ask:** keep the file-path form for dataclass groups under the mode (or explain
why it fails); list nested fields in `--help`.

#### <a id="j30"></a>J30 `class_path` specs in `Any` fields are turned into filled-in Namespaces
🟡 **S3** · small · debatable · hit in 3 of 6 · [`J30_any_spec_namespace.py`](repros/J30_any_spec_namespace.py)

**In short:** with instantiation off (`instantiate_subclass_spec_in_any=False`
on 4.x, the default on v5), a `class_path` spec inside `Any`, `object`,
`dict[str, Any]` or `dict[str, object]` is not built, but it isn't left as given
either: it becomes a Namespace with every default filled in (9 dump lines
instead of 5 in the repro), and the caller's dict is changed in place
([J43](#j43)). `dict`, `dict | None` and `Optional[dict]` pass values through
unchanged. On v5, untyped parameters of third-party classes get the Namespace
too, so sklearn meta-estimators fail with `'Namespace' object has no attribute
'__sklearn_tags__'`, far from the cause.

**Impact on us:** a rule to use bare `dict` for payloads.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Ask:** treat `Any` values as data unless instantiation is on; on v5, warn
when a spec is passed to an untyped parameter.

#### <a id="j22"></a>J22 `dump()` drops explicit `null`s
🟡 **S3** (down-ranked: clean workaround) · small · debatable · hit in 2 of 6 · [`J22_dump_drops_null.py`](repros/J22_dump_drops_null.py)

**In short:** `x: Optional[int] = 3` given `null` is saved as `{}` and reloads
as 3, also inside `init_args`. `dump(skip_unset=False)` keeps the `null` and is
accepted on 4.x and v5 alike (v5 removed `skip_none`); LightningCLI's saved
config already uses it. With `unset_sentinel=True` ([J23](#j23)) a plain
`dump()` keeps the `null` too, since only `Unset` is then skipped.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j38"></a>J38 A function as `class_path` is judged by its return annotation only
🟡 **S3** · small · debatable · hit in 1 of 6 · [`J38_function_class_path_return.py`](repros/J38_function_class_path_return.py)

**In short:** for `b: Base`, a function annotated to return `Base` or a subclass
is accepted. One returning a TypeVar bound to `Base`, `Any`, or with no
annotation is rejected with "does not correspond to a subclass of Base", which
doesn't mention the return annotation.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j40"></a>J40 `null` is accepted for non-Optional fields with a default
🟡 **S3** · small (strict option) · intended · hit in 1 of 6 · [`J40_null_for_non_optional.py`](repros/J40_null_for_non_optional.py)

**In short:** for `a: int = 3`, YAML `a: null` is accepted (null means unset),
but `--a=null` is rejected.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j47"></a>J47 A failing `default_factory` breaks parser construction without context
🟡 **S3** · trivial (message) · intended / likely (message) · hit in 1 of 6 · [`J47_default_factory_postinit.py`](repros/J47_default_factory_postinit.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-default-factory-error-context` (draft PR in `prs/`; local only for now).

**In short:** for `runtime: Runtime = field(default_factory=Runtime)` where
`Runtime.__post_init__` raises, `add_class_arguments` raises the bare
`ValueError: output_dir is required`. So `--help`, and any flag that would
supply the value, fail too. Python's own `Job()` fails the same way; what's
missing is context.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Cause:** the factory is called in `_signatures.py` (and also in
`_parameter_resolvers.py`), with no context added to the error.

**Fix:** `ex.add_note("while building the default_factory of Job.runtime ...")`.

#### <a id="j32"></a>J32 `**kwargs` and untyped constructors need typed wrappers
🟡 **S3** · n/a · intended · hit in 3 of 6 · no repro

**In short:** classes whose constructors take `**kwargs` or have no type
annotations need a typed wrapper before they can be configured.

**Impact on us:** a typed `Pipeline` re-declaration, `Sequential` wrappers and a
`copy_signature` helper. A collision between a library's `**kwargs` expansion
and private constructors was reported but not reproduced; it may be a real
resolver bug.

#### <a id="j50"></a><a id="j51"></a><a id="j52"></a><a id="j53"></a><a id="j54"></a><a id="j58"></a>J50, J51, J52, J53, J54, J58 (S4)
- **[J50](#j50)** `exit_on_error=True` (the default) raises `SystemExit` inside
  library code, so callers pass `exit_on_error=False`. Intended. Not rerun.
- **[J51](#j51)** `instantiate` returns a Namespace for a dataclass added at the
  root (`add_class_arguments(DC)`), but builds `DC` when it has a nested key.
  One project wrote a helper.
  [`J51_instantiate_root_dataclass.py`](repros/J51_instantiate_root_dataclass.py),
  all versions.
- **[J52](#j52)** field docs in `--help` need the global
  `docstring_parse_attribute_docstrings`, which also triggers [J34](#j34).
  Intended.
- **[J53](#j53)** a top-level `_anchors:` key that only holds YAML anchors is
  rejected ("Option '_anchors.w' is not accepted"), so anchors have to be
  defined deep inside a section.
  [`J53_top_level_anchor_holder.py`](repros/J53_top_level_anchor_holder.py), all
  versions.
- **[J54](#j54)** a `list[str]` field given a file path is rejected without
  `sub_configs=True` and loaded with it: a clean workaround, not a missing
  feature. [`J54_list_field_from_file.py`](repros/J54_list_field_from_file.py).
- **[J58](#j58)** `--print_config` writes relative paths as given (relative to
  the working directory), while `--config` resolves them against the config
  file, so a printed config saved elsewhere doesn't reload.
  [`J58_print_config_relative_paths.py`](repros/J58_print_config_relative_paths.py),
  all versions.

[↑ Contents](#contents)

<a id="kind-missing-features"></a>

### Missing features

#### <a id="j10"></a>J10 Global parsing settings: enabling twice fails, no public getter, no per-parser scope
🟠 **S2** · small · likely-bug (idempotence) / debatable (scope) · hit in 6 of 6 · [`J10_global_settings_not_idempotent.py`](repros/J10_global_settings_not_idempotent.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-parsing-settings-idempotent`, for the repeated call only (draft PR in `prs/`; local only for now).

**In short:** three gaps in `set_parsing_settings`:

- calling `set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])` a
  second time fails with `ValueError: There is no function 'is_pure_dataclass'
  registered in subclasses_disabled`;
- there is no public getter, only the private
  `jsonargparse._common.get_parsing_setting`;
- a parser built before the mode is enabled keeps its group structure but
  follows the live global setting at parse time, so two parsers in one process
  can't use different modes.

Calling `register_type` twice with equal but new functions fails only on 4.51
(4.53 and v5 replace the old one).

**Impact on us:** save/restore helpers that import private names, copied into 3
projects; order-dependent CI failures (11 of 12 runs red once); one release
broke every run of one config family with exit 2.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌. The private names we import still exist on v5.

**Workaround:** check the setting before enabling it again (through the private
getter). This is workable.

**Cause:** `subclass_type_behavior` in `_common.py` removes the selector from
the disabled list and raises when it is already gone.

**Fix:** make enabling an already-enabled selector a no-op (about 3 lines).

**Ask:** export `get_parsing_setting`; add a `parsing_settings(**kw)` context
manager that snapshots and restores the settings and selector tables.

#### <a id="j19"></a>J19 No placeholder interpolation before validation
🟠 **S2** · medium (or docs for `set_loader`) · debatable · hit in 5 of 6 · [`J19_placeholder_in_typed_field.py`](repros/J19_placeholder_in_typed_field.py)

**In short:** `${N}` in an `int`, `float` or `bool` field is rejected in the
default mode. `omegaconf` mode resolves placeholders only in config files;
`omegaconf+` also in CLI and `parse_object` values. Both need every variable
set, even for `--print_config`.

**Impact on us:** three hand-built strategies in one project; a parse, dump
without validation, fill, reparse loop in another; two placeholder syntaxes in a
third.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Workaround:** a custom `set_loader` that runs `os.path.expandvars` before
`yaml.safe_load` works for config files on 4.x and v5 (and for CLI values on
v5).

#### <a id="j20"></a>J20 No deferred instantiation
🟠 **S2** · medium · debatable · hit in 2 of 6 · no repro

**In short:** there is no way to validate a `class_path` spec now and build it
later. `lazy_instance` is discouraged in the docs and doesn't cover specs from
configs.

**Impact on us:** a ~700-line deferred-recipe layer (later removed); a private
re-parse step.

**Ask:** e.g. a `Spec[Tokenizer]` type that checks the spec and returns it
unbuilt.

#### <a id="j41"></a>J41 Dotted overrides can't reach list entries; links can't reach list or dict entries
🟡 **S3** · medium · debatable · hit in 1 of 6 · [`J41_dotted_override_list_index.py`](repros/J41_dotted_override_list_index.py)

**In short:** `--m.l.0.init_args.y=3` for `list[Base]` fails, while
`--m.d.k.init_args.y=3` for `dict[str, Base]` works. `link_arguments` to
`m.l.0.init_args.y` and to `m.d.k.init_args.y` both fail. Appending
(`--m.l+=...`) is the only way to edit a list.

**Impact on us:** stages were written as a mapping to make them addressable, and a
seed is set "in both stages".

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

#### <a id="j55"></a>J55 argcomplete crashes on subcommand options and misses `class_path` fields
⚪ **S4** · not checked (the project removed argcomplete).

[↑ Contents](#contents)

<a id="kind-regressions-and-pins"></a>

### Regressions and pins

#### <a id="j26"></a>J26 Tagged union with an instance default rejects another member
🟠 **S2** · small · likely-bug · hit in 1 of 6, possibly 2 · [`J26_tagged_union_instance_default.py`](repros/J26_tagged_union_instance_default.py)

> [!NOTE]
> **🔧 Fix branch**: `fix-tagged-union-instance-default` (draft PR in `prs/`), reworked after #1038: switching to another member now discards the old member's values, as #1038 does for `class_path`.

**In short:** an option typed as a union of dataclasses told apart by a
`type: Literal[...]` field, with a default instance of one member, rejects a
value for another member.

**Example:**

```python
@dataclass
class A:
    type: Literal["a"] = "a"

@dataclass
class B:
    type: Literal["b"] = "b"
    x: int = 0

p.add_argument("--u", type=A | B, default=A())
p.parse_args(['--u={"type": "b", "x": 3}'])
```

The value is rejected. It is accepted without `default=A()`, and with dotted
flags (`--u.type=b`).

**Impact on us:** one project had an earlier `<4.50` cap.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌. Broken since 4.50 (#921).

#### <a id="j59"></a>J59 With `unset_sentinel=True`, a `None` in a callable field is dumped as "Unable to serialize instance None"
🟠 **S2** · trivial · likely-bug · hit in 1 of 6 · [`J59_unset_sentinel_none_callable_dump.py`](repros/J59_unset_sentinel_none_callable_dump.py)

**In short:** with `set_parsing_settings(unset_sentinel=True)`, a field typed
`Callable[...] | None` or `SomeCallableProtocol | None` whose value is `None`
is dumped as the text `Unable to serialize instance None`. The dump then fails
to load back. Plain `int | None` fields are dumped as `null`, as expected.

**Example:**

```python
class Factory(Protocol):
    def __call__(self, *, d: int) -> Head: ...

@dataclass
class Config:
    f: Factory | None = None

p.add_class_arguments(Config, "x")
p.dump(p.parse_args([]))   # writes   f: Unable to serialize instance None
```

**Impact on us:** it blocks adopting `unset_sentinel=True` ([J23](#j23)): in
one project it broke 15 tests, through a head-defaults field typed
`HeadFactory | None = None`, whose saved configs no longer reloaded.

**Status:** 4.51 ✅ 4.52 ❌ 4.53 ❌ v5 ❌ (main 670f094 too), only with
`unset_sentinel=True`. With the default settings `None` is the unset value and
is never serialized.

**Cause:** when dumping a union, the Callable arm in `adapt_typehints`
(`_typehints.py`) serializes the value with `serialize_as_import_path`, which
since #966 (4.52) returns the text "Unable to serialize instance ..." instead of
raising. So the Callable arm accepts `None` and the `None` arm is never tried.
4.51 called `object_path_serializer`, which raised.

**Fix:** in that branch, reject `None` when serializing (two lines), so the
union falls through to `None`. Tested in a copy of main: the repro and all 15
tests pass.

[J01](#j01) and [J18](#j18), both from 4.52, are the regressions behind most of our version pins ([J03](#j03)).

[↑ Contents](#contents)

<a id="kind-lightningcli-interplay"></a>

### LightningCLI interplay

#### <a id="j07"></a>J07 LightningCLI 2.6.x calls APIs removed in v5
🔴 **S1** for v5 · small (in Lightning) · n/a (Lightning PR open) · hit in 4 of 6 · [`J07_lightningcli_removed_v5_apis.py`](repros/J07_lightningcli_removed_v5_apis.py)

**In short:** on v5, `LightningCLI(...)` fails with `AttributeError:
'LightningArgumentParser' object has no attribute 'add_instantiator'` (with
`load_from_checkpoint_support=False`, the missing attribute is
`instantiate_classes`). `--help` and `--print_config` exit before this, so they
work.

**Impact on us:** every LightningCLI entry point fails.

**Status:** 4.51 ✅ 4.53 ✅ v5 ❌ (Lightning 2.6.5).

**Workaround:** a monkeypatch shim that stores `add_instantiator` calls and
passes them as `instantiators=`, sets `instantiate_classes = instantiate`, and
maps `skip_none` to `skip_unset`. With it, 17 of 18 v5-only failures in one
project pass, and a small model's saved `config.yaml` and checkpoint hparams are
identical to 4.53.

**Cause:** `lightning/pytorch/cli.py` in Lightning 2.6.5 and 2.6.6 calls
`add_instantiator`, `instantiate_classes` and `skip_none=False`, all removed in
v5.

**Fix:** in Lightning. Lightning main uses `instantiate`/`skip_unset` since
#21906, but still calls the per-parser `add_instantiator` (with a TODO for v5)
and pins `jsonargparse <4.51.0` in `requirements/pytorch/extra.txt`. Draft PR
Lightning-AI/pytorch-lightning#22014 passes instantiators through
`instantiate(..., instantiators=...)`.

#### <a id="j42"></a>J42 Saved LightningCLI `config.yaml` doesn't load into `run=False`
🟡 **S3** · small (Lightning) · debatable · hit in 1 of 6 · [`J42_lightning_saved_config_reload.py`](repros/J42_lightning_saved_config_reload.py)

**In short:** the saved config is flattened for the subcommand and contains
`ckpt_path` and `weights_only`, so a `run=False` CLI rejects it ("Option
'ckpt_path' is not accepted"). `fit --config saved.yaml` works.

**Impact on us:** one project carries an override of a private Lightning method,
and scripts that pop keys.

**Status:** 4.51 ❌ 4.53 ❌; v5 blocked by [J07](#j07).

[↑ Contents](#contents)

<a id="kind-v5-migration"></a>

### v5 migration

#### <a id="j23"></a>J23 v5: a required `X | None` can't be given `null` unless `unset_sentinel=True`
🟠 **S2** · n/a (on our side) · intended · hit in 2 of 6 · [`J23_required_optional_null.py`](repros/J23_required_optional_null.py)

**In short:** on v5, a parameter typed `X | None` with no default is required.
With the default settings it then can't be given `null`: an explicit `None`
counts as "not given", so it fails with "the following arguments are required".
This is deliberate. `set_parsing_settings(unset_sentinel=True)` is the intended
way to have a required field where `None` is a real value.

**Example:**

```python
class Seq:
    def __init__(self, count: int | None, dim: int = 1): ...

p.add_class_arguments(Seq, "seq")
p.parse_object({"seq": {"count": None}})
```

v5 fails with "the following arguments are required: seq.count". The same
happens via `--seq.count=null`, YAML, `init_args`, nested dataclasses, and
`dict`/`list` values. 4.x accepts it, with a deprecation warning that such
parameters "will be required" (shown only with
`JSONARGPARSE_DEPRECATION_WARNINGS=all`). With `unset_sentinel=True`, `null`
gives `None` and leaving the field out fails as required.

**Impact on us:** fields where `None` is a meaningful choice that must be made
explicitly, e.g. a token count where `None` means "variable", or an
augmentation where `None` means "views produced by the workers". 7 and 14 v5
test failures in two projects; 15 recipe files write `null` for such a field.

**Status:** 4.51 ✅ 4.53 ✅ v5 ❌ (main 670f094 too) with default settings;
v5 ✅ with `unset_sentinel=True`.

**Why it's intended:** in #678 the maintainer explained that, since argparse
records a missing required argument as `None`, a required `Optional` argument
can't be given `None`. #909 then added `unset_sentinel` to separate "not given"
from `null`, and #969 made these parameters required, with a test asserting that
`--param=null` fails under the default settings. The "Unset values" section of
the docs describes the setting.

**Workaround, tested (2026-11-26):** `set_parsing_settings(unset_sentinel=True)`
when moving to v5. On upstream main 670f094 with the J01 fix, two projects'
suites ran with and without it: it fixed all 21 and 14 `null` failures and
broke nothing, once two small jsonargparse bugs it exposes were patched in
both runs: [J59](#j59) (a `None` in a callable field is dumped as text) and
[J13](#j13) (a `None` path becomes `'None'`). Without those patches it broke 18
tests in one project. Things to adjust when adopting it:

- don't turn it on under 4.x: there these parameters aren't required yet, so a
  missing one reaches the constructor as `Unset`;
- plain `add_argument` options without a default give `Unset` instead of
  `None` when not given (`Unset` is falsy, so `if not x` works but `is None`
  doesn't);
- `get_defaults()` shows `Unset` for required fields, and
  `dump(skip_unset=False)` writes `==UNSET==`, which doesn't reload. A plain
  `dump()` now keeps explicit `null`s ([J22](#j22)), so the `skip_unset=False`
  calls added for that can go.

For a field that has to be given explicitly but could do without `None`, naming
the choice (e.g. `int | Literal["variable"]`) also works on any setting.

**Ask:** a docs note only. The migration guide's "become required" entry and
the v4 deprecation message could say that such fields can't take `null` unless
`unset_sentinel=True` is set. Better as a comment in the v5 thread (#999) than
an issue. Note: [`issues/required-nullable-null.md`](issues/required-nullable-null.md).

#### <a id="j45"></a>J45 v5 migration of our own code, and guide gaps
🟡 **S3** · small · likely (docs) · hit in 5 of 6 · no repro

**In short:** what our own code has to change for v5:

- removed `parser.instantiate_classes` in 2 projects (one production CLI, one
  test, some scripts);
- `skip_none` in docstrings and comments;
- pytest filters on `jsonargparse._deprecated` in 2 projects ([J48](#j48));
- one stale `<5` pin comment blaming a call the project no longer makes;
- two `instantiate` overrides that must forward `**kwargs`;
- the `jsonargparse[signatures,yaml]` extra.

All private imports we use (`_common` selectors, `_optionals` docstring options,
`_parameter_resolvers`, `_namespace.expand_dict`) still resolve on 5.0.0rc2.

**Guide gaps:** listed in [v5 feedback](#v5-feedback) item 4.

#### <a id="j49"></a>J49 v5 dumps `init_args: {args: []}` for `nn.Module` subclasses
⚪ **S4** · trivial · likely-bug · [`J49_varargs_dump_nn_module.py`](repros/J49_varargs_dump_nn_module.py)

**In short:** an `nn.Module` subclass without its own `__init__` inherits
`__init__(*args, **kwargs)`. With v5's `*args` support (#986), every dump gains
`init_args: {args: []}`. It reloads fine, but adds noise to saved configs and
diffs.

**Status:** 4.51 ✅ 4.53 ✅ v5 ❌.

**Fix:** omit empty varargs from dumps.

[↑ Contents](#contents)

<a id="kind-warning-noise"></a>

### Warning noise

#### <a id="j48"></a>J48 No public warning category; the private filter path is gone in v5
⚪ **S4** · trivial · debatable · hit in 3 of 6 · [`J48_deprecation_warning_filter.py`](repros/J48_deprecation_warning_filter.py)

**In short:** Lightning's calls trigger `JsonargparseDeprecationWarning`s. On
4.x the first one shown is a generic "only one per type is shown" banner, so the
real message reads as a second warning. Projects filter by
`jsonargparse._deprecated.JsonargparseDeprecationWarning`; on v5 that module is
gone and pytest reports "Failed to import filter module". No version exports a
public warning class.

**Workaround:** until one is exported, use a message filter or
`JSONARGPARSE_DEPRECATION_WARNINGS=off`.

#### <a id="j56"></a>J56 `Union[Dataclass, dict]` with an empty-dict default is filled
⚪ **S4** · small · debatable · hit in 1 of 6 · [`J56_union_dataclass_dict_empty_default.py`](repros/J56_union_dataclass_dict_empty_default.py)

**In short:** a third-party config class has `quant: Union[QuantConfig, dict] =
field(default_factory=dict)`. jsonargparse takes the dataclass arm for the empty
default and fills it (`Namespace(bits=4, iters=1)`), so the library gets a
non-empty value it never asked for.

**Impact on us:** a third-party warning on every run in one project, which we
filter.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌.

**Fix:** better raised as an example in a general issue about unions of
dataclass and dict.

[↑ Contents](#contents)

---

<a id="resolved"></a>

# 🟢 Fixed upstream

Merged upstream. *Released* says whether a release has the fix yet.

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
🟠 **S2** · done (main, v4 branch; unreleased) · intended · hit in 3 of 6 · [`J21_class_path_switch_keeps_init_args.py`](repros/J21_class_path_switch_keeps_init_args.py)

> [!TIP]
> **🟢 Fixed upstream by the maintainer (merged 2026-11-25, not yet released)**:
> [#1038](https://github.com/mauvilsa/jsonargparse/pull/1038) (main, v5) makes a
> `class_path` change discard the earlier `init_args`, adds a
> `prior_init_args: keep | discard` key (`--opt:keep` / `--opt:discard` on the
> command line), and makes `keep` skip the old class's signature defaults.
> [#1037](https://github.com/mauvilsa/jsonargparse/pull/1037) (v4 branch, 4.54)
> adds the same options to v4 and deprecates keeping. Together they cover both
> fixes suggested below.
>
> **Verified on main (3b30c14, 2026-11-26)**: the repro gives `OptB` its own
> `weight_decay=0.01` and `RMSNormOpts` its own `eps=1e-6`. With layered config
> files, a `dict[str, Base]` entry switched from `OptA` to `OptB` gets `OptB`'s
> defaults; repeating the same class still layers; `prior_init_args: keep` keeps
> the given values for both the dict entry and the union-of-dataclasses field
> (rc2 rejects the key). [J26](#j26) still reproduces on main, so its branch is
> still needed.

**In short:** when `class_path` changes, only the `init_args` the new class
doesn't accept are dropped. Everything else carries over, including values that
were only the old class's *defaults*.

**Example:** two shapes, and the same happens inside `dict[str, Base]` overlays.

- Default `OptA` (`weight_decay` default 0.0), config `class_path: OptB`
  (default 0.01): `OptB` gets 0.0.
- A union field `LayerNormOpts | RMSNormOpts` with default instance
  `LayerNormOpts()` (eps 1e-5), config `class_path: RMSNormOpts` with no
  `init_args`: `RMSNormOpts` gets eps 1e-5 instead of its own 1e-6. This is not
  the #968 leak (fixed in 4.52); it is this documented carry-over, present on
  every released version.

**Impact on us:** an optimizer switched from Adam to AdamW trained with
`weight_decay=0`; it also shows up as a replace-only config edit language and as
required optimizer fields. With the fix, on v5 check whether any of our
overlays switch `class_path` and rely on values carrying over: those now need
`prior_init_args: keep`.

**Status:** 4.51 ❌ 4.53 ❌ v5 ❌ (5.0.0rc2); main ✅ (3b30c14, #1038).

**Cause (before #1038):** `discard_init_args_on_class_path_change` in
`_typehints.py`, and its Namespace twin. The behaviour was documented in
`DOCUMENTATION.rst` and pinned by tests.

**Fix (as suggested before #1038):** an opt-in "reset on class change"
(prototyped, about one line; breaks 14 tests if on by default); or reset only
values whose provenance is "default", keeping ones the user set.

#### <a id="j08"></a>🟢 J08 Nested `class_path` parse time grows exponentially with depth
🟠 **S2** · done on main (#1036, v5 only); backport medium · likely-bug · hit in 3 of 6 · [`J08_nested_class_path_depth.py`](repros/J08_nested_class_path_depth.py)

> [!TIP]
> **🟢 Fixed upstream by our #1036** (merged 2026-11-23 into main, after
> 5.0.0rc2; not yet released). There is no 4.x backport.

**In short:** parsing a chain of nested `Optional[Base]` specs gets about 2.5x
slower per level on 4.x: on 4.53, depth 4 takes 0.06 CPU s and depth 8 takes
2.6 s; on v5, depth 8 takes 0.02 s.

**Impact on us:** real configs took 35.3 and 17.3 CPU s on 4.53, against 3.8 s
each on v5, with identical output apart from [J49](#j49). Another project takes
17-22 s per parse on 4.51, and a third is about 3x faster on v5. One project
parked a ~180-line cache mixin that touches five private context variables.

**Status:** 4.51 ❌ 4.53 ❌ v5 ✅.

#### <a id="j28"></a>🟢 J28 Constructor errors reported as a union mismatch
🟡 **S3** · done (#1015, v5) · hit in 4 of 6 · [`J28_ctor_error_union_report.py`](repros/J28_ctor_error_union_report.py)

**In short:** a constructor's `ValueError` inside `Optional[Base]` arrives as
"Does not validate against any of the Union subtypes", with the real error as
`__cause__` (4.50 chains the wrong cause). v5 raises the constructor's own
exception.

**Impact on us:** two copies of a message-matching unwrapper, one imported by a
third project. On v5 the unwrappers become dead code, and a subclass that
overrides `instantiate` must forward v5's `instantiators=` keyword.

**Status:** 4.51 ❌ 4.53 ❌ v5 ✅. See also [J12](#j12), [J47](#j47).

#### <a id="j29"></a>🟢 J29 Quadratic list parsing
🟡 **S3** · done (#975, v5) · hit in 2 of 6 · [`J29_list_parse_quadratic.py`](repros/J29_list_parse_quadratic.py)

**In short:** `list[str]` via `--x=<json>` takes 3.2 s for 4k items and 51 s for
16k items on 4.51; 0.09 s and 0.38 s on v5.

**Impact on us:** a 74k-item list took about an hour; large lists were moved out
of typed fields.

**Status:** 4.51 ❌ 4.53 ❌ v5 ✅.

#### <a id="j03"></a>🟢 J03 Version pins keep 4 of 6 projects on 4.51.0, which has the #968 leak
🔴 **S1** (meta) · n/a (unblocked by [J01](#j01), [J18](#j18), [J07](#j07)) · hit in 6 of 6

**In short:** four projects lock 4.51.0 (one with an exact `==4.51.0` pin, the
others with `!=4.52.0`); two lock 4.53.0. The pin comments cite #959
([J18](#j18)) and Protocol `class_path` handling ([J01](#j01)). One project's own
configs pass on 4.52.0, so its exclusion is defensive. One floor is `>=4.50`,
which would allow 4.50's worse behaviour if the lock were regenerated.

**The #968 leak:** fixed in 4.52.0 ("each union subtype is now adapted against a
pristine copy of the value"). On 4.51, one project's smoke config came out with
`eps: 1.0e-05` in two places where its RMSNorm default is 1e-6; 4.52, 4.53 and
v5 are correct. A by-hand check of another project's production config on 4.51
(87 `class_path` nodes) found no leaked value, and its output is identical on
v5. There is no standalone repro: the trigger needs the real classes. The
instance-default carry-over that remains on every released version is
[J21](#j21).

**Upper bounds:** Lightning caps `jsonargparse<5` only in its
`pytorch-extra`/`pytorch-all` extras. 3 of 6 projects have no `<5` of their own,
so a fresh resolve after v5 ships would pick v5 and break LightningCLI
([J07](#j07)).

[↑ Contents](#contents)

---

<a id="not-an-issue"></a>

# Checked, not an issue (or not reproduced)

Claims from our notes that didn't hold up when re-checked.

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
  see [v5 feedback](#v5-feedback) item 6.

[↑ Contents](#contents)
