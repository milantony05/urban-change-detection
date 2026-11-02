# Hard-negative weak-label experiment

The v2 Dynamic World export aligned exactly with the North Bengaluru 10 m grid. It contained 1,410 weak positive pixels, 935,212 weak negatives and 5,034,178 ignored pixels. SHA-256: `235366cc1ede1bcba14dcc0e384ad1ff4de296f93e9b0c4ee0285c9d2a2d3771`.

The v2 rules added 95,698 negatives absent from v1 but also dropped 269,160 stable negatives. `scripts/combine_weak_labels.py` checked that the positive masks were identical and combined both negative sets, yielding 1,204,372 weak negatives, 1,410 positives and 4,765,018 ignored pixels. This derived union remains a model-based training label, not a reference map.

With the same architecture, seed, five epochs and training settings, the union produced 410 block-separated chips (258 train, 75 validation, 77 weak check). The selected epoch 5 had validation weak-label precision 0.335, recall 0.943 and F1 0.494, with 263 positive weak pixels. The v1 run had validation weak-label F1 0.650, but its negatives and validation chips differed, so these scores are not a paired accuracy comparison.

The full-area diagnostic at threshold 0.5 flagged 1,277,461 of 5,841,346 valid pixels (21.87%), down from 1,640,069 (28.08%) with v1. This remains too broad to interpret as detected conversion. The threshold is uncalibrated, and no area conversion estimate is reported. Additional weak-label tuning is paused until a modest independent reference set can measure false positives and missed changes.

The independent reference should identify **both** the 2018 source class and the 2025 destination class at each sampled location, with an `unclear` option. Random and model-disagreement samples from geographically reserved blocks are needed; a general `change` checkbox is insufficient. Some cases may require contemporaneous higher-resolution imagery or a second reviewer. The Kochi transfer set remains untouched.
