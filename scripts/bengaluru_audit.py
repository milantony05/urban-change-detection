"""Create or summarize a small, blinded Bengaluru OSCD-model alert audit.

The sample is stratified by predictions and is not an area-wide accuracy sample.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
import rasterio
import rasterio.warp
from PIL import Image, ImageDraw

FIELDS = ['id', 'longitude', 'latitude', 'label', 'notes']


def rgb(bands, y, x, radius=48):
    crop = bands[[2, 1, 0], y-radius:y+radius, x-radius:x+radius]
    return Image.fromarray(np.moveaxis(np.clip(crop / 3500 * 255, 0, 255).astype('uint8'), 0, 2)).resize((384, 384), Image.Resampling.NEAREST)


def create(args):
    args.out.mkdir(parents=True, exist_ok=True)
    if any(args.out.iterdir()):
        raise ValueError('Output directory must be empty; do not overwrite a review in progress')
    with rasterio.open(args.before) as before, rasterio.open(args.after) as after, rasterio.open(args.probability) as prediction:
        if len({(d.crs, d.transform, d.shape) for d in (before, after, prediction)}) != 1:
            raise ValueError('Before, after, and probability rasters must share the exact grid')
        if before.count != 7 or after.count != 7 or prediction.count != 1 or before.crs is None:
            raise ValueError('Expected two seven-band composites and a georeferenced one-band probability raster')
        a, b, scores = before.read(), after.read(), prediction.read(1)
        valid = (a[6] >= 2) & (b[6] >= 2) & np.isfinite(scores) & (scores >= 0) & (scores <= 1)
        valid[:48] = False; valid[-48:] = False
        valid[:, :48] = False; valid[:, -48:] = False
        rng = np.random.default_rng(args.seed)
        selected = []
        used = set()
        for group, condition in [('alert', scores >= args.threshold), ('low_score', scores < args.threshold)]:
            # Uniformly sample eligible 1 km blocks, then a pixel within each block.
            blocks = []
            for y0 in range(0, before.height, 100):
                for x0 in range(0, before.width, 100):
                    if (y0//100, x0//100) in used:
                        continue
                    positions = np.argwhere((valid & condition)[y0:y0+100, x0:x0+100])
                    if len(positions):
                        blocks.append((y0, x0, positions))
            rng.shuffle(blocks)
            for y0, x0, positions in blocks[:args.per_group]:
                dy, dx = positions[rng.integers(len(positions))]
                y, x = y0 + int(dy), x0 + int(dx)
                used.add((y0//100, x0//100))
                selected.append((group, y, x))
            if len([s for s in selected if s[0] == group]) < args.per_group:
                raise ValueError(f'Only {len([s for s in selected if s[0] == group])} eligible blocks for {group}; choose fewer sites')
        rng.shuffle(selected)
        rows, manifest = [], []
        for i, (group, y, x) in enumerate(selected, 1):
            ident = f'B{i:03d}'
            lon, lat = rasterio.warp.transform(before.crs, 'EPSG:4326', [before.xy(y, x)[0]], [before.xy(y, x)[1]])
            card = Image.new('RGB', (768, 414), 'white')
            for j, source in enumerate((a, b)):
                card.paste(rgb(source, y, x), (j*384, 30))
            draw = ImageDraw.Draw(card)
            draw.text((8, 8), f'{ident}  2018', fill='black')
            draw.text((393, 8), '2025', fill='black')
            for center_x in (192, 576):
                draw.rectangle((center_x-2, 220, center_x+1, 223), outline='yellow', width=2)
            card.save(args.out / f'{ident}.jpg', quality=90)
            rows.append(dict(id=ident, longitude=f'{lon[0]:.6f}', latitude=f'{lat[0]:.6f}', label='', notes=''))
            manifest.append(dict(id=ident, group=group, pixel_x=x, pixel_y=y, probability=float(scores[y, x])))
    with (args.out / 'review.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    (args.out / 'sample_manifest.json').write_text(json.dumps(dict(seed=args.seed, threshold=args.threshold, per_group=args.per_group, sites=manifest), indent=2))
    print(f'Created {len(rows)} blinded cards, review.csv and a private sample_manifest.json in {args.out}')


def summarize(args):
    manifest = json.loads(args.manifest.read_text())
    with args.review.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    sites = {s['id']: s for s in manifest['sites']}
    if len(rows) != len(sites) or {r['id'] for r in rows} != set(sites):
        raise ValueError('Review IDs must match the manifest exactly, once each')
    counts = {g: {k: 0 for k in ('urban_change', 'no_urban_change', 'unclear')} for g in ('alert', 'low_score')}
    for row in rows:
        label = row['label'].strip().lower()
        if label not in counts['alert']:
            raise ValueError(f"Invalid or missing label for {row['id']}: {label!r}")
        counts[sites[row['id']]['group']][label] += 1
    for group, values in counts.items():
        print(group, values)
    print('These are counts within a prediction-stratified point review, not pixel F1, city accuracy, or change area.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    c = sub.add_parser('create')
    for name in ('before', 'after', 'probability', 'out'):
        c.add_argument('--' + name, type=Path, required=True)
    c.add_argument('--per-group', type=int, default=20)
    c.add_argument('--threshold', type=float, default=0.5)
    c.add_argument('--seed', type=int, default=20261103)
    s = sub.add_parser('summarize')
    s.add_argument('--manifest', type=Path, required=True)
    s.add_argument('--review', type=Path, required=True)
    args = p.parse_args()
    if args.command == 'create':
        if args.per_group < 1 or not 0 < args.threshold < 1:
            p.error('per-group must be positive and threshold must be between zero and one')
        create(args)
    else:
        summarize(args)


if __name__ == '__main__':
    main()
