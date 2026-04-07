# auctionhouse Deployment Document

## Platform

- Base image: `ubuntu:20.04`
- Node.js: 8.x or 10.x (for Truffle v4 + node-sass compatibility)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.25.1-1ubuntu3 build-essential=12.8ubuntu1 python3=3.8.2-0ubuntu2 curl=7.68.0-1ubuntu2
curl -fsSL https://deb.nodesource.com/setup_10.x | bash -
apt-get install -y nodejs
```

## Build Steps


Migration files reference undeclared artifacts. Add imports at the top of each file:

- `migrations/2_deploy_contracts.js`: add `var SampleName = artifacts.require("SampleName");`
- `migrations/3_deploy_auctionhouse.js`: add `var AuctionHouse = artifacts.require("AuctionHouse");`
- Test files (`test/Simple.js`, `test/AuctionHouse.js`, `test/FullAuctionTest.js`, `test/MultipleBidTest.js`): add `var SampleName = artifacts.require("SampleName");` and `var AuctionHouse = artifacts.require("AuctionHouse");` at top


```bash
npm install -g truffle@4.1.16 ganache-cli

cd /app/auctionhouse
npm install
```

## Test Steps

```bash
# Start ganache-cli in background
ganache-cli --port 8545 > /dev/null 2>&1 &
sleep 3

# Compile and test
truffle compile
truffle test
```

## Unexpected Issues

- Must use **Truffle v4** (not v5) - the project uses `truffle.js` config format, `truffle-default-builder`, and web3 0.x API patterns
- A local Ethereum blockchain (ganache-cli) must be running before any `truffle test` command
- node-sass requires Python 2 + old Node.js for native compilation
