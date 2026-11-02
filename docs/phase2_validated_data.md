# Phase 2 validated North Bengaluru data

Validated 2 November 2026 against four supplied v3 exports. The source GeoTIFFs remain outside Git.

| Period | GeoTIFF SHA-256 | Scene CSV SHA-256 | Source scenes | Grid |
|---|---|---|---:|---|
| 2018 Jan–Mar | `4d422ca4b18e317f248852ef5161e5d18e2aa2fec3cf46c6a956047a2f110b02` | `14a87ca15be2da507244a0d983c7b762f3d4621986d4ee72ee408d3ace26835e` | 7 | 2950 × 2024, EPSG:32643, 10 m |
| 2025 Jan–Mar | `a00c507e167338b7fa97fe203f8b6c4a6120957ac490b1c250b3a4f7c1087f86` | `5d9f929a66840394388df1947ddfeebb7d3492441c919cdf8ad850622f1685b2` | 17 | same grid |

Each GeoTIFF has UInt16 bands `B2, B3, B4, B8, B11, B12, valid_count`. Both share identical extent (UTM metres: west 768770, south 1442870, east 798270, north 1463110) and transform. The six reflectance bands have thousands of distinct values, restoring the spatial detail lost in the v2 exports. RGB inspection confirms that major features line up between years.

The observation-count band is positive for 97.832% of raster pixels in each period; the remaining 2.168% is the rectangular export outside the AOI. Valid pixels have 5–7 clear observations in 2018 and 12–17 in 2025. The CSVs identify 7 and 17 scenes respectively; they contain image IDs, acquisition times and tile-wide cloud percentages. Use `valid_count > 0` **in both periods** as the analysis mask. Do not interpret zeros outside that mask as reflectance.

The window lengths and number of contributing scenes differ, so a seven-year image difference is not automatically vegetation-to-built-up conversion. Change labels must be checked independently, and the later cross-city test requires its own data. The Pune candidate remains reserved for external evaluation; no external-city pixels have been acquired or used to tune a model.

## Reproduce local inspection

```bash
python scripts/inspect_rasters.py data/raw/north_bengaluru_2018_dry_season_v3.tif data/raw/north_bengaluru_2025_dry_season_v3.tif
```

The repository's `data/` directory is ignored by Git. Keep the supplied source files and CSVs together under `data/raw/` locally. No label quality or model accuracy has yet been established.
