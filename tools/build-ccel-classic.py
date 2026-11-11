#!/usr/bin/env python3
"""Convert a CCEL ThML book (e.g. https://ccel.org/ccel/o/owen/mort.xml) into a Classic Writings
work for the reader.

  python3 tools/build-ccel-classic.py mort.xml owen-mort "Of the Mortification of Sin in Believers" "John Owen"

Every <divN> with text of its own becomes a section, labelled with its title and the titles of the
divisions above it (the single top "Work" division is left out of the labels). Title pages, tables
of contents and indexes are skipped. Writes data/classics/<id>.txt as base64(gzip(json)):
  {"id", "title", "author", "units": [{"title": ..., "path": [...], "html": ...}]}
and prints {"id", "sections", "chars"}.
"""

import json
import re
import sys

from bible_data import write_classic
from commentary_html import to_html

DIV = re.compile(r'<(/?)div(\d)\b([^>]*)>')
SKIP_TITLE = re.compile(r'^\s*(title\s*page|indexes|index\b|table of contents|contents\b)', re.I)


def attribute(attrs, name):
    match = re.search(rf'\b{name}="([^"]*)"', attrs)
    return match.group(1).strip() if match else ''


def main():
    source, work_id, title, author = sys.argv[1:5]
    xml = open(source, encoding='utf-8').read()
    body = xml[xml.find('<ThML.body>'):] if '<ThML.body>' in xml else xml

    stack = []      # [level, title, type, skip, pieces, order]
    units = []
    position = 0
    order = 0

    def skipping():
        return any(item[3] for item in stack)

    def close_top():
        level, div_title, kind, skip, pieces, opened = stack.pop()
        if skip or skipping():
            return
        html = to_html(''.join(pieces), 'ThML', 'gen', 1)
        if not re.sub(r'<[^>]+>|\s', '', html):
            return
        labels = [item[1] for item in stack if item[1]]
        if stack and stack[0][2].lower() == 'work':
            labels = labels[1:]
        units.append({'title': div_title or (labels[-1] if labels else title), 'path': labels, 'html': html, 'order': opened})

    for match in DIV.finditer(body):
        if stack and not skipping():
            stack[-1][4].append(body[position:match.start()])
        closing, level, attrs = match.group(1), int(match.group(2)), match.group(3)
        if closing:
            while stack and stack[-1][0] >= level:
                close_top()
        else:
            div_title = re.sub(r'\s+', ' ', attribute(attrs, 'title'))
            kind = attribute(attrs, 'type')
            skip = bool(SKIP_TITLE.match(div_title)) or kind.lower() in ('titlepage', 'index', 'toc')
            order += 1
            stack.append([level, div_title, kind, skip, [], order])
        position = match.end()
    while stack:
        close_top()

    # A division's own text closes after its children; put sections back in reading order.
    units.sort(key=lambda unit: unit.pop('order'))
    print(json.dumps(write_classic(work_id, title, author, units)))


if __name__ == '__main__':
    main()
