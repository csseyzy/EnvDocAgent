# wordlists Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: LTS

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 curl=8.5.0-2ubuntu10.8
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt-get install -y nodejs
```

## Build Steps

No build step needed - the project is a collection of plain text files with a validation script.

## Test Steps

The existing `test.js` checks for duplicate entries in .txt files but always exits 0 (even when duplicates are found):

```bash
cd /app/wordlists
node test.js
```

For a proper pass/fail test, use a wrapper that exits non-zero on duplicates:

```bash
node -e "
const fs = require('fs');
const path = require('path');
let failures = 0, total = 0;
function walk(dir, cb) {
  fs.readdirSync(dir).forEach(f => {
    const p = path.join(dir, f);
    fs.statSync(p).isDirectory() ? walk(p, cb) : cb(p);
  });
}
walk('.', f => {
  if (!f.endsWith('.txt') || f === 'test.js') return;
  total++;
  const lines = fs.readFileSync(f, 'utf8').split('\n').filter(l => l);
  const dupes = lines.filter((l, i) => lines.indexOf(l) !== i);
  if (dupes.length) { failures++; console.log('FAIL:', f, 'dupes:', dupes); }
  else { console.log('PASS:', f); }
});
console.log(total + ' files, ' + (total - failures) + ' passed, ' + failures + ' failed');
process.exit(failures > 0 ? 1 : 0);
"
```

## Unexpected Issues

- `test.js` is a data validation script, not a traditional test suite - it uses `assert` but catches errors and only logs them
- The script exits 0 regardless of whether duplicates are found, so it's not a proper pass/fail test
- There's no `package.json`, no test framework (Mocha, Jest, etc.), no `npm test` command
- Known duplicates: `spicy` in food.txt, `Moncada` in spain.txt
- To make this a proper test, modify `test.js` to exit non-zero on duplicates, or add a `package.json` with a test script
