"""Train on OSCD's human annotated urban-change masks with city holdouts."""
import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler

from scripts.train_weak import Chips
from urban_change.model import SmallUNet, SiameseUNet


def score(model, loader, device):
    model.eval()
    tp = fp = fn = tn = 0
    with torch.no_grad():
        for x, y in loader:
            predicted = model(x.to(device)).sigmoid() >= .5
            actual = y.to(device) == 2
            tp += int((predicted & actual).sum())
            fp += int((predicted & ~actual).sum())
            fn += int((~predicted & actual).sum())
            tn += int((~predicted & ~actual).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'precision': precision,
            'recall': recall, 'f1': 2*precision*recall/max(precision+recall, 1e-12)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chips', type=Path, default=Path('data/oscd_chips'))
    p.add_argument('--out', type=Path, default=Path('outputs/oscd_model'))
    p.add_argument('--epochs', type=int, default=15)
    p.add_argument('--batch-size', type=int, default=8)
    p.add_argument('--architecture', choices=('unet', 'siamese'), default='unet')
    p.add_argument('--seed', type=int, default=20261102)
    p.add_argument('--positive-pixel-weight', type=float, default=5.0)
    p.add_argument('--positive-chip-weight', type=float, default=3.0)
    args = p.parse_args()
    if args.positive_pixel_weight <= 0 or args.positive_chip_weight <= 0:
        raise ValueError('Positive weights must be greater than zero')
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(min(torch.get_num_threads(), 4))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    training, validation = Chips(args.chips, 'train'), Chips(args.chips, 'val')
    with (args.chips/'manifest.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    positive_ids = {r['id'] for r in rows if r['split'] == 'train' and int(r['change_pixels']) > 0}
    weights = [args.positive_chip_weight if path.stem in positive_ids else 1.0 for path in training.files]
    train = DataLoader(training, batch_size=args.batch_size,
                       sampler=WeightedRandomSampler(weights, len(training), replacement=True))
    val = DataLoader(validation, batch_size=args.batch_size)
    model = (SiameseUNet() if args.architecture == 'siamese' else SmallUNet()).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    args.out.mkdir(parents=True, exist_ok=True)
    best = -1.0
    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        for x, y in train:
            x, truth = x.to(device), (y.to(device) == 2).float()
            optimizer.zero_grad()
            loss = nn.functional.binary_cross_entropy_with_logits(
                model(x), truth, pos_weight=torch.tensor(args.positive_pixel_weight, device=device))
            loss.backward()
            optimizer.step()
        result = score(model, val, device)
        history.append({'epoch': epoch, **result})
        print(json.dumps(history[-1]), flush=True)
        if result['f1'] > best:
            best = result['f1']
            torch.save({'model': model.state_dict(), 'architecture': args.architecture,
                        'epoch': epoch, 'seed': args.seed,
                        'positive_pixel_weight': args.positive_pixel_weight,
                        'positive_chip_weight': args.positive_chip_weight,
                        'dataset': 'OSCD', 'task': 'binary urban change',
                        'warning': 'OSCD urban change does not mean vegetation-to-built-up'}, args.out/'best.pt')
    (args.out/'history.json').write_text(json.dumps({'device': device, 'seed': args.seed,
        'positive_pixel_weight': args.positive_pixel_weight,
        'positive_chip_weight': args.positive_chip_weight, 'history': history}, indent=2)+'\n')
    checkpoint = torch.load(args.out/'best.pt', map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model'])
    test = score(model, DataLoader(Chips(args.chips, 'test'), batch_size=args.batch_size), device)
    (args.out/'test_metrics.json').write_text(json.dumps({'architecture': args.architecture,
                                                        'seed': args.seed,
                                                        'positive_pixel_weight': args.positive_pixel_weight,
                                                        'positive_chip_weight': args.positive_chip_weight,
                                                        'checkpoint_epoch': checkpoint['epoch'],
                                                        'city_holdout_test': test}, indent=2)+'\n')
    print('Untouched official test cities:', json.dumps(test))


if __name__ == '__main__':
    main()
