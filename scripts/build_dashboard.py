"""Bundle committed OSCD metrics and illustration into an offline HTML dashboard."""
import base64
import csv
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    template = (root/'dashboard/template.html').read_text(encoding='utf-8')
    with (root/'paper/data/oscd_city_metrics.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    illustration = (root/'paper/figures/oscd_validation_example.svg').read_bytes()
    src = 'data:image/svg+xml;base64,'+base64.b64encode(illustration).decode('ascii')
    page = template.replace('/*METRICS*/[]', json.dumps(rows, separators=(',', ':')))
    page = page.replace('/*EXAMPLE*/', src)
    out = root/'dashboard/index.html'
    out.write_text(page, encoding='utf-8')
    print(f'{out}: {len(rows)} city/model rows; open in any browser')


if __name__ == '__main__':
    main()
