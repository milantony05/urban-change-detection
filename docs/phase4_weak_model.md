# Phase 4: first two-date U-Net checkpoint

The compact U-Net takes twelve channels: six Sentinel-2 reflectance bands from each date, scaled by 10,000. It predicts one logit per 10 m pixel. A masked binary cross-entropy loss ignores weak-label class 0, treats class 1 as negative and class 2 as positive. Positive-containing chips are oversampled only in training; loss gives positive pixels additional weight. The split uses non-overlapping 1 km blocks and each 64 × 64 chip stays within its block.

On 2 November 2026, five CPU epochs were run with seed 20261102 and batch size 8. The checkpoint selected by lowest validation weak loss was epoch 4. Against **Dynamic World-derived weak labels only**:

| Geographic split | Positive weak-label pixels | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Validation | 263 | 0.496 | 0.943 | 0.650 |
| Separate weak-label check | 291 | 0.627 | 1.000 | 0.771 |

These figures show that the code learns to reproduce weak labels in held-out local blocks. They do not measure true vegetation-to-built-up detection accuracy; Dynamic World supplied the weak labels from Sentinel-2 imagery, and the positive examples are rare. The test split here is named `test_weak` to prevent confusion with an independently annotated test. Kochi remains completely unused.

Reproduce after creating local chips:

```bash
pip install -r requirements-model.txt
python -m scripts.train_weak --chips data/weak_chips --out outputs/weak_model --epochs 5
```

The model checkpoint is an ignored local output. The next milestones are full-AOI inference, meaningful independent pixel labels, and transfer assessment on a locked Kochi dataset. Do not cite weak-label F1 as paper performance.

## Full-area diagnostic

`scripts/predict_raster.py` ran the selected checkpoint over the aligned North Bengaluru composites. It wrote a georeferenced exploratory probability raster and masked pixels with fewer than two clear observations in either period. At the conventional 0.5 threshold, it flagged 1,640,069 of 5,841,346 valid pixels (28.08%). Only 194,528 of 296,187 separate spectral candidates were in that set. This is far too broad for a credible vegetation-to-built-up map and demonstrates that the model extrapolates badly outside the sparse, easy weak-label classes. The probability values are **not calibrated**.

Do not convert these flagged pixels into an area estimate or paper figure implying observed conversion. The next training iteration needs diverse hard negatives such as bare soil, water and seasonal crop differences, plus a genuinely independent reference set. This diagnostic does not establish which method is more accurate.

The v2 weak-label export adds high-confidence negative examples: source pixels already built, water or bare in 2018, and destination pixels still vegetated, water or bare in 2025. Those classes logically exclude the target transition, subject to Dynamic World's errors. Crops remain ignored as a source because their dry-season spectral appearance is variable. We will retrain only after the v2 raster passes the same grid and label checks as v1. The positive rule is unchanged, making the comparison interpretable.
