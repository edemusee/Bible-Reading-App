#!/usr/bin/env python3
"""Convert 17th-century commentaries transcribed by the Text Creation Partnership (EEBO-TCP,
CC0, https://github.com/textcreationpartnership) into this reader's format.

  python3 tools/build-tcp-commentary.py <id> <book> A41670.xml [more files of the same work ...]

e.g. python3 tools/build-tcp-commentary.py gouge heb A41670.xml

The TEI is read as a stream of blocks (headings, paragraphs, quoted text). A block that starts
with a chapter marker ("CHAP. XI.", "PSAL. II.", "JOB, Chap. 4.") or a verse marker
("Vers. 7, 8.", "VERSE II.", "IOB 1.1, 2.") starts a new note; a run of markers with only
quoted Scripture between them becomes one verse range. Front matter, errata, tables and indexes
are skipped, the long s is normalised and marginal notes are dropped.
Writes data/commentaries/<id>/<book>.txt and prints {"bookIds": [...]}.
"""

import html
import json
import re
import sys
import xml.etree.ElementTree as ET

from bible_data import chapter_counts, write_commentary_book
from tcp_tei import clean, inline_html, strip_ns
from commentary_html import book_from_name

SKIP_DIVS = {
    'title_page', 'to_the_reader', 'to_the_Christian_reader', 'dedication', 'imprimatur', 'license', 'errata',
    'table_of_contents', 'index', 'frontispiece', 'contents', 'table', 'preface', 'commendatory_verses',
}
SKIP_HEAD = re.compile(r'\b(TABLE|INDEX|CONTENTS|ERRATA|Errata|OMISSIONS|Omissions)\b')
CHAPTER_DIVS = {'chapter', 'Psalm', 'psalm', 'exegesis_of_chapter'}
ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
ORDINALS = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
            'eleventh', 'twelfth', 'thirteenth']

NUMBER = r'(\d+|[IVXLC]+\b)'
VERSE_WORD = r'(?:Ver(?:s(?:es?)?|se)?|VER(?:S(?:ES?)?|SE)?)\.?'
CHAPTER_MARK = re.compile(rf'^\W*(?:[A-Za-z]+\W+){{0,2}}?(?:CHAP(?:TER)?|Chap(?:ter)?)\.?\s*{NUMBER}', re.I)
PSALM_MARK = re.compile(rf'^\W*PSAL(?:M)?\.?\s*{NUMBER}', re.I)
VERSE_MARK = re.compile(rf'^\W*(?:[A-Za-z]+\W+)?(?:(?:CHAP|Chap)\w*\.?\s*{NUMBER}\W+)?{VERSE_WORD}\s*{NUMBER}((?:\s*(?:[,&]|and|to|-|–)\s*(?:\d+|[IVXLC]+\b))*)')
# "HEBREWS 1. Vers. 1, 2, 3." / "IOB 1.1, 2." / "Hosea 1. 6. 7." (book name, chapter, verses)
BOOK_CV = re.compile(rf'^\W*((?:[1-3]\s?)?[A-Za-z]+)\W*{NUMBER}\s*[.:,]\s*(?:{VERSE_WORD}\s*)?(\d+)((?:\s*[,&.]\s*\d+)*)')
LEADING_WORD = re.compile(r'^\W*((?:[1-3]\s?)?[A-Za-z]+)')
MARKER_WORDS = {'chap', 'chapter', 'ver', 'vers', 'verse', 'verses', 'psal', 'psalm'}
BARE_VERSE = re.compile(r'^\W*(\d{1,3})\.\s*$')


def number(value):
    value = value.strip()
    if value.isdigit():
        return int(value)
    total = 0
    for index, char in enumerate(value.upper()):
        current = ROMAN.get(char, 0)
        total += -current if index + 1 < len(value) and ROMAN.get(value[index + 1].upper(), 0) > current else current
    return total


def belongs_to(word, collector):
    return bool(own_book(word, collector.book_id)) and bool(BOOK_CV.match(word + ' 1.1'))


def own_book(word, book_id):
    """Is a leading word this commentary's own book (True), another book (False), or neither (None)?"""
    key = word.lower().replace(' ', '')
    if key in MARKER_WORDS:
        return None
    found = book_from_name('job' if key == 'iob' else key)
    return None if found is None else found == book_id


class Collector:
    def __init__(self, book_id):
        self.book_id = book_id
        self.max_chapter = chapter_counts()[book_id]
        self.chapter = None
        self.notes = {}           # chapter -> list of [start, end, [html blocks], only_quotes]
        self.current = None

    def start_chapter(self, chapter):
        if chapter and chapter <= self.max_chapter and chapter != self.chapter:
            self.chapter = chapter
            self.current = None

    def start_verse(self, first, last):
        if not self.chapter:
            return
        notes = self.notes.setdefault(self.chapter, [])
        if self.current is not None and self.current[3] and first <= self.current[1] + 1 and first >= self.current[0]:
            self.current[1] = max(self.current[1], last)   # quoted verses run on into one range
            return
        self.current = [first, last, [], True]
        notes.append(self.current)

    def add(self, block, quoted):
        if not self.chapter:
            return
        if self.current is None:
            self.current = [0, 0, [], quoted]
            self.notes.setdefault(self.chapter, []).append(self.current)
        self.current[2].append(block)
        if not quoted:
            self.current[3] = False


