"""Compare fixed methods on independently reviewed points, not area prevalence."""
import argparse
import csv
from pathlib import Path

import numpy as np
import rasterio


def metrics(predicted, truth):
    tp = int(np.sum(predicted & truth))
    fp = int(np.sum(predicted & ~truth))
    fn = int(np.sum(~predicted & truth))
    tn = int(np.sum(~predicted & ~truth))
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': precision, 'recall': recall,
            'f1': 2*precision*recall/max(precision+recall, 1e-12)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--spectral', type=Path, required=True)
    p.add_argument('--model', type=Path, required=True)
    p.add_argument('--threshold', type=float, default=0.5)
    args = p.parse_args()
    if not 0 <= args.threshold <= 1:
        raise ValueError('Threshold must be between 0 and 1')
    with rasterio.open(args.spectral) as s, rasterio.open(args.model) as m:
        if (s.crs, s.transform, s.shape) != (m.crs, m.transform, m.shape):
            raise ValueError('Prediction grids differ')
        spectral, model = s.read(1), m.read(1)
    with args.reference.open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate IDs in reference')
    accepted = []
    for row in rows:
        a, b = row['class_2018'].strip().lower(), row['class_2025'].strip().lower()
        confidence = row['confidence'].strip().lower()
        if not a or not b or a == 'unclear' or b == 'unclear' or confidence not in {'high', 'medium'}:
            continue
        x, y = int(row['pixel_x']), int(row['pixel_y'])
        if not (0 <= y < spectral.shape[0] and 0 <= x < spectral.shape[1]):
            raise ValueError(f"Point {row['id']} outside prediction raster")
        if spectral[y, x] == 0 or model[y, x] < 0:
            continue
        target = a == 'vegetation' and b == 'built-up'
        accepted.append((target, spectral[y, x] == 2, model[y, x] >= args.threshold, row['sampling_stratum']))
    if not accepted:
        raise ValueError('No usable reviewed points')
    truth = np.array([r[0] for r in accepted], dtype=bool)
    print(f'Accepted {len(accepted)} of {len(rows)} points; target positives: {truth.sum()}')
    for method, column in [('spectral', 1), ('model', 2)]:
        result = metrics(np.array([r[column] for r in accepted], dtype=bool), truth)
        print(method, result)
    print('This challenge sample is deliberately stratified by predictions. '
          'Do not infer area-wide conversion rate or population precision from these counts.')


if __name__ == '__main__':
    main()
