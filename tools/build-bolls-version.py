#!/usr/bin/env python3
"""Convert a bolls.life translation export into this reader's data format.

Download the export from https://bolls.life/static/translations/<CODE>.zip and unzip it,
then run:

  python3 tools/build-bolls-version.py <CODE>.json <abbreviation>

e.g. python3 tools/build-bolls-version.py HSV17.json nl_hsv

Writes data/<abbreviation>.txt (base64(gzip(json))) and prints the manifest entry
fields (bookIds, chaptersByBook) to add to MANIFEST in index.html.
Only the 66 Protestant-canon books (bolls book numbers 1-66) are converted.
"""

import base64
import gzip
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BOOK_IDS = [
    'gen', 'exod', 'lev', 'num', 'deut', 'josh', 'judg', 'ruth', '1sam', '2sam', '1kgs', '2kgs',
    '1chr', '2chr', 'ezra', 'neh', 'esth', 'job', 'ps', 'prov', 'eccl', 'song', 'isa', 'jer',
    'lam', 'ezek', 'dan', 'hos', 'joel', 'amos', 'obad', 'jonah', 'mic', 'nah', 'hab', 'zeph',
    'hag', 'zech', 'mal', 'matt', 'mark', 'luke', 'john', 'acts', 'rom', '1cor', '2cor', 'gal',
    'eph', 'phil', 'col', '1thess', '2thess', '1tim', '2tim', 'titus', 'phlm', 'heb', 'jas',
    '1pet', '2pet', '1john', '2john', '3john', 'jude', 'rev',
]


def clean(text):
    text = re.sub(r'<sup>.*?</sup>', '', text)   # cross-reference markers (ⓐ, ⓑ, ...)
    text = re.sub(r'<S>.*?</S>', '', text)       # Strong's numbers
    text = re.sub(r'<br\s*/?>', ' ', text)
    text = re.sub(r'<[^>]+>', '', text)          # <i>, <b>, ...
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()


def main():
    source, abbreviation = Path(sys.argv[1]), sys.argv[2]
    rows = json.loads(source.read_text(encoding='utf-8'))

    books = {}
    for row in rows:
        if not 1 <= row['book'] <= 66:
            continue
        chapters = books.setdefault(BOOK_IDS[row['book'] - 1], {})
        chapters.setdefault(row['chapter'], {})[row['verse']] = clean(row['text'])

    dataset = {'books': []}
    for book_id in BOOK_IDS:
        if book_id not in books:
            continue
        chapters = []
        for number in range(1, max(books[book_id]) + 1):
            verses = books[book_id].get(number, {})
            chapters.append([verses.get(v, '') for v in range(1, max(verses, default=0) + 1)])
        dataset['books'].append({'id': book_id, 'chapters': chapters})

    raw = json.dumps(dataset, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    (ROOT / 'data' / f'{abbreviation}.txt').write_text(base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode('ascii'))

    print(json.dumps({
        'bookIds': [b['id'] for b in dataset['books']],
        'chaptersByBook': {b['id']: len(b['chapters']) for b in dataset['books']},
    }, separators=(',', ':')))


if __name__ == '__main__':
    main()
