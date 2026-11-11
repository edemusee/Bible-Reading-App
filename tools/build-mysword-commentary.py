#!/usr/bin/env python3
"""Convert a MySword commentary module (*.cmt.mybible, SQLite) into this reader's format.

Download e.g. https://mysword-bible.info/download/getfile.php?file=gill.cmt.mybible.gz,
gunzip it, then run:

  python3 tools/build-mysword-commentary.py gill.cmt.mybible gill

Writes data/commentaries/<id>/<book>.txt (see build-sword-commentary.py for the format)
and prints {"bookIds": [...]}.
"""

import json
import sqlite3
import sys

from bible_data import BOOK_IDS, write_commentary_book
from commentary_html import to_html


def main():
    source, commentary_id = sys.argv[1], sys.argv[2]
    rows = sqlite3.connect(source).execute(
        'select book, chapter, fromverse, toverse, data from commentary order by book, chapter, fromverse, id'
    ).fetchall()

    books = {}
    for number, chapter, first, last, data in rows:
        if not 1 <= number <= 66:
            continue
        book_id = BOOK_IDS[number - 1]
        html = to_html(data or '', 'HTML', book_id, max(chapter, 1))
        if not html:
            continue
        book = books.setdefault(book_id, {'intro': None, 'chapters': {}})
        if chapter == 0:
            book['intro'] = f"{book['intro']}\n{html}" if book['intro'] else html
            continue
        notes = book['chapters'].setdefault(str(chapter), [])
        if notes and notes[-1][0] == first:
            notes[-1][2] += '\n' + html  # several rows for the same verse
        else:
            notes.append([first, max(first, last or first), html])

    for book_id in BOOK_IDS:
        if book_id in books:
            write_commentary_book(commentary_id, book_id, books[book_id])
    print(json.dumps({'bookIds': [book_id for book_id in BOOK_IDS if book_id in books]}))


if __name__ == '__main__':
    main()
