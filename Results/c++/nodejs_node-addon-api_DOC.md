# node-addon-api Deployment Document

## Platform

- Tech: Node.js 18.0.0 + Node-API; node-addon-api 8.6.0

## Prerequisites

- Node.js 18.0.0

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/nodejs/node-addon-api.git
cd node-addon-api

# 2. Install dependencies (dev tools for tests/linters)
npm install

# 3. Configure environment variables (optional for tests/benchmarks)
cat > .env << 'EOF'
NAPI_VERSION=9
NODE_API_BUILD_CONFIG=Release
npm_config_debug=false
BUILD_PATH=build
npm_config_filter=.*
npm_config_benchmarks=false
EOF

echo "No init step required"

# 5. Start service
echo "No runtime service; this is a header-only library"


```

## Test Steps

```
node -e 'require("./"); console.log("ok")'

```
## Unexpected Issues

- `Error: Cannot find module 'bindings'` — dev dependencies not installed. Fix with `npm install`.
- `Node.js version too low for this module` — the current node-addon-api supports Node.js 18.x and newer. Upgrade Node.js to 18.x or newer.
- Smoke test run from the wrong directory — the require path `./` is resolved relative to the current working directory. Run from the project root.
