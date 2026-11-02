# Sentinel-2 urban change detection

A final-year deep learning and GIS project using the human-labeled [OSCD](https://rcdaudt.github.io/oscd/) dataset. It compares a two-date early-fusion U-Net, a shared-encoder Siamese U-Net and a spectral change-vector baseline on **unseen cities**.

## Problem

Given co-registered Sentinel-2 images from two dates, predict which 10 m pixels contain urban change such as new buildings or roads. The 24 OSCD cities are separated into ten for training, four for validation and ten official test cities. The project examines how architecture, class imbalance and geography affect generalization. OSCD's binary urban-change label does **not** identify vegetation-to-built-up conversion specifically.

## Results

| Method | Test precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Six-band change vector | 0.312 | 0.418 | 0.357 |
| Early-fusion U-Net | 0.644 | 0.305 | 0.414 |
| Siamese U-Net, initial seed | 0.404 | 0.556 | 0.468 |

The Siamese model's three-seed mean F1 was 0.412 with the original loss and sampling setting, and 0.441 with a conservative setting that raised precision and lowered recall. Performance varies greatly by city. These are exploratory results: follow-up experiments were designed after the first official test result was viewed. See the [full metrics](docs/oscd_results.md), [three-seed comparison](docs/oscd_weight_sensitivity.md), [city figure](paper/figures/oscd_city_f1.svg) and [working manuscript](paper/oscd_manuscript_draft.md).

## Reproduce

Install Python 3.10 or later and dependencies:

```bash
pip install -r requirements-research.txt
```

Download OSCD Images, Train Labels and Test Labels from the [author's page](https://rcdaudt.github.io/oscd/) and extract the three top-level folders under `data/oscd/`. The supplied split image archives can be extracted to the same folder. Keep data and checkpoints outside Git.

```bash
python -m scripts.prepare_oscd --root data/oscd --out data/oscd_chips
python -m scripts.oscd_baseline --chips data/oscd_chips
python -m scripts.train_oscd --chips data/oscd_chips --out outputs/oscd_model --epochs 8 --batch-size 16
python -m scripts.train_oscd --chips data/oscd_chips --out outputs/oscd_siamese --architecture siamese --epochs 8 --batch-size 16
python -m scripts.make_oscd_demo
```

Read each model's `outputs/.../test_metrics.json`. For the repeated-seed commands and dataset layout, see [OSCD instructions](docs/oscd_benchmark.md) and the [final project handoff](docs/final_project_handoff.md).

## Repository layout

- `urban_change/model.py`: early-fusion and Siamese architectures.
- `scripts/prepare_oscd.py`, `train_oscd.py`, `oscd_baseline.py`: data and evaluation pipeline.
- `scripts/report_oscd_city.py`, `plot_oscd_city.py`, `make_oscd_demo.py`: analysis and figures.
- `paper/`: manuscript drafts, figures and per-city metrics.
- `docs/`: data provenance, methods, results and limitations.
- `data/`, `outputs/`: local ignored datasets and checkpoints.

The earlier Bengaluru/Kochi [vegetation-to-built-up pilot](paper/manuscript_draft.md) remains documented separately. It used Dynamic World weak labels and a small independent review; it is not the supervised OSCD benchmark.

## Scope and attribution

This repository does not contain third-party imagery or model checkpoints. Cite Daudt et al., *Urban Change Detection for Multispectral Earth Observation Using Convolutional Neural Networks*, IGARSS 2018, DOI 10.1109/IGARSS.2018.8518015 when using OSCD. No repository license has been selected; source data retain their providers' terms. The project is complete as an exploratory final-year demonstration. The manuscript still needs a confirmatory design and deeper comparison for journal submission.
