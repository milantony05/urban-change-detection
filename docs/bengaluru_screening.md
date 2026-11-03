# Bengaluru urban-change screening

## Project question

Can a compact model trained on labeled OSCD city pairs highlight useful locations for human review in North Bengaluru between dry-season 2018 and 2025 Sentinel-2 composites? How often do sampled alerts show visible urban change, and what kinds of false alarms or misses occur?

The **main output** is a georeferenced Bengaluru candidate map and a small human review. OSCD supplies supervised training and a geographically separate *benchmark*, not measured Bengaluru accuracy. Kochi can remain an optional qualitative example. The target is visible urban change at roughly 10 m Sentinel-2 scale, such as substantial new built surfaces or road works. It is not specifically vegetation-to-built-up conversion or individual building detection.

## Prepare the map

Use the existing aligned seven-band composites (B02, B03, B04, B08, B11, B12, valid_count), and the frozen OSCD Siamese checkpoint. These are normally local files under `data/` and `outputs/`; they are not in Git.

```bash
python -m scripts.predict_raster \
  --before data/<bengaluru_2018_composite>.tif \
  --after data/<bengaluru_2025_composite>.tif \
  --checkpoint outputs/oscd_siamese/best.pt \
  --out outputs/bengaluru_oscd_probability.tif
```

Substitute your actual paths; inspect the saved checkpoint name in your local output directory. If a probability TIFF has already been generated from the frozen checkpoint on precisely these rasters, use it directly.

## Generate the 40-site review

```bash
python -m scripts.bengaluru_audit create \
  --before data/<bengaluru_2018_composite>.tif \
  --after data/<bengaluru_2025_composite>.tif \
  --probability outputs/bengaluru_oscd_probability.tif \
  --out outputs/bengaluru_audit
```

This samples one pixel from each of 20 distinct eligible 1 km blocks with model probability at least 0.5 and 20 distinct blocks below 0.5, using a fixed seed. The JPEG cards show 2018 and 2025 RGB crops and a yellow outline around the selected 10 m pixel. The CSV shown to reviewers omits the model group. Keep `sample_manifest.json` hidden until labels are complete. A second reviewer can make a copy of the blank CSV and label independently.

Open each `B###.jpg` and fill `review.csv` with exactly one of `urban_change`, `no_urban_change`, or `unclear` and a short reason. Inspect the highlighted pixel **and its surrounding context**. A new road, large built surface, or substantial urban earthwork may be change; seasonal vegetation, wet soil, shadows, clouds, and misalignment are not confirmed urban change. Mark cases that cannot be resolved from the images `unclear`. Dated independent imagery may help adjudicate a difficult site, but record its source and dates. Keep all cards, including ambiguous ones. Do not select impressive examples in place of the fixed sample.

```bash
python -m scripts.bengaluru_audit summarize \
  --manifest outputs/bengaluru_audit/sample_manifest.json \
  --review outputs/bengaluru_audit/review.csv
```

Report counts separately: confirmed changes, no visible changes, and unclear among the 20 sampled alerts; the same counts among 20 sampled low-score locations. Describe confirmed low-score changes as *observed misses in the reviewed sample*. Since sampling deliberately balances model groups and samples points rather than full masks, these counts are **not** Bengaluru pixel precision, recall, F1, area-wide prevalence, or a verified growth-area estimate. If the two reviewers disagree, show disagreement counts and adjudication decisions.

## Suggested report structure

1. Motivation: screen a large Bengaluru scene for locations worth inspecting.
2. Data and method: Sentinel-2 2018/2025 composites; OSCD labels and city-separated training; frozen Siamese inference.
3. Map: georeferenced candidate probabilities with dates, valid-data mask, and legend.
4. Local review: preselected 40 sites, label definitions, counts, examples of alerts and misses.
5. Limits: cloud and seasonal effects, OSCD-to-India domain shift, 10 m mixed pixels, small point sample.

The previously reported OSCD test F1 of 0.468 belongs in the benchmark section only. Enter Bengaluru review counts after the labels are actually completed. Prior OSCD test inspection makes subsequent model comparisons exploratory.
