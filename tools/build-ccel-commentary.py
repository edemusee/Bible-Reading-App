#!/usr/bin/env python3
"""Convert a CCEL ThML commentary into this reader's format, using its <scripCom> verse anchors.

Download the ThML from ccel.org (e.g. https://ccel.org/ccel/h/hodge/ephesians.xml), then run:

  python3 tools/build-ccel-commentary.py hodge ephesians.xml [more.xml ...]

Each comment runs from one <scripCom parsed="|Eph|1|2|0|0"/> anchor to the next anchor
(or the end of the enclosing <div1>), and is keyed to that verse (verse 0 = chapter
introduction). Several files can be combined into one commentary id. Writes
data/commentaries/<id>/<book>.txt and prints {"bookIds": [...]}.
"""

import json
import re
import sys

from bible_data import BOOK_IDS, write_commentary_book
from commentary_html import book_from_name, to_html

ANCHOR = re.compile(r'<scripCom\b[^>]*\bparsed="\|([^|]+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)"[^>]*/>')


def main():
    commentary_id, sources = sys.argv[1], sys.argv[2:]
    books = {}
    for source in sources:
        xml = open(source, encoding='utf-8').read()
        anchors = list(ANCHOR.finditer(xml))
        for index, anchor in enumerate(anchors):
            name, chapter, verse, end_chapter, end_verse = anchor.groups()
            book_id = book_from_name(name)
            if not book_id:
                continue
            stop = anchors[index + 1].start() if index + 1 < len(anchors) else len(xml)
            div_end = xml.find('</div1>', anchor.end())
            if div_end != -1:
                stop = min(stop, div_end)
            html = to_html(xml[anchor.end():stop], 'ThML', book_id, int(chapter))
            if not html:
                continue
            first = int(verse)
            last = int(end_verse) if int(end_chapter) == int(chapter) and int(end_verse) > first else first
            notes = books.setdefault(book_id, {'intro': None, 'chapters': {}})['chapters'].setdefault(chapter, [])
            if notes and notes[-1][0] == first:
                notes[-1][2] += '\n' + html
            else:
                notes.append([first, last, html])

    for book_id, content in books.items():
        for notes in content['chapters'].values():
            notes.sort(key=lambda note: note[0])
        write_commentary_book(commentary_id, book_id, content)
    print(json.dumps({'bookIds': [book_id for book_id in BOOK_IDS if book_id in books]}))


if __name__ == '__main__':
    main()
