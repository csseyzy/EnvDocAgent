# openzeppelin-labs Deployment Document

## Platform

- Base image: `node:16-bullseye`
- Node.js: 16.x

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 python3=3.12.3-0ubuntu2 build-essential=12.10ubuntu1
npm install -g ganache-cli truffle
```

## Build Steps


Some sub-projects are missing `migrations/` directories required by Truffle:

```bash
for dir in initializable_with_multiple_inheritance initializer_with_sol_editing upgradeability_using_eternal_storage upgradeability_using_inherited_storage upgradeability_using_unstructured_storage; do
  if [ -d "$dir" ] && [ ! -d "$dir/migrations" ]; then
    mkdir -p "$dir/migrations"
    echo "module.exports = function(deployer) {};" > "$dir/migrations/1_initial_migration.js"
  fi
done
```


```bash
cd /app/openzeppelin-labs
npm install
npm run install-all
```

## Test Steps

```bash
# Start Ganache in background
ganache-cli --port 8545 --deterministic --quiet --networkId 1337 --gasLimit 8000000 &
sleep 3

# Run tests per sub-project with timeout
for dir in $(find . -maxdepth 1 -type d ! -name . ! -name scripts ! -name node_modules); do
  if [ -f "$dir/package.json" ]; then
    echo "=== Testing $dir ==="
    (cd "$dir" && timeout 120s npm test 2>&1) || echo "FAILED: $dir"
  fi
done
```

## Unexpected Issues

- Monorepo with ~15 independent sub-projects, each with their own `package.json` and `truffle.js`
- Several sub-projects are missing `migrations/` directories - Truffle requires them even for `truffle test`
- The root `npm test` runs `scripts/test.sh` which iterates all sub-dirs and can hang on projects needing Ganache
- Each sub-project's `truffle.js` needs a development network config pointing to `localhost:8545` (most have this as default)
