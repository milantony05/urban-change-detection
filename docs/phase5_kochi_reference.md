# Kochi external reference, batch 01

The frozen Bengaluru model and fixed spectral thresholds were compared with the Kochi class-by-date review returned on 2 November 2026. Source CSV SHA-256: `7028f64ef7b0845be0758f219cf4ec3674db6121c0ce13d6afd78e1c9c03d083`. The source CSV is retained outside Git. The page sampled 12 points in each hidden prediction stratum, one point per 1 km block. All 48 rows had answers; 38 had clear classes and medium or high confidence. Of these 38, 21 were labeled vegetation in 2018 and built-up in 2025. The other ten were excluded because of low confidence or an unclear class.

| Method | TP | FP | FN | TN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed spectral NDVI/NDBI rule | 16 | 3 | 5 | 14 | 0.842 | 0.762 | 0.800 |
| Frozen weak-label U-Net at 0.5 | 13 | 5 | 8 | 12 | 0.722 | 0.619 | 0.667 |

The high-confidence-only subset has 23 accepted points and 14 target positives. The spectral rule has TP=12, FP=1, FN=2, TN=8; the U-Net has TP=9, FP=1, FN=5. The direction is unchanged, but this subset is even smaller.

| Prediction stratum | Accepted | Reference target positives | Excluded |
| --- | ---: | ---: | ---: |
| Both flag | 10 | 8 | 2 |
| Model only | 8 | 5 | 4 |
| Spectral only | 9 | 8 | 3 |
| Neither flags | 11 | 0 | 1 |

The numbers describe a **prediction-stratified challenge sample**. Neither the target fraction (21/38) nor these unweighted precision values estimates real-world conversion prevalence or area-wide accuracy. The spectral rule outperformed the frozen model on this selected set; this does not prove a statistically reliable population difference. In Bengaluru, only three accepted positives were available and both methods found two. We cannot claim the network improves on a simpler rule or generalizes better.

The single reviewer worked from enlarged Sentinel-2 10 m pixels. Images can be ambiguous. R009 was labeled vegetation-to-bare-soil with a note describing quarry-like clearing; both methods flagged it. R022 was labeled built-up in both years but includes a note about stadium grass; the class definition needs independent adjudication. R044 was labeled stable built-up with an airport note. Seek a second blind review of these and a larger random or probability-sampled reference before a journal accuracy claim. Kochi 2018 imagery ends in February, whereas 2025 extends through March; seasonal mismatch is another possible source of apparent change.

Reproduce the fixed challenge-set comparison with:

```bash
python -m scripts.evaluate_reference \
  --reference data/reference/kochi_reference_batch_01.csv \
  --spectral outputs/kochi_spectral_candidates.tif \
  --model outputs/kochi_weak_probability.tif
```

The CSV and large raster outputs are intentionally outside Git. Any method revision informed by these Kochi labels requires a new untouched external set for an honest transfer evaluation.
