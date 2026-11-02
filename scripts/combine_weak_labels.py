"""Union compatible weak negatives while preserving identical positives."""
import argparse
from pathlib import Path

import numpy as np
import rasterio


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v1', type=Path, required=True)
    p.add_argument('--v2', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    with rasterio.open(args.v1) as first, rasterio.open(args.v2) as second:
        if (first.crs, first.transform, first.shape) != (second.crs, second.transform, second.shape):
            raise ValueError('Weak label grids differ')
        a, b = first.read(1), second.read(1)
        profile = first.profile.copy()
    if set(np.unique(a)) - {0, 1, 2} or set(np.unique(b)) - {0, 1, 2}:
        raise ValueError('Unknown class in weak labels')
    if not np.array_equal(a == 2, b == 2):
        raise ValueError('Positive rules differ; cannot compare training sets safely')
    if np.any(((a == 1) | (b == 1)) & (a == 2)):
        raise ValueError('Positive and negative conflict')
    combined = np.where(a == 2, 2, np.where((a == 1) | (b == 1), 1, 0)).astype('uint8')
    profile.update(count=1, dtype='uint8', nodata=None, compress='deflate')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(args.out, 'w', **profile) as dst:
        dst.write(combined, 1)
        dst.set_band_description(1, 'weak_label')
        dst.update_tags(warning='Union of model-derived weak labels, not ground truth')
    values, counts = np.unique(combined, return_counts=True)
    print(dict(zip(values.tolist(), counts.tolist())))


if __name__ == '__main__':
    main()
