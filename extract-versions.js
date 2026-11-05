#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('Reading index.html...');
const html = fs.readFileSync('index.html', 'utf8');

// Extract the EMBEDDED_PAYLOADS line
const payloadsMatch = html.match(/const EMBEDDED_PAYLOADS = ({.*?});/s);
if (!payloadsMatch) {
  console.error('Could not find EMBEDDED_PAYLOADS in index.html');
  process.exit(1);
}

console.log('Parsing embedded payloads...');
const payloads = JSON.parse(payloadsMatch[1]);
const versions = Object.keys(payloads);

console.log(`Found ${versions.length} versions`);

// Create data directory
if (!fs.existsSync('data')) {
  fs.mkdirSync('data');
}

// Extract each version to its own file
versions.forEach((version, idx) => {
  const data = payloads[version];
  const filename = `data/${version}.txt`;
  fs.writeFileSync(filename, data, 'utf8');
  console.log(`[${idx + 1}/${versions.length}] Extracted ${version} (${(data.length / 1024).toFixed(1)} KB)`);
});

// Create a manifest
const manifest = {
  versions: versions.map(v => ({
    id: v,
    file: `data/${v}.txt`,
    size: payloads[v].length
  })),
  totalVersions: versions.length,
  extractedAt: new Date().toISOString()
};

fs.writeFileSync('data/manifest.json', JSON.stringify(manifest, null, 2));
console.log('\nManifest written to data/manifest.json');
console.log('Extraction complete!');
