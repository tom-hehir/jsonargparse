# jsonargparse issues from heavy use

Problems found while using jsonargparse for training and pipeline configs:
nested dataclasses with subclass mode, `class_path` values several levels deep,
callable Protocols, generics and LightningCLI. The items are ordered by their
impact on these projects. The first table lists the ones planned to be sent
upstream, as issues or pull requests; the other tables are for reference.

Every issue ID links to a longer description in [`inventory.md`](inventory.md),
with a standalone script in [`repros/`](repros/). Each fix branch is cut from
`main` (3b30c14); its new tests fail without the fix, the full test suite passes
on Python 3.12 and 3.14, and ruff and mypy report nothing new.

**Severity** (estimated): **S1** silent wrong values or lost validation in normal
use, or blocks an upgrade · **S2** forces an awkward workaround, or is silent but
needs an unusual setup · **S3** real but contained, or has a clean workaround ·
**S4** cosmetic or rare.

**Lines** are added / removed against `main`: library code, tests, docs
(`DOCUMENTATION.rst`) and changelog.

## Planned, in order

| # | ID | What goes wrong | Sev | Planned as | Code | Tests | Docs | Changelog | Links |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [J01](inventory.md#j01) | A class whose instances implement a callable Protocol (or `Callable[..., Class]`) is rejected as its `class_path`, since 4.52 | S1 | PR; the `Callable` part as a question | +23 −4 | +49 | – | +7 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances) · [draft](prs/fix-factory-protocol-instances.md) |
| 2 | [J59](inventory.md#j59) | With `unset_sentinel=True`, a `None` in a `Path`, `timedelta` or `Callable` field (`X \| None`) is dumped as text, so saved configs, LightningCLI's included, don't reload | S2 | PR (no branch yet; one-line fix tested) | +2 | – | – | – | [repro](repros/J59_unset_sentinel_none_dumped_as_text.py) |
| 3 | [J16](inventory.md#j16) + [J39](inventory.md#j39) | A dataclass default with attributes that aren't `__init__` parameters (set in `__post_init__`, or `init=False`), or with `slots=True`, is rejected for union, `Optional` and subclass types | S2 | PR | +8 −1 | +45 | – | +8 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) · [draft](prs/fix-default-instance-non-field-attributes.md) |
| 4 | [J24](inventory.md#j24) | A class default of a Protocol field, inside a default instance or a union, is dumped as a bare import path without its `init_args` | S2 | PR | +3 −1 | +27 −1 | – | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) · [draft](prs/fix-protocol-class-default-dump.md) |
| 5 | [J15](inventory.md#j15) | A subscripted generic (`Model[int]`) rejects the `init_args` of a subclass given as `class_path` | S2 | PR | +3 −4 | +27 | – | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) · [draft](prs/fix-subscripted-generic-init-args.md) |
| 6 | [J13](inventory.md#j13) | `os.PathLike` turns any value into a string, so a command-line `null` becomes `"None"` (the `None` part is also fixed by J59's fix) | S2 | PR | +8 −1 | +8 | – | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) · [draft](prs/fix-pathlike-coercion.md) |
| 7 | [J14](inventory.md#j14) | With `sub_configs=True`, a `str` value that names an existing file is replaced by the file's contents, and large files are read several times | S2 | Issue, with a prototype fix | +2 | +32 | – | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) · [draft](issues/str-value-read-as-config.md) |
| 8 | [J04](inventory.md#j04) + [J44](inventory.md#j44) | A dataclass whose second base is in another module silently loses validation of every field; or an inherited field resolves to a different class of the same name | S1 | PR | +18 −7 | +40 −1 | – | +5 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) · [draft](prs/fix-inherited-annotation-namespace.md) |
| 9 | [J26](inventory.md#j26) | A union of tagged dataclasses with an instance default rejects values for another member, since 4.50 | S2 | PR, with a question | +5 −1 | +36 −1 | – | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) · [draft](prs/fix-tagged-union-instance-default.md) |

## Fixed locally, lower priority

Fix branches exist for these, but they are not planned to be sent for now.

| ID | What goes wrong | Sev | Code | Tests | Docs | Changelog | Links |
|---|---|---|---|---|---|---|---|
| [J27](inventory.md#j27) | One annotation that can't be evaluated leaves every field of the class unvalidated | S2 | +16 −1 | +27 | – | +4 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) · [draft](prs/fix-unevaluable-annotation-fallback.md) |
| [J09](inventory.md#j09) | Lists, tuples and dicts of dataclass defaults are dumped as "Unable to serialize instance" text that doesn't reload | S2 | +13 −1 | +65 | – | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) · [draft](prs/fix-dump-container-defaults.md) |
| [J43](inventory.md#j43) | `parse_object` replaces `class_path` dicts in the caller's lists and dicts with Namespaces | S3 | +5 −3 | +16 | – | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) · [draft](prs/fix-parse-object-mutates-input.md) |
| [J10](inventory.md#j10) | A second identical `set_parsing_settings(subclasses_enabled=[...])` call raises | S2 | +5 −2 | +9 | +4 −4 | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) · [draft](prs/fix-parsing-settings-idempotent.md) |
| [J12](inventory.md#j12) | Two error messages that point away from the cause | S2 | – | – | – | – | [issue draft](issues/error-message-wording.md) |
| [J17](inventory.md#j17) | A Protocol whose members all start with `_` matches nothing, with an unhelpful message | S2 | +8 −1 | +15 | – | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) · [draft](prs/fix-protocol-private-members-message.md) |
| [J47](inventory.md#j47) | A `default_factory` that raises gives no hint of which class or field | S3 | +4 −1 | +21 | – | +3 | [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) · [draft](prs/fix-default-factory-error-context.md) |

## Other open points

For context only: no fix work, and nothing planned. Several are intended or
documented behaviour that was awkward in these projects, not bugs.

| ID | What | Kind | Sev |
|---|---|---|---|
| [J05](inventory.md#j05) | Plain-class instance default: a partial override silently discards its values | bug | S1 |
| [J06](inventory.md#j06) | Dict fields in overlays: key set replaced, surviving keys merged; dotted form merges | intended but awkward | S1 |
| [J07](inventory.md#j07) | LightningCLI 2.6.x calls APIs removed in v5 | lightning interplay | S1 |
| [J02](inventory.md#j02) | Protocol matching needs identical annotations: jaxtyping never equal; Modules need `-> Any` | bug | S2 |
| [J11](inventory.md#j11) | Subclass mode: section files rejected, nested options hidden from `--help`, dump shape changes | intended but awkward | S2 |
| [J18](inventory.md#j18) | C builtins rejected for `Callable[[Tensor], Tensor]`; stubs setting read once | intended but awkward | S2 |
| [J19](inventory.md#j19) | No placeholder interpolation before validation | missing feature | S2 |
| [J20](inventory.md#j20) | No deferred instantiation (validate a `class_path` now, build later) | missing feature | S2 |
| [J23](inventory.md#j23) | v5: a required `X \| None` can't be given `null` unless `unset_sentinel=True` (intended; a docs note for the v5 thread) | v5 migration | S2 |
| [J25](inventory.md#j25) | A section file given to a parent group resets nullable sections | intended but awkward | S2 |
| [J22](inventory.md#j22) | `dump()` drops explicit `null`s; reload gives the default | intended but awkward | S3 |
| [J30](inventory.md#j30) | `class_path` specs in `Any` fields are converted to Namespaces and filled; input mutated | intended but awkward | S3 |
| [J31](inventory.md#j31) | `stubs_resolver_allow_py_files=True` gives sklearn `Ridge` zero parameters | bug | S3 |
| [J32](inventory.md#j32) | `**kwargs`/untyped constructors need hand-written typed wrappers | intended but awkward | S3 |
| [J33](inventory.md#j33) | Recursive PEP 695 alias with a quoted self-reference fails | bug | S3 |
| [J34](inventory.md#j34) | A docstring-parser failure silently drops constructor parameters | bug | S3 |
| [J35](inventory.md#j35) | Stale `--config` in nested parsers of a parser subclass | bug | S3 |
| [J36](inventory.md#j36) | Tuple-keyed dicts keep string keys; tuple-key default dump doesn't reload | bug | S3 |
| [J37](inventory.md#j37) | Sentinels: `register_type` serializer applied by union arm; `Unset` doesn't reload on v5 | bug | S3 |
| [J38](inventory.md#j38) | Function as `class_path` judged by return annotation only | intended but awkward | S3 |
| [J40](inventory.md#j40) | `null` accepted for non-Optional fields with a default (config only) | intended but awkward | S3 |
| [J41](inventory.md#j41) | Dotted overrides can't reach list entries; links can't reach list or dict entries | missing feature | S3 |
| [J42](inventory.md#j42) | Saved LightningCLI `config.yaml` doesn't load into `run=False` | lightning interplay | S3 |
| [J45](inventory.md#j45) | v5 migration of our own code, and migration-guide gaps | v5 migration | S3 |
| [J48](inventory.md#j48) | No public warning category; private filter path removed in v5 | warning noise | S4 |
| [J49](inventory.md#j49) | v5 dumps `init_args: {args: []}` for `nn.Module` subclasses | v5 migration | S4 |
| [J50](inventory.md#j50) | `exit_on_error=True` default raises `SystemExit` in library code | intended but awkward | S4 |
| [J51](inventory.md#j51) | `instantiate` doesn't build a dataclass added at the root | intended but awkward | S4 |
| [J52](inventory.md#j52) | Field docs in `--help` need a global setting | intended but awkward | S4 |
| [J53](inventory.md#j53) | A top-level `_anchors:` holder for YAML anchors is rejected | intended but awkward | S4 |
| [J54](inventory.md#j54) | A list field can't be loaded from a file path (without `sub_configs=True`) | missing feature | S4 |
| [J55](inventory.md#j55) | argcomplete crashes on subcommand options and misses `class_path` fields | missing feature | S4 |
| [J56](inventory.md#j56) | `Union[Dataclass, dict]` with an empty-dict default is filled with the dataclass defaults | warning noise | S4 |
| [J57](inventory.md#j57) | Bare-generic dataloader fields failed with `__args__` | bug | S4 |
| [J58](inventory.md#j58) | `--print_config` writes relative paths as given; `--config` resolves them against the file | intended but awkward | S4 |
| [J60](inventory.md#j60) | With `unset_sentinel=True`, `--help` shows required options as `default: Unset` | bug | S4 |

## Fixed upstream

| ID | Problem | Fixed in |
|---|---|---|
| [J21](inventory.md#j21) | Changing `class_path` kept the old class's `init_args`, so an optimizer switched from `Adam` to `AdamW` kept `weight_decay=0.0` (documented behaviour until then) | main ([#1038](https://github.com/mauvilsa/jsonargparse/pull/1038)): discarded by default, `prior_init_args: keep` to opt back in; v4 branch for 4.54 ([#1037](https://github.com/mauvilsa/jsonargparse/pull/1037)): the same option, with keeping deprecated |
| [J08](inventory.md#j08) | Parsing nested `class_path` values took time exponential in the nesting depth | main ([#1036](https://github.com/mauvilsa/jsonargparse/pull/1036)) |
| [J28](inventory.md#j28) | An error raised in a constructor was reported as "Does not validate against any of the Union subtypes" | 5.0 ([#1015](https://github.com/mauvilsa/jsonargparse/pull/1015)) |
| [J29](inventory.md#j29) | Parsing a list took time quadratic in its length | 5.0 ([#975](https://github.com/mauvilsa/jsonargparse/pull/975)) |
| [J03](inventory.md#j03) | Changing `class_path` wrote another union member's defaults into the value (e.g. `eps=1e-5` from `LayerNorm` in an `RMSNorm`) | 4.52.0 ([#968](https://github.com/mauvilsa/jsonargparse/pull/968)) |
| [J30](inventory.md#j30) (partly) | `class_path` specs inside `object` / `Any` fields were instantiated | 5.0, off by default ([#969](https://github.com/mauvilsa/jsonargparse/pull/969)); `instantiate_subclass_spec_in_any=False` on 4.x |

## Files

- [`inventory.md`](inventory.md): every issue in detail, including the design
  requests and the v5 feedback.
- [`FIX-STATUS.md`](FIX-STATUS.md): working notes on the fix branches: open
  decisions, questions for the maintainer, filing order.
- [`issues/`](issues/) and [`prs/`](prs/): draft issue and PR texts.
- [`repros/`](repros/): one standalone script per issue, with results per
  version.
