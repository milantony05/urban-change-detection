"""Create the manuscript's descriptive challenge-set comparison figure.

Counts are transcribed from the frozen, independently reviewed batches and
documented in docs/phase5_initial_evaluation.md and phase5_kochi_reference.md.
The figure does not represent area-wide accuracy.
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    out = Path('paper/figures/reference_comparison.svg')
    out.parent.mkdir(parents=True, exist_ok=True)
    cities = [
        ('North Bengaluru', 27, 3, [(2, 11, 1), (2, 10, 1)]),
        ('Kochi', 38, 21, [(16, 3, 5), (13, 5, 8)]),
    ]
    names = ['Spectral rule', 'Frozen U-Net']
    colors = ['#2b8a5e', '#ce633e', '#d0a328']
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.6), sharey=True)
    for ax, (city, accepted, positive, methods) in zip(axes, cities):
        x = np.arange(2)
        bottom = np.zeros(2)
        for idx, label in enumerate(('True positives', 'False positives', 'False negatives')):
            values = np.array([method[idx] for method in methods])
            ax.bar(x, values, bottom=bottom, color=colors[idx], label=label, width=.63)
            for j, value in enumerate(values):
                if value:
                    ax.text(x[j], bottom[j]+value/2, str(value), ha='center', va='center',
                            color='white' if idx < 2 else '#242424', fontsize=11, weight='bold')
            bottom += values
        ax.set_xticks(x, names)
        ax.set_title(f'{city}\n{accepted} accepted; {positive} target positives', fontsize=12)
        ax.set_ylim(0, 25)
        ax.grid(axis='y', alpha=.22)
        ax.set_axisbelow(True)
    axes[0].set_ylabel('Reviewed locations (count)')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=3, frameon=False,
               bbox_to_anchor=(.5, 1.04))
    fig.text(.5, .012, 'Prediction-stratified challenge samples; counts do not estimate citywide accuracy.',
             ha='center', fontsize=9, color='#444')
    fig.tight_layout(rect=(0, .06, 1, .91))
    fig.savefig(out, format='svg')
    print(out)


if __name__ == '__main__':
    main()
