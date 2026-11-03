# Bengaluru urban-change screening with Sentinel-2

This final-year project uses paired 2018 and 2025 Sentinel-2 composites to **highlight possible urban changes in North Bengaluru for human review**. A compact Siamese network was trained on the labeled OSCD dataset. The Bengaluru candidate map is the main application; [the 40-site review workflow](docs/bengaluru_screening.md) provides a small, transparent local check. Bengaluru review labels and accuracy have not yet been collected.

## Problem

Finding possible changes across a large satellite scene by eye is slow. The model assigns a change probability to each valid 10 m pixel so a person can inspect promising locations. It may confuse seasonal or imaging differences with construction. OSCD training and city-disjoint evaluation supply an external benchmark, while sampled Bengaluru observations address whether its local alerts are useful. The OSCD target is general annotated urban change; it is not specifically vegetation-to-built-up conversion.

## Bengaluru workflow

The existing [raster predictor](scripts/predict_raster.py) reads aligned six-band plus valid-count composites and a frozen OSCD checkpoint. The [audit script](scripts/bengaluru_audit.py) produces 20 blinded alert cards and 20 low-score cards, with a CSV for human labels and a count summary. See [step-by-step instructions](docs/bengaluru_screening.md). Source imagery, trained checkpoints and local probability rasters are not committed; the local audit has not yet been run, so no Bengaluru score is claimed.

## OSCD benchmark

The models were trained and evaluated with ten training, four validation, and ten official test cities. OSCD results below are exploratory because the first official test was viewed before later design choices.

## Results

| Method | Test precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Six-band change vector | 0.312 | 0.418 | 0.357 |
| Early-fusion U-Net | 0.644 | 0.305 | 0.414 |
| Siamese U-Net, initial seed | 0.404 | 0.556 | 0.468 |

The Siamese model's three-seed mean F1 was 0.412 with the original loss and sampling setting, and 0.441 with a conservative setting that raised precision and lowered recall. Performance varies greatly by city. These are exploratory results: follow-up experiments were designed after the first official test result was viewed. See the [full metrics](docs/oscd_results.md), [three-seed comparison](docs/oscd_weight_sensitivity.md), [city figure](paper/figures/oscd_city_f1.svg) and [working manuscript](paper/oscd_manuscript_draft.md).

## Showcase

- Open [the interactive dashboard](dashboard/index.html) after downloading or cloning the repository. It is a self-contained HTML file and works offline; select a city and model to inspect F1 and confusion counts.
- Open [the Jupyter showcase notebook](notebooks/oscd_showcase.ipynb) on GitHub to see its saved figures and narrative. To run the cells locally, install `requirements-research.txt`, launch `jupyter lab` from the repository root, and open the notebook.
- The dashboard is generated from committed metrics with `python -m scripts.build_dashboard`; the notebook is generated with `python -m scripts.build_showcase_notebook`. Neither requires retraining.
- The [saved test metrics](artifacts/README.md) are included for review. The larger `data/` and runtime `outputs/` directories are created locally by scripts and do not appear in Git.

## Reproduce

Install Python 3.10 or later and dependencies:

```bash
pip install -r requirements-research.txt
```

Download OSCD Images, Train Labels and Test Labels from the [author's page](https://rcdaudt.github.io/oscd/) and extract the three top-level folders under `data/oscd/`. The supplied split image archives can be extracted to the same folder. Keep source imagery and trained checkpoints outside Git; rerunning the scripts regenerates them locally.

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
- [`docs/`](docs/README.md): current-project links and earlier-pilot provenance.
- `artifacts/`: small tracked metric summaries and an explanation of generated outputs.
- `data/`, `outputs/`: local ignored datasets and generated runtime files; scripts create them as needed.

The earlier Bengaluru/Kochi [vegetation-to-built-up pilot](paper/manuscript_draft.md) remains documented separately. It used Dynamic World weak labels and a small independent review; it is not the supervised OSCD benchmark.

## Scope and attribution

This repository does not contain third-party imagery or model checkpoints. Cite Daudt et al., *Urban Change Detection for Multispectral Earth Observation Using Convolutional Neural Networks*, IGARSS 2018, DOI 10.1109/IGARSS.2018.8518015 when using OSCD. No repository license has been selected; source data retain their providers' terms. The project is complete as an exploratory final-year demonstration. The manuscript still needs a confirmatory design and deeper comparison for journal submission.
