# OSCD supervised urban-change benchmark

OSCD provides 24 registered Sentinel-2 pairs with manually annotated binary urban-change masks, including new buildings and roads. The original 14 training cities and ten test cities have labels available. This benchmark tests **general urban change**, not the specific vegetation-to-built-up transition in our Bengaluru/Kochi study. The city split prevents nearby chips from the same scene appearing in both training and evaluation.

## Data acquisition

Visit the [OSCD author's page](https://rcdaudt.github.io/oscd/) and download these three archives from its Links section: `Images.zip` (about 489 MB), `Train labels.zip`, and `Test labels.zip`. The author also links IEEE DataPort. Extract each archive under `data/oscd/`, preserving the archive's top-level folder names:

```text
data/oscd/
  Onera Satellite Change Detection dataset - Images/
  Onera Satellite Change Detection dataset - Train Labels/
  Onera Satellite Change Detection dataset - Test Labels/
```

The images folder contains city directories with `imgs_1_rect/B02.tif` through `B12.tif` and `imgs_2_rect`; each label folder contains `city/cm/city-cm.tif`. The TIFF masks encode no change=1 and change=2. Use these rather than the preview PNGs; the `aguasclaras` PNG includes intermediate grayscale values. Keep the archive files and extracted data outside Git. Expected SHA-256 archives according to TorchGeo's dataset implementation: Images `940b87887511058a933e67cd6d0e43e2eb825a55d8e79a50983dee7f23003656`; Train Labels `89fb54cd12ad0dbea6c447528139dec305b865294215434bf6dd170fb8fd3ca5`; Test Labels `2e195eaa1b788b99fa93ea8073e3780bc0b763000b0c49dbf70548acf1e5d67d`. The received Train and Test archives match their expected hashes. The Images archive has not yet become available in this workspace.

## Run

```bash
python -m scripts.prepare_oscd --root data/oscd --out data/oscd_chips
python -m scripts.train_oscd --chips data/oscd_chips --out outputs/oscd_model
```

The preparer selects six bands in our existing input order (B02, B03, B04, B08, B11, B12), divides values by 10,000 and creates non-overlapping 64-pixel chips. It assigns four of the 14 original training cities to validation by sorted city name and keeps all ten official test cities for one final test after the validation-selected checkpoint. A 3:1 positive-chip sampler and positive pixel loss weight 5 address class imbalance. Output includes `best.pt`, `history.json` and `test_metrics.json`. The existing `scripts.predict_raster` can run the checkpoint on Bengaluru/Kochi six-band composites, but these outputs are **qualitative transfer examples**: OSCD predicts any urban change, and its imagery dates/product properties may differ from our surface-reflectance composites. Do not compare those predictions against vegetation-to-built-up labels as if the class definitions matched.

The benchmark was run on the uploaded 24-city images repacked into ten valid ZIPs and the checksum-matching official label archives. We used eight epochs and batch size 16, with separate U-Net and Siamese checkpoints chosen by validation F1. Results and city variation appear in [oscd_results.md](oscd_results.md). Cite Daudt et al., *Urban Change Detection for Multispectral Earth Observation Using Convolutional Neural Networks*, IGARSS 2018, DOI 10.1109/IGARSS.2018.8518015.
