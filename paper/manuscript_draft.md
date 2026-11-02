# A weakly supervised Sentinel-2 pipeline for vegetation-to-built-up change detection: Bengaluru development and Kochi transfer assessment

**Status:** Working manuscript, 2 November 2026. The Kochi reference analysis, expanded Bengaluru reference and second-reviewer adjudication are pending. Do not submit this draft as a completed validation study.

## Abstract

Monitoring vegetation-to-built-up conversion with freely available satellite imagery is important for urban environmental assessment, but seasonal appearance, mixed pixels and geographic transfer make the target transition difficult to verify. We developed a compact two-date U-Net using six Sentinel-2 surface-reflectance bands from season-matched 2018 and 2025 composites in North Bengaluru. Dynamic World class probabilities supplied conservative weak training labels; a spectral NDVI/NDBI rule served as a transparent baseline. Geographic blocks separated model development from a blind, class-by-date reference review. Among 48 reviewed Bengaluru locations, 27 satisfied the medium/high-confidence rule and three represented the target transition. On this limited, prediction-stratified challenge set, the spectral baseline and U-Net each detected two of three target locations and produced 11 and 10 false positives, respectively. The frozen model flagged 21.87% of valid Bengaluru pixels and 3.12% of valid pixels in Kochi. These candidate fractions cannot be interpreted as conversion rates or transfer accuracy without independent Kochi labels. The current findings emphasize the limits of model-generated supervision and motivate independent class-by-date validation before operational mapping.

**Keywords:** Sentinel-2; urban expansion; vegetation loss; change detection; weak supervision; geographic transfer; geospatial machine learning.

## 1. Introduction

Urban conversion of vegetated land affects landscape structure and local environmental conditions. Sentinel-2 provides repeatable, freely available multispectral observations at a nominal 10 m grid for key bands, making city-scale screening possible. Yet a spectral difference between dates is not automatically a land-cover transition: dry-season vegetation, exposed soil, clouds, water and mixed urban pixels can yield similar signals. Detecting the specific transition from vegetation to built-up therefore requires both a defined source class and a defined destination class.

Automated land-cover products such as Dynamic World provide convenient class probabilities, but a model trained and evaluated against those same derived labels can appear successful while reproducing their biases. We examine a practical low-compute workflow and explicitly separate weak-label development from independent human reference. North Bengaluru is the development case because its peri-urban landscape contains visible growth between 2018 and 2025. Kochi, a coastal city with different vegetation and water patterns, is reserved as an external transfer case.

The current research questions are: (i) whether a compact two-date U-Net improves on a fixed NDVI/NDBI rule on independently interpreted locations; (ii) how its fixed predictions behave on a city excluded from all training and threshold selection; and (iii) which non-target changes produce false positives. The current reference size supports an exploratory comparison, not an operational accuracy claim.

## 2. Materials and methods

### 2.1 Study areas and imagery

The North Bengaluru candidate area spans approximately 77.48–77.75° E and 13.04–13.22° N. The Kochi candidate area spans approximately 76.20–76.42° E and 9.88–10.10° N. Sentinel-2 Level-2A harmonized surface-reflectance images were filtered to January–March 2018 and January–March 2025. Cloud shadows, cloud classes, cirrus, snow and defective pixels were masked using the Scene Classification Layer. The median across clear observations provided six bands (B2, B3, B4, B8, B11 and B12), regridded to a common 10 m UTM zone 43N export grid. Each export includes a per-pixel count of valid observations. Pixels with fewer than two clear observations in either period were excluded from analysis.

North Bengaluru composites used 7 and 17 catalogued scenes; the Kochi composites used 25 and 59. The Kochi 2018 manifest ends in February while the 2025 manifest extends through March, a residual seasonal mismatch to consider in interpretation. All four raster pairs passed checks for alignment, band identity, spatial variation and valid observation counts. Exact checksums and scene manifest summaries appear in the repository's data records.

### 2.2 Candidate labels and baselines

Dynamic World probabilities suggested a weak positive where high-confidence vegetation (trees, grass or shrub) in 2018 was followed by high-confidence built-up in 2025. Stable classes and high-confidence non-vegetated source or non-built destination pixels supplied weak negatives. Other pixels were ignored. The union training raster contains 1,410 positive pixels, 1,204,372 negative pixels and 4,765,018 ignored pixels. These are training suggestions from a model-derived product, not independent truth. Crops were excluded from the positive vegetation rule because their dry-season appearance is unstable.

