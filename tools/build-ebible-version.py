#!/usr/bin/env python3
"""Convert an eBible.org verse-per-line (VPL) export into this reader's data format.

Download https://ebible.org/Scriptures/<id>_vpl.zip and unzip it, then run:

  python3 tools/build-ebible-version.py <id>_vpl.txt <abbreviation>

e.g. python3 tools/build-ebible-version.py yor_vpl.txt yo_yor

Each line looks like "GEN 1:1 text" (or "GEN 1:1-2 text" for combined verses, which
are stored under the first verse). Writes data/<abbreviation>.txt and prints the
manifest entry fields. Books outside the 66-book Protestant canon are skipped.
"""

import json
import re
import sys
from pathlib import Path

from bible_data import BOOK_IDS, USFM_CODES, write_dataset

BOOK_BY_CODE = dict(zip(USFM_CODES, BOOK_IDS))
# The VPL exports use older three-letter codes for some books.
BOOK_BY_CODE.update({
    'SOL': 'song', 'EZE': 'ezek', 'JOE': 'joel', 'NAH': 'nah', 'MAR': 'mark', 'JOH': 'john',
    'PHI': 'phil', 'JAM': 'jas', '1JO': '1john', '2JO': '2john', '3JO': '3john',
})
LINE = re.compile(r'^([0-9A-Z]{3}) (\d+):(\d+)(?:-(\d+))? ?(.*)$')


def main():
    source, abbreviation = Path(sys.argv[1]), sys.argv[2]
    books = {}
    merged = set()
    for line in source.read_text(encoding='utf-8-sig').splitlines():
        match = LINE.match(line.strip())
        if not match or match.group(1) not in BOOK_BY_CODE:
            continue
        code, chapter, verse, last, text = match.groups()
        if last:
            merged.update((BOOK_BY_CODE[code], int(chapter), v) for v in range(int(verse) + 1, int(last) + 1))
        text = re.sub(r'\{[^}]*\}', '', text)    # inline footnotes: { [*...] }
        text = re.sub(r'\*ፍ\d+\*', '', text)    # Amharic footnote markers
        text = re.sub(r'(?<=\w)\*', '', text)     # footnote asterisks after words
        text = re.sub(r'\s+', ' ', text).strip()
        if text == '#':                           # placeholder for an omitted verse
            text = ''
        verses = books.setdefault(BOOK_BY_CODE[code], {}).setdefault(int(chapter), {})
        verses[int(verse)] = f'{verses[int(verse)]} {text}'.strip() if int(verse) in verses else text

    print(json.dumps(write_dataset(books, abbreviation, merged), separators=(',', ':')))


if __name__ == '__main__':
    main()
