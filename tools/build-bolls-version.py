#!/usr/bin/env python3
"""Convert a bolls.life translation export into this reader's data format.

Download the export from https://bolls.life/static/translations/<CODE>.zip and unzip it,
then run:

  python3 tools/build-bolls-version.py <CODE>.json <abbreviation>

e.g. python3 tools/build-bolls-version.py HSV17.json nl_hsv

Writes data/<abbreviation>.txt and prints the manifest entry fields (bookIds,
chaptersByBook) to add to MANIFEST in index.html.
Only the 66 Protestant-canon books (bolls book numbers 1-66) are converted.
"""

import html
import json
import re
import sys
from pathlib import Path

from bible_data import BOOK_IDS, write_dataset


def clean(text):
    text = re.sub(r'<sup>.*?</sup>', '', text)   # cross-reference markers (ⓐ, ⓑ, ...)
    text = re.sub(r'<S>.*?</S>', '', text)       # Strong's numbers
    text = re.sub(r'<br\s*/?>', ' ', text)
    text = re.sub(r'<[^>]+>', '', text)          # <i>, <b>, ...
    text = html.unescape(text)
    text = re.sub(r'\*?\[\d+(?::\d+)?[ab]?(?:-\d+[ab]?)?\]', '', text)  # footnote / source-verse numbers: [1], [31:55], *[3b]
    text = re.sub(r'\{\s*\}|¶', '', text)        # empty braces, paragraph marks
    text = re.sub(r'(?<!\S)[*+](?=\w)', '', text)   # Darby's *Dieu / +Dieu name markers
    text = re.sub(r'\s+', ' ', text).strip()
    # Chinese texts space out every character; join them back up.
    return re.sub(r'(?<=[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef{}─]) (?=[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef{}─])', '', text).replace('{', '').replace('}', '')


def main():
    source, abbreviation = Path(sys.argv[1]), sys.argv[2]
    rows = json.loads(source.read_text(encoding='utf-8'))

    books = {}
    for row in rows:
        if not 1 <= row['book'] <= 66:
            continue
        chapters = books.setdefault(BOOK_IDS[row['book'] - 1], {})
        chapters.setdefault(row['chapter'], {})[row['verse']] = clean(row['text'])

    print(json.dumps(write_dataset(books, abbreviation), separators=(',', ':')))


if __name__ == '__main__':
    main()
