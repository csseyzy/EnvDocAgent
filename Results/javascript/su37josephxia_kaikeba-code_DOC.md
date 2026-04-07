# kaikeba-code Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: 18.x
- MongoDB: 7.0

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 curl=8.5.0-2ubuntu10.8 build-essential=12.10ubuntu1 python3=3.12.3-0ubuntu2 \
    libcairo2-dev=1.18.0-3build1 libjpeg-dev=8c-2ubuntu11 libpango1.0-dev libgif-dev
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
```

## Build Steps

```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb.gpg
echo "deb [signed-by=/usr/share/keyrings/mongodb.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" > /etc/apt/sources.list.d/mongodb.list
apt-get update && apt-get install -y mongodb-org
mkdir -p /data/db
```

```bash
mongod --fork --logpath /var/log/mongod.log --dbpath /data/db

cd /app/kaikeba-code/node/08/egg-server
npm install
```

## Test Steps

```bash
# Start MongoDB first
mongod --fork --logpath /var/log/mongod.log --dbpath /data/db

cd /app/kaikeba-code/node/08/egg-server
npm run test-local
```

## Unexpected Issues

- The egg-server tests require a running MongoDB instance at `127.0.0.1:27017` - without it, all tests fail with `ECONNREFUSED`
- Most sub-modules have placeholder test scripts (`"test": "echo \"Error: no test specified\" && exit 1"`)
- The Dockerfile used Node.js 10.x (EOL) but the actual run used Node.js 18 - use Node.js 18.x
- The taobao npm registry (`registry.npm.taobao.org`) is deprecated - use default registry or `registry.npmmirror.com`
- Only `node/08/egg-server` has real tests; other modules like `node/07/egg` and `node/07/mvc` may also have tests
