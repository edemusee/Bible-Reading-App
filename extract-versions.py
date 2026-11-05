#!/usr/bin/env python3

import json
import re
import os
from pathlib import Path

print('Reading index.html...')
with open('index.html', 'r', encoding='utf8') as f:
    html = f.read()

# Extract the EMBEDDED_PAYLOADS line (it's on line 633)
print('Extracting EMBEDDED_PAYLOADS...')
match = re.search(r'const EMBEDDED_PAYLOADS = (\{.*?\});', html, re.DOTALL)
if not match:
    print('ERROR: Could not find EMBEDDED_PAYLOADS')
    exit(1)

print('Parsing JSON...')
payloads = json.loads(match.group(1))
versions = list(payloads.keys())

print(f'Found {len(versions)} versions')

# Create data directory
Path('data').mkdir(exist_ok=True)

# Extract each version to its own file
for idx, version in enumerate(versions):
    data = payloads[version]
    filename = f'data/{version}.txt'
    with open(filename, 'w', encoding='utf8') as f:
        f.write(data)
    size_kb = len(data) / 1024
    print(f'[{idx + 1}/{len(versions)}] Extracted {version} ({size_kb:.1f} KB)')

# Create a manifest
manifest = {
    'versions': [
        {
            'id': v,
            'file': f'data/{v}.txt',
            'size': len(payloads[v])
        }
        for v in versions
    ],
    'totalVersions': len(versions),
    'extractedAt': '2026-10-08'
}

with open('data/manifest.json', 'w', encoding='utf8') as f:
    json.dump(manifest, f, indent=2)

print('\nManifest written to data/manifest.json')
print('Extraction complete!')
