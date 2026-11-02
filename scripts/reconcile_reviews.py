"""Merge first-round answers and clarifications without inventing reference truth."""
import argparse
import csv
from pathlib import Path


def read_csv(path):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first', type=Path, required=True)
    parser.add_argument('--clarifications', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    first = read_csv(args.first)
    revised = {r['id']: r for r in read_csv(args.clarifications)}
    if len({r['id'] for r in first}) != len(first) or not set(revised) <= {r['id'] for r in first}:
        raise ValueError('Duplicate or unknown review IDs')

    records = []
    for row in first:
        change = revised.get(row['id'])
        raw = change['adjudicated_label'].strip().lower() if change else row['label'].strip().lower()
        normalized = {'other_changes': 'other_change'}.get(raw, raw)
        if normalized not in {'change', 'no_change', 'other_change', 'unclear'}:
            raise ValueError(f"Unexpected label for {row['id']}: {raw!r}")
        note = (change['adjudication_notes'] if change else row['notes']).strip()
        # The cards give context, but neither a binary label nor a scene-wide
        # visual impression establishes both source and destination classes.
        records.append({
            'id': row['id'], 'sampling_stratum': row['sampling_stratum'],
            'pixel_x': row['pixel_x'], 'pixel_y': row['pixel_y'],
            'longitude': row['longitude'], 'latitude': row['latitude'],
            'first_label': row['label'], 'review_label': normalized,
            'review_note': note, 'source_2018': '', 'destination_2025': '',
            'target_transition': 'unverified',
        })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f'Preserved {len(records)} reviews; all target transitions remain unverified')


if __name__ == '__main__':
    main()
