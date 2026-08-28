import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const required = [
  'app/layout.js',
  'app/page.js',
  'app/globals.css',
  'components/ShivaShell.js',
  'app/api/players/route.js',
  'app/api/edge/route.js',
  'app/api/coach/route.js',
  'app/api/espn/route.js',
  'public/shiva-trophy.png',
];

const failures = [];
for (const rel of required) {
  if (!fs.existsSync(path.join(root, rel))) failures.push(`Missing required file: ${rel}`);
}

const packageJson = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
if (!packageJson.dependencies?.next) failures.push('Next.js dependency is missing.');
if (!packageJson.scripts?.build?.includes('next build')) failures.push('Build script is not Next.js native.');

const textFiles = [];
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['.git', '.next', 'node_modules'].includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.(js|mjs|json|css|md|yml|yaml|txt)$/i.test(entry.name)) textFiles.push(full);
  }
}
walk(root);
const combined = textFiles.map((file) => fs.readFileSync(file, 'utf8')).join('\n').toLowerCase();
for (const forbidden of ['streamlit', 'sttoolbar', 'ststatuswidget']) {
  if (combined.includes(forbidden)) failures.push(`Legacy Streamlit marker found: ${forbidden}`);
}

const css = fs.readFileSync(path.join(root, 'app/globals.css'), 'utf8');
if (!/html\{[^}]*background:var\(--bg\)/.test(css)) failures.push('Root html background is not locked to Shiva navy.');
if (!/\.splash\{[^}]*background:#071426/.test(css)) failures.push('Splash background is not locked to Shiva navy.');
if (/background:\s*(white|#fff(?:fff)?)/i.test(css)) failures.push('White background found in app CSS; this can cause startup flashes.');

if (failures.length) {
  console.error('\nShiva Vercel-native verification FAILED:\n');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('Shiva Vercel-native verification passed.');
console.log(`Checked ${required.length} required files and ${textFiles.length} text files.`);
