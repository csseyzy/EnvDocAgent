# elementor Deployment Document

## Platform

- Base image: `node:14-slim` (Node.js 14 avoids `fs.write` callback issue)
- Node.js: 14.x

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
```

## Build Steps


In `lib/config-helper.js` line 21, add callback to `fs.write()`:

```javascript
fs.write(info.fd, fileContents, function(writeErr) {
  if (writeErr) throw Error('Error writing to file');
  fs.close(info.fd, function(err) {
    if (err) throw Error('Error closing file');
    deferred.resolve(info.path);
  });
});
```

Using Node.js 14 avoids this issue entirely.


```bash
cd /app/elementor
npm install
```

## Test Steps

### Unit tests only (no server needed)

```bash
./node_modules/.bin/jasmine-node test/config-helper-spec.js test/locatorFinder-spec.js --verbose --forceExit
```

### All tests including HTTP integration (requires running server)

```bash
# Start the elementor server in background
node bin/elementor.js --nonAngular http://www.protractortest.org &
sleep 5

# Run all tests
./node_modules/.bin/jasmine-node test/ --verbose --forceExit
```

## Unexpected Issues

- 5/17 test failures were caused by HTTP integration tests connecting to `http://localhost:13000` without the elementor server running
- On Node.js 18+, `fs.write()` without callback throws an error - use Node.js 14 or patch `config-helper.js`
- Project dependencies (`protractor: 4.0.11`, `q: 2.0.3`) are from the Node.js 6-14 era
