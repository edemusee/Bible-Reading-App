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
