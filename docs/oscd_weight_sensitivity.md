# OSCD Siamese loss and sampling sensitivity

After the first OSCD test run was inspected, we compared two Siamese training settings using the same fixed city split, eight epochs, batch size 16, seed list and validation-F1 checkpoint rule. This is an **exploratory** analysis; the official test cities have now informed the experimental design, so these test comparisons cannot be presented as an untouched confirmatory result.

| Setting | Positive pixel BCE weight | Positive chip sampler weight |
| --- | ---: | ---: |
| Original | 5 | 3 |
| Conservative | 2 | 1 |

| Setting | Seed | Selected epoch | Test precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 20261102 | 7 | 0.404 | 0.556 | 0.468 |
| Original | 20261103 | 8 | 0.262 | 0.672 | 0.377 |
| Original | 20261104 | 4 | 0.327 | 0.480 | 0.389 |
| Conservative | 20261102 | 6 | 0.457 | 0.360 | 0.403 |
| Conservative | 20261103 | 5 | 0.422 | 0.545 | 0.476 |
| Conservative | 20261104 | 7 | 0.454 | 0.436 | 0.445 |

The original setting has mean precision 0.331 ± 0.071, recall 0.570 ± 0.097 and F1 0.412 ± 0.049 across the three seeds (sample standard deviations). The conservative setting has mean precision 0.444 ± 0.019, recall 0.447 ± 0.093 and F1 0.441 ± 0.036. Reducing change emphasis improved precision on every paired seed but reduced recall on every paired seed. The F1 direction differed by seed: conservative minus original was −0.065, +0.098 and +0.055. Three runs do not establish a reliable F1 advantage. The conservative setting may suit lower false-alarm use cases, while the original setting may suit higher recall; operational thresholds and city costs require separate study.

Reproduction uses `scripts.train_oscd` with `--seed`, `--positive-pixel-weight`, and `--positive-chip-weight`. Checkpoints, per-epoch histories and metrics remain in ignored `outputs/` directories. The comparison should be repeated with a **new external holdout** if the weights are chosen based on these test scores and a confirmatory claim is desired.
