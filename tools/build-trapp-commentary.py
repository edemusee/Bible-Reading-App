#!/usr/bin/env python3
"""Convert John Trapp's commentary (archive.org item JohnTrappsBibleCommentaries, one EPUB per
book named "JTrapp NN Book - John Trapp.epub") into this reader's format.

  python3 tools/build-trapp-commentary.py <folder with the 66 EPUBs> trapp

Each book's XHTML has "Chapter N" <h2> headings and "Ver. N." paragraphs; text before the
first heading is the book introduction. References like "#Jud 12:8" become links.
Writes data/commentaries/<id>/<book>.txt and prints {"bookIds": [...]}.
"""

import json
import re
import sys
import zipfile
from pathlib import Path

from bible_data import BOOK_IDS, write_commentary_book
from commentary_html import to_html

CHAPTER = re.compile(r'<h2\b[^>]*>\s*Chapter\s*(\d+)\s*</h2>')
# "Ver. 3." / "Ver. 3, 4." at the start of a paragraph or text run (not "see ver. 3" in prose).
VERSE = re.compile(r'(?<=>)\s*Ver\.\s*(\d[\dIl]*|[Il][\dIl]*)((?:\s*[,\-–]\s*[\dIl]+)*)\.?')  # OCR: I7 = 17


def book_html(epub_path):
    with zipfile.ZipFile(epub_path) as epub:
        names = sorted(name for name in epub.namelist() if re.search(r'index_split_\d+\.x?html$', name))
        bodies = []
        for name in names:
            page = epub.read(name).decode('utf-8')
            match = re.search(r'<body[^>]*>(.*)</body>', page, re.S)
            bodies.append(match.group(1) if match else '')
    html = '\n'.join(bodies)
    html = re.sub(r'<h1\b.*?</h1>', '', html, flags=re.S)
    # Class names differ from volume to volume, so drop the spans and work from the text.
    html = re.sub(r'</?span\b[^>]*>', '', html)
    html = re.sub(r'<p\b[^>]*>\s*</p>', '', html)
    # "{#Jud 12:8}" / "#Mt 1:5" -> references the converter links.
    ref = r'#((?:[1-3]\s?)?[A-Z][a-z]*\.?\s?\d+:\d+(?:\s*[-,]\s*\d+(?::\d+)?)*)'
    html = re.sub(r'\{\s*' + ref + r'\s*\}', r'(<scripRef>\1</scripRef>)', html)
    html = re.sub(ref, r'<scripRef>\1</scripRef>', html)
    # Trapp quotes the words he comments on and closes them with "]": bold the quotation.
    return re.sub(r'(<p\b[^>]*>\s*(?:Ver\.\s*[\dIl]+(?:\s*[,\-–]\s*[\dIl]+)*\.?\s*)?)([^<\]]{1,250}?)\]', r'\1<b>\2</b>', html)


def main():
    folder, commentary_id = Path(sys.argv[1]), sys.argv[2]
    book_ids = []
    for epub_path in sorted(folder.glob('JTrapp *.epub')):
        number = int(re.match(r'JTrapp (\d+)', epub_path.name).group(1))
        book_id = BOOK_IDS[number - 1]
        html = book_html(epub_path)
        chapters = list(CHAPTER.finditer(html))
        intro = to_html(html[:chapters[0].start()] if chapters else html, 'HTML', book_id, 1) or None
        content = {'intro': intro, 'chapters': {}}
        for index, chapter in enumerate(chapters):
            number_ch = int(chapter.group(1))
            body = html[chapter.end():chapters[index + 1].start() if index + 1 < len(chapters) else len(html)]
            verses = list(VERSE.finditer(body))
            notes = []
            lead = to_html(body[:verses[0].start()] if verses else body, 'HTML', book_id, number_ch)
            if lead:
                notes.append([0, 0, lead])
            for position, verse in enumerate(verses):
                digits = lambda value: int(re.sub('[Il]', '1', value))
                first = digits(verse.group(1))
                numbers = [digits(n) for n in re.findall(r'[\dIl]+', verse.group(2) or '')]
                last = max([first] + [n for n in numbers if n >= first])
                end = verses[position + 1].start() if position + 1 < len(verses) else len(body)
                note = to_html(body[verse.end():end], 'HTML', book_id, number_ch)
                if note:
                    notes.append([first, last, note])
            if notes:
                content['chapters'][str(number_ch)] = notes
        if content['chapters'] or intro:
            write_commentary_book(commentary_id, book_id, content)
            book_ids.append(book_id)
    print(json.dumps({'bookIds': [book_id for book_id in BOOK_IDS if book_id in book_ids]}))


if __name__ == '__main__':
    main()
