#!/usr/bin/env python3
"""Convert an EEBO-TCP TEI transcription (CC0) into a Classic Writings work for the reader.

  python3 tools/build-tcp-classic.py A77614.xml brooks-precious-remedies "Precious Remedies Against Satan's Devices" "Thomas Brooks"

Every <div> with text of its own becomes a section titled by its <head> (or its type and number),
labelled with the headings of the divisions above it. Title pages, licences, errata, tables of
contents and indexes are skipped; marginal notes are dropped and the long s is normalised.
Writes data/classics/<id>.txt (same format as build-ccel-classic.py) and prints a summary.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET

from bible_data import write_classic
from tcp_tei import clean, inline_html, strip_ns

SKIP_TYPES = {
    'title_page', 'imprimatur', 'license', 'licence', 'errata', 'table_of_contents', 'contents', 'index',
    'colophon', 'publishers_advertisement', 'advertisement', 'catalogue', 'books_printed', 'frontispiece',
}
SKIP_HEAD = re.compile(r'^\s*(THE\s+)?(TABLE|INDEX|CONTENTS|ERRATA|A CATALOGUE)\b', re.I)
BLOCK_TAGS = {'p', 'lg', 'list', 'q', 'quote', 'epigraph', 'table', 'argument', 'opener', 'closer', 'trailer', 'byline', 'dateline', 'signed', 'salute', 'l', 'head', 'bibl', 'cit', 'sp', 'castList'}


def block_html(element):
    tag = element.tag
    if tag in ('note', 'pb', 'fw', 'figure', 'gap', 'milestone'):
        return ''
    if tag == 'head':
        text = clean(inline_html(element))
        return f'<h4>{text}</h4>' if text else ''
    if tag == 'lg':
        lines = [clean(inline_html(line)) for line in element.iter('l')]
        lines = [line for line in lines if line]
        return '<p>' + '<br>'.join(lines) + '</p>' if lines else ''
    if tag == 'list':
        items = [clean(inline_html(item)) for item in element.findall('item')]
        return '<ul>' + ''.join(f'<li>{item}</li>' for item in items if item) + '</ul>' if items else ''
    if tag == 'table':
        rows = []
        for row in element.findall('row'):
            cells = ''.join(f'<td>{clean(inline_html(cell))}</td>' for cell in row.findall('cell'))
            rows.append(f'<tr>{cells}</tr>')
        return f'<table>{"".join(rows)}</table>' if rows else ''
    if tag in ('q', 'quote', 'epigraph', 'cit', 'argument', 'opener', 'closer', 'sp'):
        inner = ''.join(block_html(child) for child in element if child.tag in BLOCK_TAGS or child.tag in ('p', 'lg'))
        if not inner:
            text = clean(inline_html(element))
            inner = f'<p>{text}</p>' if text else ''
        return f'<blockquote>{inner}</blockquote>' if inner and tag in ('q', 'quote', 'epigraph', 'cit') else inner
    text = clean(inline_html(element))
    return f'<p>{text}</p>' if text else ''


def division_title(div):
    head = div.find('head')
    if head is not None:
        text = re.sub(r'<[^>]+>', '', clean(inline_html(head)))
        if text:
            return text[:140]
    kind = (div.get('type') or 'section').replace('_', ' ')
    number = div.get('n')
    return f'{kind.capitalize()} {number}' if number else kind.capitalize()


def walk(div, path, units):
    kind = (div.get('type') or '').lower()
    title = division_title(div)
    if kind in SKIP_TYPES or SKIP_HEAD.match(title):
        return
    own = []
    first_head = True
    for child in div:
        if child.tag == 'div':
            continue
        if child.tag == 'head' and first_head:
            first_head = False
            continue  # shown as the section title
        own.append(block_html(child))
    html = '\n'.join(piece for piece in own if piece)
    if re.sub(r'<[^>]+>|\s', '', html):
        units.append({'title': title, 'path': path, 'html': html})
    for child in div:
        if child.tag == 'div':
            walk(child, path + [title], units)


def main():
    sources_and_args = sys.argv[1:]
    *sources, work_id, title, author = sources_and_args
    units = []
    for source in sources:
        tree = ET.parse(source)
        strip_ns(tree)
        text = tree.getroot().find('.//text')
        for part in text.iter():
            if part.tag in ('front', 'body', 'back'):
                for div in part.findall('div'):
                    walk(div, [], units)
    # Top-level labels are usually the whole book's title; drop a label every section shares.
    if units and all(unit['path'][:1] == units[0]['path'][:1] for unit in units) and units[0]['path']:
        for unit in units:
            unit['path'] = unit['path'][1:]
    # Old books often give many sections the same heading ("Now the Remedies against this Device
    # are these."); number repeats so the section list stays usable.
    totals, seen = {}, {}
    for unit in units:
        totals[unit['title']] = totals.get(unit['title'], 0) + 1
    for unit in units:
        if totals[unit['title']] > 1:
            seen[unit['title']] = seen.get(unit['title'], 0) + 1
            unit['title'] = f"{unit['title']} ({seen[unit['title']]})"
    print(json.dumps(write_classic(work_id, title, author, units)))


if __name__ == '__main__':
    main()
