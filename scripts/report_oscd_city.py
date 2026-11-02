"""Report OSCD test metrics by held-out city for saved checkpoints."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Subset

from scripts.train_weak import Chips
from scripts.train_oscd import score
from urban_change.model import SmallUNet, SiameseUNet


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chips', type=Path, default=Path('data/oscd_chips'))
    p.add_argument('--model', action='append', required=True,
                   help='Repeat as name=checkpoint.pt')
    p.add_argument('--baseline', type=Path, default=Path('outputs/oscd_change_vector.json'))
    p.add_argument('--out', type=Path, default=Path('outputs/oscd_city_metrics.csv'))
    args = p.parse_args()
    torch.set_num_threads(min(torch.get_num_threads(), 4))
    with (args.chips/'manifest.csv').open(newline='') as stream:
        cities = {r['id']: r['city'] for r in csv.DictReader(stream) if r['split'] == 'test'}
    dataset = Chips(args.chips, 'test')
    groups = {city: [i for i, f in enumerate(dataset.files) if cities[f.stem] == city]
              for city in sorted(set(cities.values()))}
    threshold = json.loads(args.baseline.read_text())['threshold']
    rows = []
    for city, indices in groups.items():
        raw, truth = [], []
        for i in indices:
            x, y = dataset[i]
            a = x.numpy()
            raw.append(np.sqrt(np.mean((a[:6] - a[6:]) ** 2, axis=0)).ravel())
            truth.append((y.numpy() == 2).ravel())
        diff, actual = np.concatenate(raw), np.concatenate(truth)
        pred = diff >= threshold
        tp, fp = int((pred & actual).sum()), int((pred & ~actual).sum())
        fn, tn = int((~pred & actual).sum()), int((~pred & ~actual).sum())
        precision, recall = tp/max(tp+fp, 1), tp/max(tp+fn, 1)
        rows.append({'model': 'change_vector', 'city': city, 'chips': len(indices),
                     'change_fraction': float(actual.mean()), 'tp': tp, 'fp': fp,
                     'fn': fn, 'tn': tn, 'precision': precision, 'recall': recall,
                     'f1': 2*precision*recall/max(precision+recall, 1e-12)})
    for spec in args.model:
        name, sep, filename = spec.partition('=')
        if not sep:
            raise ValueError('Each --model must be name=checkpoint.pt')
        ck = torch.load(filename, map_location='cpu', weights_only=False)
        net = SiameseUNet() if ck.get('architecture') == 'siamese' else SmallUNet()
        net.load_state_dict(ck['model'])
        for city, indices in groups.items():
            result = score(net, DataLoader(Subset(dataset, indices), batch_size=16), 'cpu')
            rows.append({'model': name, 'city': city, 'chips': len(indices),
                         'change_fraction': (result['tp']+result['fn']) /
                                            sum(result[k] for k in ('tp','fp','fn','tn')),
                         **result})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} city/model rows to {args.out}')


if __name__ == '__main__':
    main()
