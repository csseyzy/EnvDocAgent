# telepat-api Deployment Document

## Platform

- Base image: `node:4.8.3`
- Node.js: 4.8.3, npm 2.x

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 build-essential=12.10ubuntu1 python make=4.3-4.1build2 g++=4:13.2.0-7ubuntu1 redis-server
```

## Build Steps

```bash
cd /app/telepat-api
cp config.example.json config.json
npm install
npm install -g mocha istanbul
```


Edit `config.json` to point to localhost services:

```bash
sed -i 's/"host": "10.0.0.1"/"host": "127.0.0.1"/' config.json
sed -i 's/"host": "10.0.0.2"/"host": "127.0.0.1"/' config.json
```

## Test Steps

```bash
redis-server --daemonize yes
npm test
```

## Unexpected Issues

- Must use **Node.js 4.8.3** - native modules (`bcrypt 0.8.5`, `hiredis 0.5.0`, `lz4`/`xxhash`) fail on modern Node.js
- Tests are integration tests requiring Redis at minimum; full stack needs Redis + Elasticsearch + Kafka/RabbitMQ
- `lz4` depends on `xxhash` native addon which requires Python 2 + old node-gyp
- The `before all` hook starts the Express app which connects to Redis - without Redis, all tests fail
- `config.example.json` has hosts pointing to `10.0.0.x` (internal IPs) - must be changed to `127.0.0.1`
