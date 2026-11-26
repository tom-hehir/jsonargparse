# J23: not an issue; a docs note for the v5 thread

Not to be filed as a bug. A required `X | None` parameter rejecting `null`
under the default settings is intended (see [J23](../inventory.md#j23)):

- in #678 the maintainer explained that, with argparse's convention, a required
  `Optional` argument can't be given `None`;
- #909 added `set_parsing_settings(unset_sentinel=True)` to separate "not given"
  from `null`;
- #969 made these parameters required in v5, with a test asserting that
  `--param=null` fails under the default settings.

## Suggested note, for the comment in #999

> The migration guide's entry "Untyped/optional signature parameters become
> required" could mention that, with the default settings, such a parameter
> can't then be given `null`, and point to `unset_sentinel=True` for fields
> where `None` is a real value. The v4 deprecation message could say the same.
> We have fields like that (`None` meaning "variable count"), and with
> `unset_sentinel=True` they work as intended on v5.

Before relying on `unset_sentinel=True`, [J59](../inventory.md#j59) needs
fixing: with the setting on, a `None` in a `Path`, `timedelta` or callable field
is dumped as text, so saved configs (including LightningCLI's `config.yaml`)
don't reload.
