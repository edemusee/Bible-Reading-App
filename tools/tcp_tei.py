"""Shared helpers for reading EEBO-TCP TEI transcriptions (CC0, https://github.com/textcreationpartnership)."""

import html
import re


def strip_ns(tree):
    for element in tree.iter():
        if isinstance(element.tag, str) and '}' in element.tag:
            element.tag = element.tag.split('}', 1)[1]


def inline_html(element):
    """Text of an element as small HTML, dropping marginal notes, page breaks and gaps."""
    parts = [html.escape(element.text or '', quote=False)]
    for child in element:
        tag = child.tag
        if tag in ('note', 'pb', 'fw', 'figure'):
            pass
        elif tag == 'gap':
            parts.append('…')
        elif tag == 'g' and 'EOLhyphen' in (child.get('ref') or ''):
            pass
        elif tag == 'lb':
            parts.append(' ' if (child.get('rend') or '') != 'hidden' else '')
        elif tag == 'hi':
            parts.append(f'<i>{inline_html(child)}</i>')
        else:
            parts.append(inline_html(child))
        parts.append(html.escape(child.tail or '', quote=False))
    return ''.join(parts)


def clean(text):
    text = text.replace('ſ', 's').replace('∣', '').replace('&amp;', '&amp;')
    return re.sub(r'\s+', ' ', text).strip()
