#!/usr/bin/env python3
"""Convert Robert Haldane's Exposition of Romans from the godrules.net HTML pages
(https://www.godrules.net/library/haldane/31haldane0.htm ... 31haldane24.htm) into this
reader's format.

  python3 tools/build-haldane-commentary.py <folder with 31haldane*.htm or haldane*.htm> haldane

Each page's <title> names the chapter ("... ROMANS - CHAPTER 3"); comments start at
"<p> Ver. N" paragraphs. The site wraps ordinary words in shop links, so every <a> tag is
dropped. A verse number that runs backwards within a chapter (a typo such as 2 for 27) is
read as the next verse. Pages before the first chapter form the book introduction.
"""

import json
import re
import sys
from pathlib import Path

from bible_data import write_commentary_book
from commentary_html import to_html

VERSE = re.compile(r'<p>\s*Ver\.\s*(\d+)')
NAVIGATION = re.compile(r'(NEXT|PREVIOUS) CHAPTER|GOTO|INDEX &amp; SEARCH|HELP - VIDEOS|YOUTUBE')
INTRO_PAGES = ('FOREWORD', 'PREFACE', 'INTRODUCTION')


def without_navigation(html):
    return '\n'.join(block for block in html.split('\n') if not NAVIGATION.search(block))


def main():
    folder, commentary_id = Path(sys.argv[1]), sys.argv[2]
    pages = sorted(folder.glob('*haldane*.htm'), key=lambda path: int(re.search(r'(\d+)\.htm$', path.name).group(1)))
    content = {'intro': None, 'chapters': {}}
    intro = []
    for page in pages:
        raw = page.read_text(encoding='latin-1')
        title = re.search(r'<title>(.*?)</title>', raw, re.S)
        title = title.group(1) if title else ''
        chapter = re.search(r'CHAPTER\s+(\d+)', title)
        chapter = chapter.group(1) if chapter else None
        body = re.search(r'<body[^>]*>(.*)</body>', raw, re.S | re.I)
        body = re.sub(r'</?a\b[^>]*>', '', body.group(1) if body else raw)
        body = re.sub(r'<(script|style|form|select|table)\b.*?</\1>', '', body, flags=re.S | re.I)
        markers = list(VERSE.finditer(body))
        if not chapter and markers:
            # "EXPOSITION" opens chapter 1 without saying so in its title.
            chapter = str(max(map(int, content['chapters']), default=1))
        if not chapter:
            if any(name in title for name in INTRO_PAGES):
                intro.append(body)
            continue
        notes = content['chapters'].setdefault(chapter, [])
        for index, marker in enumerate(markers):
            verse = int(marker.group(1))
            if notes and verse <= notes[-1][0]:
                verse = notes[-1][0] + 1
            end = markers[index + 1].start() if index + 1 < len(markers) else len(body)
            html = without_navigation(to_html(body[marker.start():end], 'HTML', 'rom', int(chapter)))
            if html:
                notes.append([verse, verse, html])
    if intro:
        content['intro'] = without_navigation(to_html('\n'.join(intro), 'HTML', 'rom', 1)) or None
    write_commentary_book(commentary_id, 'rom', content)
    print(json.dumps({'bookIds': ['rom']}))


if __name__ == '__main__':
    main()
