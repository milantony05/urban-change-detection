# City-held-out Sentinel-2 urban change detection with compact paired convolutional networks: an OSCD benchmark

**Working draft, 2 November 2026.** The existing vegetation-to-built-up manuscript remains a separate exploratory study. This draft is not submission ready; the benchmark comparison remains exploratory and requires an independent confirmatory design and deeper error analysis.
The Siamese weight-sensitivity analysis now includes three seeds, but it was designed after viewing the initial test result and remains exploratory.

## Abstract

Generalization across cities is a central difficulty in detecting urban change from bi-temporal satellite imagery. We compared a compact early-fusion U-Net and a shared-encoder Siamese U-Net with a validation-tuned six-band change-vector baseline on the human annotated Onera Satellite Change Detection (OSCD) dataset. Six co-registered Sentinel-2 bands from each date were converted into 64 × 64 chips; ten original training cities were used for fitting, four for validation, and the ten official test cities for evaluation. Checkpoints and the baseline threshold were chosen on validation cities. On the ten test cities, the change-vector baseline reached F1 0.357, the early-fusion U-Net F1 0.414, and the Siamese model F1 0.468. The Siamese network reached recall 0.556 and precision 0.404; its F1 ranged from 0.019 in Valencia to 0.736 in Montpellier. The paired model improved pooled recall but added false positives, underscoring the need for city-specific evaluation. Repeated seeds and error analysis are required before a journal claim.

## 1. Problem and contribution under development

OSCD supplies manually annotated urban change (including buildings and roads) across 24 Sentinel-2 image pairs from multiple regions [1]. This paper asks whether a compact shared-encoder two-date model improves city-held-out change detection over an early-fusion U-Net, and how reliably either transfers across cities. The current result is a reproducible pilot comparison, not a novel architecture claim. Its contribution must be sharpened through a controlled cross-city analysis and a credible classical baseline.

## 2. Data and methods

The 14 original OSCD training cities were sorted by name. Every fourth city (`abudhabi`, `bercy`, `mumbai`, `rennes`) was assigned to validation before any image or label inspection for model selection. The other ten trained the models. All ten official OSCD test cities remained separate. We used B02, B03, B04, B08, B11 and B12 in each date, divided by 10,000, and a non-overlapping 64-pixel chip grid. Incomplete image-edge chips were omitted. The original TIFF masks encode no change as 1 and change as 2. Exact data preparation and city list are in the repository.

The early-fusion U-Net takes twelve bands jointly. The Siamese U-Net uses a shared encoder for the two dates, computes NDVI and NDBI internally, and fuses features from both dates and their absolute differences at three scales. Both were trained for eight epochs with Adam (learning rate 0.001), batch size 16, positive pixel loss weight 5 and positive-containing chip sampler weight 3. A fixed probability threshold of 0.5 was used. The selected checkpoint maximized validation F1. A simple comparator computed the root-mean-square band difference between dates and selected its threshold from 60 values spanning 0.01–0.30 by validation F1. Test confusion counts were micro-aggregated over included chips. Code and complete run commands are in `docs/oscd_results.md`.

## 3. Preliminary results

| Model | TP | FP | FN | TN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Change-vector baseline | 60,987 | 134,434 | 85,038 | 2,435,189 | 0.312 | 0.418 | 0.357 |
| Early-fusion U-Net | 44,492 | 24,592 | 101,533 | 2,545,031 | 0.644 | 0.305 | 0.414 |
| Shared-encoder Siamese U-Net | 81,204 | 119,657 | 64,821 | 2,449,966 | 0.404 | 0.556 | 0.468 |

The Siamese model gained 0.054 pooled F1 and 0.251 recall, while precision declined by 0.240. It outscored early fusion in eight of ten test cities, but both performed poorly in Valencia. The range and per-city scores are recorded in `docs/oscd_results.md`. These differences are descriptive; statistical uncertainty has not been assessed.

### Exploratory loss and sampling sensitivity

The first Siamese test motivated a second setting with positive pixel weight reduced from 5 to 2 and positive-chip sampler weight reduced from 3 to 1. Three seeds (20261102–20261104) were run for each setting. Original Siamese F1 values were 0.468, 0.377 and 0.389 (mean 0.412, sample SD 0.049); conservative F1 values were 0.403, 0.476 and 0.445 (mean 0.441, SD 0.036). Mean precision increased from 0.331 to 0.444, while mean recall decreased from 0.570 to 0.447. The F1 ordering reversed for one of three paired seeds. The observed precision-recall tradeoff is more consistent than the small mean F1 difference. Because both settings and additional runs were considered after the first test result, the test set cannot support a fresh confirmatory model-selection claim. Full settings and results are in `docs/oscd_weight_sensitivity.md`.

### City-level errors

![OSCD held-out city F1 by model and setting](figures/oscd_city_f1.svg)

**Figure 1.** Per-city F1 for a validation-tuned change-vector rule, an early-fusion U-Net (one seed), and each Siamese setting (mean of three seeds). The parenthesized percentage is the annotated change fraction in the evaluated chips. The diagram reports exploratory test-set analysis and does not establish an independently confirmed ranking.

The conservative Siamese setting averaged F1 0.732 in Montpellier and 0.699 in Las Vegas but only 0.016 in Valencia. Valencia has 0.37% annotated change in its evaluated chips, and the original Siamese model produced many false positives there. The result suggests that sparse changes can be a difficult operating regime; scene characteristics and label structure may also contribute, so prevalence alone should not be asserted as the cause. Chongqing shows the opposite tradeoff: the original setting averaged F1 0.556 and the conservative setting 0.349. These cases motivate separate analysis of false alarms, missed change, and shift in land-cover appearance across cities.

![Illustrative OSCD validation-city chip](figures/oscd_validation_example.svg)

**Figure 2.** Before and after Sentinel-2 RGB, human change mask, and predicted probabilities for a fixed Abu Dhabi validation-city chip. The chip was selected for visible change and is an illustration, not an estimate of accuracy or a test-set example.

## 4. Limitations and next experiments

Model families and weight settings were compared after an exploratory first test result had already been viewed. The test labels did not enter gradient updates, but this sequence limits claims about wholly untouched model selection. A final paper should predefine comparisons on a new external holdout and report repeated seeds, per-city precision/recall, uncertainty and error examples. The OSCD binary mask does not distinguish vegetation-to-built-up from other urban change, and direct prediction on Bengaluru or Kochi composites would be qualitative transfer rather than validated performance on the same label definition. OSCD imagery and our Google Earth Engine seasonal composites may differ in acquisition and processing. No claim about publication tier or superiority over published methods follows from this pilot.

## Reference

1. Daudt, R. C., Le Saux, B., Boulch, A., & Gousseau, Y. (2018). [Urban Change Detection for Multispectral Earth Observation Using Convolutional Neural Networks](https://doi.org/10.1109/IGARSS.2018.8518015). *IEEE International Geoscience and Remote Sensing Symposium*, 2115–2118. Official dataset: https://rcdaudt.github.io/oscd/.

## Code and data availability

Code, parameters, per-city metrics, and figures are available in the [project repository](https://github.com/milantony05/urban-change-detection). The original OSCD imagery and annotations are available from the dataset author's site [1]; large images, chips, and checkpoints are excluded from Git. See `docs/final_project_handoff.md` for exact commands. The uploaded source data and derived artifacts should be checked for redistribution terms before any journal submission.
