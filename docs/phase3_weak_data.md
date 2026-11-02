# Weak-label training data checkpoint

The supplied `north_bengaluru_weak_labels_v1.tif` has exactly the same 2950 × 2024 pixel EPSG:32643 grid and 10 m transform as both v3 Sentinel composites. It is a single UInt8 band with values 0 ignored (4,860,716 pixels), 1 stable-class weak negative (1,108,674), and 2 proposed vegetation-to-built-up weak positive (1,410). SHA-256: `a247b00eaae40cc2a88afcadc550d2bfbfcd7f88b73d3c560bbfd870f7019b2d`.

The positive pixels form 99 connected components across 63 distinct 1 km blocks. Only 662 of the 1,410 also meet the separate spectral candidate threshold, showing that the methods disagree substantially; neither one is ground truth.

`scripts/build_weak_chips.py` creates 64 × 64 pixel two-date input chips with a 12-band feature tensor and a weak label mask. Each chip stays inside one 1 km block. A seeded block hash assigns distinct blocks to train, validation and `test_weak`; 0 labels are excluded from any loss or score. The first run created 397 chips: 249 train (38 with positives), 74 validation (13 with positives), 74 `test_weak` (9 with positives). The latter split is a pipeline check against model-generated labels, **not** a publishable test result.

The positive class is sparse (1,410 pixels), so training will require positive-chip oversampling or class-weighted loss. Any resulting model needs independent source-and-destination class annotations for evaluation. The user's first card review supplies contextual feedback but is not yet that pixel-level reference.

```bash
python scripts/build_weak_chips.py --before data/raw/north_bengaluru_2018_dry_season_v3.tif --after data/raw/north_bengaluru_2025_dry_season_v3.tif --labels data/raw/north_bengaluru_weak_labels_v1.tif --out data/weak_chips
```
