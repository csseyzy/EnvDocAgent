# learn-postgresql Deployment Document

## Platform

- Base image: `node:10-slim` (Node.js 10-12 for dependency compatibility)
- Node.js: 10.x or 12.x
- PostgreSQL: required

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 postgresql postgresql-contrib sudo
```

## Build Steps

```bash
service postgresql start
sleep 3
sudo -u postgres createdb codeface
sudo -u postgres psql -d codeface -f schema.sql
```

```bash
cd /app/learn-postgresql
npm install
```

The `postinstall` script runs `npm run recreate` which needs PostgreSQL running with the `postgres` user.

## Test Steps

```bash
service postgresql start
npm run quick
```

Test framework: tap (`tap ./test/*.test.js`)

## Unexpected Issues

- **Node.js version is critical**: The dependency chain `cheerio -> htmlparser2 -> entities` breaks on Node.js 18 because `entities` declares `"type": "module"` but `htmlparser2` uses `require()` (CommonJS)
- Use Node.js 10-12 to avoid the ES Module conflict entirely
- The source code `server/db.js` defaults to `postgres://postgres:@localhost/codeface` - keep the default `postgres` user
- The `postinstall` script uses `psql -U postgres`, so the whole project expects the `postgres` user
- If using Node.js 18+, fix the ESM issue: `sed -i 's/"type": "module"/"type": "commonjs"/' node_modules/htmlparser2/node_modules/entities/package.json`
