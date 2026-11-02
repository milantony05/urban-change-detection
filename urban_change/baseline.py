"""Exploratory spectral candidate map; no accuracy claims without reference labels.

Usage: python -m urban_change.baseline --before data/raw/2018.tif --after data/raw/2025.tif --output outputs/candidates.tif
"""
import argparse
from pathlib import Path

import numpy as np
import rasterio


REQUIRED = ("B2", "B3", "B4", "B8", "B11", "B12", "valid_count")


def read_raster(path):
    with rasterio.open(path) as src:
        if src.count != 7 or src.descriptions != REQUIRED:
            raise ValueError(f"{path}: expected bands {REQUIRED}; found {src.descriptions}")
        data = src.read().astype(np.float32)
        profile = src.profile.copy()
        grid = (src.crs, src.transform, src.width, src.height)
    return data, profile, grid


def index(numerator, denominator):
    return np.divide(numerator - denominator, numerator + denominator,
                     out=np.zeros_like(numerator), where=(numerator + denominator) > 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-valid", type=int, default=2)
    parser.add_argument("--ndvi-before", type=float, default=0.35)
    parser.add_argument("--ndvi-after", type=float, default=0.20)
    parser.add_argument("--ndbi-after", type=float, default=0.0)
    args = parser.parse_args()

    before, profile, grid = read_raster(args.before)
    after, _, after_grid = read_raster(args.after)
    if grid != after_grid:
        raise ValueError("Before and after rasters must have identical CRS and pixel grids")

    # 0 = invalid; 1 = valid, no candidate transition; 2 = candidate transition.
    valid = (before[6] >= args.min_valid) & (after[6] >= args.min_valid)
    ndvi_before = index(before[3], before[2])
    ndvi_after = index(after[3], after[2])
    ndbi_after = index(after[4], after[3])
    candidate = (ndvi_before >= args.ndvi_before) & (ndvi_after <= args.ndvi_after) & (ndbi_after > args.ndbi_after)
    result = np.where(valid, np.where(candidate, 2, 1), 0).astype(np.uint8)

    profile.update(dtype="uint8", count=1, nodata=0, compress="deflate", tiled=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(args.output, "w", **profile) as dst:
        dst.write(result, 1)
        dst.set_band_description(1, "spectral_candidate")
        dst.update_tags(before=args.before.name, after=args.after.name,
                        min_valid=args.min_valid, ndvi_before=args.ndvi_before,
                        ndvi_after=args.ndvi_after, ndbi_after=args.ndbi_after,
                        warning="Exploratory candidate map; thresholds are not validated")
    print(f"Valid pixels: {valid.sum():,}; candidates: {(result == 2).sum():,}; "
          f"candidate fraction: {(result == 2).sum() / max(valid.sum(), 1):.2%}")


if __name__ == "__main__":
    main()
