# Data and evaluation protocol (Phase 1)

## Intended inputs

- [Copernicus Sentinel-2 Level-2A](https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-2): atmospherically corrected surface reflectance. Record product IDs, acquisition dates, bands, processing baseline and cloud masks.
- [Dynamic World](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1): class probabilities for **candidate** training labels and sampling. It is model output, not independent ground truth.
- [ESA WorldCover](https://esa-worldcover.org/en/data-access): contextual land-cover reference only. Its 2020 and 2021 versions use different algorithms; their difference is not a change label.

## Image construction

1. Inspect candidate dry-season windows for both dates and all cities. Record selected windows, cloud coverage, and scene identifiers.
2. Apply cloud, shadow and invalid-pixel masks before composing each period. Use a consistent coordinate system, pixel grid and spatial extent; preserve native band resolution metadata when resampling 20 m bands to a 10 m grid.
3. Keep nodata masks. Do not fill obscured pixels with labels or silently count them as no change.
4. Record acquisition window and source metadata in a manifest. Never compare scenes with an unexplained seasonal mismatch.

## Label policy

Target transition: a pixel or spatially coherent patch that was vegetated at t1 and built-up at t2. Define vegetation and built-up using a written annotation guide before scoring. Separate stable vegetation, stable built-up, other transitions, uncertain, and invalid pixels. Dynamic World may suggest locations for review; a human-checked reference set must be independent of its predicted labels. Sample changed and unchanged patches across different neighborhoods to avoid optimistic accuracy.

## Split and evaluation policy

- Group neighboring chips into spatial blocks. Keep whole blocks together in training, validation or test; never randomly split overlapping chips.
- Keep the external city completely outside training, model selection and threshold tuning. If the city is consulted during development, choose a different untouched city for the final external test.
- Record the split manifest and random seed. Evaluate transition precision, recall, F1, IoU and area estimation error; report the count of actual transition pixels and uncertainty/invalid coverage.
- Compare NDVI/NDBI thresholds, land-cover-map differencing and the two-date U-Net on **the same** independently checked test data. Report both within-city and external-city results.
- No individual-building, parcel-level, precise conversion-date, causal or pan-India claims from a 10 m two-period experiment.

## Phase 2 entry checklist

Confirm study windows and extent after imagery inspection, choose an external city, select acquisition/export method, and capture scene provenance. The candidate coordinates in the config are illustrative, not finalized research boundaries.
