"""Plot OSCD per-city F1 from report_oscd_city CSV."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, default=Path('outputs/oscd_city_metrics.csv'))
    p.add_argument('--out', type=Path, default=Path('paper/figures/oscd_city_f1.svg'))
    args = p.parse_args()
    with args.input.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    cities = sorted({r['city'] for r in rows})
    groups = [('change_vector','Change vector'),('unet','Early U-Net'),
              ('original_','Siamese original'),('conservative_','Siamese conservative')]
    values = np.zeros((len(cities), len(groups)))
    prevalence = []
    for i, city in enumerate(cities):
        subset = [r for r in rows if r['city']==city]
        prevalence.append(float(subset[0]['change_fraction'])*100)
        for j, (key, _) in enumerate(groups):
            matches = [float(r['f1']) for r in subset if r['model']==key or r['model'].startswith(key)]
            if not matches:
                raise ValueError(f'Missing {key} for {city}')
            values[i,j] = np.mean(matches)
    fig, ax = plt.subplots(figsize=(9, 6.2))
    im = ax.imshow(values, vmin=0, vmax=.75, cmap='YlGnBu', aspect='auto')
    ax.set_xticks(range(len(groups)), [g[1] for g in groups], rotation=18, ha='right')
    ax.set_yticks(range(len(cities)), [f'{c}  ({p:.1f}% change)' for c,p in zip(cities,prevalence)])
    for i in range(len(cities)):
        for j in range(len(groups)):
            ax.text(j, i, f'{values[i,j]:.2f}', ha='center', va='center',
                    color='white' if values[i,j] > .42 else '#17232c', fontsize=9)
    ax.set_title('OSCD held-out city F1', loc='left', weight='bold')
    fig.colorbar(im, ax=ax, label='F1', fraction=.036, pad=.03)
    fig.text(.5, .015, 'Siamese cells show means across 3 seeds; change fraction is the share of annotated pixels.',
             ha='center', fontsize=9, color='#444')
    fig.tight_layout(rect=(0,.04,1,1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out)
    print(args.out)


if __name__=='__main__':
    main()
