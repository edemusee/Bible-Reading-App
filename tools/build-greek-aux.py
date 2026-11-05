#!/usr/bin/env python3
"""Build the SBLGNT Greek lexical aids (word tokens + lemma lexicon) for the reader.

Source: MACULA Greek, SBLGNT edition (c) Biblica, Inc., CC BY 4.0
  https://github.com/Clear-Bible/macula-greek
  - SBLGNT/tsv/macula-greek-SBLGNT.tsv
  - sources/MARBLE/SDBG/marble-domain-label-mapping.json

Usage:
  python3 tools/build-greek-aux.py <macula-greek-SBLGNT.tsv> <marble-domain-label-mapping.json>

Writes data/grc_sblgnt_tokens.txt and data/grc_sblgnt_lexicon.txt in the same
base64(gzip(json)) format as the other data files.
"""

import base64
import csv
import gzip
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'

BOOKS = {
    'MAT': 'matt', 'MRK': 'mark', 'LUK': 'luke', 'JHN': 'john', 'ACT': 'acts',
    'ROM': 'rom', '1CO': '1cor', '2CO': '2cor', 'GAL': 'gal', 'EPH': 'eph',
    'PHP': 'phil', 'COL': 'col', '1TH': '1thess', '2TH': '2thess', '1TI': '1tim',
    '2TI': '2tim', 'TIT': 'titus', 'PHM': 'phlm', 'HEB': 'heb', 'JAS': 'jas',
    '1PE': '1pet', '2PE': '2pet', '1JN': '1john', '2JN': '2john', '3JN': '3john',
    'JUD': 'jude', 'REV': 'rev',
}

# Field order must match TOKEN in index.html.
TEXT, NORMALIZED, LEMMA, STRONG, POS, MORPH_CODE, MORPH, GLOSS, DOMAIN, LOUW_NIDA = range(10)

POS_LABELS = {
    'adj': 'Adjective', 'adv': 'Adverb', 'conj': 'Conjunction', 'det': 'Article',
    'intj': 'Interjection', 'noun': 'Noun', 'num': 'Numeral', 'prep': 'Preposition',
    'ptcl': 'Particle', 'pron': 'Pronoun', 'verb': 'Verb',
}
PERSON = {'first': '1st person', 'second': '2nd person', 'third': '3rd person'}


def encode(obj):
    raw = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode('ascii')


def decode(path):
    return json.loads(gzip.decompress(base64.b64decode(path.read_text())))


def pos_label(row):
    label = POS_LABELS.get(row['class'], row['class'].capitalize())
    if row['class'] == 'noun' and row['type'] == 'proper':
        label = 'Proper noun'
    if row['class'] == 'verb' and row['mood'] == 'participle':
        label = 'Verb (participle)'
    if row['class'] == 'verb' and row['mood'] == 'infinitive':
        label = 'Verb (infinitive)'
    return label


def morph_label(row):
    if row['class'] == 'verb':
        parts = [row['tense'], row['voice'], row['mood']]
        if row['mood'] == 'participle':
            parts += [row['case'], row['number'], row['gender']]
        elif row['mood'] != 'infinitive':
            parts += [PERSON.get(row['person'], row['person']), row['number']]
    else:
        parts = [PERSON.get(row['person'], row['person']), row['case'], row['number'], row['gender'], row['degree']]
    return ' '.join(p for p in parts if p)


def domain_label(code, labels):
    top = labels.get(code[:3], '')
    sub = labels.get(code, '')
    if top and sub and sub != top:
        return f'{top} › {sub}'
    return top or sub or code


def comparable(text):
    text = unicodedata.normalize('NFD', text.lower())
    return re.sub(r'[^α-ω]', '', ''.join(c for c in text if not unicodedata.combining(c)))


def main():
    tsv_path, labels_path = map(Path, sys.argv[1:3])
    labels = json.loads(labels_path.read_text(encoding='utf-8'))

    tokens = defaultdict(list)
    lex = defaultdict(lambda: {
        'occurrences': 0, 'forms': Counter(), 'glosses': Counter(), 'semantic_domains': Counter(),
        'louw_nida': Counter(), 'strongs': Counter(), 'part_of_speech': Counter(),
    })

    with tsv_path.open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle, delimiter='\t', quoting=csv.QUOTE_NONE):
            book, rest = row['ref'].split(' ', 1)
            chapter, verse = rest.split('!')[0].split(':')
            key = f'{BOOKS[book]}|{int(chapter)}|{int(verse)}'

            domains = [domain_label(code, labels) for code in row['domain'].split()]
            ln_entries = row['ln'].split()
            strong = f"G{row['strong']}" if row['strong'] else ''
            pos = pos_label(row)
            english = row['english'].strip()

            tokens[key].append([
                row['text'] + row['after'].strip(),
                row['normalized'],
                row['lemma'],
                strong,
                pos,
                row['morph'],
                morph_label(row),
                row['gloss'].strip(),
                '; '.join(domains),
                ', '.join(ln_entries),
            ])

            entry = lex[row['lemma']]
            entry['occurrences'] += 1
            entry['forms'][row['normalized']] += 1
            if english:
                entry['glosses'][english] += 1
            for label in domains:
                entry['semantic_domains'][label] += 1
            for ln in ln_entries:
                entry['louw_nida'][ln] += 1
            if strong:
                entry['strongs'][strong] += 1
            entry['part_of_speech'][pos] += 1

    lexicon = {
        lemma: {
            'occurrences': e['occurrences'],
            'forms': [{'form': k, 'occurrences': n} for k, n in e['forms'].most_common()],
            'glosses': [{'gloss': k, 'occurrences': n} for k, n in e['glosses'].most_common(12)],
            'semantic_domains': [{'domain': k, 'occurrences': n} for k, n in e['semantic_domains'].most_common(12)],
            'louw_nida': [{'entry': k, 'occurrences': n} for k, n in e['louw_nida'].most_common(12)],
            'strongs': [{'number': k, 'occurrences': n} for k, n in e['strongs'].most_common()],
            'part_of_speech': [k for k, _ in e['part_of_speech'].most_common()],
        }
        for lemma, e in lex.items()
    }

    # Check every verse of the reader's SBLGNT text against the token stream.
    text = decode(DATA / 'grc_sblgnt.txt')
    mismatched, missing, verses = [], [], 0
    for book in text['books']:
        for c, chapter in enumerate(book['chapters'], 1):
            for v, verse_text in enumerate(chapter, 1):
                if not verse_text.strip():
                    continue
                verses += 1
                key = f"{book['id']}|{c}|{v}"
                if key not in tokens:
                    missing.append(key)
                elif comparable(verse_text) != comparable(''.join(t[TEXT] for t in tokens[key])):
                    mismatched.append(key)
    extra = sorted(set(tokens) - {f"{b['id']}|{c}|{v}" for b in text['books'] for c, ch in enumerate(b['chapters'], 1) for v, _ in enumerate(ch, 1)})
    print(f'{sum(map(len, tokens.values()))} tokens, {len(tokens)} verses, {len(lexicon)} lemmas')
    print(f'reader verses: {verses}; missing tokens: {len(missing)}; text mismatches: {len(mismatched)}; token-only verses: {len(extra)}')
    for label, keys in (('missing', missing), ('mismatch', mismatched), ('extra', extra)):
        if keys:
            print(f'  {label}: {keys[:15]}')

    (DATA / 'grc_sblgnt_tokens.txt').write_text(encode(tokens))
    (DATA / 'grc_sblgnt_lexicon.txt').write_text(encode(lexicon))


if __name__ == '__main__':
    main()
