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
