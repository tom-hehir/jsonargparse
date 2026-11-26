# A str value that names an existing file is replaced by the file's content when sub_configs=True

(Issue draft. A prototype fix exists on the local branch `fix-str-value-read-as-config`; nothing is opened.)

## Description

With `sub_configs=True`, a value for a parameter typed `str | SomeClass` (or for
`add_argument(type=str, sub_configs=True)`) that names an existing file is
replaced by the content of the file. `sub_configs=True` is the default of
`auto_cli` and what LightningCLI uses, so in practice any `str | SomeClass`
parameter is affected.

```python
import dataclasses, os, tempfile
from typing import Union
from jsonargparse import ArgumentParser

@dataclasses.dataclass
class D:
    x: int = 1

def f(plain: str = "", uni: Union[str, D] = ""): ...

os.chdir(tempfile.mkdtemp())
open("data.csv", "w").write("a,b\n1,2\n")

for sub_configs in (False, True):
    p = ArgumentParser(exit_on_error=False)
    p.add_function_arguments(f, "f", sub_configs=sub_configs)
    print(sub_configs, p.parse_args(["--f.plain=data.csv", "--f.uni=data.csv"]).f)

p = ArgumentParser(exit_on_error=False)
p.add_argument("--path", type=str, sub_configs=True)
print(p.parse_args(["--path=data.csv"]).path)
```

Actual (4.51.0, 4.53.0 and main, 5.0.0rc2; silent, no warning):

```
False Namespace(plain='data.csv', uni='data.csv')
True  Namespace(plain='data.csv', uni='a,b\n1,2\n')
a,b
1,2
```

Expected: the value stays `'data.csv'`. `plain: str` is not affected (the
signature path only enables sub-configs when a type of the union can hold one),
and neither is `os.PathLike | str`.

## Why I think this is unintended, and why I am asking

The documentation (Sub-config files) describes `sub_configs` as accepting "a path
to a config file that holds" a subclass spec, i.e. it is meant for the class
arms. Nothing says a `str` value should be replaced by file content, and the
result is surprising: a CSV path becomes its text.

Related history: #516/#518 ("Parsing incorrectly provides file content when type
is a union with a subclass, PathLike and string") treated the same symptom as a
bug and fixed it for unions containing `os.PathLike` (`is_pathlike` turns
`enable_path` off). The `str` case without `PathLike` was not covered, which
makes `os.PathLike | str` a workaround that every path parameter has to follow.
The question is whether you also consider the plain `str | SomeClass` case a bug.

## Cause

`ActionTypeHint.__init__` keeps `enable_path` unless the type contains
`os.PathLike` (`_typehints.py`, `self._enable_path = False if is_pathlike(typehint) else enable_path`),
and the signature code enables it for any type with a class arm
(`_signatures.py`). `ActionTypeHint._check_type` then calls
`parse_value_or_config` (`_util.py`), which reads any string that names a file
and replaces the value by the loaded content. For a text file the content loads
as a `str`, which the `str` arm accepts, so the content becomes the value. When
the content is not valid for the type (a binary file, a number) the value falls
back to the original string, but only after the file was read.

## Possible fix

In `_check_type`, when the type accepts a `str` and the loaded content is itself
just a string, a file with plain text is not a config: keep the original string,
the same way the existing `list_file` case does. Files holding a mapping or a
list are still loaded as sub-configs, so `str | SomeClass` can still be given a
config path. This is a 2-line change plus tests (prototype on the local branch
`fix-str-value-read-as-config`; the suite passes, and the new tests fail
without it).

Trade-offs the prototype leaves open, which are for you to decide:

- A `str | SomeClass` value naming a file whose content is a mapping is still
  read as the class config (the `str` arm does not win). Only a stricter rule
  (never read when `str` accepts the value) would change that, and it would
  break config paths for such unions.
- A file holding only a class name (`LogHook`) was a valid sub-config for a
  class type; with a `str` arm in the union it is now the path. A pure class
  type is unchanged (the prototype only applies to types with a `str` arm).
- Files that load as other scalars (`7`, `true`) for e.g. `int | str | SomeClass`
  are still replaced by the scalar. Treating any scalar content as "not a
  config" would be a wider rule.
- For `Any`, `dict`, etc. with `sub_configs=True` nothing changes.

## Performance note

The file is read even when it is not used. With an audit hook counting `open`
calls on a small file, an undecodable (binary) file named by a `str | D` value
is opened 3 times in `parse_args` (one in `_check_type`, two more from
`_check_value_key`) and once again in `dump`, then the value stays the path.
A text file is opened once in `parse_args` and not in `dump` (its content is
the value). The prototype does not change the read counts, since deciding
whether a file is a config requires reading it; it only fixes the value. For
very large files (I did not measure; a multi-GB HDF5 file made a dump hang in
practice) avoiding the reads would need a different rule, e.g. only read when
the extension is a known config one, which I did not prototype.

## Versions

jsonargparse 4.51.0 (checked), 4.53.0 (reported in my notes, not re-run here),
main at 3b30c14 (5.0.0rc2).
