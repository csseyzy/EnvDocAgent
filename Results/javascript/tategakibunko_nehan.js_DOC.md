# nehan.js Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: 18+ (for Puppeteer)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 curl=8.5.0-2ubuntu10.8
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
```

## Build Steps

The project has no `package.json`. Install tooling manually:

```bash
cd /app/nehan_js
npm init -y
npm install gulp gulp-concat gulp-uglify gulp-rename gulp-ignore
npm install jasmine-core puppeteer http-server
```

Build the concatenated library:

```bash
npx gulp nehan.js
```

## Test Steps


```bash
mkdir -p static/jasmine static/js
cp node_modules/jasmine-core/lib/jasmine-core/jasmine.js static/jasmine/
cp node_modules/jasmine-core/lib/jasmine-core/jasmine-html.js static/jasmine/
cp node_modules/jasmine-core/lib/jasmine-core/boot.js static/jasmine/
cp node_modules/jasmine-core/lib/jasmine-core/jasmine.css static/jasmine/
cp dist/nehan.js static/js/
```

```bash
npx http-server -p 8080 &
sleep 2
# Use Puppeteer to open http://localhost:8080/tests/index.html
# and scrape Jasmine results from the DOM
node run_tests.js
```

## Unexpected Issues

- No `package.json` exists in the repo - no npm/build system
- The `/static/` directory referenced by `tests/index.html` does not exist in the repo - must be created with Jasmine framework files and the built library
- The Gulp build concatenates source files from `src/` into `dist/nehan.js`
- Tests are browser-based Jasmine specs - require an HTTP server + headless browser
