# Independent Bengaluru challenge and Kochi transfer diagnostic

## Input provenance

The first independent reference CSV contains 48 reviewed, prediction-stratified locations in held-out Bengaluru blocks. SHA-256: `fb0c581d2869fffc4a31c4ed734b8110b50763aa9bec0679f16a207d0e0ad3c5`.

The Kochi 2018 and 2025 Sentinel-2 exports both have 2422 × 2443 pixels, six reflectance bands plus `valid_count`, matching EPSG:32643 10 m grids, and 99.25% valid-pixel coverage. Their GeoTIFF SHA-256 values are `44fdfb0b31f22056732542a2c199b10107f9aacd2bdc273f2c260a0470d94d91` (2018) and `8ee278b48cb3ac1c5260c883e7fb278f1893dd45bd18c1e331dcf78682a70a0c` (2025). The scene CSVs list 25 and 59 source scenes respectively; the 2018 manifest ends on February 26 and the 2025 manifest includes March 31. This seasonal and scene-count difference warrants caution.

## Bengaluru review result

Of 48 points, 27 had both date classes and medium or high confidence; 21 were excluded for low confidence or unclear classes. Only 3 of the 27 accepted points were labeled vegetation in 2018 and built-up in 2025.

| Fixed method | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| NDVI/NDBI spectral baseline | 2 | 11 | 1 | 13 | 0.154 | 0.667 | 0.250 |
| U-Net with union weak labels, threshold 0.5 | 2 | 10 | 1 | 14 | 0.167 | 0.667 | 0.267 |

The sample deliberately balances method-agreement strata, so these figures describe this small challenge set only. They do not estimate citywide precision or conversion prevalence. Three positives make recall highly unstable; one additional error would change it substantially. The labels were reviewed by one person from 10 m imagery, without a second review or independent higher-resolution date evidence. The model and threshold were fixed before the reference CSV was received.

## Kochi diagnostic with the frozen Bengaluru settings

No model training, threshold choice or label creation used Kochi. On 5,872,493 valid pixels, the model flagged 183,514 (3.12%) at threshold 0.5 and the spectral baseline flagged 72,285 (1.23%). The maps overlap on 23,931 pixels. Bengaluru's corresponding model flag fraction was 21.87%. These fractions are **candidate flags**, not measured change areas or accuracy. Different urban form, ecology, seasonal observations and domain shift could all influence them. An independently reviewed Kochi sample is needed to assess transfer.

The present evidence does not support a journal claim of accurate vegetation-to-built-up mapping or demonstrated cross-city generalization. It supports an honest methodology and a clear next experiment: enlarge the reference, seek second-reviewer adjudication, and evaluate both methods on the locked Kochi sample.
