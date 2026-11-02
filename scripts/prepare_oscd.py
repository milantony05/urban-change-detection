"""Convert extracted, manually labeled OSCD cities into 64-pixel PyTorch chips.

Keep the official ten test cities untouched. Four of the fourteen official
training cities become validation cities; no patches from a city cross splits.
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image

BANDS = ('B02', 'B03', 'B04', 'B08', 'B11', 'B12')


def read_city(folder, mask_path):
    dates = []
    for date in (1, 2):
        channels = []
        for band in BANDS:
            path = folder / f'imgs_{date}_rect' / f'{band}.tif'
            if not path.exists():
                raise FileNotFoundError(path)
            with rasterio.open(path) as ds:
                channels.append(ds.read(1).astype('float32'))
        if len({a.shape for a in channels}) != 1:
            raise ValueError(f'Bands in {folder} are not aligned')
        dates.append(np.stack(channels))
    mask = np.asarray(Image.open(mask_path).convert('L'))
    if dates[0].shape != dates[1].shape or mask.shape != dates[0].shape[1:]:
        raise ValueError(f'Image or mask shape differs in {folder.name}')
    image = np.concatenate(dates) / 10000.0
    if not np.isfinite(image).all():
        raise ValueError(f'Nonfinite reflectance in {folder.name}')
    return image.astype('float32'), (mask > 0).astype('uint8') + 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('data/oscd'))
    p.add_argument('--out', type=Path, default=Path('data/oscd_chips'))
    p.add_argument('--chip', type=int, default=64)
    args = p.parse_args()
    images = args.root / 'Onera Satellite Change Detection dataset - Images'
    train_labels = args.root / 'Onera Satellite Change Detection dataset - Train Labels'
    test_labels = args.root / 'Onera Satellite Change Detection dataset - Test Labels'
    if not images.is_dir() or not train_labels.is_dir() or not test_labels.is_dir():
        raise FileNotFoundError('Extract the official Images, Train Labels, and Test Labels ZIPs under --root')
    train_cities = sorted(p.name for p in train_labels.iterdir() if p.is_dir())
    test_cities = sorted(p.name for p in test_labels.iterdir() if p.is_dir())
    if len(train_cities) != 14 or len(test_cities) != 10 or set(train_cities) & set(test_cities):
        raise ValueError(f'Expected 14 disjoint training and 10 test cities, got {len(train_cities)} and {len(test_cities)}')
    val_cities = set(train_cities[::4])  # four city holdouts, chosen without labels
    rows = []
    for city in train_cities + test_cities:
        split = 'test' if city in test_cities else ('val' if city in val_cities else 'train')
        labels = test_labels if split == 'test' else train_labels
        image, mask = read_city(images / city, labels / city / 'cm' / 'cm.png')
        height, width = mask.shape
        for y in range(0, height - args.chip + 1, args.chip):
            for x in range(0, width - args.chip + 1, args.chip):
                target = mask[y:y+args.chip, x:x+args.chip]
                name = f'{city}_{y}_{x}'
                folder = args.out / split
                folder.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(folder / f'{name}.npz',
                                    image=image[:, y:y+args.chip, x:x+args.chip], label=target)
                rows.append((name, city, split, x, y, int((target == 2).sum())))
    with (args.out / 'manifest.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('id', 'city', 'split', 'pixel_x', 'pixel_y', 'change_pixels'))
        writer.writerows(rows)
    print(f'Wrote {len(rows)} chips; validation cities: {sorted(val_cities)}')


if __name__ == '__main__':
    main()
