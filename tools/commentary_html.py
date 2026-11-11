"""Turn commentary markup (SWORD OSIS / ThML, or plain HTML) into the small HTML subset the
reader renders: <p>, <h4>, <i>, <b>, <sup>, <u>, <span class="sc">, <span class="c-note">,
<blockquote>, <ul>/<li>, <table>/<tr>/<td>, <br>, and <a class="cref" data-ref="book.ch.v">
links for Scripture references."""

import html
import re
from html.parser import HTMLParser

from bible_data import BOOK_IDS

# Abbreviations used by ThML modules and old commentaries, plus full names; keys are
# lowercased with spaces and dots removed.
_NAMES = {
    'gen': ['ge', 'gn', 'genesis'], 'exod': ['ex', 'exo', 'exod', 'exodus'], 'lev': ['le', 'lev', 'lv', 'leviticus'],
    'num': ['nu', 'num', 'nm', 'numbers'], 'deut': ['de', 'deu', 'deut', 'dt', 'deuteronomy'],
    'josh': ['jos', 'josh', 'joshua'], 'judg': ['jud', 'jdg', 'judg', 'judges'], 'ruth': ['ru', 'rut', 'ruth'],
    '1sam': ['1sa', '1sam', '1samuel'], '2sam': ['2sa', '2sam', '2samuel'], '1kgs': ['1ki', '1kgs', '1kings', '1kin'],
    '2kgs': ['2ki', '2kgs', '2kings', '2kin'], '1chr': ['1ch', '1chr', '1chron', '1chronicles'],
    '2chr': ['2ch', '2chr', '2chron', '2chronicles'], 'ezra': ['ezr', 'ezra'], 'neh': ['ne', 'neh', 'nehemiah'],
    'esth': ['es', 'est', 'esth', 'esther'], 'job': ['job', 'jb'], 'ps': ['ps', 'psa', 'psalm', 'psalms', 'pss'],
    'prov': ['pr', 'pro', 'prov', 'proverbs'], 'eccl': ['ec', 'ecc', 'eccl', 'eccles', 'ecclesiastes'],
    'song': ['so', 'song', 'sos', 'canticles', 'cant', 'songofsolomon', 'songofsongs'],
    'isa': ['isa', 'is', 'isaiah'], 'jer': ['jer', 'je', 'jeremiah'], 'lam': ['la', 'lam', 'lamentations'],
    'ezek': ['eze', 'ezek', 'ezk', 'ezekiel'], 'dan': ['da', 'dan', 'daniel'], 'hos': ['ho', 'hos', 'hosea'],
    'joel': ['joe', 'joel'], 'amos': ['am', 'amos'], 'obad': ['ob', 'oba', 'obad', 'obadiah'],
    'jonah': ['jon', 'jonah'], 'mic': ['mic', 'micah'], 'nah': ['na', 'nah', 'nahum'], 'hab': ['hab', 'habakkuk'],
    'zeph': ['zep', 'zeph', 'zephaniah'], 'hag': ['hag', 'haggai'], 'zech': ['zec', 'zech', 'zechariah'],
    'mal': ['mal', 'malachi'], 'matt': ['mt', 'mat', 'matt', 'matthew'], 'mark': ['mr', 'mk', 'mar', 'mark'],
    'luke': ['lu', 'lk', 'luk', 'luke'], 'john': ['joh', 'jn', 'jhn', 'john'], 'acts': ['ac', 'act', 'acts'],
    'rom': ['ro', 'rom', 'romans'], '1cor': ['1co', '1cor', '1corinthians'], '2cor': ['2co', '2cor', '2corinthians'],
    'gal': ['ga', 'gal', 'galatians'], 'eph': ['eph', 'ephes', 'ephesians'], 'phil': ['php', 'phil', 'philippians'],
    'col': ['col', 'colossians'], '1thess': ['1th', '1thess', '1thes', '1thessalonians'],
    '2thess': ['2th', '2thess', '2thes', '2thessalonians'], '1tim': ['1ti', '1tim', '1timothy'],
    '2tim': ['2ti', '2tim', '2timothy'], 'titus': ['tit', 'titus'], 'phlm': ['phm', 'phlm', 'philem', 'philemon'],
    'heb': ['heb', 'hebrews'], 'jas': ['jas', 'jam', 'james'], '1pet': ['1pe', '1pet', '1peter'],
    '2pet': ['2pe', '2pet', '2peter'], '1john': ['1jo', '1jn', '1john'], '2john': ['2jo', '2jn', '2john'],
    '3john': ['3jo', '3jn', '3john'], 'jude': ['jude', 'jud.'], 'rev': ['re', 'rev', 'rv', 'revelation', 'apoc'],
}
BOOK_BY_NAME = {}
for _book, _names in _NAMES.items():
    for _name in _names:
        BOOK_BY_NAME.setdefault(_name, _book)
