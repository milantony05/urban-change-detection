"""Train a small U-Net on weak labels; reported scores are pipeline checks only."""
import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

from urban_change.model import SmallUNet, SiameseUNet


class Chips(Dataset):
    def __init__(self, root, split):
        self.files = sorted((root / split).glob('*.npz'))
        if not self.files:
            raise ValueError(f'No chips in {root / split}')

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        with np.load(self.files[index]) as chip:
            x = torch.from_numpy(chip['image'].copy()).float()
            y = torch.from_numpy(chip['label'].copy()).long()
        return x, y


def masked_loss(logits, target, positive_weight=40.0):
    known = target != 0
    truth = (target == 2).float()
    per_pixel = nn.functional.binary_cross_entropy_with_logits(
        logits, truth, reduction='none', pos_weight=torch.tensor(positive_weight, device=logits.device))
    return (per_pixel * known).sum() / known.sum().clamp(min=1)


def evaluate(model, loader, device, positive_weight=40.0):
    model.eval()
    tp = fp = fn = 0
    losses = []
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            losses.append(float(masked_loss(logits, y, positive_weight)))
            predicted = logits.sigmoid() >= 0.5
            positive = y == 2
            known = y != 0
            tp += int((predicted & positive).sum())
            fp += int((predicted & ~positive & known).sum())
            fn += int((~predicted & positive).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {'weak_loss': float(np.mean(losses)), 'weak_precision': precision,
            'weak_recall': recall, 'weak_f1': 2*precision*recall/max(precision+recall, 1e-12),
            'weak_positive_pixels': tp+fn}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chips', type=Path, default=Path('data/weak_chips'))
    p.add_argument('--out', type=Path, default=Path('outputs/weak_model'))
    p.add_argument('--epochs', type=int, default=5)
    p.add_argument('--batch-size', type=int, default=8)
    p.add_argument('--seed', type=int, default=20261102)
    p.add_argument('--architecture', choices=('unet', 'siamese'), default='unet')
    p.add_argument('--positive-weight', type=float, default=None,
                   help='Default 40 for U-Net, 10 for the Siamese experiment')
    args = p.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(min(torch.get_num_threads(), 4))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    training = Chips(args.chips, 'train')
    validation = Chips(args.chips, 'val')
    rows = list(csv.DictReader((args.chips / 'manifest.csv').open(newline='')))
    positive_ids = {row['id'] for row in rows if row['split']=='train' and int(row['weak_positive_pixels'])>0}
    weights = [8.0 if file.stem in positive_ids else 1.0 for file in training.files]
    sampler = WeightedRandomSampler(weights, len(training), replacement=True)
    train_loader = DataLoader(training, batch_size=args.batch_size, sampler=sampler)
    val_loader = DataLoader(validation, batch_size=args.batch_size)
    positive_weight = args.positive_weight if args.positive_weight is not None else (10.0 if args.architecture == 'siamese' else 40.0)
    if positive_weight <= 0:
        raise ValueError('Positive weight must be positive')
    model = (SiameseUNet() if args.architecture == 'siamese' else SmallUNet()).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    args.out.mkdir(parents=True, exist_ok=True)
    best = float('inf')
    history = []
    for epoch in range(1, args.epochs+1):
        model.train()
        train_losses = []
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = masked_loss(model(x), y, positive_weight)
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.detach()))
        metrics = evaluate(model, val_loader, device, positive_weight)
        record = {'epoch': epoch, 'train_weak_loss': float(np.mean(train_losses)), **metrics}
        history.append(record)
        print(json.dumps(record), flush=True)
        if metrics['weak_loss'] < best:
            best = metrics['weak_loss']
            torch.save({'model': model.state_dict(), 'seed': args.seed, 'epoch': epoch,
                        'architecture': args.architecture, 'positive_weight': positive_weight,
                        'warning': 'Trained with Dynamic World weak labels; not independently validated'}, args.out/'best.pt')
    (args.out/'history.json').write_text(json.dumps({'device':device,'history':history},indent=2)+'\n')


if __name__ == '__main__':
    main()
