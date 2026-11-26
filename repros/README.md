# Repro scripts for the jsonargparse inventory

One standalone script per issue in [`../inventory.md`](../inventory.md), named by
its stable ID. Each script:

- starts with a docstring: the issue, what it checks, and the expected outcome
  per version;
- prints the jsonargparse version, a few result rows, and a final
  `RESULT: REPRODUCED` (the problem was observed) or `RESULT: NOT REPRODUCED`;
- uses temporary directories only and imports nothing from our projects.

Most need only jsonargparse (with pyyaml). Extra requirements are named in each
docstring: `torch` (J02, J07, J18, J42, J49), `lightning` (J07, J42),
`jaxtyping` (J02), `scikit-learn` (J31). J33 needs Python 3.12+. Runs here used
Python 3.13.5, torch 2.15.0, lightning 2.6.5, scikit-learn 1.9.1.

## Running

```bash
python J04_mixin_base_unvalidated.py            # one script, current environment
./run_all.sh /path/to/venv-4.53/bin/python /path/to/venv-v5/bin/python
```

`run_all.sh` prints one `RESULT` line per script and interpreter. A full run on
three versions takes about two and a half minutes (J08 and J29 time parses
deliberately). Some scripts call themselves in a subprocess to get a clean
process-wide setting (J11, J12, J18, J23, J31).

## Results (2026-11-24)

✗ the problem was reproduced; ✓ it was not. "v5" is 5.0.0rc2 plus main at
29d6f00. Every outcome matches the expectation in the script's docstring and the
status in the inventory.

| Script | Issue | 4.51.0 | 4.53.0 | v5 |
|---|---|---|---|---|
| `J01_protocol_call_returns_class.py` | J01 | ✓ | ✗ | ✗ |
| `J02_protocol_exact_annotations.py` | J02 | ✗ (`nn.Linear` vs `-> Tensor` OK) | ✗ | ✗ |
| `J04_mixin_base_unvalidated.py` | J04 | ✗ | ✗ | ✗ |
| `J05_instance_default_partial_override.py` | J05 | ✗ | ✗ | ✗ |
| `J06_dict_overlay_key_set.py` | J06 | ✗ | ✗ | ✗ |
| `J07_lightningcli_removed_v5_apis.py` | J07 | ✓ | ✓ | ✗ |
| `J08_nested_class_path_depth.py` | J08 | ✗ | ✗ | ✓ |
| `J09_undumpable_container_defaults.py` | J09 | ✗ | ✗ | ✗ |
| `J10_global_settings_not_idempotent.py` | J10 | ✗ | ✗ | ✗ |
| `J11_subclass_mode_side_effects.py` | J11 | ✗ | ✗ | ✗ |
| `J12_error_messages_bury_cause.py` | J12 | ✗ | ✗ | ✗ (shorter in case 2) |
| `J13_pathlike_null_and_coercion.py` | J13 | ✗ | ✗ | ✗ |
| `J14_str_value_read_as_config_file.py` | J14 | ✗ | ✗ | ✗ |
| `J15_subscripted_generic_subclass.py` | J15 | ✗ | ✗ | ✗ |
| `J16_default_instance_nonfield_attrs.py` | J16 | ✗ | ✗ | ✗ |
| `J17_protocol_private_members.py` | J17 | ✗ | ✗ | ✗ |
| `J18_c_builtin_callable.py` | J18 | ✓ | ✗ (late setting ignored) | ✗ (late setting ignored) |
| `J19_placeholder_in_typed_field.py` | J19 | ✗ | ✗ | ✗ |
| `J21_class_path_switch_keeps_init_args.py` | J21 | ✗ | ✗ | ✗ |
| `J22_dump_drops_null.py` | J22 | ✗ | ✗ | ✗ |
| `J23_required_optional_null.py` | J23 | ✓ | ✓ | ✗ (OK with `unset_sentinel=True`) |
| `J24_protocol_class_default_dump.py` | J24 | ✗ | ✗ | ✗ |
| `J25_section_file_resets_section.py` | J25 | ✗ | ✗ | ✗ |
| `J26_tagged_union_instance_default.py` | J26 | ✗ | ✗ | ✗ |
| `J27_quoted_forward_ref_in_union.py` | J27 | ✗ | ✗ | ✗ |
| `J28_ctor_error_union_report.py` | J28 | ✗ | ✗ | ✓ |
| `J29_list_parse_quadratic.py` | J29 | ✗ | ✗ | ✓ |
| `J30_any_spec_namespace.py` | J30 | ✗ | ✗ | ✗ |
| `J31_stubs_py_files_sklearn_ridge.py` | J31 | ✗ | ✗ | ✗ |
| `J33_pep695_recursive_alias.py` | J33 | ✗ (tuples) | ✗ (nested rejected) | ✗ (nested rejected) |
| `J35_stale_config_nested_parser.py` | J35 | ✗ | ✗ | ✗ |
| `J36_tuple_keyed_dict.py` | J36 | ✗ | ✗ | ✗ |
| `J37_register_type_union_serializer.py` | J37 | ✗ | ✗ | ✗ (and `Unset` doesn't reload) |
| `J38_function_class_path_return.py` | J38 | ✗ | ✗ | ✗ |
| `J39_slotted_dataclass_default.py` | J39 | ✗ | ✗ | ✗ |
| `J40_null_for_non_optional.py` | J40 | ✗ | ✗ | ✗ |
| `J41_dotted_override_list_index.py` | J41 | ✗ | ✗ | ✗ |
| `J42_lightning_saved_config_reload.py` | J42 | ✗ | ✗ | – (blocked by J07) |
| `J43_parse_object_mutates_input.py` | J43 | ✗ | ✗ | ✗ |
| `J44_inherited_annotation_namespace.py` | J44 | ✗ | ✗ | ✗ |
| `J47_default_factory_postinit.py` | J47 | ✗ | ✗ | ✗ |
| `J48_deprecation_warning_filter.py` | J48 | ✓ (private path works) | ✓ (private path works) | ✗ |
| `J49_varargs_dump_nn_module.py` | J49 | ✓ | ✓ | ✗ |
| `J51_instantiate_root_dataclass.py` | J51 | ✗ | ✗ | ✗ |
| `J53_top_level_anchor_holder.py` | J53 | ✗ | ✗ | ✗ |
| `J54_list_field_from_file.py` | J54 | ✗ (works with `sub_configs=True`) | ✗ (same) | ✗ (same) |
| `J56_union_dataclass_dict_empty_default.py` | J56 | ✗ | ✗ | ✗ |
| `J58_print_config_relative_paths.py` | J58 | ✗ | ✗ | ✗ |
| `J59_unset_sentinel_none_callable_dump.py` | J59 | ✓ | ✗ | ✗ (also main 670f094; added 2026-11-26) |

No script for J03 (the #968 leak needs real model classes to trigger; no minimal
form was found), J20, J32, J45, J50, J52, J55, J57 (features, intended behaviour
or migration notes), or J34 (needs `bidict`; not rerun). J46 is not an issue.
