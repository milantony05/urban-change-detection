"""Compact U-Net for paired six-band Sentinel-2 composites."""
import torch
from torch import nn


class ConvBlock(nn.Module):
    def __init__(self, incoming, outgoing):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(incoming, outgoing, 3, padding=1),
            nn.BatchNorm2d(outgoing), nn.ReLU(inplace=True),
            nn.Conv2d(outgoing, outgoing, 3, padding=1),
            nn.BatchNorm2d(outgoing), nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.layers(x)


class SmallUNet(nn.Module):
    def __init__(self, channels=12, width=16):
        super().__init__()
        self.enc1 = ConvBlock(channels, width)
        self.enc2 = ConvBlock(width, width * 2)
        self.middle = ConvBlock(width * 2, width * 4)
        self.pool = nn.MaxPool2d(2)
        self.up2 = nn.ConvTranspose2d(width * 4, width * 2, 2, stride=2)
        self.dec2 = ConvBlock(width * 4, width * 2)
        self.up1 = nn.ConvTranspose2d(width * 2, width, 2, stride=2)
        self.dec1 = ConvBlock(width * 2, width)
        self.head = nn.Conv2d(width, 1, 1)

    def forward(self, x):
        a = self.enc1(x)
        b = self.enc2(self.pool(a))
        middle = self.middle(self.pool(b))
        c = self.dec2(torch.cat([self.up2(middle), b], dim=1))
        return self.head(self.dec1(torch.cat([self.up1(c), a], dim=1))).squeeze(1)


class SiameseUNet(nn.Module):
    """Shared two-date encoder with index, difference and context features."""
    def __init__(self, width=16):
        super().__init__()
        self.enc1 = ConvBlock(8, width)
        self.enc2 = ConvBlock(width, width * 2)
        self.middle = ConvBlock(width * 2, width * 4)
        self.pool = nn.MaxPool2d(2)
        self.up2 = nn.ConvTranspose2d(width * 12, width * 2, 2, stride=2)
        self.dec2 = ConvBlock(width * 8, width * 2)
        self.up1 = nn.ConvTranspose2d(width * 2, width, 2, stride=2)
        self.dec1 = ConvBlock(width * 4, width)
        self.head = nn.Conv2d(width, 1, 1)

    @staticmethod
    def date_features(bands):
        # Input order: blue, green, red, NIR, SWIR1, SWIR2.
        ndvi = (bands[:, 3:4] - bands[:, 2:3]) / (bands[:, 3:4] + bands[:, 2:3] + 1e-4)
        ndbi = (bands[:, 4:5] - bands[:, 3:4]) / (bands[:, 4:5] + bands[:, 3:4] + 1e-4)
        return torch.cat((bands, ndvi, ndbi), dim=1)

    def encode(self, bands):
        a = self.enc1(self.date_features(bands))
        b = self.enc2(self.pool(a))
        c = self.middle(self.pool(b))
        return a, b, c

    def forward(self, x):
        a0, b0, c0 = self.encode(x[:, :6])
        a1, b1, c1 = self.encode(x[:, 6:])
        fuse = lambda left, right: torch.cat((left, right, torch.abs(right-left)), dim=1)
        c = self.dec2(torch.cat((self.up2(fuse(c0, c1)), fuse(b0, b1)), dim=1))
        return self.head(self.dec1(torch.cat((self.up1(c), fuse(a0, a1)), dim=1))).squeeze(1)
