# OSCD supervised benchmark: first complete run

**Task:** binary urban change (buildings, roads and related change), not vegetation-to-built-up transition. **Data:** 24 Sentinel-2 image pairs and human annotated TIFF masks. The 14 original training cities were split by sorted name into ten fitting cities and four validation cities (`abudhabi`, `bercy`, `mumbai`, `rennes`); all ten official test cities were held out. Non-overlapping 64 × 64 chips exclude incomplete image edges. Six bands were used in order B02, B03, B04, B08, B11, B12, scaled by 10,000. We received the imagery as ten valid city-complete ZIP archives; the Train and Test Label ZIPs matched their published SHA-256 checksums.

Both PyTorch models used eight epochs, batch size 16, Adam 0.001, positive-pixel weight 5, positive-containing chip sampler weight 3, and seed 20261102. The best checkpoint for each architecture was selected by **validation F1**, then scored once on the official ten test cities at a fixed 0.5 threshold. These are exploratory comparisons: the Siamese experiment was run after seeing the first U-Net's test score, so a fresh benchmark would be needed for a strictly untouched model-selection claim.

| Architecture | Selected epoch | Test TP | FP | FN | TN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Six-band RMS change vector | Threshold 0.0788 | 60,987 | 134,434 | 85,038 | 2,435,189 | 0.312 | 0.418 | 0.357 |
| Two-date U-Net | 5 | 44,492 | 24,592 | 101,533 | 2,545,031 | 0.644 | 0.305 | 0.414 |
| Shared-encoder Siamese U-Net | 7 | 81,204 | 119,657 | 64,821 | 2,449,966 | 0.404 | 0.556 | 0.468 |

The baseline uses the root-mean-square spectral difference across all six bands, with a threshold selected from 60 values in [0.01, 0.30] by validation F1 alone. Its validation F1 was 0.172. Both networks outperform it in pooled test F1. The Siamese network detects more of the annotated changes than the early-fusion network but produces many more false positives. Pooled F1 alone hides large geographic variation:

| Official test city | U-Net F1 | Siamese F1 |
| --- | ---: | ---: |
| Brasilia | 0.242 | 0.528 |
| Chongqing | 0.216 | 0.540 |
| Dubai | 0.301 | 0.370 |
| Las Vegas | 0.630 | 0.721 |
| Milano | 0.231 | 0.429 |
| Montpellier | 0.635 | 0.736 |
| Norcia | 0.283 | 0.133 |
| Rio | 0.356 | 0.483 |
| Saclay West | 0.173 | 0.206 |
| Valencia | 0.045 | 0.019 |

Pixel counts are micro-aggregated over the included 64-pixel chips, not averaged over cities. Both models perform poorly in Valencia and the Siamese model also overflags Norcia. No external literature benchmark comparison is claimed here: preprocessing, band selection, split, cropping and metric definitions may differ. The project now has a working supervised deep learning benchmark, but a journal paper still needs a stronger experimental question, baseline, repeated seeds or uncertainty analysis, and careful city-specific error investigation.

Reproduce from the extracted official folders:

```bash
python -m scripts.prepare_oscd --root data/oscd --out data/oscd_chips
python -m scripts.train_oscd --chips data/oscd_chips --out outputs/oscd_model --epochs 8 --batch-size 16
python -m scripts.train_oscd --chips data/oscd_chips --out outputs/oscd_siamese --architecture siamese --epochs 8 --batch-size 16
python -m scripts.oscd_baseline --chips data/oscd_chips
```
