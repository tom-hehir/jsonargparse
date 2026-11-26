# Two error messages that point away from the cause

Kind: small issue, or a comment in the v5 feedback thread (#999); not a PR.
Inventory: J12. On main most of what we had noted is already better (`Source:`
lines, the value printed once, known subclasses listed), so only two cases are
left, both wording.

## 🐛 Bug report

### 1. "Problem with given class_path" for dataclasses given no `class_path`

With `subclasses_enabled=["is_pure_dataclass"]`, a typo inside nested
dataclasses is reported as a chain of `class_path` problems, although the
config never mentions a `class_path`:

```python
import json
from dataclasses import dataclass, field

from jsonargparse import ArgumentParser, set_parsing_settings

set_parsing_settings(subclasses_enabled=["is_pure_dataclass"])


@dataclass
class Optim:
    lr: float = 0.1


@dataclass
class Training:
    optim: Optim = field(default_factory=Optim)


@dataclass
class Experiment:
    training: Training = field(default_factory=Training)


parser = ArgumentParser(exit_on_error=False)
parser.add_class_arguments(Experiment, "exp")
parser.parse_args(["--exp", json.dumps({"training": {"optim": {"lrr": 0.01}}})])
```

```
ArgumentError: Parser key "exp":
Unable to load config '{"training": {"optim": {"lrr": 0.01}}}'
  - Parser key "exp.training":
    Problem with given class_path '__main__.Training':
      Parser key "optim":
        Problem with given class_path '__main__.Optim':
          Option 'lrr' is not accepted
```

In configs with deeper nesting, users read the `class_path` lines as the
problem. Suggestion: when the class came from the type (implicit
`class_path`), say e.g. `Problem with value for '__main__.Training'`, or omit
that line and keep the `Parser key` lines.

### 2. `add_subclass_arguments` with a dataclass while subclass mode is off

```python
from dataclasses import dataclass

from jsonargparse import ArgumentParser


@dataclass
class Data:
    path: str = "x"


ArgumentParser().add_subclass_arguments(Data, "data")
```

```
ValueError: Expected 'baseclass' to be a subclass type or a tuple of subclass types: (<class '__main__.Data'>,)
```

The message doesn't say why a dataclass isn't a subclass type, nor how to
enable it. Suggestion: mention `set_parsing_settings(subclasses_enabled=...)`,
as the message for a `class_path` given to such a type already does.

### Environment

- jsonargparse version: main (3b30c14); the same on 4.53.0
- Python version: 3.12
- How jsonargparse was installed: from source
- OS: macOS
