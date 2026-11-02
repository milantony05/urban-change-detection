# Phase 3: candidate labels and independent reference

The first spectral baseline proposes locations for inspection. Its output classes are 0 invalid, 1 valid but not selected, 2 vegetation-to-built-up **candidate**. It is not a land-cover truth map or an accuracy result.

## Reference definition

A positive reference patch was visibly vegetated in the 2018 period and visibly dominated by built surfaces in the 2025 period at the 10 m support scale. Stable vegetation, stable built-up land, vegetation-to-bare soil, crops in a dry phase, water, cloud contamination and ambiguous mixed pixels must be recorded separately. Use contemporaneous high-resolution evidence where licensing and access permit, or mark uncertain instead of guessing. Two independent reviewers should inspect a subset and reconcile disagreements.

## Sampling and splits

1. Divide the North Bengaluru raster into spatial blocks, for example 1 km squares on the EPSG:32643 grid. Assign entire blocks to train, validation or test before selecting image chips, and keep buffer space between split boundaries to reduce spatial leakage.
2. Sample candidates and non-candidates from across different blocks, including water edges, bare soil, cropland and stable built-up hard negatives. Include some randomly chosen blocks so evaluation does not measure only the spectral method's preferred examples.
3. For each reviewed patch, record location, split, 2018 class, 2025 class, transition, confidence, reviewer, source imagery and notes. Keep label provenance separate from model predictions.
4. The external city, now candidate Kochi, remains outside all training and threshold selection. Confirm suitable imagery and independent labels before locking it as the final external test.

## Baseline command

```bash
python -m urban_change.baseline --before data/raw/north_bengaluru_2018_dry_season_v3.tif --after data/raw/north_bengaluru_2025_dry_season_v3.tif --output outputs/north_bengaluru_spectral_candidates.tif
```

Current exploratory thresholds: NDVI in 2018 >= 0.35; NDVI in 2025 <= 0.20; NDBI in 2025 > 0; at least 2 clear observations per period. The initial run selected 296,187 of 5,841,346 valid pixels (5.07%). This percentage is **not** a measured conversion rate. Thresholds are provisional and must be chosen on the development/validation split only, then frozen before test evaluation.
