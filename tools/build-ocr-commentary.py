#!/usr/bin/env python3
"""Convert a scanned (OCR) commentary from archive.org's *_djvu.txt into this reader's format.

  python3 tools/build-ocr-commentary.py <id> <book> <style> file_djvu.txt [more files ...] [--chapters 1-5] [--merge]

Styles say how a verse comment starts:
  verse-heading  a paragraph opening "Verse 3." / "Verses 3, 4." (Hodge on Romans)
  verse-caps     a heading line "VERSE 3." / "VERSES 1, 2." (Owen, Goold edition)
  verse-number   a paragraph opening "3.  And I baptized ..." whose words match the KJV text of that
                 verse in this chapter or the next (Hodge on 1 and 2 Corinthians)
Chapters start at "CHAPTER <numeral>" lines; when the OCR mangles the numeral the count simply
continues from the previous chapter. Running page headers ("2  I. CORINTHIANS 1, 1.2."), page
numbers and line-end hyphenation are removed, and paragraphs split by page breaks are rejoined.
Text before the first chapter is skipped. --chapters keeps a range; --merge adds chapters to an
existing data/commentaries/<id>/<book>.txt without replacing chapters it already has.
"""

import base64
import gzip
import html
import json
import re
import sys

from bible_data import ROOT, write_commentary_book

ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50}
CHAPTER = re.compile(r'^\s*CHAPTER\s+(\S{1,8}?)\.?\s*$')
STYLES = {
    'verse-heading': re.compile(r'^\s*Verses?\s+([\dIl]{1,3})((?:\s*[,\-–]\s*\d{1,3})*)[.,]'),
    'verse-caps': re.compile(r'^\s*VERSES?\s+(\d{1,3})((?:\s*[,\-–]\s*\d{1,3})*)\.\s*$'),
    'verse-number': re.compile(r'^\s*(\d{1,2})\.((?:\s*\d{1,2}\.)*)\s+\S'),  # "15. 16. If the foot ..."
}
RUNNING_HEAD = re.compile(
    r'^\s*\d*\s*(?:[IV]+\.\s*)?(?:ROMANS|CORINTHIANS|HEBREWS|INTRODUCTION|AN EXPOSITION|EXPOSITION|THE EPISTLE)\b.{0,40}$'
    r'|^\s*\d{1,4}\s*$|^.{0,30}\[CHAP\..{0,20}$|^\s*CHAP\.\s*[IVXL\d]+\.?.{0,30}\d+\s*$'
)


def roman(value):
    value = value.upper().strip('.')
    if not value or any(char not in ROMAN for char in value):
        return None
    total = 0
    for index, char in enumerate(value):
        current = ROMAN[char]
        total += -current if index + 1 < len(value) and ROMAN[value[index + 1]] > current else current
    return total


def kjv_words(book_id):
    raw = (ROOT / 'data' / 'en_kjv.txt').read_text()
    book = next(b for b in json.loads(gzip.decompress(base64.b64decode(raw)))['books'] if b['id'] == book_id)
    return [[words(verse)[:10] for verse in chapter] for chapter in book['chapters']]


def words(text):
    return re.findall(r'[a-z]+', text.lower())