for _numeral, _digit in (('i', '1'), ('ii', '2'), ('iii', '3')):
    for _name, _book in list(BOOK_BY_NAME.items()):
        if _name[0] == _digit:
            BOOK_BY_NAME.setdefault(_numeral + _name[1:], _book)
OSIS_BOOKS = {book: book for book in BOOK_IDS}


def book_from_name(name):
    key = re.sub(r'[\s.]', '', name.lower())
    return BOOK_BY_NAME.get(key)


def ref_link(book, chapter, verse, text):
    return f'<a class="cref" data-ref="{book}.{chapter}.{verse}">{text}</a>'


_BOOK_NAME = r'(?:[1-3]|I{1,3})\s?[A-Z][a-z]+\.?|[A-Z][a-z]+\.?'
_REF_TOKEN = re.compile(rf'(?:(?P<book>{_BOOK_NAME})\s*)?(?P<a>\d+)(?:\s*[:.]\s*(?P<b>\d+))?(?P<rest>(?:\s*[-–]\s*\d+(?:[:.]\d+)?)?)')


def link_reference_list(text, book, chapter, explicit_only=False):
    """Link a list of references such as "Job 26:7; Isa 45:18" or "15; Mt 9:13; 1:14,18".
    Bare numbers resolve against the running book/chapter context."""
    out, pos, after_comma = [], 0, False
    for match in _REF_TOKEN.finditer(text):
        name, first, second = match.group('book'), match.group('a'), match.group('b')
        new_book = book_from_name(name) if name else None
        if name and not new_book:
            continue
        if explicit_only and not new_book:
            continue
        between = text[pos:match.start()]
        if new_book:
            book = new_book
        if second:
            chapter, verse = int(first), int(second)
        elif new_book:
            chapter, verse = int(first), 1
        elif after_comma or not explicit_only:
            verse = int(first)
        out.append(html.escape(between, quote=False))
        out.append(ref_link(book, chapter, verse, html.escape(match.group(0), quote=False)))
        pos = match.end()
        after_comma = text[pos:pos + 2].strip().startswith(',')
    out.append(html.escape(text[pos:], quote=False))
    return ''.join(out)


def link_osis_ref(osis_ref):
    """'Gen.1.1' / 'Gen.1.1-Gen.1.5' / 'Matt.5' -> (book, chapter, verse) or None."""
    first = osis_ref.split('-')[0].split(':')[-1]
    parts = first.split('.')
    book = OSIS_BOOKS.get(parts[0].lower())
    if not book:
        return None
    chapter = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
    verse = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
    return book, chapter, verse


INLINE = {'i': 'i', 'em': 'i', 'b': 'b', 'strong': 'b', 'u': 'u', 'sup': 'sup', 'sub': 'sub'}
HI = {'italic': 'i', 'bold': 'b', 'super': 'sup', 'underline': 'u', 'emphasis': 'i'}
BLOCK_BREAK = {'div', 'p', 'lg', 'chapter', 'verse'}
DROP_WITH_CONTENT = {'milestone', 'figure', 'img', 'sync', 'rdg', 'w:sync', 'see'}


