# Phase 2 v2 export quality failure

The two supplied v2 GeoTIFFs have matching EPSG:32643 10 m grids and seven UInt16 bands, but their reflectance bands are nearly constant across the AOI. They must not be used for training, change maps or area estimates.

| Period | Size | B2 distinct values | B4 distinct values | B8 distinct values | SHA-256 |
|---|---:|---:|---:|---:|---|
| 2018 | 1,492,424 bytes | 2 | 2 | 2 | `75d7635b23b7a3e0f23702a0c3abe0529ba0b413e12824c9ee89eb0f1a7ebd93` |
| 2025 | 6,492,700 bytes | 3 | 3 | 2 | `d4d16c688e3c437850e6e2a8798614f5e40673e63d9ad3f7751bc30a9cb6b943` |

This failure is consistent with bilinear resampling of a median composite at its coarse default projection. The revised v3 GEE script removes that resampling and casts all bands to UInt16 at export. This explanation is a diagnosis, not yet a verified GEE execution: new exports must pass the spatial-variation check in `scripts/inspect_rasters.py`.

The earlier six-band pilot exports contain spatial detail, so the data source and date windows remain viable. The final seven-band rasters and scene manifest CSVs are still required to close Phase 2.
