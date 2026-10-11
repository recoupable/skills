"""Retrieve a small set of curated experience references; Python standard library only."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', default='', help='Case-insensitive literal text match')
    parser.add_argument('--category', help='Exact category name, case-insensitive')
    parser.add_argument('--ids', nargs='+', type=int, help='Specific reference IDs')
    parser.add_argument('--limit', type=int, default=4, help='Maximum entries (1-60)')
    args = parser.parse_args()
    if not 1 <= args.limit <= 60:
        parser.error('--limit must be between 1 and 60')
    library = json.loads((Path(__file__).resolve().parent.parent / 'references' / 'library.json').read_text())
    entries = library['references']
    if args.ids:
        missing = set(args.ids) - {entry['id'] for entry in entries}
        if missing:
            parser.error(f'Unknown reference IDs: {sorted(missing)}')
        by_id = {entry['id']: entry for entry in entries}
        entries = [by_id[i] for i in dict.fromkeys(args.ids)]
    if args.category:
        entries = [e for e in entries if e['category'].casefold() == args.category.casefold()]
    if args.query:
        entries = [e for e in entries if args.query.casefold() in ' '.join(str(v) for v in e.values()).casefold()]
    print(json.dumps({'match_count': len(entries), 'returned_count': min(len(entries), args.limit),
                      'method': 'Literal lookup; listed order is not a quality ranking.',
                      'references': entries[:args.limit]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