class _Converter(HTMLParser):
    def __init__(self, book, chapter):
        super().__init__(convert_charrefs=True)
        self.book, self.chapter = book, chapter
        self.blocks = []      # finished block-level html strings
        self.inline = []      # current paragraph pieces
        self.stack = []       # open output tags for the current paragraph
        self.ref = None       # collecting a <reference>/<scripRef>
        self.title = None     # collecting a <title>
        self.skip = 0
        self.table = None

    # ---- helpers
    def _emit(self, piece):
        if self.ref is not None:
            self.ref['text'].append(piece)
        elif self.title is not None:
            self.title.append(piece)
        elif self.table is not None and self.table['cell'] is not None:
            self.table['cell'].append(piece)
        else:
            self.inline.append(piece)

    def _flush(self):
        while self.stack:
            self.inline.append(f'</{self.stack.pop()}>')
        text = ''.join(self.inline).strip()
        self.inline = []
        if re.sub(r'<[^>]+>|\s', '', text):
            self.blocks.append(f'<p>{text}</p>')

    def _open(self, tag, attrs=''):
        self._emit(f'<{tag}{attrs}>')
        if self.ref is None and self.title is None and self.table is None:
            self.stack.append(tag.split()[0])

    def _close(self, tag):
        if self.ref is None and self.title is None and self.table is None:
            if tag in self.stack:
                while self.stack:
                    open_tag = self.stack.pop()
                    self.inline.append(f'</{open_tag}>')
                    if open_tag == tag:
                        break
            return
        self._emit(f'</{tag}>')

    # ---- parser callbacks
    def handle_starttag(self, tag, attrs):
        self._start(tag, dict(attrs), closed=False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, dict(attrs), closed=True)

    def _start(self, tag, attrs, closed):
        if self.skip:
            if not closed:
                self.skip += 1
            return
        kind = (attrs.get('type') or '').lower()
        if tag in DROP_WITH_CONTENT or (tag == 'x-title' and kind == 'x-ms'):
            if not closed and tag not in ('img',):
                self.skip = 1
            return
        if tag in BLOCK_BREAK or (tag == 'br' and self.ref is None and self.table is None and self._double_break()):
            self._flush()
        elif tag in ('br', 'lb'):
            self._emit('<br>')
        elif tag == 'l':
            pass
        elif tag == 'x-title' and not closed:
            self._flush()
            self.title = []
        elif tag in ('reference', 'scripref') and not closed:
            self.ref = {'attrs': attrs, 'text': []}
        elif tag == 'a' and not closed and re.match(r'#[bc]\d+\.\d+', attrs.get('href') or ''):
            self.ref = {'attrs': {'mybible': attrs['href']}, 'text': []}
        elif tag in INLINE:
            self._open(INLINE[tag])
        elif tag == 'hi':
            if kind == 'small-caps':
                self._open('span', ' class="sc"')
            elif HI.get(kind):
                self._open(HI[kind])
            else:
                self._open('span')
        elif tag == 'note' and not closed:
            self._open('span', ' class="c-note"')
        elif tag == 'blockquote':
            self._flush()
            self._open('blockquote')
        elif tag in ('list', 'ul', 'ol'):
            self._flush()
            self.blocks.append('<ul>')
        elif tag == 'item' or tag == 'li':
            self._flush()
        elif tag == 'table':
            self._flush()
            self.table = {'rows': [], 'row': None, 'cell': None}
        elif tag in ('row', 'tr') and self.table is not None:
            self.table['row'] = []
        elif tag in ('cell', 'td', 'th') and self.table is not None:
            self.table['cell'] = []

    def _double_break(self):
        pieces = [piece for piece in self.inline if piece.strip()]
        return bool(pieces) and pieces[-1] == '<br>'

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= 1
            return
        if tag in BLOCK_BREAK or tag in ('item', 'li'):
            self._flush()
            if tag in ('item', 'li') and self.blocks and self.blocks[-1].startswith('<p>'):
                self.blocks[-1] = '<li>' + self.blocks[-1][3:-4] + '</li>'
        elif tag in ('list', 'ul', 'ol'):
            self._flush()
            self.blocks.append('</ul>')
        elif tag == 'x-title' and self.title is not None:
            text = ''.join(self.title).strip()
            self.title = None
            if re.sub(r'<[^>]+>|\s', '', text):
                self.blocks.append(f'<h4>{text}</h4>')
        elif tag in ('reference', 'scripref', 'a') and self.ref is not None:
            ref, self.ref = self.ref, None
            self._emit(self._render_ref(ref))
        elif tag in INLINE:
            self._close(INLINE[tag])
        elif tag == 'hi':
            for candidate in ('sup', 'i', 'b', 'u', 'span'):
                if candidate in self.stack or self.ref is not None or self.title is not None:
                    self._close(candidate)
                    break
        elif tag == 'note':
            self._close('span')
        elif tag == 'blockquote':
            self._close('blockquote')
            self._flush()
            if self.blocks and self.blocks[-1].startswith('<p><blockquote>'):
                self.blocks[-1] = '<blockquote>' + self.blocks[-1][len('<p><blockquote>'):-len('</blockquote></p>')] + '</blockquote>'
        elif tag in ('cell', 'td', 'th') and self.table is not None and self.table['cell'] is not None:
            self.table['row'].append(''.join(self.table['cell']).strip())
            self.table['cell'] = None
        elif tag in ('row', 'tr') and self.table is not None and self.table['row'] is not None:
            self.table['rows'].append(self.table['row'])
            self.table['row'] = None
        elif tag == 'table' and self.table is not None:
            rows = ''.join('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in self.table['rows'])
            self.table = None
            if rows:
                self.blocks.append(f'<table>{rows}</table>')

    def handle_data(self, data):
        if self.skip:
            return
        text = html.escape(data, quote=False)
        # Geneva-style note markers: {a}, {5}
        text = re.sub(r'\{(\w{1,3})\}', r'<sup>\1</sup>', text)
        self._emit(text)

    def _render_ref(self, ref):
        text = ''.join(ref['text'])
        plain = re.sub(r'<[^>]+>', '', text)
        attrs = ref['attrs']
        if attrs.get('mybible'):
            # MySword links: #b<book number>.<chapter>.<verse>[-...]
            number, chapter, verse = re.match(r'#[bc](\d+)\.(\d+)\.?(\d*)', attrs['mybible']).groups()
            if 1 <= int(number) <= 66:
                return ref_link(BOOK_IDS[int(number) - 1], int(chapter), int(verse or 1), text)
            return text
        target = attrs.get('osisref') or attrs.get('passage')
        if attrs.get('osisref'):
            resolved = link_osis_ref(attrs['osisref'])
            return ref_link(*resolved, text) if resolved else text
        if target:
            match = _REF_TOKEN.search(target)
            book = book_from_name(match.group('book')) if match and match.group('book') else self.book
            if match and book:
                chapter = int(match.group('a'))
                verse = int(match.group('b')) if match.group('b') else 1
                return ref_link(book, chapter, verse, text)
            return text
        if '<' in text:
            return text
        return link_reference_list(html.unescape(plain), self.book, self.chapter)

    def result(self):
        self._flush()
        return '\n'.join(self.blocks)


def to_html(markup, source_type, book, chapter):
    # html.parser treats <title> content as raw text, so rename it before parsing.
    markup = re.sub(r'<(/?)title\b', r'<\1x-title', markup)
    markup = markup.replace('{Bogus footnote}', '')
    converter = _Converter(book, chapter)
    converter.feed(markup)
    converter.close()
    out = converter.result()
    out = re.sub(r'(<br>\s*)+</p>', '</p>', out)
    out = re.sub(r'<p>(\s*<br>)+', '<p>', out)
    return out.strip()
