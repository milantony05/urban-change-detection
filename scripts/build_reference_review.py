"""Build an offline, blind, one-location-at-a-time annotation page.

Sampling is restricted to geographic test_weak blocks never used for training
or validation. Model and spectral strata are hidden until CSV export.
"""
import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
import rasterio
import rasterio.warp
from PIL import Image, ImageDraw

from scripts.build_weak_chips import split_for_block


def picture(bands, y, x, radius, size):
    rgb = np.moveaxis(np.clip(bands[[2, 1, 0], y-radius:y+radius, x-radius:x+radius]
                              / 3500 * 255, 0, 255).astype('uint8'), 0, 2)
    image = Image.fromarray(rgb).resize((size, size), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(image)
    pixel = size / (2 * radius)
    center = size / 2
    draw.rectangle((center-pixel/2, center-pixel/2,
                    center+pixel/2-1, center+pixel/2-1), outline='#ffff00', width=2)
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=82)
    return 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('before', 'after', 'spectral', 'model', 'weak'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--per-stratum', type=int, default=12)
    args = p.parse_args()
    paths = [args.before, args.after, args.spectral, args.model, args.weak]
    opened = [rasterio.open(path) for path in paths]
    try:
        grids = {(ds.crs, ds.transform, ds.shape) for ds in opened}
        if len(grids) != 1:
            raise ValueError('All input rasters must have exactly the same grid')
        before, after = opened[0].read(), opened[1].read()
        spectral, model, weak = opened[2].read(1), opened[3].read(1), opened[4].read(1)
        height, width = spectral.shape
        rng = np.random.default_rng(20261102)
        seen_blocks = set()
        items = []
        groups = ('both', 'model_only', 'spectral_only', 'neither')
        for group in groups:
            candidates = []
            for by in range(0, height-100+1, 100):
                for bx in range(0, width-100+1, 100):
                    block_id = (by//100, bx//100)
                    if split_for_block(*block_id, 20261102) != 'test_weak':
                        continue
                    local = (before[6, by:by+100, bx:bx+100] >= 2) & (after[6, by:by+100, bx:bx+100] >= 2)
                    a = spectral[by:by+100, bx:bx+100] == 2
                    b = model[by:by+100, bx:bx+100] >= 0.5
                    if group == 'both': local &= a & b
                    elif group == 'model_only': local &= b & ~a
                    elif group == 'spectral_only': local &= a & ~b
                    else: local &= ~a & ~b & (weak[by:by+100, bx:bx+100] == 1)
                    positions = np.argwhere(local)
                    if len(positions):
                        rng.shuffle(positions)
                        for dy, dx in positions[:15]:
                            y, x = by+int(dy), bx+int(dx)
                            if 36 <= x < width-36 and 36 <= y < height-36:
                                candidates.append((block_id, y, x))
                                break
            rng.shuffle(candidates)
            for block_id, y, x in candidates:
                if block_id in seen_blocks:
                    continue
                seen_blocks.add(block_id)
                lon, lat = rasterio.warp.transform(opened[0].crs, 'EPSG:4326',
                                                   [opened[0].xy(y, x)[0]], [opened[0].xy(y, x)[1]])
                items.append({'id': f'R{len(items)+1:03d}', 'group': group, 'x': x, 'y': y,
                              'lon': round(lon[0], 6), 'lat': round(lat[0], 6),
                              'beforeContext': picture(before, y, x, 32, 256),
                              'beforeZoom': picture(before, y, x, 16, 256),
                              'afterContext': picture(after, y, x, 32, 256),
                              'afterZoom': picture(after, y, x, 16, 256)})
                if sum(item['group'] == group for item in items) >= args.per_stratum:
                    break
        if not items:
            raise ValueError('No eligible locations found')
        template = Path(__file__).with_name('reference_review_template.html').read_text()
        html = template.replace('/*DATA_PLACEHOLDER*/[]', json.dumps(items, separators=(',', ':')))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(html, encoding='utf-8')
        print('Review items:', len(items), {g: sum(i['group']==g for i in items) for g in groups})
    finally:
        for ds in opened: ds.close()


if __name__ == '__main__':
    main()
