"""Validate study-area metadata without geospatial dependencies.

Run: python -m urban_change.config --config configs/study_areas.json
"""
import argparse
import json
from datetime import date
from pathlib import Path


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []
    if config.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if config.get("crs") != "EPSG:4326":
        errors.append("area coordinates must use EPSG:4326")
    areas = config.get("areas")
    if not isinstance(areas, list) or not areas:
        return errors + ["areas must be a nonempty list"]
    seen: set[str] = set()
    roles: set[str] = set()
    for index, area in enumerate(areas):
        prefix = f"areas[{index}]"
        if not isinstance(area, dict):
            errors.append(f"{prefix} must be an object")
            continue
        identifier = area.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{prefix}.id must be a nonempty string")
        elif identifier in seen:
            errors.append(f"{prefix}.id is duplicated")
        else:
            seen.add(identifier)
        role = area.get("role")
        if role not in {"development", "external_test"}:
            errors.append(f"{prefix}.role is invalid")
        else:
            roles.add(role)
        status = area.get("status")
        if status not in {"candidate", "to_select", "confirmed"}:
            errors.append(f"{prefix}.status is invalid")
        bbox = area.get("bbox")
        periods = area.get("periods")
        if status == "to_select":
            if bbox is not None or periods != []:
                errors.append(f"{prefix}: to_select must have null bbox and empty periods")
            continue
        if (not isinstance(bbox, list) or len(bbox) != 4
                or any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in bbox)):
            errors.append(f"{prefix}.bbox must be [west, south, east, north]")
        else:
            west, south, east, north = bbox
            if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
                errors.append(f"{prefix}.bbox coordinates are invalid")
        if not isinstance(periods, list) or len(periods) != 2:
            errors.append(f"{prefix}.periods must contain exactly two windows")
            continue
        previous_end = None
        for number, period in enumerate(periods):
            try:
                start = date.fromisoformat(period["start"])
                end = date.fromisoformat(period["end"])
                if start > end or (previous_end is not None and start <= previous_end):
                    raise ValueError("overlapping or reversed windows")
                previous_end = end
            except (KeyError, TypeError, ValueError):
                errors.append(f"{prefix}.periods[{number}] has invalid dates")
    if not {"development", "external_test"} <= roles:
        errors.append("include development and external_test areas")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    errors = validate_config(config)
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print(f"Valid configuration: {len(config['areas'])} study-area entries")


if __name__ == "__main__":
    main()
