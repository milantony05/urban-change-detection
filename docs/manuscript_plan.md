# Manuscript plan (results pending)

## Working title

**Evaluating Cross-City Transfer of Sentinel-2 Vegetation-to-Built-Up Change Detection with Weak Supervision and Independent Reference Data**

The title remains provisional. The result must demonstrate a defensible comparison and an independent Kochi test before any claim of transfer.

## Research questions

1. How do a fixed NDVI/NDBI baseline and a compact two-date U-Net compare on independently reviewed North Bengaluru locations?
2. How much does the model's performance change when applied without tuning to Kochi?
3. Which false positives arise from seasonal vegetation, bare soil, water and mixed 10 m pixels?

## Methods already implemented

- Season-matched Sentinel-2 L2A composites for North Bengaluru, 2018 and 2025, with valid-observation counts and scene manifests.
- Conservative Dynamic World weak labels, including a hard-negative union, for training only.
- Spatially separated 1 km block chip splits; compact two-date U-Net and spectral threshold baseline.
- A blind, stratified 48-location reference review in held-out Bengaluru blocks. Its classes are collected separately for each date.
- A fixed 0.5 model threshold for the first independent challenge comparison, chosen before seeing reviewed labels. Threshold changes after this review must use a distinct validation set, not the reviewed test sample.

## Required evidence before a journal submission

- Completed independent class-by-date reference with ambiguous pixels excluded or adjudicated by a second reviewer and date-appropriate evidence. Increase sample size substantially beyond the first 48 locations and publish the sampling design.
- Kochi composites on a common 10 m grid, imagery quality check, and a separately reviewed Kochi reference set. Do not use Kochi to select model architecture or threshold.
- Report per-class confusion, precision, recall, F1, uncertainty intervals and method differences on the same points. Stratified sampling means raw positive fraction is not an area conversion estimate; weighted estimates require known stratum inclusion probabilities.
- Compare with spectral and public-map baselines on the same reference data. Include failure maps and ablations for hard negatives and valid-pixel masking.
- Reproducible versions, checksums, scene IDs, source licenses, model checkpoint and hardware/runtime details.

## Current limitations

Weak-label F1 and the full-area model probabilities do not establish true change accuracy. The v1 and hard-negative models flagged 28.08% and 21.87% of valid pixels at 0.5, respectively, so neither should be published as a conversion map. The first review had a marker placement error and broad `change` semantics; it is contextual feedback, not an independent target-class reference. No Kochi imagery or evaluation has been supplied yet. Journal fit and quartile should be checked against current indexing after results exist.
