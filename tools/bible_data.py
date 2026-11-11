"""Shared helpers for converting Bible texts into this reader's data format.

A version's data file is data/<abbreviation>.txt holding base64(gzip(json)) of
{"books": [{"id": "gen", "chapters": [["verse 1", "verse 2", ...], ...]}, ...]}.
"""

import base64
import gzip
import json
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

# USFM book codes, in the same order as BOOK_IDS.
USFM_CODES = [
    'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA', '1KI', '2KI',
    '1CH', '2CH', 'EZR', 'NEH', 'EST', 'JOB', 'PSA', 'PRO', 'ECC', 'SNG', 'ISA', 'JER',
    'LAM', 'EZK', 'DAN', 'HOS', 'JOL', 'AMO', 'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP',
    'HAG', 'ZEC', 'MAL', 'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL',
    'EPH', 'PHP', 'COL', '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS',
    '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV',
]


def write_commentary_book(commentary_id, book_id, content):
    """content: {"intro": html | None, "chapters": {"1": [[start, end, html], ...]}}."""
    folder = ROOT / 'data' / 'commentaries' / commentary_id
    folder.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(content, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    (folder / f'{book_id}.txt').write_text(base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode('ascii'))


def write_dataset(books, abbreviation, merged=frozenset()):
    """books: {book_id: {chapter_number: {verse_number: text}}}.

    merged: (book_id, chapter, verse) keys whose text is folded into an earlier verse
    of a combined range ("1:1-4"); they stay blank but count as translated.

    Writes data/<abbreviation>.txt and returns the manifest fields
    {"bookIds": [...], "chaptersByBook": {...}} for MANIFEST in index.html.
    """
    dataset = {'books': []}
    for book_id in BOOK_IDS:
        if book_id not in books:
            continue
        chapters = []
        for number in range(1, max(books[book_id]) + 1):
            verses = books[book_id].get(number, {})
            chapters.append([verses.get(v, '') for v in range(1, max(verses, default=0) + 1)])
        # Skip books the source has only partly translated (mostly blank verses).
        filled = sum(
            1
            for c, chapter in enumerate(chapters, 1)
            for v, verse in enumerate(chapter, 1)
            if verse or (book_id, c, v) in merged
        )
        if filled < sum(map(len, chapters)) * 0.7:
            continue
        dataset['books'].append({'id': book_id, 'chapters': chapters})

    raw = json.dumps(dataset, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    (ROOT / 'data' / f'{abbreviation}.txt').write_text(base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode('ascii'))
    return {
        'bookIds': [book['id'] for book in dataset['books']],
        'chaptersByBook': {book['id']: len(book['chapters']) for book in dataset['books']},
    }


def chapter_counts():
    """{book_id: number of chapters} from the KJV data file."""
    raw = (ROOT / 'data' / 'en_kjv.txt').read_text()
    dataset = json.loads(gzip.decompress(base64.b64decode(raw)))
    return {book['id']: len(book['chapters']) for book in dataset['books']}


def write_classic(work_id, title, author, units, limit=40000):
    """Write data/classics/<id>.txt. Sections longer than `limit` characters are split at
    paragraph boundaries into "(part n of m)" sections so each page stays readable."""
    import re

    def text_length(unit):
        return len(re.sub(r'<[^>]+>|\s+', '', unit['html']))

    # A heading-only section (a chapter title or one-line summary whose text sits in the
    # sections below it) is folded into the next section instead of getting its own page.
    merged = []
    pending = ''
    for unit in units:
        if pending:
            unit = {**unit, 'html': pending + '\n' + unit['html']}
            pending = ''
        if text_length(unit) < 120:
            pending = unit['html'] if unit['html'].lstrip().startswith('<h4>') else f"<h4>{unit['title']}</h4>\n{unit['html']}"
            continue
        merged.append(unit)
    if pending:
        if merged:
            merged[-1] = {**merged[-1], 'html': merged[-1]['html'] + '\n' + pending}
        else:
            merged.append({'title': title, 'path': [], 'html': pending})
    units = merged

    split = []
    for unit in units:
        html = unit['html']
        if len(html) <= limit:
            split.append(unit)
            continue
        blocks = re.split(r'\n(?=<(?:p|h4|blockquote|ul|table)\b)', html)
        parts, current = [], ''
        for block in blocks:
            if current and len(current) + len(block) > limit:
                parts.append(current)
                current = ''
            current = f'{current}\n{block}' if current else block
        if current:
            parts.append(current)
        for index, part in enumerate(parts, 1):
            label = f" (part {index} of {len(parts)})" if len(parts) > 1 else ''
            split.append({**unit, 'title': unit['title'] + label, 'html': part})
    data = {'id': work_id, 'title': title, 'author': author, 'units': split}
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    folder = ROOT / 'data' / 'classics'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'{work_id}.txt').write_text(base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode('ascii'))
    return {'id': work_id, 'sections': len(split), 'chars': sum(len(unit['html']) for unit in split)}
