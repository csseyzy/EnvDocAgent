# ZeroToBlockchain Deployment Document

## Platform

- Base image: `node:8-stretch`
- Node.js: 8.x (required by Hyperledger Composer ^0.16.2)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 python make=4.3-4.1build2 g++=4:13.2.0-7ubuntu1
```

## Build Steps

```bash
cd /app/ZeroToBlockchain/Chapter06
npm install
```

## Test Steps

Tests are pure integration tests requiring a live Hyperledger Fabric blockchain network (4-6 Docker containers: peer, orderer, CA, CouchDB).

```bash
cd /app/ZeroToBlockchain/Chapter06
npm test
```

### Alternative: Use embedded connector for unit testing


### Lint check only (no blockchain needed)

```bash
cd /app/ZeroToBlockchain/Chapter06
npx eslint ./network
```

## Unexpected Issues

- **Fundamentally untestable in a single container** - tests require a live Hyperledger Fabric blockchain network (Docker-in-Docker)
- Hyperledger Composer was **archived in 2019** - the technology is deprecated
- The test `before all` hook calls `BusinessNetworkConnection.connect('admin@zerotoblockchain-network')` which requires a deployed business network card
- Without Docker-in-Docker or Docker socket mounting, no actual tests can execute
- To make tests work without Fabric: modify test files to use `composer-connector-embedded` (in-memory runtime)