The spectral baseline marks a candidate where 2018 NDVI is at least 0.35, 2025 NDVI is at most 0.20, and 2025 NDBI is greater than zero. These values were set before reviewing the independent reference. Candidate maps from either method are hypotheses for inspection, not conversion-area measurements.

### 2.3 U-Net and spatial separation

The U-Net receives twelve channels: six reflectance bands for each date, divided by 10,000. Its small encoder-decoder uses two downsampling levels and a single-logit pixel head. A masked, positively weighted binary cross-entropy loss excludes unknown weak-label pixels. Inputs were divided into 64 × 64 chips wholly contained in 1 km geographic blocks. Block assignments separated training, validation and a weak-label diagnostic split. Positive-containing chips were oversampled within training only. Training used five epochs, batch size eight, Adam and a fixed random seed. The checkpoint was selected using validation weak loss. A probability threshold of 0.5 was fixed before the independent review.

### 2.4 Independent reference and analysis

A blind review page sampled 48 North Bengaluru locations from geographic blocks excluded from training. It balanced four prediction strata: flagged by both methods, by the U-Net only, by the spectral rule only, and by neither. A reviewer classified the outlined 10 m square independently in 2018 and 2025 as vegetation, built-up, water, bare soil, other or unclear, and recorded confidence. Only medium/high-confidence points with clear classes were scored. The target positive required vegetation in 2018 and built-up in 2025. The same fixed U-Net and spectral threshold were applied without modification to Kochi. A Kochi reference batch follows the same class-by-date protocol and is pending.

Because the points were selected by prediction stratum, the raw positive fraction and unweighted precision do not estimate a population-wide conversion rate or operational precision. With so few target positives, uncertainty intervals and second-reviewer adjudication are necessary before manuscript submission.

## 3. Preliminary results

The first Bengaluru review yielded 27 accepted points of 48, including only three target positives. The spectral baseline recorded TP=2, FP=11, FN=1 and TN=13 (precision 0.154, recall 0.667, F1 0.250). The U-Net recorded TP=2, FP=10, FN=1 and TN=14 (precision 0.167, recall 0.667, F1 0.267). The one-point false-positive difference is not evidence of a meaningful advantage. These are descriptive results for a small enriched challenge set.

Against weak labels, the first U-Net checkpoint reached validation F1 0.650, but its full-area probability map flagged 28.08% of valid Bengaluru pixels. Adding conservative weak negatives reduced the flagged fraction to 21.87%, still implausibly broad as a conversion map. On Kochi, the frozen model flagged 183,514 of 5,872,493 valid pixels (3.12%) and the spectral baseline flagged 72,285 (1.23%). These are differences in candidate output, not verified land-cover change or accuracy. Kochi's independent reference remains pending.

## 4. Discussion and limitations

The principal observation is that a favorable weak-label score did not translate into a credible full-area map. Sparse positive labels, incomplete hard negatives and differences between cities can cause broad extrapolation. The independent Bengaluru sample also shows that both methods flag many non-target locations. Kochi's water and coastal vegetation are likely to challenge transfer, but no performance conclusion is possible before its reference labels are reviewed.

The study is limited by 10 m mixed pixels, one reviewer, a small number of independently accepted target transitions, season-window differences, and a sample enriched by model predictions. The project does not identify individual buildings, legal encroachment, causal effects of development or an exact date of conversion. Future analysis must enlarge and independently adjudicate the reference set, evaluate Kochi without changing the frozen model, examine stratum-specific errors, and only then decide whether the evidence supports a journal contribution.

## Data and code availability

Code, configuration, preprocessing instructions and provenance records: [urban-change-detection](https://github.com/milantony05/urban-change-detection). Sentinel-2 source products are available through Copernicus/Google Earth Engine under their respective terms. Dynamic World supplies weak training probabilities. The large GeoTIFF exports and model checkpoints are retained separately; publication packaging and licenses must be confirmed before submission.

## References to complete

- Copernicus Sentinel-2 Level-2A product documentation.
- Brown et al., Dynamic World, *Scientific Data* 9, 251 (2022), DOI: 10.1038/s41597-022-01307-4.
- Daudt et al., Onera Satellite Change Detection benchmark and related method paper.
- Original U-Net architecture citation and recent urban change-detection comparison papers.

**Before submission:** replace this working reference list with complete verified citations and update all results after the expanded independent reference and Kochi transfer analysis.