def walk(element, collector, quoted=False):
    tag = element.tag
    if tag == 'div':
        kind = element.get('type') or ''
        head = element.find('head')
        head_text = clean(re.sub(r'<[^>]+>', '', inline_html(head))) if head is not None else ''
        if kind in SKIP_DIVS or SKIP_HEAD.search(head_text[:60]):
            return
        if kind in CHAPTER_DIVS:
            n = element.get('n')
            chapter = int(n) if n and n.isdigit() else None
            if not chapter:
                match = CHAPTER_MARK.search(head_text) or (PSALM_MARK.search(head_text) if collector.book_id == 'ps' else None)
                chapter = number(match.group(1)) if match else None
            if not chapter:
                ordinal = re.search(r'\b(' + '|'.join(ORDINALS) + r')\s+chapter', head_text, re.I)
                chapter = ORDINALS.index(ordinal.group(1).lower()) + 1 if ordinal else None
            collector.start_chapter(chapter)
    if tag in ('note', 'pb', 'fw', 'figure', 'gap', 'trailer'):
        return
    if tag in ('head', 'p', 'l', 'bibl', 'item', 'argument', 'label', 'lg') and tag != 'lg':
        if tag == 'argument':
            for child in element:
                walk(child, collector, quoted)
            return
        block = clean(inline_html(element))
        text = re.sub(r'<[^>]+>', '', block)
        if not text:
            return
        if marker(text, collector):
            if tag in ('head', 'bibl', 'label') and len(text) < 80:
                return
        tag_out = 'h4' if tag == 'head' else 'p'
        collector.add(f'<{tag_out}>{block}</{tag_out}>', quoted or tag == 'bibl')
        return
    for child in element:
        walk(child, collector, quoted or tag in ('q', 'epigraph', 'quote'))


def marker(text, collector):
    """Apply a chapter/verse marker at the start of a block; return True if there was one."""
    found = False
    if text.lstrip()[:1] in '([':
        return False  # "(Chap. 12.4.)" is a citation, not a heading
    leading = LEADING_WORD.match(text)
    if len(text) > 120 and leading and leading.group(1).lower() not in MARKER_WORDS and not belongs_to(leading.group(1), collector):
        return False  # in running prose only a marker that opens the paragraph counts
    belongs = own_book(leading.group(1), collector.book_id) if leading else None
    if belongs is False:
        return False  # a cross reference to another book, not a heading of this one
    book_cv = BOOK_CV.search(text[:60]) if belongs else None
    if book_cv and number(book_cv.group(2)) <= collector.max_chapter:
        collector.start_chapter(number(book_cv.group(2)))
        verses = [int(book_cv.group(3))] + [int(n) for n in re.findall(r'\d+', book_cv.group(4) or '')]
        verses = [v for v in verses if v >= verses[0]]
        collector.start_verse(verses[0], max(verses))
        return True
    chapter = CHAPTER_MARK.search(text[:40]) or (PSALM_MARK.search(text[:40]) if collector.book_id == 'ps' else None)
    verse = VERSE_MARK.search(text[:80])
    if chapter and (not verse or chapter.start() <= verse.start()):
        collector.start_chapter(number(chapter.group(1)))
        found = True
    if verse:
        if verse.group(1):
            collector.start_chapter(number(verse.group(1)))
        first = number(verse.group(2))
        rest = [number(n) for n in re.findall(r'\d+|[IVXLC]+\b', verse.group(3) or '')]
        if 0 < first <= 176:
            collector.start_verse(first, max([first] + [n for n in rest if first <= n <= 176]))
            found = True
    elif not found:
        bare = BARE_VERSE.match(text)
        if bare and collector.current is not None and int(bare.group(1)) <= 176:
            collector.start_verse(int(bare.group(1)), int(bare.group(1)))
            found = True
    return found


def main():
    commentary_id, book_id, sources = sys.argv[1], sys.argv[2], sys.argv[3:]
    collector = Collector(book_id)
    for source in sources:
        tree = ET.parse(source)
        strip_ns(tree)
        body = tree.getroot().find('.//text')
        collector.chapter = None
        collector.current = None
        walk(body, collector)

    chapters = {}
    for chapter, notes in sorted(collector.notes.items()):
        merged = []
        for first, last, blocks, _ in notes:
            text = '\n'.join(blocks)
            if not re.sub(r'<[^>]+>|\s', '', text):
                continue
            if merged and merged[-1][0] == first:
                merged[-1][1] = max(merged[-1][1], last)
                merged[-1][2] += '\n' + text
            else:
                merged.append([first, last, text])
        merged.sort(key=lambda note: note[0])
        if merged:
            chapters[str(chapter)] = merged
    write_commentary_book(commentary_id, book_id, {'intro': None, 'chapters': chapters})
    print(json.dumps({'bookIds': [book_id]}))


if __name__ == '__main__':
    main()
