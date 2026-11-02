# Phase 2: scene inventory and acquisition decision

## Catalog inspection, 2 November 2026

The public Copernicus STAC Sentinel-2 Level-2A search returned candidate scenes in the January–March windows of 2018 and 2025 for North Bengaluru and Pune. Pune is a **candidate** external test area, not a confirmed benchmark. The repository command records all returned scene IDs, dates, cloud percentages and band asset URIs in an ignored local manifest:

```bash
python -m urban_change.catalog --config configs/study_areas.json --output data/catalog_manifest.json
```

The search uses each AOI's bounding box and the two windows in the configuration. The catalog's `eo:cloud_cover` applies to the whole Sentinel tile, not our smaller AOI. A low value does not establish a usable cloud-free pair or actual vegetation-to-built-up change.

## Acquisition gate before model development

1. Confirm download or cloud-processing access to the B02/B03/B04/B08 10 m bands, B11/B12 20 m bands, and SCL 20 m scene-classification mask. STAC reports `s3://eodata/...` asset URIs, which may need Copernicus Data Space credentials or a processing service; catalog search alone does not download pixels.
2. Inspect actual SCL valid-pixel coverage inside each AOI and choose matching seasonal composites. Record image IDs and processing metadata; export a common georeferenced 10 m grid while retaining each original band's resolution in metadata.
3. Visually check multiple candidate changes in the *development* AOI against independent imagery. For Pune, check only image usability and annotation feasibility; preserve it for final external testing.
4. Lock AOIs, periods and split before manual reference-label creation. If Pune is unsuitable, replace it and document the reason before any model tuning.

The inventory is reproducible, but raster acquisition and valid-pixel inspection remain outstanding. This is a deliberate gate: no imagery or change labels have been asserted based only on scene metadata.
