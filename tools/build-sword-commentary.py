#!/usr/bin/env python3
"""Convert a CrossWire SWORD commentary module (zCom / zCom4) into this reader's format.

Requires pysword for the KJV versification table:  pip install pysword

Download and unzip a module, e.g.
  https://www.crosswire.org/ftpmirror/pub/sword/packages/rawzip/MHC.zip
then run:

  python3 tools/build-sword-commentary.py <unzipped module dir> <commentary id>

Writes data/commentaries/<id>/<book>.txt, one file per book, each base64(gzip(json)):
  {"intro": "<html>" | null, "chapters": {"1": [[start_verse, end_verse, "<html>"], ...]}}
Start verse 0 is the chapter introduction. Notes SWORD links across several verses are
stored once with their verse range. Prints {"bookIds": [...]} for the COMMENTARIES list.
"""

import glob
import json
import re
import struct
import sys
import zlib
from pathlib import Path

from pysword.canons import canons

from commentary_html import to_html
from bible_data import BOOK_IDS, write_commentary_book


def read_conf(module_dir):
    conf_path = next(Path(module_dir, 'mods.d').glob('*.conf'))
    text = conf_path.read_text(encoding='latin-1')

    def get(key, default=''):
        match = re.search(rf'^{key}=(.*)$', text, re.M | re.I)
        return match.group(1).strip() if match else default

    return {
        'driver': get('ModDrv').lower(),
        'encoding': 'utf-8' if get('Encoding').upper() == 'UTF-8' else 'latin-1',
        'block': (get('BlockType', 'BOOK') or 'BOOK')[0].lower(),
        'source': get('SourceType', 'GBF').upper(),
    }


class Module:
    def __init__(self, module_dir):
        self.conf = read_conf(module_dir)
        data_dir = Path(glob.glob(f'{module_dir}/modules/comments/*/*/')[0])
        self.record = '<III' if self.conf['driver'].endswith('4') else '<IIH'
        self.record_size = struct.calcsize(self.record)
        self.files = {}
        for testament in ('ot', 'nt'):
            names = [data_dir / f'{testament}.{self.conf["block"]}z{ext}' for ext in 'svz']
            if names[1].exists():
                self.files[testament] = [name.read_bytes() for name in names]
        self.blocks = {}

    def entry(self, testament, index):
        """Return ((block, start, length), text) or None for an empty entry."""
        if testament not in self.files:
            return None
        block_index, verse_index, compressed = self.files[testament]
        position = self.record_size * index
        if position + self.record_size > len(verse_index):
            return None
        block, start, length = struct.unpack(self.record, verse_index[position:position + self.record_size])
        if not length:
            return None
        if (testament, block) not in self.blocks:
            offset, size, _ = struct.unpack('<III', block_index[12 * block:12 * block + 12])
            self.blocks[(testament, block)] = zlib.decompress(compressed[offset:offset + size])
        raw = self.blocks[(testament, block)][start:start + length]
        return (block, start, length), raw.decode(self.conf['encoding'], 'replace')


def main():
    module_dir, commentary_id = sys.argv[1], sys.argv[2]
    module = Module(module_dir)
    book_ids = []
    for testament, offset in (('ot', 0), ('nt', 39)):
        index = 2  # each testament starts with two header entries
        for book_number, (_, _, _, chapter_lengths) in enumerate(canons['kjv'][testament]):
            book_id = BOOK_IDS[offset + book_number]
            book_entry = module.entry(testament, index)
            intro = to_html(book_entry[1], module.conf['source'], book_id, 1) if book_entry else None
            chapters = {}
            index += 1
            for chapter, verse_count in enumerate(chapter_lengths, 1):
                notes = []
                previous_key = None
                for verse in range(0, verse_count + 1):  # verse 0 = chapter introduction
                    found = module.entry(testament, index)
                    index += 1
                    if not found:
                        previous_key = None
                        continue
                    key, text = found
                    if key == previous_key and verse > 1:
                        notes[-1][1] = verse  # SWORD link: same note covers this verse too
                        continue
                    previous_key = key
                    html = to_html(text, module.conf['source'], book_id, chapter)
                    if html:
                        notes.append([verse, verse, html])
                if notes:
                    chapters[str(chapter)] = notes
            if chapters or intro:
                write_commentary_book(commentary_id, book_id, {'intro': intro, 'chapters': chapters})
                book_ids.append(book_id)
    print(json.dumps({'bookIds': book_ids}))


if __name__ == '__main__':
    main()
