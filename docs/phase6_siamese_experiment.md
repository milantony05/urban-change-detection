# Phase 6: Siamese U-Net experiment

Implemented a shared-encoder two-date Siamese U-Net with six Sentinel-2 bands and internally computed NDVI/NDBI for each date. Features from 2018, 2025 and their absolute differences are fused at three scales. It uses the same spatially separated Bengaluru chips and Dynamic World-derived weak labels as the earlier U-Net. No Kochi labels entered training or checkpoint selection. The checkpoint was selected by validation weak loss after five epochs. The main run used positive weight 10 (versus 40 in the earlier U-Net); a weight-1 diagnostic also failed to control full-map overprediction.

| Model at threshold 0.5 | Bengaluru flagged / valid | Kochi flagged / valid | Bengaluru accepted TP/FP/FN/TN | Kochi accepted TP/FP/FN/TN |
| --- | ---: | ---: | --- | --- |
| Fixed spectral rule | See phase 5 | 72,285 / 5,872,493 (1.23%) | 2/11/1/13 | 16/3/5/14 |
| Earlier weak-label U-Net | 21.87% | 183,514 / 5,872,493 (3.12%) | 2/10/1/14 | 13/5/8/12 |
| Siamese U-Net, weight 10 | 3,824,048 / 5,841,346 (65.46%) | 2,623,424 / 5,872,493 (44.67%) | 1/16/2/8 | 12/8/9/9 |

The selected reference sample has 27 accepted Bengaluru and 38 accepted Kochi points, respectively. Kochi Siamese precision 0.600, recall 0.571, F1 0.585; Bengaluru precision 0.059, recall 0.333, F1 0.100. These are descriptive values from prediction-stratified challenge samples, not operational or area-wide accuracy. Because the strata were selected using the earlier models, the Siamese comparison also inherits this evaluation limitation. The weight-1 diagnostic marked 3,981,061 of 5,841,346 valid Bengaluru pixels (68.15%), so reducing the loss weight alone did not resolve extrapolation.

The experiment establishes that a stronger architecture with spectral indices does not solve the sparse-weak-label problem in this setup. It is not a positive result and should not replace the spectral baseline in a claim of improved detection. Only 38 of 249 training chips have any weak positives. A diagnostic with uniform chip sampling (`--positive-chip-weight 1`, positive pixel weight 10) still reached only weak-label precision 0.039 and F1 0.075 at its best-loss epoch, so changing the sampler alone was insufficient. No full-city or independent-reference score is claimed for that diagnostic. Kochi has now been inspected for model development; any revised model needs a new untouched external evaluation set to support a transfer claim.

Reproduction from prepared chips:

```bash
python -m scripts.train_weak --chips data/weak_chips --out outputs/siamese_union --architecture siamese --epochs 5
python -m scripts.predict_raster --before data/raw/kochi_2018_dry_season.tif --after data/raw/kochi_2025_dry_season.tif --checkpoint outputs/siamese_union/best.pt --out outputs/kochi_siamese_probability.tif
python -m scripts.evaluate_reference --reference data/reference/kochi_reference_batch_01.csv --spectral outputs/kochi_spectral_candidates.tif --model outputs/kochi_siamese_probability.tif
```

The large imagery, chips, checkpoint and reference CSV are kept outside Git. The run used seed 20261102, 64 × 64 chips, batch size 8, Adam learning rate 0.001 and the existing one-kilometre block split.
