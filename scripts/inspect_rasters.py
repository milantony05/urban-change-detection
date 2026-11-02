"""Inspect alignment, bands and value ranges of exported GeoTIFFs."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect(path: Path) -> dict:
    with rasterio.open(path) as dataset:
        bands = []
        for index in range(1, dataset.count + 1):
            values = dataset.read(index, masked=True).compressed()
            bands.append({
                "index": index,
                "name": dataset.descriptions[index - 1],
                "dtype": dataset.dtypes[index - 1],
                "minimum": float(values.min()),
                "p01": float(np.percentile(values, 1)),
                "median": float(np.median(values)),
                "p99": float(np.percentile(values, 99)),
                "maximum": float(values.max()),
                "unique_values": int(np.unique(values).size),
            })
        return {
            "file": path.name,
            "sha256": checksum(path),
            "size_bytes": path.stat().st_size,
            "width": dataset.width,
            "height": dataset.height,
            "count": dataset.count,
            "crs": str(dataset.crs),
            "transform": list(dataset.transform)[:6],
            "bounds": list(dataset.bounds),
            "nodata": dataset.nodata,
            "bands": bands,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rasters", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {"rasters": [inspect(path) for path in args.rasters]}
    grids = {(r["width"], r["height"], r["crs"], tuple(r["transform"]), tuple(r["bounds"]))
             for r in report["rasters"]}
    report["same_grid"] = len(grids) == 1
    report["reflectance_has_spatial_variation"] = all(
        all(b["unique_values"] > 100 for b in raster["bands"][:6])
        for raster in report["rasters"]
    )
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
