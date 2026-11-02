# Saved OSCD results

The two JSON files in `metrics/` contain the confusion counts from the validation-selected, first-seed OSCD checkpoints. The detailed per-city CSV and manuscript figures are tracked under `paper/`.

`outputs/` is a local runtime directory created by training and prediction scripts. It holds checkpoints, rasters and histories, and is ignored by Git because these are generated files. GitHub does not display ignored or empty directories, so the former `outputs/.gitkeep` placeholder was removed. Rerun the commands in the main README to recreate model checkpoints locally. The original imagery and chips in `data/` are also ignored.

The OSCD task is **general urban change**, not a verified vegetation-to-built-up transition. See [full results](../docs/oscd_results.md) and the [working paper](../paper/oscd_manuscript_draft.md) for the scope and limitations.
