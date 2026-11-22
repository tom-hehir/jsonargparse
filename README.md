# jsonargparse issues we have run into

Problems found while using jsonargparse for training configs: nested dataclasses
with subclasses enabled (`set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])`),
`class_path` values several levels deep, and LightningCLI.

Each issue was checked on 2026-11-22 against jsonargparse **4.53.0** (the latest
v4 release) and **main** (5.0.0rc2, commit 2e925db). The fix branches on this
fork have no pull requests yet unless one is linked; draft descriptions are in
[`prs/`](prs/).

## Being fixed

| Issue | Broken since | Fix |
| ----- | ------------ | --- |
| Parsing nested subclass values scales exponentially with the depth of nesting | all versions | [mauvilsa/jsonargparse#1036](https://github.com/mauvilsa/jsonargparse/pull/1036) |
| A Protocol whose `__call__` returns a class rejects classes whose instances implement it | 4.52.0 | branch [`fix-factory-protocol-instances`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-factory-protocol-instances), [draft PR](prs/fix-factory-protocol-instances.md) |
| A subscripted generic annotation (`Codec[Spectrum]`) rejects a subclass's `init_args` | all versions tried | branch [`fix-subscripted-generic-init-args`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-subscripted-generic-init-args), [draft PR](prs/fix-subscripted-generic-init-args.md) |
| A union of dataclasses with an instance default rejects values for another member | 4.50.0 | branch [`fix-tagged-union-instance-default`](https://github.com/mauvilsa/jsonargparse/compare/main...tom-hehir:jsonargparse:fix-tagged-union-instance-default), [draft PR](prs/fix-tagged-union-instance-default.md) |

**Protocols with `__call__`.** Since 4.52 a Protocol whose `__call__` returns a
class is treated as a factory, so a `class_path` must be a subclass of the return
type, and a class whose instances implement the Protocol is rejected ("Expected
'...' to be a subclass of ..."). An unannotated return counts as a class too.
The fix accepts such classes. Classes whose `__call__` has no return annotation,
like `torch.nn.Module`, still don't match a Protocol with an annotated return,
since Protocol signatures must match exactly; annotating the Protocol's return as
`Any` works around it.

**Subscripted generics.** With `class Codec(Generic[M])` and a field typed
`Codec[Spectrum]`, a `class_path` naming a subclass with its own parameter fails
with "Option 'depth' is not accepted". A plain `Codec` annotation works.

**Unions with an instance default.** A field typed `A | B` with default `A()`,
where `A` and `B` have `type: Literal["a"]` and `type: Literal["b"]` fields,
rejects `{"type": "b", "x": 3}`. It works without the default, and with dotted
`--u.type=b`. Since 4.50 the default's `class_path` is kept while parsing, so
that a partial value updates the default's class (#921); every other member is
then checked against that class.

## Fixed upstream

| Issue | Fixed in |
| ----- | -------- |
| Parsing a list takes time quadratic in its length | 5.0 ([#975](https://github.com/mauvilsa/jsonargparse/pull/975)) |
| Changing `class_path` writes another union member's defaults into the value (e.g. `eps=1e-5` from `LayerNorm` ending up in an `RMSNorm`) | 4.52.0 ([#968](https://github.com/mauvilsa/jsonargparse/pull/968)) |
| An error raised in a constructor is reported as "Does not validate against any of the Union subtypes" | main ([#1015](https://github.com/mauvilsa/jsonargparse/pull/1015)) |
| `class_path` specs inside `object` / `Any` fields get instantiated | off by default in 5.0 ([#969](https://github.com/mauvilsa/jsonargparse/pull/969)); `instantiate_subclass_spec_in_any=False` on 4.x |

## Still open

Present on both 4.53.0 and main. None of these is being worked on here.

### Wrong values without an error

- **A path is read as a config.** With `sub_configs=True`, a string for a type
  that also accepts a class (`str | SomeDataclass`) is loaded when it names an
  existing file. A `.csv` path becomes the file's text, and that text is what
  gets dumped.
- **`register_type` serializers chosen by union member, not by value.** With
  `INHERIT | bool`, `False` is dumped as `INHERIT`; a `type_check` doesn't help.
- **`dump` drops explicit `null`s.** `--a=null` over a default of 3 dumps as
  `{}`, so reloading gives 3.
- **Path types.** For `os.PathLike | None`, a command-line `null` becomes the
  string `"None"`, and `os.PathLike` turns `7` into `"7"`.
- **Tuple keys.** `dict[tuple[str, str], float]` accepts any string as a key,
  and a dumped tuple-key default can't be reloaded.
- **Unevaluable annotations.** One annotation that can't be resolved leaves every
  field of that dataclass unvalidated.
- **`Unset` sentinel.** `==UNSET==` dumps but doesn't reload. On main an explicit
  `Unset` default can't be reloaded at all ("denied by the import path
  denylist"), which is new in 5.0.

### Valid configs rejected

- **Protocols.** A Protocol whose members are all `_`-prefixed matches nothing,
  and signatures must match annotations exactly (`x: float | int` doesn't
  implement `x: float`; a narrower return type is rejected).
- **Functions as `class_path`.** A function is judged only by its return
  annotation: a TypeVar return is rejected, and so is a broader return type than
  the field's.
- **Default instances.** A dataclass default that sets attributes in
  `__post_init__` is rejected in a union or with subclasses enabled ("Option
  '_x' is not accepted"), and `dict` or `functools.partial` defaults can't be
  dumped ("Unable to serialize instance").
- **Slotted dataclasses.** `slots=True` dataclass defaults fail with "vars()
  argument must have __dict__ attribute".

### Other

- **Docstring parsing.** If the docstring parser fails on a class (e.g. a base
  class like `bidict`), its constructor parameters are silently dropped.
- **Global settings.** Calling `set_parsing_settings(subclasses_enabled=[...])` a
  second time with the same value raises, and there's no public way to read the
  setting.
- **Stale `--config` in nested parsers.** With a parser subclass that adds
  `--config` in `__init__`, a class with a `config` parameter fails with
  "argument '--config' already exists".
- **`link_arguments`** can't target a dict or list entry.

## Intended behaviour, or not reproduced

- **C builtins such as `torch.log1p` rejected for `Callable[[Tensor], Tensor]`
  (since 4.52).** A function given by import path must have a return annotation,
  or a return type in a stub file, that matches the callable's (documented; added
  in #959, stub fallback in #963). torch's stubs are only found with
  `set_parsing_settings(stubs_resolver_allow_py_files=True)`, which fixes it, but
  only if set before the first parse: the stubs resolver is created once and
  later setting changes are ignored. That caching is a possible small upstream
  fix.

- Changing a `class_path` keeps the old class's `init_args` that the new class
  accepts. This is documented, but it can change results silently: an optimizer
  defaulting to `Adam`, switched to `AdamW`, keeps `weight_decay=0.0`.
- `null` means "unset", so it's accepted for non-Optional fields.
- A section file (`--trainer b.yaml`) replaces the section instead of merging
  into it; 5.0 adds `__include__` for composing configs.
- `**kwargs` and untyped parameters can't be checked.
- PEP 695 generic aliases: on main they work when the self-reference isn't
  quoted (`type D[T] = dict[str, T | D[T]]`). On 4.53 that form hits a recursion
  error.
- Not reproduced on 4.53 or main: a parameter with an unevaluable annotation
  being dropped (it's kept, unvalidated); a leading `Any` union member swallowing
  a sentinel; `field(init=False)` breaking defaults.
