"""Validation-tuned six-band change-vector baseline for the OSCD chips."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def load(root, split):
    scores, truth = [], []
    for path in sorted((root / split).glob('*.npz')):
        with np.load(path) as data:
            x = data['image']
            scores.append(np.sqrt(np.mean((x[:6] - x[6:]) ** 2, axis=0)).ravel())
            truth.append((data['label'] == 2).ravel())
    if not scores:
        raise ValueError(f'No chips in {root / split}')
    return np.concatenate(scores), np.concatenate(truth)


def metrics(pred, truth):
    tp = int((pred & truth).sum())
    fp = int((pred & ~truth).sum())
    fn = int((~pred & truth).sum())
    tn = int((~pred & ~truth).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'precision': precision,
            'recall': recall, 'f1': 2 * precision * recall / max(precision + recall, 1e-12)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chips', type=Path, default=Path('data/oscd_chips'))
    p.add_argument('--out', type=Path, default=Path('outputs/oscd_change_vector.json'))
    args = p.parse_args()
    validation, val_truth = load(args.chips, 'val')
    thresholds = np.linspace(.01, .30, 60)
    threshold = max(thresholds, key=lambda t: metrics(validation >= t, val_truth)['f1'])
    val_result = metrics(validation >= threshold, val_truth)
    test, test_truth = load(args.chips, 'test')
    result = {'method': 'six-band RMS change vector', 'threshold': float(threshold),
              'validation': val_result, 'test': metrics(test >= threshold, test_truth)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
