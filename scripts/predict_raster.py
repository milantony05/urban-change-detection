"""Apply a weak-label U-Net checkpoint to paired, aligned Sentinel-2 rasters."""
import argparse
from pathlib import Path

import numpy as np
import rasterio
import torch

from urban_change.model import SmallUNet, SiameseUNet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--min-valid', type=int, default=2)
    args = parser.parse_args()
    torch.set_num_threads(min(torch.get_num_threads(), 4))
    checkpoint = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
    model = SiameseUNet() if checkpoint.get('architecture', 'unet') == 'siamese' else SmallUNet()
    model.load_state_dict(checkpoint['model'])
    model.eval()
    with rasterio.open(args.before) as before, rasterio.open(args.after) as after:
        if (before.crs, before.transform, before.shape) != (after.crs, after.transform, after.shape):
            raise ValueError('Rasters must use identical grids')
        if before.count != 7 or after.count != 7:
            raise ValueError('Expected six reflectance bands and valid_count')
        a = before.read().astype('float32')
        b = after.read().astype('float32')
        good = (a[6] >= args.min_valid) & (b[6] >= args.min_valid)
        features = np.concatenate([a[:6], b[:6]], axis=0) / 10000.0
        height, width = before.shape
        probability = np.full((height, width), -1, dtype='float32')
        with torch.no_grad():
            for y in range(0, height, 64):
                for x in range(0, width, 64):
                    tile = features[:, y:y+64, x:x+64]
                    padded = np.zeros((12, 64, 64), dtype='float32')
                    padded[:, :tile.shape[1], :tile.shape[2]] = tile
                    tensor = torch.from_numpy(padded[None])
                    scores = model(tensor).sigmoid().numpy()[0]
                    result = scores[:tile.shape[1], :tile.shape[2]]
                    patch_valid = good[y:y+tile.shape[1], x:x+tile.shape[2]]
                    probability[y:y+tile.shape[1], x:x+tile.shape[2]] = np.where(patch_valid, result, -1)
        profile = before.profile.copy()
    profile.update(count=1, dtype='float32', nodata=-1, compress='deflate', tiled=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(args.out, 'w', **profile) as dst:
        dst.write(probability, 1)
        dst.set_band_description(1, checkpoint.get('architecture', 'unet') + '_probability')
        dst.update_tags(warning='Exploratory probability; no independent accuracy validation',
                        checkpoint_epoch=checkpoint['epoch'], min_valid=args.min_valid)
    print(f'Wrote {args.out}; valid pixels: {good.sum():,}; '
          f'probability >= 0.5: {np.count_nonzero(probability >= 0.5):,}')


if __name__ == '__main__':
    main()
