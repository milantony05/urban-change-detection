"""Search the public Copernicus STAC catalog and record scene provenance.

This command only inventories scenes. Scene-level cloud cover is not an AOI cloud mask.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from urban_change.config import validate_config

SEARCH_URL = "https://stac.dataspace.copernicus.eu/v1/search"
BANDS = ("B02_10m", "B03_10m", "B04_10m", "B08_10m", "B11_20m", "B12_20m", "SCL_20m")


def search(bbox, period, limit=100):
    payload = {
        "collections": ["sentinel-2-l2a"], "bbox": bbox,
        "datetime": f"{period['start']}T00:00:00Z/{period['end']}T23:59:59Z",
        "limit": limit,
    }
    request = Request(SEARCH_URL, data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json", "Accept": "application/geo+json"})
    with urlopen(request, timeout=90) as response:
        page = json.load(response)
    # The date windows and AOIs are small, but do not silently truncate results.
    if any(link.get("rel") == "next" for link in page.get("links", [])):
        raise RuntimeError("More than one STAC page; narrow the query or implement pagination")
    return page["features"]


def summarize(feature):
    props = feature["properties"]
    assets = feature.get("assets", {})
    return {
        "id": feature["id"], "datetime": props["datetime"],
        "scene_cloud_cover_percent": props.get("eo:cloud_cover"),
        "tile": feature["id"].split("_R")[-1].split("_")[1] if "_R" in feature["id"] else None,
        "assets": {band: assets[band]["href"] for band in BANDS if band in assets},
    }


def build_manifest(config):
    areas = []
    for area in config["areas"]:
        if area["status"] == "to_select":
            continue
        windows = []
        for period in area["periods"]:
            features = search(area["bbox"], period)
            scenes = sorted((summarize(f) for f in features),
                            key=lambda x: (x["scene_cloud_cover_percent"] is None,
                                           x["scene_cloud_cover_percent"] or 0, x["datetime"]))
            windows.append({"period": period, "scene_count": len(scenes), "scenes": scenes})
        areas.append({"id": area["id"], "role": area["role"], "bbox": area["bbox"], "windows": windows})
    return {"source": SEARCH_URL, "collection": "sentinel-2-l2a",
            "queried_at_utc": datetime.now(timezone.utc).isoformat(),
            "warning": "Scene-level cloud cover is not AOI cloud cover; inspect SCL and valid pixel coverage before selection.",
            "areas": areas}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/study_areas.json"))
    parser.add_argument("--output", type=Path, default=Path("data/catalog_manifest.json"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    errors = validate_config(config)
    if errors:
        parser.exit(2, "\n".join(errors) + "\n")
    manifest = build_manifest(config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for area in manifest["areas"]:
        print(area["id"], ", ".join(str(w["scene_count"]) for w in area["windows"]), "scenes per period")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
