# Phase 2 pilot GeoTIFF inspection

Two Google Earth Engine exports supplied on 2 November 2026 were inspected locally:

| File | Grid | Bands | CRS | Size | SHA-256 |
|---|---:|---|---|---:|---|
| `north_bengaluru_2018_dry_season.tif` | 3007 × 2005 | B2, B3, B4, B8, B11, B12 | EPSG:4326 | 92,330,549 bytes | `1186ba3130cd5ba15203996a71da0dbe8f3ef0269ed0583cff027d9cb0940428` |
| `north_bengaluru_2025_dry_season.tif` | 3007 × 2005 | B2, B3, B4, B8, B11, B12 | EPSG:4326 | 95,431,064 bytes | `082e92d68cc28e2f3aeb362b963703cf88b6a2d710338925055c1a83e9345f24` |

The rasters have identical bounds and transforms, so their pixels align exactly. Their extent matches the configured North Bengaluru AOI, and visual RGB inspection shows usable, largely clear coverage with substantial urban change visible between 2018 and 2025.

## Decision

The pilot confirms that GEE is a workable acquisition route and that the AOI and date windows are useful. These first files are pilot inputs rather than final research rasters because:

- the median export produced 64-bit floating-point bands, making each file about 90–95 MB;
- no `valid_count` band or explicit nodata value was exported, so a reflectance zero cannot always be distinguished from missing observations;
- scene IDs and acquisition dates were not exported with the files;
- EPSG:4326 is usable for display, but projected UTM coordinates are preferable for 10 m sampling and area measurements.

The revised `gee/export_composites.js` fixes these points. It exports UInt16 reflectance plus an observation-count band on an EPSG:32643 10 m grid, creates cloud-optimized GeoTIFFs, and exports a CSV scene manifest for each period.

Large GeoTIFFs remain outside Git. File checksums allow the exact local inputs to be identified without committing imagery.
