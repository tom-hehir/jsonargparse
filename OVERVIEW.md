# Overview of the open items

What goes wrong in each open item, how much it affected the six projects, and
the workaround in use. Items are grouped by kind. Within each group, they are
ordered by importance to these projects: mainly whether results are silently
wrong, and how awkward the workaround is.

The [README](README.md) has the tables with line counts and links, and
[`inventory.md`](inventory.md) has the full entries.

Not included:

- J59, opened upstream as
  [#1044](https://github.com/mauvilsa/jsonargparse/pull/1044);
- J01's Protocol case, fixed upstream by
  [#1043](https://github.com/mauvilsa/jsonargparse/pull/1043);
- J07, which needs a change in Lightning (a PR is open there);
- the items fixed upstream;
- the minor items listed at the end.

**At a glance**

- **Silent wrong results:**
  - [J24](#j24-a-saved-config-loses-a-defaults-arguments): a saved config doesn't record a default's hyperparameters;
  - [J04](#j04--j44-a-whole-class-silently-loses-validation): validation turned off for a whole class;
  - [J06](#j06-a-later-config-drops-a-dict-fields-other-keys) and [J05](#j05-overriding-one-field-of-a-plain-class-default-loses-its-other-values): values dropped by overrides.
- **Most awkward workarounds:**
  - J06: a ~1,600-line config generator;
  - J16: classes redesigned to avoid attributes set in `__post_init__`;
  - J14: a path-typing convention in 28 files;
  - J15: +293 lines of marker ABCs.
- **Cheapest to fix:**
  - J31: a tested one-line fix, with no branch;
  - J10: about 3 lines.

## Bugs with a fix branch

### Higher priority

#### J24: a saved config loses a default's arguments

**S2** · 1 of 6 · [inventory](inventory.md#j24) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-class-default-dump) · [draft](prs/fix-protocol-class-default-dump.md)

- **What goes wrong:**
  - Take a field typed as a callable that returns a class, such as a callable
    Protocol, whose default is a class. When the default sits inside another
    default instance or in a union, it is saved as a bare import path, with no
    `init_args`.
  - So the saved config leaves out the hyperparameters. It reloads to the same
    values today, but if the default in the code changes later, an old config
    silently gives different values.
  - Values that are overridden are saved in full; only untouched defaults are
    affected.
- **Impact:** the saved config of every training run in one project.
- **Workaround:** save the code version with each config, and reload a config
  only with that version. That project already records the commit, branch and
  dirty state with each run.

#### J16 + J39: some dataclass defaults are rejected

**S2** · 2 of 6 · [J16](inventory.md#j16) · [J39](inventory.md#j39) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-instance-non-field-attributes) · [draft](prs/fix-default-instance-non-field-attributes.md)

- **What goes wrong:**
  - A dataclass instance used as a default is rejected if `__post_init__` sets
    an extra attribute. This happens when the field is `Optional`, a union or
    subclass-typed.
  - `slots=True` dataclasses crash for the same reason (J39).
- **Impact:**
  - One project redesigned a registry and turned derived values into
    properties. In that project, 9 of 223 dataclasses would break if used as
    defaults.
  - Another project carried a monkeypatch for the `slots=True` crash, since
    removed.
- **Workaround:** use properties instead of attributes set in `__post_init__`.
  It works, but it changes how the classes are written.

#### J14: a string that names a file is replaced by the file's contents

**S2** · 1 incident; the workaround is in 4 of 6 · [inventory](inventory.md#j14) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-str-value-read-as-config) · [issue draft](issues/str-value-read-as-config.md)

- **What goes wrong:**
  - With `sub_configs=True`, which LightningCLI sets, a `str` value that names
    an existing file silently becomes that file's text.
  - Large files are read several times.
- **Impact:** a predict run hung reading a multi-GB HDF5 file.
- **Workaround:**
  - Type every path field `os.PathLike | str`. 4 projects follow this
    convention, in 28 files.
  - It works, but every path field has to follow it.
- **Note:** drafted as an issue with a prototype fix, since the right fix is a
  design choice.

#### J04 + J44: a whole class silently loses validation

**S1** · 1 of 6 · [J04](inventory.md#j04) · [J44](inventory.md#j44) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-inherited-annotation-namespace) · [draft](prs/fix-inherited-annotation-namespace.md)

- **What goes wrong:**
  - With `from __future__ import annotations`, if a dataclass's second base
    comes from another module, jsonargparse can stop validating every field of
    the class. For example, `batch_size: "sixteen"` is accepted with no warning.
  - J44 is the same lookup going wrong the other way: a field can resolve to a
    different class with the same name.
- **Impact:**
  - The 5 stage config classes in one project, used by every pipeline run, are
    not validated, although that project's docs say they are.
  - A scan of 4 projects found no other affected classes.
  - J44 led to an import alias and a "don't reuse class names" rule.
- **Workaround:** put the other base first, or import the missing names in the
  subclass's module. Both are easy, but nothing shows that they are needed.

#### J15: a subclass's own arguments are rejected under `Model[int]`

**S2** · 2 of 6 · [inventory](inventory.md#j15) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args) · [draft](prs/fix-subscripted-generic-init-args.md)

- **What goes wrong:** if the type is `Model[int]`, a subclass given as
  `class_path` can't take its own parameters. With a plain `Model`, it can.
- **Impact:**
  - One project added per-type marker ABCs to avoid it: 15 files, +293 lines,
    plus a review rule.
  - Another project at first misread it as a nesting-depth problem.
- **Workaround:** type the field as plain `Model`, which drops the type
  parameter, or use marker ABCs.

#### J26: a tagged union with an instance default rejects another member

**S2** · 1 of 6, possibly 2 · broken since 4.50 · [inventory](inventory.md#j26) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default) · [draft](prs/fix-tagged-union-instance-default.md)

- **What goes wrong:** take a union `A | B` whose members are told apart by a
  `type: Literal[...]` field. With `default=A()`, a value for `B` is rejected.
- **Impact:** one project carried a `<4.50` version cap because of it.
- **Workaround:** give the value with dotted flags (`--u.type=b`), or drop the
  default.
- **Note:** with the fix, switching to another member drops the old member's
  values, matching #1038. The draft asks the maintainer to confirm this.

### Lower priority

#### J13: `os.PathLike` turns any value into a string

**S2** · 3 of 6 · [inventory](inventory.md#j13) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-pathlike-coercion) · [draft](prs/fix-pathlike-coercion.md)

- **What goes wrong:** `--p=7` gives `'7'`.
- **Impact:**
  - The harmful case was `null` becoming `'None'`: a run was staged into
    `./None`. #1044 fixes that case.
  - No impact seen from what remains.
- **Note:** the draft leaves open whether non-strings should be rejected, which
  would break numeric folder names like `path: 2024`.

#### J43: `parse_object` modifies its input

**S3** · 1 of 6 · [inventory](inventory.md#j43) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parse-object-mutates-input) · [draft](prs/fix-parse-object-mutates-input.md)

- **What goes wrong:** `class_path` dicts inside lists and dicts in the input
  are replaced by Namespaces.
- **Workaround:** build fresh dicts for every parse.

#### J09: lists and dicts of dataclass defaults are saved as text that doesn't reload

**S2** · 4 of 6 · [inventory](inventory.md#j09) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-dump-container-defaults) · [draft](prs/fix-dump-container-defaults.md)

- **What goes wrong:** a `list[Rule]` default is saved as "Unable to serialize
  instance Rule(...)", which can't be loaded back.
- **Workaround:** a `None` default plus a constant in the code. Then
  `--print_config` doesn't show the real default.
- **Note:** not urgent, but worth having fixed.

#### J27: one bad annotation turns off validation for the whole class

**S2** · 2 of 6 · [inventory](inventory.md#j27) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-unevaluable-annotation-fallback) · [draft](prs/fix-unevaluable-annotation-fallback.md)

- **What goes wrong:** with `from __future__ import annotations`, a field like
  `"Weights" | None` can't be evaluated. That silently disables validation for
  every field of the class.
- **Impact:**
  - One project removed `from __future__ import annotations` from its config
    modules.
  - Another project lost a parameter on an older version.
- **Workaround:** don't put quoted names inside `|`.

#### J12: error messages bury the cause

**S2** · 6 of 6 · [inventory](inventory.md#j12) · [issue draft](issues/error-message-wording.md), no code

- **What goes wrong:**
  - For a typo deep in a config, the real cause, such as
    `Option 'lrr' is not accepted`, is the last of 7 lines.
  - Real messages run to 2–17 KB.
- **Impact:** all 6 projects. One project's docs quote this kind of message as
  the symptom of an unrelated problem.
- **Workaround:** none. v5 improves some of the messages, but not the one for a
  deep typo.

#### J17: a Protocol with only `_private` members matches nothing

**S2** · 1 incident · [inventory](inventory.md#j17) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-protocol-private-members-message) · [draft](prs/fix-protocol-private-members-message.md)

- **What goes wrong:**
  - No class matches such a Protocol, and the message doesn't say why.
  - The fix branch only changes the message.
- **Impact:**
  - In one project, it made the only training config unusable.
  - An "ABCs, not Protocols" rule exists in 5 of 6 projects, which overstates
    the limit.

#### J10: calling `set_parsing_settings` twice raises

**S2** · 6 of 6 · [inventory](inventory.md#j10) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-parsing-settings-idempotent) · [draft](prs/fix-parsing-settings-idempotent.md)

- **What goes wrong:**
  - Enabling the same subclass mode a second time raises a `ValueError`.
  - There is also no public way to read the current settings, and two parsers
    in one process can't use different settings.
  - The fix branch covers the repeated call only.
- **Impact:**
  - Save/restore helpers that import private names, copied into 3 projects.
  - Order-dependent CI failures: 11 of 12 runs were red once.
  - One release broke every run of one config family.
- **Workaround:** check the setting before enabling it again, through the
  private getter. This is easy, so the fix is low importance despite its
  reach.

#### J47: a failing `default_factory` gives no context

**S3** · 1 of 6 · [inventory](inventory.md#j47) · [diff](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-default-factory-error-context) · [draft](prs/fix-default-factory-error-context.md)

- **What goes wrong:** the error doesn't say which class or field it came from.
  The fix only changes the message.

## Bugs without a fix branch

#### J37: a registered serializer is applied to other values in a union

**S3** · 1 of 6 · [inventory](inventory.md#j37)

- **What goes wrong:** with `x: InheritType | bool`, `--x=false` is saved as
  the sentinel. This is silent if hit.
- **Impact:** the projects avoid `register_type` because of it.
- **Note:** #1044 mentions it as a related problem.

#### J18: the stubs setting is read only once

**S2** · cited by version pins in 5 of 6 · [inventory](inventory.md#j18)

- **What goes wrong:**
  - `torch.log1p` is rejected for `Callable[[Tensor], Tensor]`, which is
    intended.
  - The bug: the setting that makes it work is ignored if it is set too late.
- **Workaround:** type the field `Callable[[Tensor], Any]`, which loses the
  type check. Setting the stubs setting early triggers J31.
- **Note:** support for torch C builtins was lost in 4.52. Restoring it cleanly
  would be useful, but the rejection was a deliberate change (#959, #963), so
  any fix needs to fit the maintainer's reasoning.

#### J31: a stubs setting gives sklearn `Ridge` zero parameters

**S3** · 3 of 6 · [inventory](inventory.md#j31)

- **What goes wrong:**
  - With `stubs_resolver_allow_py_files=True`, a recursion bug drops every
    parameter of `Ridge`.
  - Only a DEBUG log shows why.
- **Impact:**
  - One project removed the setting.
  - 2 tests failed in another project.
  - A third project had planned to use the setting.
- **Note:** a one-line fix is tested.

#### J02: Protocol matching needs identical annotations

**S2** · 2 of 6 · [inventory](inventory.md#j02)

- **What goes wrong:**
  - jaxtyping types are never equal to each other, so jaxtyped implementers
    never match a Protocol.
  - `nn.Module` matches only a Protocol returning `-> Any`.
- **Workaround:**
  - `-> Any` on the Protocol, plus a shared alias for jaxtyped arguments. This
    is verified end to end.
  - The cost: the output shape is only in docstrings.

## Intended or documented, but awkward

#### J06: a later config drops a dict field's other keys

**S1** · 3 of 6 · [inventory](inventory.md#j06)

- **What goes wrong:**
  - A second config that sets one key of a `dict` field drops every key it
    doesn't name.
  - A dotted flag keeps the other keys.
- **Impact:** the largest workaround in the tracker:
  - a ~1,600-line generator producing ~50 standalone configs;
  - a 40-way launcher switch;
  - workers crashing with `KeyError` after a successful parse.
- **Workaround:** restate every key in each overlay, or generate dotted flags.
- **Note:** better merging of configs would be very useful, but it is likely a
  fair amount of work, and it changes intended behaviour.

#### J05: overriding one field of a plain-class default loses its other values

**S1** · 1 of 6 · [inventory](inventory.md#j05)

- **What goes wrong:** with a default of `Sampler(fraction=0.2)`,
  `--sampler.seed=3` gives `fraction=0.0`.
- **Impact:**
  - A rule in one project's agent guidelines.
  - `None`-then-build defaults in 5 places, which hide the real default from
    `--help`.
- **Workaround:** use a dataclass or `lazy_instance`.

#### J11: subclass mode breaks section files and `--help`

**S2** · 3 of 6 · [inventory](inventory.md#j11)

- **What goes wrong:** with subclass mode on for dataclasses:
  - giving a section as a file fails;
  - nested options disappear from `--help`;
  - the saved config's shape changes.
- **Workaround:** pass whole-tree configs, and read
  `value.get("init_args", value)` at every level.

#### J25: a section file resets nullable sections

**S2** · 1 of 6 · [inventory](inventory.md#j25)

- **What goes wrong:** a second file given to a parent group resets the other
  fields of an `Optional` section, instead of keeping them.
- **Impact:** four sections were silently reset, including a data overlay's
  worker counts.
- **Workaround:** on v5, `__include__` merges correctly.

#### J30: `class_path` specs in `Any` fields are turned into Namespaces

**S3** · 3 of 6 · [inventory](inventory.md#j30)

- **What goes wrong:**
  - The spec is filled with every default, instead of being left as given.
  - On v5, this makes sklearn meta-estimators fail far from the cause.
- **Workaround:** a rule to use bare `dict` for these values.

## Missing features

#### J20: no way to validate a `class_path` now and build it later

**S2** · 2 of 6 · [inventory](inventory.md#j20)

- **Impact:**
  - A ~700-line deferred-build layer, later removed.
  - A private re-parse step.
- **Note:** nice to have, but not important here. It is an unusual pattern, so
  it was probably not considered.

## Left out

These are minor, have a clean workaround, or are covered elsewhere:

- [J22](inventory.md#j22), [J38](inventory.md#j38), [J40](inventory.md#j40),
  [J41](inventory.md#j41);
- [J19](inventory.md#j19), placeholder interpolation: the projects' own
  loader works fine;
- [J01](inventory.md#j01)'s `Callable[..., Class]` case: its fix is held back,
  since #959 restricted it on purpose;
- [J23](inventory.md#j23), which is intended, and raised on the v5 thread
  ([#999](https://github.com/mauvilsa/jsonargparse/issues/999));
- J33–J36, [J42](inventory.md#j42), [J45](inventory.md#j45),
  [J49](inventory.md#j49);
- the S4 items.

The [README](README.md#other-open-points) lists all of them.
