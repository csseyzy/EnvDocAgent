# SpaceTalk Deployment Document

## Platform

- Base image: `ubuntu:14.04` or `ubuntu:16.04` (for Meteor 1.1.x compatibility)
- Meteor: 1.1.0.2 (pinned in `.meteor/release`)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 curl=8.5.0-2ubuntu10.8 build-essential=12.10ubuntu1 python
```

## Build Steps


The local package `packages/useraccounts-core/package.js` uses deprecated Meteor 1.0-era APIs:

- Replace `Package.on_use` with `Package.onUse`
- Replace `api.add_files` with `api.addFiles`

```bash
cd /app/SpaceTalk
sed -i 's/Package.on_use/Package.onUse/g' packages/useraccounts-core/package.js
sed -i 's/api.add_files/api.addFiles/g' packages/useraccounts-core/package.js
```


```bash
curl https://install.meteor.com/?release=1.1.0.2 | sh
export PATH="/root/.meteor:$PATH"
export METEOR_ALLOW_SUPERUSER=1
```

## Test Steps

The only automated tests are in the local package `packages/useraccounts-core`:

```bash
export METEOR_ALLOW_SUPERUSER=1
cd /app/SpaceTalk
meteor test-packages ./packages/useraccounts-core --once --driver-package test-in-console
```

## Unexpected Issues

- **Massive version mismatch**: app is `METEOR@1.1.0.2` (2015) but latest Meteor is 3.4 (2025)
- Modern Meteor breaks `Package.on_use` / `api.add_files` (deprecated APIs removed in Meteor 2+)
- `meteor test-packages` may hit `CERT_UNTRUSTED` errors when downloading Atmosphere packages on old Meteor
- No root `package.json` exists - this is a pure Meteor app with Atmosphere packages only
- For a working deployment, either pin an old Meteor + old base image, or plan a full Meteor modernization
- The `--once` flag is critical to prevent Meteor from entering watch mode
