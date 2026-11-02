"""Create reproducible before/after review cards and a labeling CSV."""
import argparse
import csv
from pathlib import Path

import numpy as np
import rasterio
import rasterio.warp
from PIL import Image, ImageDraw


def rgb(data):
    return np.moveaxis(np.clip(data[[2, 1, 0]] / 3500 * 255, 0, 255).astype('uint8'), 0, 2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--before', type=Path, required=True)
    p.add_argument('--after', type=Path, required=True)
    p.add_argument('--candidates', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--count', type=int, default=24)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    with rasterio.open(a.before) as b, rasterio.open(a.after) as t, rasterio.open(a.candidates) as m:
        if (b.crs, b.transform, b.shape) != (t.crs, t.transform, t.shape) or (b.crs, b.transform, b.shape) != (m.crs, m.transform, m.shape):
            raise ValueError('Input grids differ')
        before, after, mask = b.read(), t.read(), m.read(1)
        rng = np.random.default_rng(20261102)
        rows = []
        # One sample per coarse 1 km block; candidate and random controls.
        used = set()
        for kind, value in [('candidate', 2), ('control', 1)]:
            ys, xs = np.where((mask == value) & (before[6] >= 2) & (after[6] >= 2))
            for k in rng.permutation(len(xs)):
                x, y = int(xs[k]), int(ys[k])
                if x < 64 or y < 64 or x + 64 >= b.width or y + 64 >= b.height:
                    continue
                block = (x // 100, y // 100)
                if block in used:
                    continue
                used.add(block)
                card = Image.new('RGB', (512, 280), 'white')
                for j, array in enumerate((before, after)):
                    crop = rgb(array[:6, y-64:y+64, x-64:x+64])
                    card.paste(Image.fromarray(crop).resize((256, 256)), (j*256, 24))
                draw = ImageDraw.Draw(card)
                ident = f'{kind}_{len(rows)+1:03d}'
                draw.text((4, 4), f'{ident}  2018', fill='black')
                draw.text((260, 4), '2025', fill='black')
                # The selected pixel is the center of each 128 x 128 crop.
                # Show it on BOTH dates, rather than on the separator.
                for cx in (128, 384):
                    cy = 152
                    draw.ellipse((cx-5, cy-5, cx+5, cy+5), outline='yellow', width=2)
                    draw.line((cx-9, cy, cx-6, cy), fill='yellow', width=2)
                    draw.line((cx+6, cy, cx+9, cy), fill='yellow', width=2)
                card.save(a.out / f'{ident}.png')
                lon, lat = rasterio.warp.transform(b.crs, 'EPSG:4326', [b.xy(y, x)[0]], [b.xy(y, x)[1]])
                rows.append([ident, kind, x, y, round(lon[0], 6), round(lat[0], 6), '', ''])
                if sum(r[1] == kind for r in rows) >= a.count // 2:
                    break
        with (a.out / 'labels.csv').open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['id', 'sampling_stratum', 'pixel_x', 'pixel_y', 'longitude', 'latitude', 'label', 'notes'])
            w.writerows(rows)
        print(f'Created {len(rows)} cards in {a.out}')


if __name__ == '__main__':
    main()