def quotes_verse(paragraph, kjv, chapter, verse):
    """Does the paragraph open with (an OCR'd copy of) the KJV text of chapter:verse?"""
    if not 1 <= chapter <= len(kjv) or not 1 <= verse <= len(kjv[chapter - 1]):
        return False
    expected = kjv[chapter - 1][verse - 1]
    found = set(words(re.sub(r'^\s*[\d\s.]+', '', paragraph))[:14])
    return bool(expected) and sum(1 for word in expected if word in found) >= max(3, len(expected) // 2)


def digits(value):
    return int(re.sub('[Il]', '1', value))


# Running heads that name the page's chapter and verses: "I. CORINTHIANS 7, 12.13." / "ROMANS VIII. 28."
HEAD_POSITION = re.compile(r'(?:CORINTHIANS|ROMANS|HEBREWS)\s+([IVXL\d]+)[.,]?\s*,?\s*(\d+)')


def paragraphs(text, positions):
    """Blank-line separated blocks with running heads removed and page-split paragraphs rejoined.
    positions collects (paragraph index, chapter, verse) for running heads that name them."""
    blocks, current = [], []
    for line in text.splitlines():
        if RUNNING_HEAD.match(line) and len(line.strip()) < 60:
            found = HEAD_POSITION.search(line)
            if found:
                chapter = int(found.group(1)) if found.group(1).isdigit() else roman(found.group(1))
                if chapter:
                    positions.append((len(blocks), chapter, int(found.group(2))))
            continue
        if line.strip():
            current.append(line.strip())
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    merged, merged_index = [], []
    for block in blocks:
        if merged and (merged[-1][-1].endswith('-') or not re.search(r'[.?!:;”"\')\]]$', merged[-1][-1])) \
                and not CHAPTER.match(block[0]) and not CHAPTER.match(merged[-1][-1]):
            merged[-1].extend(block)
        else:
            merged.append(block)
        merged_index.append(len(merged) - 1)
    # Re-point each running head at the paragraph that follows it after rejoining.
    positions[:] = [(merged_index[index] if index < len(merged_index) else len(merged) - 1, chapter, verse)
                    for index, chapter, verse in positions]
    out = []
    for block in merged:
        text = ''
        for line in block:
            line = re.sub(r'\s{2,}', ' ', line)
            if text.endswith('-') and line[:1].islower():
                text = text[:-1] + line
            else:
                text = f'{text} {line}' if text else line
        out.append(text)
    return out


def main():
    args = sys.argv[1:]
    chapters_range = None
    merge = '--merge' in args
    if merge:
        args.remove('--merge')
    if '--chapters' in args:
        index = args.index('--chapters')
        low, high = map(int, args[index + 1].split('-'))
        chapters_range = range(low, high + 1)
        del args[index:index + 2]
    commentary_id, book_id, style, sources = args[0], args[1], args[2], args[3:]
    verse_mark = STYLES[style]
    kjv = kjv_words(book_id) if style == 'verse-number' else None

    chapters = {}
    chapter = 0
    for source in sources:
        current = None
        verse = 0
        positions = []
        texts = paragraphs(open(source, encoding='utf-8', errors='replace').read(), positions)
        position_at = {}
        for paragraph_index, head_chapter, head_verse in positions:
            position_at.setdefault(paragraph_index, (head_chapter, head_verse))
        for index, paragraph in enumerate(texts):
            if index in position_at and chapter:
                head_chapter, head_verse = position_at[index]
                if head_chapter == chapter and head_verse - 1 > verse + 3 and kjv is None:
                    verse = head_verse - 1  # resynchronise after a misread verse number
            heading = CHAPTER.match(paragraph)
            if heading and len(paragraph) < 30:
                # Headings come in order; when the OCR garbles the numeral ("CHAPTER Yin.") just count.
                # A heading that repeats the current chapter continues it (a new volume).
                parsed = roman(heading.group(1))
                chapter = parsed if parsed in (chapter, chapter + 1) else chapter + 1
                verse = 0
                current = [0, 0, []]
                chapters.setdefault(chapter, []).append(current)
                continue
            if not chapter:
                continue
            match = verse_mark.match(paragraph)
            if match:
                first = digits(match.group(1))
                rest = [int(n) for n in re.findall(r'\d+', match.group(2) or '')] if len(match.groups()) > 1 else []
                if first == 1 and verse >= 6 and style != 'verse-number':
                    chapter, verse = chapter + 1, 0  # verse 1 again: a chapter whose heading the OCR lost
                if kjv is not None:
                    if quotes_verse(paragraph, kjv, chapter + 1, first) and not quotes_verse(paragraph, kjv, chapter, first):
                        chapter, verse = chapter + 1, 0  # the CHAPTER heading was lost in the OCR
                    if not quotes_verse(paragraph, kjv, chapter, first) or first <= verse:
                        match = None  # a numbered point in the comment, not a verse
                elif first < verse:
                    match = None
            if match:
                verse = first
                current = [first, max([first] + [n for n in rest if n >= first]), []]
                chapters.setdefault(chapter, []).append(current)
                if style == 'verse-caps':
                    continue
            if current is not None:
                current[2].append(f'<p>{html.escape(paragraph, quote=False)}</p>')

    content = {'intro': None, 'chapters': {}}
    path = ROOT / 'data' / 'commentaries' / commentary_id / f'{book_id}.txt'
    if merge and path.exists():
        content = json.loads(gzip.decompress(base64.b64decode(path.read_text())))
    for number, notes in sorted(chapters.items()):
        if chapters_range and number not in chapters_range or str(number) in content['chapters']:
            continue
        kept = [[first, last, '\n'.join(blocks)] for first, last, blocks in notes if blocks]
        if kept:
            content['chapters'][str(number)] = kept
    content['chapters'] = dict(sorted(content['chapters'].items(), key=lambda item: int(item[0])))
    write_commentary_book(commentary_id, book_id, content)
    print(json.dumps({'bookIds': [book_id]}))


if __name__ == '__main__':
    main()
