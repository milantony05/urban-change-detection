"""Repack OSCD Images.zip into valid, smaller ZIP archives by city."""
import argparse
import hashlib
import zipfile
from collections import defaultdict
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('--target-mb', type=int, default=65)
    args = p.parse_args()
    source = args.archive.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if args.target_mb < 1:
        raise ValueError('Target size must be positive')
    groups = defaultdict(list)
    with zipfile.ZipFile(source) as archive:
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            components = Path(entry.filename).parts
            city = components[1] if len(components) > 2 else '_metadata'
            groups[city].append(entry)
        bundles, current, size = [], [], 0
        limit = args.target_mb * 1024 * 1024
        for city, entries in sorted(groups.items()):
            estimate = sum(e.compress_size for e in entries)
            if current and size + estimate > limit:
                bundles.append(current)
                current, size = [], 0
            current.extend(entries)
            size += estimate
        if current:
            bundles.append(current)
        for number, entries in enumerate(bundles, 1):
            dest = source.with_name(f'oscd_images_part_{number:02d}.zip')
            if dest.exists():
                raise FileExistsError(f'{dest} exists; move old parts before retrying')
            with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
                for entry in entries:
                    output.writestr(entry.filename, archive.read(entry))
            print(f'{dest.name}: {dest.stat().st_size / 1024**2:.1f} MiB')
    digest = hashlib.sha256()
    with source.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    print(f'Created {len(bundles)} valid ZIPs; source SHA-256: {digest.hexdigest()}')


if __name__ == '__main__':
    main()
