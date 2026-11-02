"""Create a fixed validation-city example for presentations (not an accuracy metric)."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch

from urban_change.model import SmallUNet, SiameseUNet


def load_model(path, cls):
    checkpoint = torch.load(path, map_location='cpu', weights_only=False)
    model = cls()
    model.load_state_dict(checkpoint['model'])
    return model.eval()


def rgb(bands):
    image = np.moveaxis(bands[[2, 1, 0]], 0, 2)
    return np.clip(image / .35, 0, 1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chips', type=Path, default=Path('data/oscd_chips/val'))
    p.add_argument('--unet', type=Path, default=Path('outputs/oscd_model/best.pt'))
    p.add_argument('--siamese', type=Path, default=Path('outputs/oscd_siamese/best.pt'))
    p.add_argument('--out', type=Path, default=Path('paper/figures/oscd_validation_example.svg'))
    args = p.parse_args()
    torch.set_num_threads(min(torch.get_num_threads(), 4))
    candidates = sorted(args.chips.glob('abudhabi_*.npz'))
    if not candidates:
        raise FileNotFoundError('No Abu Dhabi validation chips found')
    # Fixed city; use the highest-change chip for an illustrative, visible case.
    selected = max(candidates, key=lambda path: int((np.load(path)['label'] == 2).sum()))
    with np.load(selected) as data:
        image, truth = data['image'].copy(), data['label'].copy() == 2
    tensor = torch.from_numpy(image[None]).float()
    with torch.no_grad():
        predictions = [load_model(args.unet, SmallUNet)(tensor).sigmoid().numpy()[0],
                       load_model(args.siamese, SiameseUNet)(tensor).sigmoid().numpy()[0]]
    fig, axes = plt.subplots(1, 5, figsize=(12, 2.9))
    layers = [rgb(image[:6]), rgb(image[6:]), truth, predictions[0], predictions[1]]
    titles = ['Before', 'After', 'Human mask', 'Early U-Net', 'Siamese U-Net']
    for ax, layer, title in zip(axes, layers, titles):
        ax.imshow(layer, cmap=None if layer.ndim == 3 else 'magma', vmin=0 if layer.ndim == 2 else None,
                  vmax=1 if layer.ndim == 2 else None, interpolation='nearest')
        ax.set_title(title, fontsize=10)
        ax.axis('off')
    fig.suptitle(f'OSCD validation example: {selected.stem} (models show change probability)', fontsize=11)
    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
