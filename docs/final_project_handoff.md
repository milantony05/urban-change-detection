# Final-year project handoff: Sentinel-2 urban change detection

**Project status:** the core deep learning project is complete as an exploratory benchmark. Two PyTorch architectures, one spectral baseline, human-labeled data preparation, a city-separated evaluation, three-seed sensitivity analysis, figures, and a working manuscript are available. A journal submission needs further confirmatory research; it is not complete merely because this project is demonstrable.

## Formal problem statement

Develop and evaluate compact paired-image neural networks for binary urban change detection in multispectral Sentinel-2 imagery, with particular attention to performance variation across unseen cities and sparse-change settings. Compare an early-fusion U-Net and a shared-encoder Siamese U-Net against a validation-tuned spectral change-vector rule using OSCD's human-annotated masks. The predicted class is **urban change**, including roads or buildings; it does not specify a vegetation-to-built-up transition.

## What is implemented

- `scripts/prepare_oscd.py`: selects six bands from the 24 OSCD image pairs, reads exact TIFF masks, creates 64 × 64 chips, and splits by city (10 training, four validation, ten official test).
- `urban_change/model.py` and `scripts/train_oscd.py`: early-fusion and Siamese U-Nets, validation checkpoint selection, saved training histories and test confusion counts.
- `scripts/oscd_baseline.py`: six-band change-vector rule with threshold selected only on validation cities.
- `scripts/report_oscd_city.py`, `scripts/plot_oscd_city.py`, `scripts/make_oscd_demo.py`: city metrics, comparison figure, and an illustrative validation-city image.
- `paper/oscd_manuscript_draft.md`: working journal-style writeup. `docs/oscd_results.md` and `docs/oscd_weight_sensitivity.md` contain exact evidence and caveats.

## Headline results

| Method | Test precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Spectral change vector | 0.312 | 0.418 | 0.357 |
| Early-fusion U-Net, one seed | 0.644 | 0.305 | 0.414 |
| Siamese U-Net, first seed | 0.404 | 0.556 | 0.468 |

For the Siamese model, three original-setting seeds averaged F1 0.412 ± 0.049; three conservative-setting seeds averaged F1 0.441 ± 0.036 (sample SD). The conservative setting consistently increased precision while reducing recall. The F1 direction changed across seeds. City-level performance ranges widely; Valencia is a severe failure case. Test observations influenced later experiment design, so these results are exploratory rather than a final unbiased model-selection claim.

## Reproduce locally

1. Install Python dependencies: `pip install -r requirements-research.txt`.
2. Download and extract OSCD's Images, Train Labels and Test Labels ZIPs into `data/oscd/`, retaining the three official top-level folder names. See `docs/oscd_benchmark.md`. The uploaded imagery arrived as ten smaller city-complete ZIPs; extracting all ten to the same directory recreates the Images folder.
3. Run `python -m scripts.prepare_oscd --root data/oscd --out data/oscd_chips`.
4. Run the baseline: `python -m scripts.oscd_baseline --chips data/oscd_chips`.
5. Run early fusion: `python -m scripts.train_oscd --chips data/oscd_chips --out outputs/oscd_model --epochs 8 --batch-size 16`.
6. Run paired encoding: `python -m scripts.train_oscd --chips data/oscd_chips --out outputs/oscd_siamese --architecture siamese --epochs 8 --batch-size 16`.
7. Read the saved `test_metrics.json` in each output folder and the manuscript's figures. Large dataset files and checkpoints are excluded from Git.

## Presentation flow

1. Explain the two-date input and why a changed road or building matters.
2. Show the before, after, human mask and predictions in `paper/figures/oscd_validation_example.svg`; this was selected from a **validation** city as a visible illustration, not as a performance estimate.
3. Explain early fusion (stack both dates) versus Siamese encoding (shared encoder, compare features).
4. Compare the test precision/recall/F1 table. F1 balances precision and recall; the Siamese model trades more detections for more false alarms.
5. Show `paper/figures/oscd_city_f1.svg` and explain why a pooled score hides location-specific failure.
6. State the limitations: six bands, one split, eight epochs, cropped edges, seed variation, and exploratory reuse of the official test set for follow-up decisions.

## Journal readiness

The working manuscript is a credible starting point, **not a submission-ready novel method**. A publication attempt should first freeze a new research question and model choices, obtain a genuinely fresh external evaluation set or a strictly predeclared cross-city protocol, compare against current published methods using matched preprocessing, inspect representative errors, report uncertainty, and check dataset licensing and target journal scope. These are additional research tasks; they do not block final-year project submission or a working demonstration.
