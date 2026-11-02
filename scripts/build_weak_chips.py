"""Build 64-pixel chips with geographically separated weak-label splits.

The labels are Dynamic World-derived suggestions. Scores against them do not
constitute independent accuracy estimates.
"""
import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np
import rasterio


def split_for_block(row, col, seed):
    digest = hashlib.sha256(f'{seed}:{row}:{col}'.encode()).digest()
    value = int.from_bytes(digest[:8], 'big') / 2**64
    return 'train' if value < 0.7 else ('val' if value < 0.85 else 'test_weak')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=20261102)
    args = parser.parse_args()

    with rasterio.open(args.before) as b, rasterio.open(args.after) as a, rasterio.open(args.labels) as l:
        if (b.crs, b.transform, b.shape) != (a.crs, a.transform, a.shape) or (b.crs, b.transform, b.shape) != (l.crs, l.transform, l.shape):
            raise ValueError('Inputs must share the exact pixel grid')
        before, after, label = b.read(), a.read(), l.read(1)
    if set(np.unique(label)) - {0, 1, 2}:
        raise ValueError('Weak labels must use only 0, 1, 2')
    good = (before[6] >= 2) & (after[6] >= 2)
    label = np.where(good, label, 0).astype('uint8')
    features = np.concatenate((before[:6], after[:6]), axis=0).astype('float32') / 10000.0

    rng = np.random.default_rng(args.seed)
    rows = []
    chip = 64
    block = 100  # 1 km on the 10 m UTM grid
    for by in range(0, label.shape[0] - block + 1, block):
        for bx in range(0, label.shape[1] - block + 1, block):
            portion = label[by:by+block, bx:bx+block]
            positives = np.argwhere(portion == 2)
            split = split_for_block(by // block, bx // block, args.seed)
            centers = []
            if len(positives):
                rng.shuffle(positives)
                py, px = positives[0]
                # Keep the chip inside its block while including the sampled
                # positive even when it lies close to a block boundary.
                cy, cx = int(np.clip(py, 32, 68)), int(np.clip(px, 32, 68))
                centers.append((by+cy, bx+cx))
            if not centers and np.count_nonzero(portion == 1) > 100:
                centers.append((by+50, bx+50))
            for cy, cx in centers:
                y0, x0 = cy - 32, cx - 32
                target = label[y0:y0+chip, x0:x0+chip]
                if target.shape != (chip, chip) or (np.count_nonzero(target) < 100 and not np.any(target == 2)):
                    continue
                identifier = f'b{by//block:03d}_{bx//block:03d}'
                folder = args.out / split
                folder.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(folder / f'{identifier}.npz',
                                    image=features[:, y0:y0+chip, x0:x0+chip], label=target)
                rows.append((identifier, split, by // block, bx // block, x0, y0,
                             int(np.count_nonzero(target == 2)), int(np.count_nonzero(target == 1))))
    with (args.out / 'manifest.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['id', 'split', 'block_row', 'block_col', 'x0', 'y0', 'weak_positive_pixels', 'weak_negative_pixels'])
        writer.writerows(rows)
    print(f'Wrote {len(rows)} spatially separated chips: '
          + ', '.join(f'{name}={sum(r[1] == name for r in rows)}' for name in ('train', 'val', 'test_weak')))


if __name__ == '__main__':
    main()
