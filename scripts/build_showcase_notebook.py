"""Build an OSCD presentation notebook with saved outputs and runnable cells."""
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def markdown(source):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': source.splitlines(True)}


def code(source, outputs=None, count=None):
    return {'cell_type': 'code', 'metadata': {}, 'execution_count': count,
            'source': source.splitlines(True), 'outputs': outputs or []}


def display_svg(path):
    return {'output_type': 'display_data', 'metadata': {},
            'data': {'image/svg+xml': path.read_text(encoding='utf-8').splitlines(True),
                     'text/plain': ['<SVG image>']}}


def main():
    data = pd.read_csv(ROOT/'paper/data/oscd_city_metrics.csv')
    first = data[data.model.isin(['change_vector','unet','original_20261102'])]
    totals = first.groupby('model')[['tp','fp','fn','tn']].sum()
    totals['precision'] = totals.tp/(totals.tp+totals.fp)
    totals['recall'] = totals.tp/(totals.tp+totals.fn)
    totals['f1'] = 2*totals.precision*totals.recall/(totals.precision+totals.recall)
    table = totals[['precision','recall','f1']].rename(index={
        'change_vector':'Spectral change vector','unet':'Early U-Net',
        'original_20261102':'Siamese U-Net'}).round(3)
    table_html = table.to_html(classes='dataframe', border=0)
    summary_source = '''import pandas as pd
from pathlib import Path
data = pd.read_csv(Path('../paper/data/oscd_city_metrics.csv'))
first = data[data.model.isin(['change_vector', 'unet', 'original_20261102'])]
totals = first.groupby('model')[['tp', 'fp', 'fn', 'tn']].sum()
totals['precision'] = totals.tp / (totals.tp + totals.fp)
totals['recall'] = totals.tp / (totals.tp + totals.fn)
totals['f1'] = 2 * totals.precision * totals.recall / (totals.precision + totals.recall)
table = totals[['precision', 'recall', 'f1']].rename(index={
    'change_vector': 'Spectral change vector', 'unet': 'Early U-Net',
    'original_20261102': 'Siamese U-Net'})
table.round(3)'''
    cells = [
        markdown('''# Urban change detection with Sentinel-2 and deep learning

**Final-year project showcase · OSCD benchmark**

We compare a spectral rule, an early-fusion U-Net and a Siamese U-Net on human-labeled urban change. The task includes roads and buildings; it does **not** specifically identify vegetation-to-built-up conversion. This notebook reads committed result tables, so you can present it without retraining.

**Presentation route:** problem → data split → model ideas → pooled results → city failures → honest conclusion.'''),
        markdown('''## 1. What is the model asked to do?

Each sample contains two aligned six-band Sentinel-2 views of the same place. The output is a binary pixel mask: change or no change. We trained on ten cities, selected checkpoints on four different cities, and measured results on ten official test cities. Entire cities, rather than random pixels, form each split to make the transfer question meaningful.

**Models:** Early fusion stacks the two dates as twelve input channels. The Siamese network encodes each date with shared weights, then compares their feature maps. A six-band root-mean-square spectral difference is the simple baseline.'''),
        markdown('''## 2. Pooled test results

Precision asks *of the pixels flagged, how many really changed?* Recall asks *of the changes, how many were found?* F1 combines those two. The table below is micro-aggregated across the evaluated test chips; it does not show whether every city performs equally well.'''),
        code(summary_source, [{'output_type':'execute_result','execution_count':1,'metadata':{},
                               'data':{'text/html':[table_html], 'text/plain':[table.to_string()]}}], 1),
        markdown('''The first Siamese run finds more true changes than early fusion but makes more false alarms. Across three seeds its mean F1 is 0.412, so the first run's 0.468 must not be presented as a stable expected score. A conservative loss setting averages F1 0.441 over three seeds, with higher precision and lower recall.'''),
        markdown('''## 3. Does it generalize to each city?

The figure shows per-city F1. The Siamese columns average three seeds for each setting. The percentage beside each city is the fraction of evaluated pixels annotated as change.'''),
        code("from IPython.display import SVG, display\ndisplay(SVG(filename='../paper/figures/oscd_city_f1.svg'))",
             [display_svg(ROOT/'paper/figures/oscd_city_f1.svg')], 2),
        markdown('''**What to point out:** Montpellier and Las Vegas have substantially stronger results than Valencia. Valencia contains very little annotated change (0.37% of evaluated pixels), but prevalence alone has not been proven to cause the failure. This is why the pooled F1 cannot stand in for performance everywhere.'''),
        markdown('''## 4. What does one prediction look like?

This fixed Abu Dhabi **validation** chip has visible change. The two model panels display probabilities, while the human mask is binary. It was selected as an illustration and does not estimate test accuracy.'''),
        code("display(SVG(filename='../paper/figures/oscd_validation_example.svg'))",
             [display_svg(ROOT/'paper/figures/oscd_validation_example.svg')], 3),
        markdown('''## 5. What can we conclude?

- The supervised models beat our simple spectral baseline in the first pooled run.
- More recall can come with many more false alarms. Reducing positive-class emphasis raises precision but lowers recall across the three paired seeds.
- Transfer varies widely by city; the method is not ready for operational mapping.
- Later model settings were explored after the first official test result was viewed. The follow-up is exploratory, and an untouched confirmatory evaluation is required for a stronger journal claim.

**To reproduce:** see the repository README, `docs/oscd_benchmark.md`, and `docs/oscd_weight_sensitivity.md`. The interactive companion dashboard is `dashboard/index.html`.''')
    ]
    for i, cell in enumerate(cells):
        cell['id'] = f'oscd-showcase-{i:02d}'
    notebook = {'cells': cells, 'metadata': {'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'},
        'language_info': {'name':'python','version':'3.12'}}, 'nbformat':4, 'nbformat_minor':5}
    out = ROOT/'notebooks/oscd_showcase.ipynb'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
